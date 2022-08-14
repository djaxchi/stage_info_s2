import random
import csv

import networkx as nx
import matplotlib.pyplot as plt

P = 0.5


def proba(p):
    return random.random() <= p


class Matrix:
    @classmethod
    def load(cls, filename):
        matrix = []
        with open(filename) as f:
            reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            for line in reader:
                matrix.append([int(x) for x in line])
        return cls(matrix)

    @classmethod
    def load_from_data(cls, filename):
        matrix = []
        with open(filename) as f:
            reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
            for line in reader:
                matrix.append([1 if x >= 0 else 0 for x in line])
        return cls(matrix)

    @classmethod
    def random(cls, n, m, P=0.5):
        matrix = []
        for i in range(n):
            matrix.append([])
            for j in range(m):
                if proba(P):
                    matrix[-1].append(1)
                else:
                    matrix[-1].append(0)

        return cls(matrix)

    def __init__(self, matrix):
        self.matrix = [[x for x in line] for line in matrix]

    def column(self, j):
        return frozenset([i for i in range(len(self.matrix)) if self.matrix[i][j] == 1])

    def co_column(self, j):
        return frozenset(range(len(self.matrix))) - self.column(j)

    def buneman(self, i, j):
        if self.column(i).isdisjoint(self.column(j)):
            return (1, 1)
        elif self.column(i).isdisjoint(self.co_column(j)):
            return (1, 0)
        elif self.co_column(i).isdisjoint(self.column(j)):
            return (0, 1)
        elif self.co_column(i).isdisjoint(self.co_column(j)):
            return (0, 0)
        else:
            return None

    def proper(self):
        proper = set()

        for i in range(len(self.matrix[0])):
            to_add = True
            if not self.column(i) or not self.co_column(i):
                to_add = False
                continue
            if to_add:
                for j in range(i + 1, len(self.matrix[0])):
                    if self.column(i) in (self.column(j), self.co_column(j)):
                        to_add = False

                        break
            if to_add:
                proper.add(i)
        return frozenset(proper)

    def distance_matrix(self):
        distance = []
        for i in range(len(self.matrix)):
            distance.append([])
            for j in range(i + 1):
                distance[-1].append(self.d(i, j))
        return distance

    def d(self, i, j):
        d = 0
        for k in range(len(self.matrix[0])):
            d += abs(self.matrix[i][k] - self.matrix[j][k])
        return d

    def d_vect(self, i, vect):
        d = 0
        for k in range(len(self.matrix[0])):
            d += abs(self.matrix[i][k] - vect[k])
        return d

    def __len__(self):
        return len(self.matrix)

    def __str__(self):

        s = " " * (len(self.matrix) // 10 + 3)
        for j in range(len(self.matrix[0])):
            s += str(j).center(len(self.matrix[0]) // 10 + 3)
        s += "\n"
        for i, line in enumerate(self.matrix):
            s += str(i).rjust(len(self.matrix) // 10 + 1)
            for x in line:
                if x:
                    s += "X".rjust(len(line) // 10 + 3)
                else:
                    s += "·".rjust(len(line) // 10 + 3)
            s += "\n"

        return s

    def save(self, filename):
        with open(filename, "w") as f:
            writer = csv.writer(f)
            writer.writerows(self.matrix)

    def transpose(self):
        t = []
        for i in range(len(self.matrix[0])):
            t.append([])
            for j in range(len(self.matrix)):
                t[-1].append(self.matrix[j][i])
        return type(self)(t)

    def buneman_graph(self):
        proper = list(self.proper())

        g = nx.Graph()
        g.add_nodes_from(proper)

        for i in range(len(proper)):
            for j in range(i + 1, len(proper)):
                if self.buneman(proper[i], proper[j]):
                    g.add_edge(proper[i], proper[j])
        return g

    def medianes(self):
        current = []
        for i in range(len(self.matrix[0])):
            if self.matrix[0][i] == 1:
                current.append((1, self.column(i)))
            else:
                current.append((0, self.co_column(i)))

        medianes = set()

        next = [tuple(current)]

        while next:
            current = next.pop()
            # print([x for x, y in current])
            if current in medianes:
                continue

            medianes.add(current)

            for i in range(len(current)):
                to_add = True
                for j in range(len(current)):
                    if j == i:
                        continue
                    if current[j][1].issubset(current[i][1]):
                        to_add = False
                        break
                if to_add:

                    x = list(current)
                    if x[i][0] == 0:
                        x[i] = (1, self.column(i))
                    else:
                        x[i] = (0, self.co_column(i))

                    if tuple(x) not in medianes:
                        next.append(tuple(x))

        return Matrix(
            [
                line
                for line in [[x for x, y in line] for line in medianes]
                if line not in self.matrix
            ]
        )


def hypercube_graph(matrix, medianes):
    hc = nx.Graph()
    hc.add_nodes_from(range(len(matrix)))
    hc.add_nodes_from(["M" + str(x) for x in range(len(medianes))])

    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            if matrix.d(i, j) == 1:
                hc.add_edge(i, j)
        for j in range(len(medianes)):
            if matrix.d_vect(i, medianes.matrix[j]) == 1:
                hc.add_edge(i, "M" + str(j))

    for i in range(len(medianes)):
        for j in range(i + 1, len(medianes)):
            if medianes.d(i, j) == 1:
                hc.add_edge("M" + str(i), "M" + str(j))

    return hc


def etude(matrix):
    print(matrix)
    # print("ok: ", matrix.proper())
    # print("ko: ", set(range(len(matrix.matrix[0]))) - set(matrix.proper()))

    # for i, l in enumerate(matrix.distance_matrix()):
    #     print(i, l)

    g = matrix.buneman_graph()

    for x, y in g.edges:
        print(y, x, matrix.buneman(y, x))

    # #fig, ax = plt.subplots(figsize=(8, 8))

    # #nx.draw(g, with_labels=True, font_weight='bold', ax=ax)

    # plt.show()

    # medianes = matrix.medianes()
    # print(len(medianes.matrix))
    # print(medianes)

    # hc = hypercube_graph(matrix, medianes)

    # fig, ax = plt.subplots(figsize=(8, 8))

    # nx.draw(hc, with_labels=True, font_weight='bold', ax=ax)

    plt.show()


if __name__ == "__main__":
    N = 20
    M = 15

    # matrix = Matrix.random(N, M, 1/4)
    # matrix.save("matrice.csv")

    matrice = Matrix.load("animaux.csv")
    # matrice = Matrix.load_from_data("depense_etat_centre_reduit.csv")

    # etude(matrice)
    # visuelle(matrice.buneman_graph())
    # print("transpose")
    # etude(matrice.transpose())
