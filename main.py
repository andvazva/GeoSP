#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 19/05/2019
#Last update: 11/10/2019

from classes import *
import IO
import networkx as nx
from scipy.spatial import distance
import geo_kmeans
import argparse
import time
import multiprocessing as mp
from functools import partial
import collections

created_sparcels = []
NPARCELS = 36  # Son 36 parcelas de desikan

#
def labeling(polygons,points,labels):
    triangles = []
    aparcels = []
    vertices = {}
    for i in range(NPARCELS):
        aparcels.append(Parcel(i))
    for i,p in enumerate(polygons):
        v0_index = p[0]
        v1_index = p[1]
        v2_index = p[2]
        label0 = labels[v0_index]
        label1 = labels[v1_index]
        label2 = labels[v2_index]
        if v0_index not in vertices:
            v0 = Vertex(v0_index, points[v0_index])
            vertices[v0_index] = v0
        else:
            v0 = vertices[v0_index]
        if v1_index not in vertices:
            v1 = Vertex(v1_index, points[v1_index])
            vertices[v1_index] = v1
        else:
            v1 = vertices[v1_index]
        if v2_index not in vertices:
            v2 = Vertex(v2_index, points[v2_index])
            vertices[v2_index] = v2
        else:
            v2 = vertices[v2_index]

        if (label0 == label1 == label2):
            trilabel = label2
        elif (label0 == label1 and label0!=label2):
            trilabel = label0
        elif (label1 == label2 and (label1!= label0)):
            trilabel = label1
        elif (label0 == label2) and (label0!=label1):
            trilabel = label0
        else:
            trilabel = label0
        tri = Triangle(i,trilabel,v0,v1,v2)
        aparcels[trilabel].triangles.append(tri)

    return aparcels,triangles


def create_matrix(aparcel):
    graph = nx.Graph()
    node_list = []
    for tri in aparcel.triangles:
        node0 = tri.v0
        node1 = tri.v1
        node2 = tri.v2
        if node0 not in graph.nodes():
            graph.add_node(node0)
            node_list.append(node0)
        if node1 not in graph.nodes():
            graph.add_node(node1)
            node_list.append(node1)
        if node2 not in graph.nodes():
            graph.add_node(node2)
            node_list.append(node2)

        dist01 = distance.euclidean(node0.points, node1.points)
        dist02 = distance.euclidean(node0.points, node2.points)
        dist12 = distance.euclidean(node1.points, node2.points)
        graph.add_edge(node0, node1, weight=dist01)
        graph.add_edge(node0, node2, weight=dist02)
        graph.add_edge(node1, node2, weight=dist12)

    if nx.number_connected_components(graph) > 1:
        remove_small_cc(graph,node_list)
    point_list = [node.points for node in node_list]

    if len(graph.nodes)>0:
        scipy_matrix = nx.to_scipy_sparse_matrix(graph)
    else:
        scipy_matrix = None
    return scipy_matrix,node_list,point_list



def label_triangles(ap):
    for tri in ap.triangles:
        label0 = tri.v0.label_sparcel
        label1 = tri.v1.label_sparcel
        label2 = tri.v2.label_sparcel

        if (label0 == label1 == label2):
            trilabel = label2
        elif (label0 == label1 and label0!=label2):
            trilabel = label0
        elif (label1 == label2 and (label1!= label0)):
            trilabel = label1
        elif (label0 == label2) and (label0!=label1):
            trilabel = label0
        else:
            trilabel = label0
        tri.label_sparcel = trilabel

def create_sparcels(ap):
    map_triangles = {}
    for tri in ap.triangles:
        label = tri.label_sparcel
        if label != -1:
            if label not in map_triangles:
                map_triangles[label] = [tri]
            else:
                map_triangles[label].append(tri)
    for label,triangles in map_triangles.items():
        global created_sparcels
        if label not in created_sparcels:
            sp = Parcel(label)
            sp.triangles = triangles
            sp.parent = ap
            ap.sub_parcels.append(sp)
            created_sparcels.append(label)

def remove_small_cc(graph,nodelist):
    cc = list(nx.connected_components(graph))
    max_len = -1
    for c in cc:
        if len(c) >= max_len:
            max_len = len(c)
    for c in cc:
        if len(c) < max_len:
            for node in c:
                graph.remove_node(node)
                nodelist.remove(node)
    return nodelist

def find_aparcel(parcels,label):
    for p in parcels:
        if p.label == label:
            return p

def merge_results(clusters,matrices,Laparcels,Raparcels):
    global NPARCELS
    i = 0
    for key,matrix in matrices.items():
        hemi = key.split("_")[0]
        alabel = int(key.split("_")[1])
        if hemi == 'L':
            ap = find_aparcel(Laparcels,alabel)
        else:
            ap = find_aparcel(Raparcels, alabel)
        nodelist = matrix[1]
        clusts = clusters[i]
        i+=1
        if len(clusts) > 0:
            for c in clusts:
                for index in c:
                    vertex = nodelist[index]
                    vertex.label_sparcel = NPARCELS
                NPARCELS += 1
        else:
            c = nodelist
            for vertex in c:
                vertex.label_sparcel = NPARCELS
            NPARCELS += 1
        label_triangles(ap)
        create_sparcels(ap)

