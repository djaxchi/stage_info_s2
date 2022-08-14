from collections import defaultdict
import random
import networkx as nx
import matplotlib.pyplot as plt

def return_list(l):
    return l

def mix(x):
    return random.sample(x,len(x))

def louvain_partitions(G, weight="weight",shuffle = return_list):
    """
    Permet de partitionner un Graphe non orientée
    Entrée : -Un graphe non orientée
             -Un attribut correspondant au poids des aretes
             -Une variable permettant de définir une qualité souhaiter de pertioinnement, plus elle est petite plus le graphe sera partitionné
    Sortie : -Une partition des noeuds présents a l'origine
    """
    noeuds_graph=list(G.nodes())
    noeuds_graph = shuffle(noeuds_graph)
    partition = [{u} for u in noeuds_graph]
    mod = modularity(G, partition, weight=weight)
    graph = nx.Graph()
    graph.add_nodes_from(list(noeuds_graph))
    graph.add_weighted_edges_from(G.edges(data=weight, default=1))

    m = graph.size(weight="weight")
    partition, inner_partition, gain = niveau_1(graph, m, partition)
    gain = True
    while (
        gain
    ):  # itération des phase 1 et 2 jusqu'au partitionnement avec la meilleure modularité
        new_mod = modularity(graph, inner_partition, weight="weight")
        if new_mod - mod <= 1:
            mod = new_mod
            graph = niveau_2(graph, inner_partition)
            partition, inner_partition, gain = niveau_1(graph, m, partition)
    #print("partitionnement optimale", partition)

    return partition,modularity(G,partition )


def modularity(G, communities, weight="weight"):
    """
    Permet de calculé la modularité d'un graphe, c'est a dire mesurer la qualité d'un partitionnement.

    Entrée: -Un graphe
            -son partitionnement en communautées
    Sortie: -Un int compris entre -1 et 1

    """
    
    dico_degree = dict(
        G.degree(weight=weight)
    )  # dico comportant tout les noeuds associés a leurs degrées
    deg_sum = sum(dico_degree.values())  # somme de tout les degrées
    if deg_sum == 0:
        return 0
    m = deg_sum / 2  # somme des poids du graphe
    norm = 1 / deg_sum**2
    mod = 0

    def norme_commu(community):
        """
        Permet d'obtenir une comparaison des aretes intra et inter communauté d'une communauté du graphe

        Entrée: -Une liste de noeuds représantant une communauté
        Sortie: -Un int compris entre -1 et 1
        """
        comm = set(community)
        in_commu = sum(
            wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm
        )  # le nombre de d'aretes au sein de la commu

        commu_degree_sum = sum(
            dico_degree[u] for u in comm
        )  # la somme des degrées des noeuds de la commu
        return in_commu / m - (commu_degree_sum**2) * norm
    for commu in communities:
        mod += norme_commu(commu)
    return mod


def niveau_1(G, m, partition):
    """
    Correspond a la première phase de la méthode de Louvain.
    Entrée: -Un graph non orientée
            -Le poid total du graphe
            -La partition de ce graphe
    Sortie: -Une nouvelle partition du graphe avec les noeuds d'origines
            -Une partition du graphe avec les noeuds d'origines fusionnées
            -un booléen qui indique si il y a bien eu un changement de partionnement
    """
    
    commu = {u: i for i, u in enumerate(G.nodes())}
    partition_G = [{u} for u in G.nodes()]
    dico_poids = dict(G.degree(weight="weight"))
    poids_rangé = [deg for deg in dico_poids.values()]
    dico_voisins = {
        u: {v: data["weight"] for v, data in G[u].items() if v != u} for u in G
    }
    compteur = 1
    gain = False
    if m == 0:
        return partition,partition_G,gain

    while compteur > 0:
        compteur = 0
        for node in G.nodes:
            best_mod = 0
            best_com = commu[node]
            voisins_commu = poid_réel_voisins(dico_voisins[node], commu)
            degree = dico_poids[node]
            poids_rangé[best_com] -= degree  # le noeud est enlevé de sa commu
            for nbr_com, poid in voisins_commu.items():
                modul_local = 2 * poid - (poids_rangé[nbr_com] * degree) / m
                if modul_local > best_mod:
                    best_mod = modul_local
                    best_com = nbr_com
            poids_rangé[best_com] += degree
            if best_com != commu[node]:
                com = G.nodes[node].get("nodes", {node})
                partition[commu[node]].difference_update(com)
                partition_G[commu[node]].remove(node)
                partition[best_com].update(com)
                partition_G[best_com].add(node)
                gain = True
                compteur += 1
                commu[node] = best_com
    partition = list(filter(len, partition))
    partition_G = list(filter(len, partition_G))

    return partition, partition_G, gain


