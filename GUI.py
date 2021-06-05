from EditDistance import *
import tkinter as tk
import re


class EditApplication(tk.Tk):
    curr_frame = 0

    def __init__(self):
        tk.Tk.__init__(self)
        self.editDistance = EditDistance()

        container = tk.Frame(self)
        self.title("Edit Distance")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.container = container

        bottom = tk.Frame(self)
        bottom.pack(side="bottom", fill="x", expand=True)
        tk.Button(bottom, text="Prev", width=10, height=1, command=self.prev_frame).pack(side="left", expand=True)
        tk.Button(bottom, text="Next", width=10, height=1, command=self.next_frame).pack(side="left", expand=True)

        self.frames = []
        for F in (StartPage, AlphabetInput, WeightsInput, StringsInput, ResultShow):
            frame = F(parent=container, controller=self)
            self.frames.append(frame)
            frame.grid(row=0, column=0, sticky="nsew")

        self.frames[self.curr_frame].tkraise()

    def prev_frame(self):
        # on click of "previous" button
        if self.curr_frame > 0:
            self.curr_frame -= 1
        self.frames[self.curr_frame].tkraise()

    def next_frame(self):
        # on click of "next" button
        self.frames[self.curr_frame].on_next()
        if self.curr_frame < len(self.frames) - 1:
            self.curr_frame += 1

        frame = self.frames[self.curr_frame]
        frame.on_entry()
        frame.tkraise()


class AbsFrame(tk.Frame):
    """ Abstract Frame """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def on_entry(self):
        """ before showing this frame """
        pass

    def on_next(self):
        """ before leaving this frame """
        pass


class StartPage(AbsFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        label = tk.Label(self, text="Calcolatore per la\nDistanza di Edit")
        label.pack(side="top", fill="x", pady=10)


class AlphabetInput(AbsFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        tk.Label(self, text="Alphabet").pack()
        self.a = tk.Entry(self, width=30)
        self.a.insert(0, 'abcdefghijklmnopqrstuvwxyz')
        self.a.pack()

    def on_next(self):
        alph = self.a.get()
        regex = re.compile('[^a-zA-Z0-9]')
        alph = regex.sub('', alph)
        alph = sorted(list({ch for ch in alph}))
        self.controller.editDistance.alphabet = alph


class WeightsInput(AbsFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self._entry = {}
        self.rows = len(controller.editDistance.alphabet) + 1
        self.columns = len(controller.editDistance.alphabet) + 1

    def on_entry(self):
        self._entry = {}
        self.rows = len(self.controller.editDistance.alphabet) + 1
        self.columns = len(self.controller.editDistance.alphabet) + 1

        # register a command to use for validation
        vcmd = (self.register(self.validator), "%P")

        # create the table of widgets
        for row in range(self.rows):
            for column in range(self.columns):
                index = (row, column)
                e = tk.Label(self, text="")
                if row == 0 and column == 0:
                    e = tk.Label(self, text="")
                elif row == 0:
                    e = tk.Label(self, text=self.controller.editDistance.alphabet[column-1])
                elif column == 0:
                    e = tk.Label(self, text=self.controller.editDistance.alphabet[row-1])

                if row > 0 and column > 0:
                    e = tk.Entry(self, validate="key", validatecommand=vcmd, width=5)
                    e.insert(0, '1')
                    e.bind("<KeyRelease>", self.key_pressed)
                e.grid(row=row, column=column, stick="nsew")
                self._entry[index] = e

        # adjust column weights so they all expand equally
        for column in range(self.columns):
            self.grid_columnconfigure(column, weight=1)
        # designate a final, empty row to fill up any extra space
        self.grid_rowconfigure(self.rows, weight=1)

    def on_next(self):
        self.controller.editDistance.weights = self.get()

    def get(self):
        """Return a list of lists, containing the data in the table"""
        result = {}
        for row in range(1, self.rows):
            current_row = {}
            for column in range(1, self.columns):
                index = (row, column)
                current_row[self.controller.editDistance.alphabet[column-1]] = float('0' + self._entry[index].get())
            result[self.controller.editDistance.alphabet[row-1]] = current_row
        return result

    def validator(self, P):
        if P.strip() == "":
            return True
        try:
            i = int(P)
            return True if i > 0 else False
        except ValueError:
            self.bell()
            return False

    def key_pressed(self, event):
        entry = event.widget
        for k, v in self._entry.items():
            if v == entry:
                key = k
        if key[0] != key[1]:
            # set the diagonal entry to the same value
            diag_entry = self._entry[(key[1], key[0])]
            diag_entry.delete(0, tk.END)
            diag_entry.insert(0, entry.get())


class StringsInput(AbsFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        valdt = (self.register(self.validator), "%S", "%d")

        tk.Label(self, text="A").pack()
        self.a = tk.Entry(self, validate="key", validatecommand=valdt)
        self.a.pack()
        tk.Label(self, text="B").pack()
        self.b = tk.Entry(self, validate="key", validatecommand=valdt)
        self.b.pack()

    def on_entry(self):
        self.a.delete(0, tk.END)
        self.b.delete(0, 'end')

    def on_next(self):
        self.controller.editDistance.A = self.a.get()
        self.controller.editDistance.B = self.b.get()

    def validator(self, new_ch, action):
        if action != '1':
            return True
        if new_ch in self.controller.editDistance.alphabet:
            return True
        return False


class ResultShow(AbsFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.c = tk.Label(self, text="Costo: ")
        self.c.pack()
        self.s = tk.Label(self, text="Sequenza: ")
        self.s.pack()

    def on_entry(self):
        cost, sequence = self.controller.editDistance.get_edit_distance()
        self.c['text'] = 'Costo: ' + str(cost)
        self.s['text'] = 'Sequenza: ' + str(sequence)


if __name__ == "__main__":
    app = EditApplication()
    app.mainloop()