def geodesic_kmeans(Lks, Rks,matrix_map):
    alabel = matrix_map[0]
    hemi = alabel.split("_")[0]
    alabel = int(alabel.split("_")[1])
    matrix,nodelist,pointlist = matrix_map[1]
    if hemi == "L":
        k = Lks[alabel]
    else:
        k = Rks[alabel]
    #print("Parcela: " + str(alabel))
    #print("longitud: "+ str(matrix.shape[0]))
    #print("K: "+str(k))
    return geo_kmeans.fit_desikan(matrix,pointlist,k)

def geodesic_kmeans_all(Lks,Rks,matrices):
    clusters = []
    for matrix_map in matrices.items():
        alabel = matrix_map[0]
        hemi = alabel.split("_")[0]
        alabel = int(alabel.split("_")[1])
        matrix,nodelist,pointlist = matrix_map[1]
        if hemi == "L":
            k = Lks
        else:
            k = Rks
        #print("Parcela: " + str(alabel))
        #print("longitud: "+ str(matrix.shape[0]))
        #print("K: "+str(k))
        clusters.append(geo_kmeans.fit_all(matrix,pointlist,k))
    return clusters

def create_matrices(aparcels,hemi):
    matrices = collections.OrderedDict()
    for ap in aparcels:
        matrices[hemi+"_"+str(ap.label)] = create_matrix(ap)
    return matrices

def desikan_parcelation(LMesh,RMesh,Llabels,Rlabels,Lk,Rk):

    Laparcels, Ltriangles = labeling(LMesh.polygons,LMesh.points, Llabels)
    Raparcels, Rtriangles = labeling(RMesh.polygons,RMesh.points, Rlabels)

    Lmatrices = create_matrices(Laparcels,"L")
    Rmatrices = create_matrices(Raparcels,"R")
    Lmatrices.update(Rmatrices)

    Lk = [1]
    Lk.extend([8]*35)
    Rk = [1]
    Rk.extend([8]*35)

    pool = mp.Pool(mp.cpu_count())
    #pool = mp.Pool(1)
    geodesic_fun = partial(geodesic_kmeans,Lk,Rk)
    clusters = pool.map(geodesic_fun, [matrix_map for matrix_map in Lmatrices.items()])
    merge_results(clusters,Lmatrices,Laparcels,Raparcels)
    pool.close()


    return Laparcels,Raparcels

def all_parcelation(LMesh,RMesh,Llabels,Rlabels,Lk,Rk):
    global NPARCELS
    NPARCELS = 1

    # Lk = 225
    # Rk = 199
#210 350 560
    Lk = 280
    Rk = 280

    Llabels = [0 for i in range(len(Llabels))]
    Rlabels = [0 for i in range(len(Rlabels))]
    print("etiquetado")
    Laparcels, Ltriangles = labeling(LMesh.polygons,LMesh.points, Llabels)
    Raparcels, Rtriangles = labeling(RMesh.polygons,RMesh.points, Rlabels)

    print("creando matrices")
    Lmatrices = create_matrices(Laparcels,"L")
    Rmatrices = create_matrices(Raparcels,"R")
    Lmatrices.update(Rmatrices)

    clusters = geodesic_kmeans_all(Lk,Rk,Lmatrices)
    merge_results(clusters,Lmatrices,Laparcels,Raparcels)


    return Laparcels,Raparcels


def main():

    parser = argparse.ArgumentParser(description='Create parcel of multiple subjects')
    parser.add_argument('--Lobj', type=str, help='Left mesh .obj of subject')
    parser.add_argument('--Robj', type=str, help='Right mesh.obj of subject')
    parser.add_argument('--d', type=int, default = 1, help='1 to use Desikan atlas, 0 to use all brain')
    parser.add_argument('--output-path', type=str, help='Output directory')
    args = parser.parse_args()

    Lmesh_path = args.Lobj
    Rmesh_path = args.Robj
    Llabels_path = "input_data/lh_labels.txt"
    Rlabels_path = "input_data/rh_labels.txt"
    Lk_path = "input_data/Lk.txt"
    Rk_path = "input_data/Rk.txt"
    output_path = args.output_path

    atlas_path = IO.create_dirs(output_path)

    LMesh = Mesh(Lmesh_path)
    RMesh = Mesh(Rmesh_path)
    Llabels = IO.read_labels(Llabels_path)
    Rlabels = IO.read_labels(Rlabels_path)
    Lk = IO.read_k(Lk_path)
    Rk = IO.read_k(Rk_path)

    init = time.time()
    if args.d == 1:
        Laparcels, Raparcels = desikan_parcelation(LMesh, RMesh, Llabels, Rlabels, Lk, Rk)
    else:
        Laparcels, Raparcels = all_parcelation(LMesh, RMesh, Llabels, Rlabels, Lk, Rk)
    end = time.time()
    print("tiempo: "+str(end-init))

    IO.write_hparcels(Laparcels, atlas_path,"L")
    IO.write_hparcels(Raparcels, atlas_path,"R")


if __name__ == '__main__':
    main()