# Copyright (C) 2019  Andrea Vázquez Varela

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 19/05/2019
#Last update: 16/10/2019

import random
import scipy
import numpy as np
import multiprocessing as mp
from functools import partial


def get_random_centers(k,matrix):
    random_centers = []
    for i in range(k):
        random_index = random.choice(list(set(matrix.indices)))
        random_centers.append(random_index)
    return random_centers

#Kmeans ++
def initialize(X, K):
    init = random.choice(np.arange(K))
    #init = 0
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

    for node in set(matrix.indices):
        min = 1000
        selected_center = -1
        for c,matrix in dist_matrices.items():
            if matrix[node] < min:
                min = matrix[node]
                selected_center = c
        if selected_center != -1:
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
        avg_distances+=np.linalg.norm(pointlist[centers[i]]- pointlist[old_centers[i]])
    avg_distances = avg_distances/len(centers)
    if avg_distances < 2:
        return True
    else:
        return False

def parallel_kmeans_ab(Lmatrix,Rmatrix,index_item,k):
    label = index_item[0]
    indices = index_item[1]
    nodes_group = {"L": [], "R": []}
    hemi = label.split("_")[0]
    if k>1:
        if hemi == "L":
            matrix = Lmatrix
        else:
            matrix = Rmatrix
        parcel_matrix = matrix[0][indices,:][:,indices]
        point_list = matrix[1]

        #centers = get_random_centers(k,parcel_matrix)
        points_init = list(point_list[i] for i in indices)
        centers = initialize(points_init,k)
        centers_tmp = centers
        groups = create_groups (centers,parcel_matrix)
        for i in range(20):
            centers = recalc_center(parcel_matrix,groups.items())
            noChange = stop_critery(point_list,centers,centers_tmp)
            centers_tmp = centers

            groups = create_groups(centers, parcel_matrix)
            if noChange:
                break
            i+=1
        for key,group in groups.items():
            group = [indices[i] for i in group]
            nodes_group[hemi].append(group)
    else:
        nodes_group[hemi]= [[indices]]
    return nodes_group

def merge_dicts(lot):
    nodes_group = {"L": [], "R": []}
    for dict in lot:
        for hemi, groups in dict.items():
            for group in groups:
                nodes_group[hemi].append(group)
    return nodes_group


def fit_ab(Lmatrix,Rmatrix,indices,ks):

    pool = mp.Pool(mp.cpu_count())
    kmeans_ab = partial(parallel_kmeans_ab, Lmatrix,Rmatrix)
    results = pool.starmap(kmeans_ab, zip([index_item for index_item in indices.items()],[k for k in ks]))
    nodes_group = merge_dicts(results)

    return nodes_group

def fit_all(matrix,point_list,k):
    if k > 1 and matrix != None:
        nodes_group = []
        centers = get_random_centers(k,matrix)
        #centers = initialize(point_list, k)
        centers_tmp = centers
        groups = create_groups (centers,matrix)

        for i in range(20):
            pool = mp.Pool(mp.cpu_count())
            centers_fun = partial(recalc_center_all, matrix)
            results = pool.map(centers_fun, [group for group in groups.items()])
            centers = merge_centroids(results)
            pool.close()
            noChange = stop_critery(point_list,centers,centers_tmp)
            centers_tmp = centers
            groups = create_groups(centers, matrix)
            if noChange:
                break
        for key,group in groups.items():
            nodes_group.append(group)
    else:
        nodes_group = []
    return nodes_group
