import open3d as o3d
import numpy as np
import json
from Mesh3df import Mesh3df

class Visualize3dfront:
    def __init__(self,path:str):
        #load json file from path
        self.path = path
        self.data = self.__load_json()
        self.meshes = {}
        datamesh = self.data['mesh']
        self.meshes = self.__load_mesh(datamesh)
        pass
    def __load_json(self):
        with open(self.path) as f:
            data = json.load(f)
        return data
    
    def __load_mesh(self,datamesh:object):
        meshes = {}
        for mesh_data in datamesh:
            xyz = np.array(mesh_data['xyz']).reshape((-1, 3))
            xyz = np.array(xyz, dtype=np.float64)
            normal = np.array(mesh_data['normal']).reshape((-1, 3))
            normal = np.array(normal, dtype=np.float64)
            faces = np.array(mesh_data['faces']).reshape((-1, 3))
            faces = np.array(faces, dtype=np.int32)

            mesh = o3d.geometry.TriangleMesh()
            mesh.vertices = o3d.utility.Vector3dVector(xyz)
            mesh.vertex_normals = o3d.utility.Vector3dVector(normal)
            mesh.triangles = o3d.utility.Vector3iVector(faces)
            mesh3df = Mesh3df(mesh, mesh_data['type'], mesh_data['uid'])

            meshes[mesh_data['uid']] = mesh3df
        return meshes
    
    def visualize(self):
        meshs = []
        for uid, mesh in self.meshes.items():
            meshs.append(mesh.o3dmesh)
        self.__visualize(meshs)
    
    def __visualize(self, objs:list[o3d.geometry.TriangleMesh]):
        vis = o3d.visualization.Visualizer()
        vis.create_window()
        vis.get_render_option().light_on = True
        render = vis.get_render_option()
        render.mesh_shade_option = o3d.visualization.MeshShadeOption.Color
        # Run the visualizer
        for obj in objs:
            color = np.random.rand(1, 3).repeat(len(obj.vertices), axis=0)
            obj.vertex_colors = o3d.utility.Vector3dVector(color)
            vis.add_geometry(obj)
        vis.run()
        vis.destroy_window()


if __name__ == "__main__":
    path = "3D-FRONT\\0a8d471a-2587-458a-9214-586e003e9cf9.json"
    vis = Visualize3dfront(path)
    vis.visualize()

    
