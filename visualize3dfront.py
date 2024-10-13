import vtk
import numpy as np
from tqdm import tqdm
import logging
import json
import os
import math
from typing import List, Tuple

from Mesh3df import Mesh3df
from MeshType import MeshType

logging.basicConfig(level=logging.DEBUG)

class Visualize3dfront:
    def __init__(self, path: str):
        # Load json file from path
        self.path = path
        self.data = self.__load_json()
        self.meshes = {}
        datamesh = self.data['mesh']
        self.meshes = self.__load_mesh(datamesh)

    def __del__(self):
        del self.meshes
        del self.data
        del self.path

    def __load_json(self):
        with open(self.path) as f:
            data = json.load(f)
        return data

    def __load_mesh(self, datamesh: object):
        meshes = {}
        for mesh_data in datamesh:
            xyz = np.array(mesh_data['xyz']).reshape((-1, 3)).astype(np.float64)
            normal = np.array(mesh_data['normal']).reshape((-1, 3)).astype(np.float64)
            faces = np.array(mesh_data['faces']).reshape((-1, 3)).astype(np.int64)

            # Create VTK points
            points = vtk.vtkPoints()
            for point in xyz:
                points.InsertNextPoint(point)

            # Create VTK faces
            vtk_faces = vtk.vtkCellArray()
            for face in faces:
                vtk_face = vtk.vtkTriangle()
                for i in range(3):
                    vtk_face.GetPointIds().SetId(i, face[i])
                vtk_faces.InsertNextCell(vtk_face)

            # Create VTK polydata
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(vtk_faces)

            # Create VTK normals
            # vtk_normals = vtk.vtkDoubleArray()
            # vtk_normals.SetNumberOfComponents(3)
            # vtk_normals.SetName("Normals")
            # for norm in normal:
            #     vtk_normals.InsertNextTuple(norm)
            # polydata.GetPointData().SetNormals(vtk_normals)

            mesh3df = Mesh3df(polydata, mesh_data['type'], mesh_data['uid'])
            meshes[mesh_data['uid']] = mesh3df
        return meshes

    def visualize(self, selected_types: None | list[MeshType]):
        meshs = []
        # Convert enum to str so that we can use it to filter
        selected_types = None if selected_types is None else [x.value for x in selected_types]
        if selected_types == []:
            selected_types = None

        for uid, mesh in self.meshes.items():
            if selected_types is None or mesh.type in selected_types:
                meshs.append(mesh.o3dmesh)
        self.__visualize(meshs)

    def __get_bbox(self, objs: list[Tuple[float, float, float, float, float, float]]):
        min_x = min([obj[0] for obj in objs])
        max_x = max([obj[1] for obj in objs])
        min_y = min([obj[2] for obj in objs])
        max_y = max([obj[3] for obj in objs])
        min_z = min([obj[4] for obj in objs])
        max_z = max([obj[5] for obj in objs])
        return min_x, max_x, min_y, max_y, min_z, max_z
        

    def __degree_to_radian(self, degree: float):
        return degree * math.pi / 180

    def __visualize(self, objs: list[vtk.vtkPolyData]):
        # Create a renderer, render window, and interactor
        renderer = vtk.vtkRenderer()
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window_interactor = vtk.vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)

        bboxs = []
        # Add the polydata to the renderer
        for obj in objs:
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(obj)
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().BackfaceCullingOff()
            bboxs.append(obj.GetBounds())
            renderer.AddActor(actor)

        # Set camera direction
        camera = renderer.GetActiveCamera()
        #get the center of the bounding box
        bbox = self.__get_bbox(bboxs)
        center = [(bbox[0] + bbox[1]) / 2, (bbox[2] + bbox[3]) / 2, (bbox[4] + bbox[5]) / 2]
        #get view angle
        view_angle = camera.GetViewAngle()
        print(view_angle)
        max_half_horizontal = max(bbox[1]-bbox[0], bbox[3]-bbox[2])/2
        distance = max_half_horizontal/math.tan(self.__degree_to_radian(view_angle/2))
        print(distance)
        camera.SetPosition(
            center[0], 
            center[1]+distance, 
            center[2])
        camera.SetViewUp(0, 0, 1)
        camera.SetFocalPoint(center[0], center[1], center[2])
        # Create SSAO pass
        ssao_pass = vtk.vtkSSAOPass()
        ssao_pass.SetRadius(5)
        # Create render passes
        basic_passes = vtk.vtkRenderStepsPass()
        ssao_pass.SetDelegatePass(basic_passes)

        # Set the render passes to the renderer
        renderer.SetPass(ssao_pass)

        # Render and start interaction
        render_window.Render()
        render_window_interactor.Start()

if __name__ == "__main__":
    path = "3D-FRONT\\0a8d471a-2587-458a-9214-586e003e9cf9.json"
    vis = Visualize3dfront(path)
    vis.visualize([
        MeshType.Floor, MeshType.Door, MeshType.Hole])