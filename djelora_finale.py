from matrix import *
from Louvain import *
from magic import *
def premier(couple):
    return couple[0]

def mix(x):
    return random.sample(x,len(x))

def needs_patching(m): #renvoie une matrice dont le graphe de buneman est complet
    g = m.buneman_graph()
    E = [] #liste de toutes le arretes
    dico = {(x, y): m.buneman(x, y) for x, y in g.edges}
    dico2 = {(x, y): m.buneman(x, y) for y, x in g.edges}
    dico.update(dico2) #dico contenant tout les omega de chaque colonnes
    for x in g.nodes():
        for y in g.nodes():
            if x != y:
                E.append((x, y))
    if len(g.edges) == (len(g.nodes)*(len(g.nodes) - 1))//2:   #condition nécéssaire a la fin de l'algo
        print(type(m))
        return m
    c = 0
    card_E = len(E)
    while c < card_E:                                                       #permet de prendre en compte l'heritage d'un triangle
        g = m.buneman_graph()
        for x in E:
            if x and x[::-1] not in g.edges:                                #on regarde tout aretes qui n'est pas dans le graphe
                dico_voisins = {u: {v for v in g[u] if v != u} for u in g}
                voisin_y = dico_voisins[x[1]]
                voisin_x = dico_voisins[x[0]]
                triangle = voisin_x.intersection(voisin_y)                  
                if len(triangle) != 0:                                      #on verifie si l'arete manquante n'est pas imposé par un triangle
                    for nodes in triangle:
                        if dico[nodes, x[0]][0] != dico[nodes, x[1]][0]:
                            dico[x] = (dico[nodes, x[0]][1], dico[nodes, x[1]][1])
                            dico[x[::-1]] = dico[x][::-1]
                            dico_remplacent = correction_lignes(m, x, dico[x])[0]
                            for ligne in dico_remplacent:
                                modif(m,dico_remplacent[ligne],x,ligne)     #on place l'arete imposée par un triangle
                            c = 0              
            else:
                c += 1
    g = m.buneman_graph()
    P = []  #element problématique
    for x in E:
        if x and x[::-1] not in g.edges:
            if x[::-1] not in P:
                P.append(x)  #elelment passé par triangle et toujours pas des edges
    liste_omega_possible = [(0, 0), (0, 1), (1, 0), (1, 1)]
    for cc in P:
        omega_choisi = None     
        cdo = 0                 #conteur de destruction omega
        for i in m.matrix:
            for j in i:
                cdo += 1
        couple_omega_choisi_cdo = (omega_choisi,cdo)
        couple_dico_omega_choisi = (None,None)
        for o_candidat in liste_omega_possible:
            couple_dico_cdo_test = correction_lignes(m,cc,o_candidat)    #ici on test le meilleur omega possible pour un edge non existant (on aurait pu choisir le meilleur pour une solution plus optimale)
            couple_omega_cdo_test = (o_candidat, couple_dico_cdo_test[1])
            if couple_omega_cdo_test[1] == None:
                couple_omega_cdo_test = (o_candidat,cdo + 1)
            if couple_omega_cdo_test[1] <= cdo:
                couple_omega_choisi_cdo = couple_omega_cdo_test
                couple_dico_omega_choisi= (couple_dico_cdo_test[0],couple_omega_cdo_test[0])
        if couple_omega_choisi_cdo [0] != None :
            dico_remplacent = couple_dico_omega_choisi[0]
            for ligne in dico_remplacent:
                modif(m,dico_remplacent[ligne],couple_omega_choisi_cdo[0],ligne)
                g= m.buneman_graph()
            print(dico_remplacent[ligne],couple_omega_choisi_cdo[0],ligne)
            print(m)
            return needs_patching(m)

    return False

