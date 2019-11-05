from Mesh import *
import IO
import geo_kmeans
import argparse
import time
import scipy.sparse as sp
import collections

def create_sp_map(labels,labels_atlas):
    sp_map = {}
    for i in range(len(labels)):
        atlas_label = labels_atlas[i]
        new_label = labels[i]
        if atlas_label not in sp_map:
            sp_map[atlas_label] = set([new_label])
        else:
            sp_map[atlas_label].add(new_label)
    return sp_map

def create_subparcels(Llabels_atlas,Rlabels_atlas,Llabels,Rlabels):
    Lsp_map = create_sp_map(Llabels,Llabels_atlas)
    Rsp_map = create_sp_map(Rlabels,Rlabels_atlas)

    return Lsp_map, Rsp_map

def create_labels(clusters,npoints):
    label = 0
    labels = np.zeros(npoints,dtype = int)
    for points in clusters:
        for p in points:
            labels[p] = label
        label+=1
    return labels

def create_labels_ab(hemi_clusters,Lnpoints,Rnpoints):
    Llabel = len(hemi_clusters["L"])
    Rlabel = len(hemi_clusters["R"])
    Llabels = np.zeros(Lnpoints,dtype= int)
    Rlabels = np.zeros(Rnpoints,dtype= int)
    for hemi,clusters in hemi_clusters.items():
        for points in clusters:
            for p in points:
                if hemi == "L":
                    Llabels[p] = Llabel
                else:
                    Rlabels[p] = Rlabel
            if hemi == "L":
                Llabel+=1
            else:
                Rlabel+=1

    return Llabels, Rlabels


def create_matrix(points, polygons):
    data = {}
    nodes = collections.OrderedDict()
    for tri in polygons:
        v0,v1,v2 = tri[0], tri[1], tri[2]
        nodes[v0], nodes[v1], nodes[v2] = 0, 0, 0

        dist01 = np.linalg.norm(points[v0] - points[v1])
        dist02 = np.linalg.norm(points[v0] - points[v2])
        dist12 = np.linalg.norm(points[v1] - points[v2])
        data[(v0, v1)], data[(v1, v0)] = dist01, dist01
        data[(v0, v2)], data[(v2, v0)] = dist02, dist02
        data[(v1, v2)], data[(v2, v1)] = dist12, dist12

    row_ind = list(k[0] for k, v in data.items())
    col_ind = list(k[1] for k, v in data.items())

    point_list = {}
    node_list = list(nodes)
    for i in node_list:
        point_list[i] = points[i]

    values = list(v for k,v in data.items())
    matrix = sp.csr_matrix((values, (row_ind, col_ind)))

    return matrix,point_list

def get_indices(labels,hemi):
    indices = collections.OrderedDict()
    for i,label in enumerate(labels):
        index = hemi+"_"+str(label)
        if index not in indices:
            indices[index] = [i]
        else:
            indices[index].append(i)
    return indices


def all_parcellation(mesh,k):
    points, polygons = mesh.points, mesh.polygons
    matrix,point_list = create_matrix(points,polygons)
    clusters = geo_kmeans.fit_all(matrix,point_list,k)
    labels = create_labels(clusters,len(points))
    return labels


def ab_parcellation(LMesh,RMesh,Llabels,Rlabels,Lk,Rk):
    Lmatrix = create_matrix(LMesh.points,LMesh.polygons)
    Rmatrix = create_matrix(RMesh.points,RMesh.polygons)
    Lindices = get_indices(Llabels,"L")
    Rindices = get_indices(Rlabels,"R")
    Lindices.update(Rindices)
    Lk.extend(Rk)

    clusters = geo_kmeans.fit_ab(Lmatrix,Rmatrix,Lindices,Lk)
    Llabels, Rlabels = create_labels_ab(clusters,len(LMesh.points),len(RMesh.points))
    return Llabels,Rlabels



def main():

    parser = argparse.ArgumentParser(description='Geodesic Parcelation')
    parser.add_argument('--Lobj', type=str, help='Left mesh .obj of subject')
    parser.add_argument('--Robj', type=str, help='Right mesh.obj of subject')
    parser.add_argument('--Llabels', type=str, help='Input file with left labels')
    parser.add_argument('--Rlabels', type=str, help='Input file with right labels')
    parser.add_argument('--Lk-file', type=str, help='Input file with left ks')
    parser.add_argument('--Rk-file', type=str, help='Input file with right ks')
    parser.add_argument('--Lk', type=int, help='Number of parcels for left hemisphere')
    parser.add_argument('--Rk', type=int, help='Number of parcels for rigth hemisphere')
    parser.add_argument('--AB', type=int, default = 0, help='Atlas Based, 1 to subdivide oter atlas (like Desikan), 0 to use all brain')
    parser.add_argument('--output-path', type=str, help='Output directory')
    args = parser.parse_args()


    IO.create_dirs(args.output_path)
    LMesh = Mesh(args.Lobj)
    RMesh = Mesh(args.Robj)

    init = time.time()
    if args.AB == 0:
        Llabels = all_parcellation(LMesh, args.Lk)
        Rlabels = all_parcellation(RMesh, args.Rk)

    else:
        Llabels_atlas = IO.read_labels(args.Llabels)
        Rlabels_atlas = IO.read_labels(args.Rlabels)
        Lk = IO.read_labels(args.Lk_file)
        Rk = IO.read_labels(args.Rk_file)
        Llabels, Rlabels = ab_parcellation(LMesh,RMesh,Llabels_atlas,Rlabels_atlas,Lk,Rk)
        Lsp_map,Rsp_map = create_subparcels(Llabels_atlas,Rlabels_atlas,Llabels,Rlabels)

    end = time.time()
    print("Execution time of kmeans: "+str(round(end-init,2))+" seconds")

    IO.write_labels(Llabels, args.output_path,"L")
    IO.write_labels(Rlabels, args.output_path,"R")

    if args.AB == 1:
        IO.write_sparcels(Lsp_map, args.output_path,"L")
        IO.write_sparcels(Rsp_map, args.output_path,"R")

if __name__ == '__main__':
    main()
