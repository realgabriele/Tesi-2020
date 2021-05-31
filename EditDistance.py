class EditDistance:
    alphabet = []
    weights = {}
    A = ""
    B = ""

    def check_weights(self):
        """ Controlla che i valori siano coerenti e consistenti per il calcolo della distanza """

        # pesi positivi
        for key1 in self.weights:
            for key2 in self.weights[key1]:
                if self.weights[key1][key2] <= 0:
                    self.weights[key1][key2] = 1

        # disuguaglianza triangolare
        for key1 in self.weights:
            for key2 in self.weights[key1]:
                for key3 in self.weights[key1]:
                    if key1 == key2 or key1 == key3 or key2 == key3:    # insert / delete
                        continue
                    else:
                        if self.weights[key1][key2] > int(self.weights[key1][key3]) + int(self.weights[key3][key2]):
                            self.weights[key1][key2] = int(self.weights[key1][key3]) + int(self.weights[key3][key2])

        # stringhe di caratteri solo nell'alfabeto
        self.A = "".join([c for c in self.A if c in self.alphabet])
        self.B = "".join([c for c in self.B if c in self.alphabet])

    def get_distance_matrix(self):
        """ Calcola la matrice delle distanze tramite programmazione dinamica
        :return: matrice delle distanze
        """

        matrix = []

        # inizializzo la prima riga della matrice
        for x in range(len(self.A) + 1):
            matrix.append([])
            if x == 0:
                matrix[0].append(0)
            else:
                matrix[x].append(matrix[x-1][0] + int(self.weights[self.A[x-1]][self.A[x-1]]))
        # inizializzo la prima colonna della matrice
        for x in range(1, len(self.B) + 1):
            matrix[0].append(matrix[0][x-1] + int(self.weights[self.B[x-1]][self.B[x-1]]))

        # calcolo tutte le distanze, da ogni i a ogni j
        i = 1
        while i <= len(self.A):
            j = 1
            while j <= len(self.B):
                if self.A[i-1] == self.B[j-1]:
                    matrix[i].append(matrix[i-1][j-1])
                else:
                    m1 = matrix[i-1][j] + int(self.weights[str(self.A[i-1])][str(self.A[i-1])])
                    m2 = matrix[i][j-1] + int(self.weights[str(self.B[j-1])][str(self.B[j-1])])
                    m3 = matrix[i-1][j-1] + int(self.weights[str(self.A[i-1])][str(self.B[j-1])])
                    matrix[i].append(min(m1, m2, m3))
                j += 1
            i += 1

        return matrix

    def get_edit_sequence(self, matrix):
        """ Calcola la sequenza di operazioni di edit
        :param matrix: matrice delle distanze
        :return: lista di coppie
        """

        sequence = []

        # scorro la matrice all'inverso
        i, j = len(self.A), len(self.B)
        while i > 0 and j > 0:
            if self.A[i-1] == self.B[j-1]:  # No operation
                sequence.insert(0, str(self.A[i-1] + "->" + self.B[j-1]))
                i = i - 1
                j = j - 1
            else:
                m1 = matrix[i-1][j]
                m2 = matrix[i][j-1]
                m3 = matrix[i-1][j-1]
                minim = min(m1, m2, m3)
                if minim == m1:     # Delete A[i-1]
                    sequence.insert(0, str(self.A[i-1] + "->\u03BB"))
                    i = i - 1
                elif minim == m2:   # Insert B[j-1]
                    sequence.insert(0, str("\u03BB->" + self.B[j-1]))
                    j = j - 1
                elif minim == m3:   # Change A[i-1]->B[j-1]
                    sequence.insert(0, str(self.A[i-1] + "->" + self.B[j-1]))
                    i = i - 1
                    j = j - 1

        while i > 0:
            sequence.insert(0, str(self.A[i-1] + "->\u03BB"))
            i = i - 1
        while j > 0:
            sequence.insert(0, str("\u03BB->" + self.B[j-1]))
            j = j - 1

        return sequence

    def get_edit_distance(self):
        """ Calcola la distanza pesata
        :return: (valore della distanza, lista di operazioni)
        """

        self.check_weights()
        matrix = self.get_distance_matrix()
        sequence = self.get_edit_sequence(matrix)

        return matrix[len(self.A)][len(self.B)], sequence


if __name__ == "__main__":
    # simple test
    ED = EditDistance()
    ED.alphabet = [c for c in "abcdefghijklmnopqrstuvwxyz"]
    ED.weights = {i: {j: 1 for j in ED.alphabet} for i in ED.alphabet}
    ED.A = "gabriele"
    ED.B = "tagliente"
    print(ED.get_edit_distance())
