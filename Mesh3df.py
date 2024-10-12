import open3d as o3d
import numpy as np
class Mesh3df:
    def __init__(self,o3dmesh:o3d.geometry.TriangleMesh,type:str,uid:str):
        self.o3dmesh = o3dmesh
        self.type = type
        self.uid = uid