def poid_réel_voisins(voisins_node, commu):
    """Renvoie un dico des voisins d'un noeud et leurs poids avec l'attachement a une communauté prise en compte
    Entrée: -Un dictionnaire des voisins de d'un noeud
            -Un dictionnaire répertoriant toutes les communautés
    Sortie: -un dictionnaire répertoriant le poid réel des noeuds adjacent au noeud étudiée"""
    weights = defaultdict(float)  # permet d'éviter des erreurs d'out of index
    for node, poids in voisins_node.items():
        weights[commu[node]] += poids
    return weights


def niveau_2(G, partition):
    """
    Crée un graphe a partir d'une partion en fusionnant les noeuds de cette partion
    Entrée: -Un garphe
            -une partition de ce graphe sous forme d'objet itérable
    Sortie: -Un nouveau graphe du meme type que le graphe précédent
    """
    H = nx.Graph()
    node2com = {}
    for i, part in enumerate(partition):
        nodes = set()
        for node in part:
            node2com[node] = i
            nodes.update(G.nodes[node].get("nodes", {node}))
        H.add_node(i, nodes=nodes)

    for node1, node2, poid in G.edges(data=True):
        poid = poid["weight"]
        com1 = node2com[node1]
        com2 = node2com[node2]
        temp = H.get_edge_data(com1, com2, {"weight": 0})["weight"]
        H.add_edge(com1, com2, **{"weight": poid + temp})
    return H


def visuelle(G,fonction=louvain_partitions):
    """
    Permet de visualiser le partionnnement fait par le programme lovain avec des couleurs associé a chaque de noeud du graphe partitionné par communauté
    Entrée: -Un graphe non orientée
            -Une partition de ce graphe"""
    affiche(G)
    all_nodes = []
    for commu in fonction(G)[0]:
        all_nodes.append(list(commu))
    G3 = nx.Graph()
    for commu in all_nodes:
        for nodes in commu:
            G3.add_node(nodes)
    for from_loc, to_loc in G.edges():
        G3.add_edge(from_loc, to_loc)
    if len(G.nodes()) < 15:
        labels = nx.get_edge_attributes(G, "weight")
    else:
        labels=None
    pos = nx.spring_layout(G3)
    if len(G3.nodes()) < 15:
        nx.draw(
            G3,
            pos,
            edge_color="k",
            with_labels=True,
            font_weight="light",
            node_size=280,
            width=0.9,
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    else:
        nx.draw(
            G3,
            pos,
            edge_color="k",
            with_labels=True,
            font_weight="light",
            node_size=280,
            width=0.9,
        )


    
    if len(all_nodes) >= 1:  # essaye de remplacé ce morceau par un default dict
        nx.draw_networkx_nodes(G3, pos, nodelist=all_nodes[0], node_color="b")
    if len(all_nodes) >= 2:
        nx.draw_networkx_nodes(G3, pos, nodelist=all_nodes[1], node_color="r")
    if len(all_nodes) >= 3:
        nx.draw_networkx_nodes(G3, pos, nodelist=all_nodes[2], node_color="g")
    if len(all_nodes) >= 4:
        nx.draw_networkx_nodes(G3, pos, nodelist=all_nodes[3], node_color="c")
    if len(all_nodes) >= 5:
        nx.draw_networkx_nodes(G3, pos, nodelist=all_nodes[4], node_color="m")
    if len(all_nodes) >= 6:
        nx.draw_networkx_nodes(G3, pos, nodelist=all_nodes[5], node_color="y")
    plt.show()


def affiche(G):
    """
    Permet d'afficher un graphe

    Entrée: -Un graphe
    sortie: -l'affichage du graphe sur matplotlib

    """
    pos = nx.spring_layout(G)
    
    if len(G.nodes())<15:
        labels = nx.get_edge_attributes(G, "weight")
        nx.draw_networkx(G, pos, with_labels=True, font_weight="bold", node_color="tab:red")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    else:
        nx.draw_networkx(G, pos, with_labels=True, font_weight="bold", node_color="tab:red")
    plt.show()

def louvain(G,qualité=100, shuffle = mix,weight="weight"):
    partition=None
    modularité=-1
    for i in range(int(qualité)):
        p=louvain_partitions(G,weight=weight,shuffle=shuffle)[0]
        mod=modularity(G,p)
        if mod>modularité:
            modularité=mod
            partition=p
    return partition,modularité

    
