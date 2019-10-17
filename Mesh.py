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
