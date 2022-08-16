from typing import FrozenSet
from matrix_proper_compatible import *
from matrix import *
from Louvain import *
import networkx as nx
import csv


def finish(M, g):
    for x in g.nodes():
        for y in g.nodes():
            if x != y:
                if M.buneman(x, y) == (0, 0):
                    return True
    return False


def inverse_colonne(M, y):
    for i in range(len(M.matrix)):
        if i in M.co_column(y):
            M.matrix[i][y] = 1
        else:
            M.matrix[i][y] = 0
    return M.column(y)


def Hierarchie(M, g):
    H = []
    for x in g.nodes():
        H.append(M.column(x))
    while finish(M, g):
        for x in g.nodes():
            sub = []
            for y in g.nodes():
                if x != y:
                    if M.buneman(x, y) == (0, 0):
                        sub.append(y)
            if len(sub) != 0:
                for y in sub:
                    H.remove(M.column(y))
                    H.append(inverse_colonne(M, y))
    return H


def H_final(H, M):
    for i in range(0, len(M.matrix)):
        if frozenset([i]) not in H:
            H.append(frozenset([i]))
    X = frozenset([i for i in range(len(M.matrix))])
    H.append(X)
    return H


def elements_max(H):
    el = []
    for A in H:
        T = True
        for B in H:
            if A != B:
                if A.intersection(B) == A:
                    T = False
        if T:
            el.append(A)
    return el


def sous_ensembles(A, H):
    sous_ensembles = []
    for B in H:
        if B != A:
            if B.intersection(A) == B:
                sous_ensembles.append(B)
    return sous_ensembles


def créer_edge(H, X, dico, arbre):
    elem_max = elements_max(H)
    for e in elem_max:
        arbre.add_node(dico[e])
        arbre.add_edge(dico[e], dico[X])
    for e in elements_max(H):
        if len(e) != 1:
            X = e
            H = sous_ensembles(e, H)
            créer_edge(H, X, dico, arbre)
    return arbre


def dico_labeling(H):
    dico = {}
    c = 0
    for A in H:
        dico[A] = c
        c += 1
    return dico


def cree_arbre(M, G):
    arbre = nx.Graph()
    H = H_final(Hierarchie(M, G), M)
    dico = dico_labeling(H)
    X = H[-1]  # j ai mis X l'union de tt les A dans H en dernier
    arbre.add_node(dico[X])
    H.remove(X)
    return créer_edge(H, X, dico, arbre)


g = nx.Graph()
m = Matrix.load("test.csv")
for i in range(len(m.matrix[0])):
    g.add_node(i)
