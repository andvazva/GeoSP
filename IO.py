# MIT License
#
# Copyright (c) 2019 Andrea
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#Authors:
# Narciso López-López lopez.lopez.narciso@gmail.com
# Andrea Vázquez Varela andvazva@gmail.com
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
