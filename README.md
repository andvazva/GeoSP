# GeoSP

This software implements the K-means method with geodesic distance to parcellate the cerebral cortex given the number of sub-parcels, k.

The parcellation can be done in two ways: 
- Whole cortex parcellation: Parcellate the entire cerebral cortex, receiving a k for each hemisphere.
- Atlas-based parcellation: Parcellate the brain cortex, creating sub-parcels in the anatomic parcels previously given by an entry atlas. 
 Any atlas can be used as input. 
 
 
## Code Dependencies

To use the code, it is necessary to install the following libraries:
- Numpy: https://numpy.org/
- Scipy: https://www.scipy.org/
- Vtk: https://vtk.org/

### Dependency installation via pip3 in Ubuntu
```
pip3 install numpy
pip3 install scipy
pip3 install vtk
```
### Dependency installation via apt in Ubuntu
```
sudo apt install python3-numpy
sudo apt install python3-scipy
```

## Use example
### All cortex parcellation
```
python3 main.py --Lobj input_data/lh.pial.obj --Robj input_data/rh.pial.obj --Lk 35 --Rk 35 --output-path output_atlas
```
It gives as a result the cortex divided into 35 anatomic parcels in the left hemisphere and another 35 in the right hemisphere.
### Atlas-based parcellation
```
python3 main.py --Lobj input_data/lh.pial.obj --Robj input_data/rh.pial.obj --Lk-file input_data/example_atlas/Lk.txt --Rk-file input_data/example_atlas/Rk.txt --Llabels input_data/example_atlas/Llabels.txt --Rlabels input_data/example_atlas/Rlabels.txt --AB 1 --output-path output_atlas
```
Delivery as a result, the entry atlas parcellated. Each anatomic parcel of the atlas is divided according to the k of the files Lk.txt and Rk.txt

## Input parameters
- **--Lobj**: Left mesh .obj of subject
- **--Robj**: Right mesh.obj of subject
- **--Llabels**: Input file with left labels **(Only for Atlas-Based parcellation)**
- **--Rlabels**: Input file with right labels **(Only for Atlas-Based parcellation)**
- **--Lk-file**: Input file with left ks **(Only for Atlas-Based parcellation)**
- **--Rk-file**: Input file with right ks **(Only for Atlas-Based parcellation)**
- **--Lk**: Number of sub-parcels for left hemisphere **(Only for all cortex parcellation)**
- **--Rk**: Number of sub-parcels for rigth hemisphere **(Only for all cortex parcellation)**
- **--AB**: Atlas-Based, 1 to subdivide other atlas (like Desikan), 0 to use all brain. Is 0 by default

## Input/output data format
### Input files
Sample data is provided in the input_data/example_atlas/ folder for the code to work. The format and source of the data are described below.
- lh.pial.obj and rh.pial.obj: It is a free sample mesh provided by the FreeSurfer test data. It has been sampled and converted to .obj. https://surfer.nmr.mgh.harvard.edu/
- Llabels.txt and Rlabels.txt: Contains the labels of the input atlas: All labels are in a column. There are as many labels as there are vertices in the mesh. Each label corresponds to a vertex. For example, if we have label 20 in row 7, it means that vertex 7 belongs to anatomic parcel 20.
- Lk-file.txt and Rk-file.txt: It contains all the values of k in a column. Each row corresponds to an anatomic parcel of the input atlas. Example: if in the example atlas we have 35 anatomic parcels, in the file we have 35 columns, if in row 5 there is a 3 (k=3), it means that parcel 5 will be divided into 3 sub-parcels.
### Output files
- Llabels.txt and Rlabels.txt: Those files are the output labels for each vertex. The format is the same as the input Llabels.txt and Rlabels.txt files.
- Lsparcels.txt and Rsparcels.txt: Indicate for each anatomic parcel of the atlas, the labels of the sub-parcels into which it is divided. The format is for row: label_parcel: label_sub-parcel1 label_sub-parcel2 label_sub-parcel3. **(Only for Atlas-Based parcellation)** Example:
0: 38 40 28
1: 29 31

## Results
### All cortex parcellation

The image below shows the result of the parcelation for the entire cortex with Lk = 35 and Rk = 35 (which are the same k as the Desikan atlas).
![alt text](https://raw.githubusercontent.com/andvazva/GeoSP/master/img/all_cortex.PNG)

### Atlas-Based parcellation
In the image below the atlas-based splitting is shown for the sample data provided. The input atlas has Lk = 35 and Rk = 35.
The method results in 92 parcels in the left hemisphere and 90 in the right hemisphere (which has been established in the files Lk-file.txt and Rk-file.txt)
![alt text](https://raw.githubusercontent.com/andvazva/GeoSP/master/img/atlas_based.PNG)

 
