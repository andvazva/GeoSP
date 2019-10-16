#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 19/05/2019
#Last update: 16/10/2019

from classes import *
import IO
from scipy.spatial import distance
import geo_kmeans
import argparse
import time
import scipy.sparse as sp
import collections

def create_labels(clusters,node_list,npoints):
    label = 0
    labels = np.zeros(npoints,dtype = int)
    for points in clusters:
        for p in points:
            point = node_list[p]
            labels[p] = label
        label+=1
    return labels


def create_matrix(points,polygons):
    point_list = {}
    data = {}
    nodes = collections.OrderedDict()
    for tri in polygons:
        v0,v1,v2 = tri[0], tri[1], tri[2]
        nodes[v0]=0
        nodes[v1]=0
        nodes[v2]=0
        point_list[v0], point_list[v1], point_list[v1] = points[v0], points[v1], points[v2]

        data[(v0,v1)] = distance.euclidean(points[v0], points[v1])
        data[(v0,v2)] = distance.euclidean(points[v0], points[v2])
        data[(v1,v2)] = distance.euclidean(points[v1], points[v2])


    row_ind = list(k[0] for k, v in data.items())
    col_ind = list(k[1] for k, v in data.items())
    values = list(v for k,v in data.items())

    matrix = sp.csr_matrix((values, (row_ind, col_ind)))

    return matrix,point_list,list(nodes)


def all_parcellation(points,polygons,k):
    matrix,point_list,node_list = create_matrix(points,polygons)
    clusters = geo_kmeans.fit_all(matrix,point_list,k)
    labels = create_labels(clusters,node_list,len(points))

    return labels


def main():

    parser = argparse.ArgumentParser(description='Geodesic Parcelation')
    parser.add_argument('--Lobj', type=str, help='Left mesh .obj of subject')
    parser.add_argument('--Robj', type=str, help='Right mesh.obj of subject')
    parser.add_argument('--Lk', type=int, help='Number of parcels for left hemisphere')
    parser.add_argument('--Rk', type=int, help='Number of parcels for rigth hemisphere')
    parser.add_argument('--d', type=int, default = 0, help='1 to use Desikan atlas, 0 to use all brain')
    parser.add_argument('--output-path', type=str, help='Output directory')
    args = parser.parse_args()

    Lmesh_path = args.Lobj
    Rmesh_path = args.Robj
    # Llabels_path = "input_data/lh_labels.txt"
    # Rlabels_path = "input_data/rh_labels.txt"
    # Lk_path = "input_data/Lk.txt"
    # Rk_path = "input_data/Rk.txt"
    output_path = args.output_path

    IO.create_dirs(output_path)

    LMesh = Mesh(Lmesh_path)
    RMesh = Mesh(Rmesh_path)
    # Llabels = IO.read_labels(Llabels_path)
    # Rlabels = IO.read_labels(Rlabels_path)
    # Lk = IO.read_k(Lk_path)
    # Rk = IO.read_k(Rk_path)

    init = time.time()
    if args.d == 0:
        Llabels = all_parcellation(LMesh.points,LMesh.polygons, args.Lk)
        Rlablels = all_parcellation(RMesh.points,RMesh.polygons, args.Rk)

    end = time.time()
    print("tiempo: "+str(end-init))

    IO.write_labels(Llabels, output_path,"L")
    IO.write_labels(Rlablels, output_path,"R")


if __name__ == '__main__':
    main()