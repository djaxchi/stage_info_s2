from Louvain import *


G = nx.Graph()                                                 #graphe de référence
G.add_nodes_from([i for i in range(5)])
G.add_weighted_edges_from(
    [
        (0, 1, 1),
        (0, 4, 1),
        (1, 2, 1),
        (2, 3, 1),
        (1, 3, 1),
        (3, 4, 1)
    
    ]
)
graph = G

commu = [{0,4},{1,3,2}]
affiche(niveau_2(graph,commu))