def correction_lignes(m, c, o):  # matrice,couple,omega #permet de renvoyer les changement optimal a faire sur chaque ligne pour un omega donné
    cdo = 0  #compteur de destruction d'un omega
    L = [] #liste contenant les lignes ou il y a ce omega
    for i in range(len(m)):
        if m.matrix[i][c[0]] == o[0] and m.matrix[i][c[1]] == o[1]:
            L.append(i)
    list_test = m.matrix.copy()
    m_test = Matrix(list_test) #création d'une matrice test
    dico_remplacent = {}  #dico qui repertotrie tout les remplacent de chaque ligne pour un omega
    for ligne in L:
        couple_remplacant_cdr = trouve_remplacant(m,c,o,ligne) #ici on appel une fonction qui nous renvoie le remplacant ideal et sa destruction
        if couple_remplacant_cdr[0] != None:
            cdo += couple_remplacant_cdr[1] #chaque ligne cause une certaine destruction
            modif(m_test,couple_remplacant_cdr[0],o,ligne) #on effectue le changement de ligne pour quu'il soit pris en compte pour les prochaines lignes
            dico_remplacent[ligne] = couple_remplacant_cdr[0] #on note le remplacent pour pouvoir le faire remonter
        else:
            return (None,None) #possibilité que le omega ne soit pas placable
    return(dico_remplacent,cdo)
    
def trouve_remplacant(m,c,o,ligne):
    remplacement_possible = [(1, 0), (0, 1), (0, 0), (1, 1)]
    remplacement_possible.remove(o)     #le omega intedit d'office un couple
    cdr = len(m.matrix[ligne])          #nombre max de destruction par ligne
    r = None                            #initialisation d'un remplacant optimal
    for candidat in remplacement_possible:
        cdr_test = 0                    #compteur pour chaque candidat
        list_test = m.matrix.copy()
        m_test = Matrix(list_test) #création d'une matrice test
        m_test.matrix[ligne][c[0]] = candidat[0]
        m_test.matrix[ligne][c[1]] = candidat[1] #insertiton du candidat
        if c[0] or c[1] not in m_test.proper(): #l'ajout du candidat rend des colonnes impropre donc le candidat est eliminé
            cdr_test = cdr + 1
        if modif(m_test,candidat,c,ligne) == None: #l'ajout réel du candidat rend des colonnes impropre donc elimination du candidat
            cdr_test = cdr + 1 
        for i in range(len(m.matrix[ligne])): #on verifie les difference entre la matrice changé et la matrice initial
            if m.matrix[ligne][i] != m_test.matrix[ligne][i]:
                cdr_test += 1
        if cdr_test <= cdr:         #on garantit un candidat optimale
            cdr = cdr_test 
            r = candidat
    print(r)
    return(r,cdr)







def modif(m, remplacant, c, ligne):   #fonction qui sert a inséré un couple remplacant sans affecter les omegas d'origine
    
    G = m.buneman_graph()
    if c[0] not in m.proper() or c[1] not in m.proper():
        return None
    dico_voisins = {u: {v for v in G[u] if v != u} for u in G}
    voisin_x = dico_voisins[c[0]]
    voisin_y = dico_voisins[c[1]]
    m.matrix[ligne][c[0]] = remplacant[0]
    m.matrix[ligne][c[1]] = remplacant[1]
    if c[0] not in m.proper() or c[1] not in m.proper():
        return None
    G = m.buneman_graph()
    dico_voisins = {u: {v for v in G[u] if v != u} for u in G}
    voisin_x1 = dico_voisins[c[0]]
    voisin_y1 = dico_voisins[c[1]]
    for a in voisin_x:
        if a not in voisin_x1:
            remplacant = (1 - m[ligne][a], m[ligne][c[0]])
            c = (a, c[0])
            modif(m, remplacant, c, ligne)
    for b in voisin_y:
        if b not in voisin_y1:
            remplacant = (1 - m[ligne][b], m[ligne][c[1]])
            c = (b, c[1])
            modif(m, remplacant, c, ligne)
    return m


def matrices_louvain(m):
    mat = []
    g = m.buneman_graph()
    sujet = m.matrix
    nouv_col = louvain(g)[0]
    print(louvain(g)[0])
    for cols in nouv_col:
        nouv_matrice = []
        for col in cols:
            
            colonne = []
            for i in sujet:
                colonne.append(i[col])
            nouv_matrice.append(colonne)
        print(nouv_matrice)
        mat.append(Matrix(nouv_matrice))
    return mat

def louvain_feat_patching(M):
    done = False
    while done:
        patch= needs_patching(M)
        if patch != False:
            return patch
        G = matrices_louvain.buneman_graph(M)
        

m = Matrix.load("animaux.csv")
print(m)
for i in (matrices_louvain(m)):
    print(i)
for i in (matrices_louvain(m)):
    print(needs_patching(i))

