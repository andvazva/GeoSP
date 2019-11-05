import vtk
from vtk.util.numpy_support import vtk_to_numpy
import numpy as np

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
