#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 19/05/2019
#Last update: 15/10/2019

import random
import scipy
import numpy as np
import multiprocessing as mp
from functools import partial

distances = {}
nodes_map = {} #Mapa que contiene los índices de los nodos como clave y los objetos como valor


def get_random_centers(k,matrix):
    random_centers = []
    for i in range(k):
        random_index = random.randrange(0, matrix.shape[0], 1)
        random_centers.append(random_index)
    return random_centers

#Kmeans ++
def initialize(X, K):
    init = random.choice(np.arange(K))
    init = 0
    C = [X[init]]
    C_indices = [init]
    for k in range(1, K):
        D2 = scipy.array([min([scipy.inner(c-x,c-x) for c in C]) for x in X])
        probs = D2/D2.sum()
        cumprobs = probs.cumsum()
        r = scipy.rand()
        for j,p in enumerate(cumprobs):
            if r < p:
                i = j
                break
        C.append(X[i])
        C_indices.append(i)
    return C_indices



def create_groups(centers,matrix):
    groups = {}
    dist_matrices = {}
    for c in centers:
        dist_matrices[c] = scipy.sparse.csgraph.dijkstra(matrix, directed=False, indices=c, return_predecessors=False, unweighted=False)

    for node in range((matrix).shape[0]):
        min = 10000000
        selected_center = -1
        for c,matrix in dist_matrices.items():
            if matrix[node] < min:
                min = matrix[node]
                selected_center = c
        if selected_center not in groups:
            groups[selected_center] = [node]
        else:
            groups[selected_center].append(node)

    return groups

def recalc_center(matrix,groups):
    centroids = []
    for group in groups:
        indices = group[1]
        group_matrix = matrix[indices,:][:,indices]
        D = scipy.sparse.csgraph.floyd_warshall(group_matrix, directed=False, unweighted=False)
        #D = scipy.sparse.csgraph.johnson(group_matrix, directed=False, indices=None, return_predecessors=False, unweighted=False)
        n = D.shape[0]
        max_value = -1
        selected_center = -1
        for r in range(0, n):
            cc = 0.0
            possible_paths = list(enumerate(D[r, :]))
            shortest_paths = dict(filter( \
                lambda x: not x[1] == np.inf, possible_paths))

            total = sum(shortest_paths.values())
            n_shortest_paths = len(shortest_paths) - 1.0
            if total > 0.0 and n > 1:
                s = n_shortest_paths / (n - 1)
                cc = (n_shortest_paths / total) * s
            if cc > max_value:
                selected_center = r
                max_value = cc
        centroids.append(indices[selected_center])
    return centroids

def recalc_center_all(matrix,group):
    indices = group[1]
    group_matrix = matrix[indices,:][:,indices]
    D = scipy.sparse.csgraph.floyd_warshall(group_matrix, directed=False, unweighted=False)
    #D = scipy.sparse.csgraph.johnson(group_matrix, directed=False, indices=None, return_predecessors=False, unweighted=False)
    n = D.shape[0]
    max_value = -1
    selected_center = -1
    for r in range(0, n):
        cc = 0.0
        possible_paths = list(enumerate(D[r, :]))
        shortest_paths = dict(filter( \
            lambda x: not x[1] == np.inf, possible_paths))

        total = sum(shortest_paths.values())
        n_shortest_paths = len(shortest_paths) - 1.0
        if total > 0.0 and n > 1:
            s = n_shortest_paths / (n - 1)
            cc = (n_shortest_paths / total) * s
        if cc > max_value:
            selected_center = r
            max_value = cc
    return indices[selected_center]

def merge_centroids(results):
    centroids = [c for c in results]
    return centroids

def merge_groups(results):
    groups = {}
    for result in results:
        for key,value in result.items():
            if key not in groups:
                groups[key] = [value]
            else:
                groups[key].append(value)
    return groups



def stop_critery(pointlist,centers,old_centers):
    avg_distances = 0
    for i in range(len(centers)):
        avg_distances+=scipy.spatial.distance.euclidean(pointlist[centers[i]], pointlist[old_centers[i]])
    avg_distances = avg_distances/len(centers)
    if avg_distances < 2:
        return True
    else:
        return False

def fit_desikan(matrix,pointlist,k):
    if k > 1 and matrix != None:
        nodes_group = []
        #centers = get_random_centers(k,matrix)
        centers = initialize(pointlist,k)
        centers_tmp = centers
        groups = create_groups (centers,matrix)

        for i in range(20):
            #print("iteración "+str(i))
            centers = recalc_center(matrix,groups.items())

            noChange = stop_critery(pointlist,centers,centers_tmp)
            centers_tmp = centers
            #print("calculando grupos")
            groups = create_groups(centers, matrix)
            if noChange:
                #print("salió")
                break
        for key,group in groups.items():
            nodes_group.append(group)
    else:
        nodes_group = []
    return nodes_group

def fit_all(matrix,pointlist,k):
    if k > 1 and matrix != None:
        nodes_group = []
        centers = get_random_centers(k,matrix)
        #centers = initialize(pointlist, k)
        print("centrois inicializados")
        centers_tmp = centers
        print("inicializando grupos")
        groups = create_groups (centers,matrix)

        for i in range(20):
            pool = mp.Pool(mp.cpu_count())
            centers_fun = partial(recalc_center_all, matrix)
            results = pool.map(centers_fun, [group for group in groups.items()])
            centers = merge_centroids(results)
            pool.close()
            noChange = stop_critery(pointlist,centers,centers_tmp)
            centers_tmp = centers
            groups = create_groups(centers, matrix)
            if noChange:
                break
        for key,group in groups.items():
            nodes_group.append(group)
    else:
        nodes_group = []
    return nodes_group