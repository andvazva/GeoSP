# GeoSP

This software implements the K-means method with geodetic distance to parcellate the cerebral cortex given the number of parcels, k.

The parcellation can be done in two ways: 
- Whole cortex parcellation: Parcellate the entire cerebral cortex, receiving a k for each hemisphere.
- Atlas based parcellation: Parcellate the brain cortex, creating sub-parcels in the parcels previously given by an entry atlas. 
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
It gives as a result the cortex divided into 35 parcels in the left hemisphere and another 35 in the right hemisphere.
### Atlas based parcellation
```
python3 main.py --Lobj input_data/lh.pial.obj --Robj input_data/rh.pial.obj --Lk-file input_data/example_atlas/Lk.txt --Rk-file input_data/example_atlas/Rk.txt --Llabels input_data/example_atlas/Llabels.txt --Rlabels input_data/example_atlas/Rlabels.txt --AB 1 --output-path output_atlas
```
Delivery as a result, the entry atlas parcellated. Each parcel of the atlas is divided according to the k of the files Lk.txt and Rk.txt

