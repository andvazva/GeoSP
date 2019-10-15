#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 19/05/2019
#Last update: 15/10/2019

import shutil
import os

#Crea los directorios
def create_dirs(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

#Lee las etiquetas del atlas
def read_labels(path):
    labels = []
    file = open(path,"r+")
    lines = file.readlines()
    for line in lines:
        label = int(line)
        if label == -1:
            label = 0
        labels.append(label)
    file.close()
    return labels

#Lee los valores de k para kmeans
def read_k(path):
    k = []
    file = open(path,"r+")
    lines = file.readlines()
    for line in lines:
        k.append(int(line.split(" ")[1]))
    file.close()
    return k

#Escribe la información de las parcelas duras del atlas
def write_hparcels(aparcels,atlas_path,hemi):
    file_path = atlas_path+"/"+hemi+"hard_parcels.txt"
    f = open(file_path,"w+")
    for ap in aparcels:
        if len(ap.sub_parcels) > 0:
            f.write("ap "+str(ap.label)+"\n") #Anatomic parcel
            for hp in ap.sub_parcels:
                if len(hp.triangles)>0:
                    f.write("hp " + str(hp.label) + "\n")  # hard parcel
                    f.write("t")
                    for t in hp.triangles:  #Se escriben los índices de los triángulos
                        f.write(" "+str(t.index))
                    f.write("\n")
    f.close()

def write_labels(labels,atlas_path,hemi):
    file_path = atlas_path+"/"+hemi+"vertex_labels.txt"
    f = open(file_path,"w+")
    for label in labels:
        f.write(str(label)+"\n")
    f.close()