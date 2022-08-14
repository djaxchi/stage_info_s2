
from Louvain import *
import random


"""Test version actuelle:"""

def return_list(l):
    return l


G = nx.Graph()                                                 #graphe de référence
G.add_nodes_from([i for i in range(15)])
G.add_weighted_edges_from(
    [
        (0, 3, 1),
        (0, 2, 1),
        (0, 4, 1),
        (0, 5, 1),
        (1, 2, 1),
        (1, 4, 1),
        (1, 7, 1),
        (2, 0, 1),
        (2, 4, 1),
        (2, 6, 1),
        (2, 5, 1),
        (3, 7, 1),
        (5, 7, 1),
        (5, 11, 1),
        (6, 7, 1),
        (8, 11, 1),
        (8, 9, 1),
        (8, 10, 1),
        (8, 14, 1),
        (8, 15, 1),
        (9, 12, 1),
        (10, 13, 1),
        (10, 11, 1),
        (10, 4, 1),
        (10, 12, 1),
        (11, 13, 1),
        (14, 10, 1),
        (14, 9, 1),
    ]
)

G_limite_1= nx.Graph()                                      #graphe ou tout les aretes valent 0
G_limite_1.add_nodes_from([i for i in range(15)])
for (u, v, w) in G_limite_1.edges(data=True):
    w["weight"] = 0

G_limite_2= nx.Graph()                                      #graphe ou tout les noeuds sont connecté avec un meme poids
G_limite_2.add_nodes_from([i for i in range(15)])
for a in G_limite_2.nodes:
    for b in G_limite_2.nodes:
        if a == b :
            break
        G_limite_2.add_edge(a,b) 
for (u, v, w) in G_limite_2.edges(data=True):
    w["weight"] = 1

def test_louvain_partitions():
    assert louvain_partitions(G)[0] == (
        [{0, 1, 2, 3, 4, 5, 6, 7}, {8, 9, 10, 11, 12, 13, 14, 15}]
    )


def test_modularity_avant():
    assert modularity(G, [{u} for u in G.nodes()]) == -0.07201646090534979


def test_modularity_aprés():
    assert (
        modularity(G, [{0, 1, 2, 3, 4, 5, 6, 7}, {8, 9, 10, 11, 12, 13, 14, 15}])
        == 0.4252400548696845
    )


def test_niveau_1():
    assert niveau_1(G, G.size(weight="weight"), [{u} for u in G.nodes()]) == (
        [{0, 1, 2, 4, 5}, {3, 6, 7}, {8, 9, 10, 12, 14, 15}, {11, 13}],
        [{0, 1, 2, 4, 5}, {3, 6, 7}, {8, 9, 10, 12, 14, 15}, {11, 13}],
        True,
    )


def test_poid_réel_voisins_avant():
    commu = {u: i for i, u in enumerate(G.nodes())}
    dico_voisins = {
        u: {v: data["weight"] for v, data in G[u].items() if v != u} for u in G
    }
    dico_voisins_1 = dico_voisins[1]
    assert poid_réel_voisins(dico_voisins_1, commu) == {2: 1.0, 4: 1.0, 7: 1.0}


def test_poid_réel_voisins_avant():
    commu = {u: i for i, u in enumerate(G.nodes())}
    dico_voisins = {
        u: {v: data["weight"] for v, data in G[u].items() if v != u} for u in G
    }
    dico_voisins_1 = dico_voisins[1]
    assert poid_réel_voisins(dico_voisins_1, commu) == {2: 1.0, 4: 1.0, 7: 1.0}


def test_poid_réel_voisins_aprés():
    commu = {0: 0, 1: 1}
    dico_voisins = {0: {1: 2}, 1: {0: 2}}
    dico_voisins_1 = dico_voisins[1]
    assert poid_réel_voisins(dico_voisins_1, commu) == {0: 2.0}


def test_niveau_2_avant():
    assert (
        len(niveau_2(G, [{u} for u in G.nodes()]).nodes()) == 16
        and len(niveau_2(G, [{u} for u in G.nodes()]).edges()) == 27
    )


def test_niveau_2_aprés():
    assert (
        len(niveau_2(G, louvain_partitions(G)[0]).nodes()) == 2
        and len(niveau_2(G, louvain_partitions(G)[0]).edges()) == 3
    )

def test_louvain_partitions_2():
    assert louvain_partitions(G_limite_1)[0]== [{u} for u in G_limite_1.nodes]

def test_louvain_partition_3():
    assert louvain_partitions(G_limite_2)[0] == [{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}]

