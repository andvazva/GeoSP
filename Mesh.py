# Copyright (C) 2019  Andrea Vázquez Varela

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

#Authors:
# Narciso López López
# Andrea Vázquez Varela
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
