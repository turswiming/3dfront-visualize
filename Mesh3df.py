import vtk

import numpy as np
class Mesh3df:
    def __init__(self,o3dmesh:vtk.vtkPolyData,type:str,uid:str):
        self.o3dmesh = o3dmesh
        self.type = type
        self.uid = uid