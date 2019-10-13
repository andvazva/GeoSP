#Authors:
# Narciso López López
# Andrea Vázquez Varela
#Creation date: 19/05/2019
#Last update: 19/05/2019

import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

class Vertex:
    def __init__(self,index,points):
        self.index = index
        self.points = points
        self.label_sparcel = -1

class Triangle:
    def __init__(self,index,label,v0,v1,v2):
        self.index = index
        self.label = label
        self.label_sparcel = -1
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2

class Parcel:
    def __init__(self,label):
        self.label = label
        self.parent = None
        self.triangles = []
        self.sub_parcels = []


class Mesh():
    def __init__(self,path):
        self.reader = vtk.vtkOBJReader()
        self.reader.SetFileName(path)
        self.reader.Update()
        self.points,self.polygons = self.set_polydata(self.reader)

    def set_polydata(self,reader):
        self.points = (vtk_to_numpy(reader.GetOutput().GetPoints().GetData()))
        cells = reader.GetOutput().GetPolys()
        nCells = cells.GetNumberOfCells()
        array = cells.GetData()
        assert (array.GetNumberOfValues() % nCells == 0)
        nCols = array.GetNumberOfValues() // nCells
        numpy_cells = vtk_to_numpy(array)
        numpy_cells = numpy_cells.reshape((-1, nCols))
        cells_reshape = []
        for i in range(len(numpy_cells)):
            cells_reshape.append(list(numpy_cells[i][1::]))
        self.polygons = np.asarray(cells_reshape)
        return self.points,self.polygons
