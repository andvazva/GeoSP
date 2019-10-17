#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 19/05/2019
#Last update: 16/10/2019

import shutil
import os

#Crea los directorios
def create_dirs(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)

#Lee las etiquetas del atlas
def read_labels(path):
    with open(path,"r+") as f:
        lines = f.readlines()
        labels = list([int(l) for l in line.split()][0] for line in lines)
    return labels


def write_labels(labels,atlas_path,hemi):
    file_path = atlas_path+"/"+hemi+"labels.txt"
    f = open(file_path,"w+")
    for label in labels:
        f.write(str(label)+"\n")
    f.close()

def write_sparcels(sp_map, path,hemi):
    with open(path+"/"+hemi+"sparcels.txt","w+") as f:
        for key,values in sp_map.items():
            f.write(str(key)+": ")
            f.write(" ".join(list(map(str,values))))
            f.write("\n")