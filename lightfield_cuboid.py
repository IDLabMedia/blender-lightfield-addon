import math
import random
import bpy
import bmesh
from .camera_position import CameraPosition

from mathutils import Color
from .lightfield import LightfieldPropertyGroup


class LightfieldCuboid(LightfieldPropertyGroup):

    def construct(self):
        visuals = self.default_construct()
        self.lf_type = 'CUBOID'
        self.obj_empty.empty_display_type = 'CUBE'

        # Update lightfield references
        self.obj_visuals.add().obj_visual = visuals[0]
        self.obj_visuals.add().obj_visual = visuals[1]
        self.obj_visuals.add().obj_visual = visuals[2]

        self.obj_grid = visuals[0]

    def construct_visuals(self, collection):
        grid = self.create_grid()
        space = self.create_space()
        front = self.create_front()

        # Add to lightfield collection
        collection.objects.link(grid)
        collection.objects.link(space)
        collection.objects.link(front)

        return [grid, space, front]

    def create_grid(self):
        """
        Create the visual grid indicating all the camera positions.

        :return: Object containing grid.
        """
        name = self.construct_names()['grid']

        # Mesh data
        mesh = bpy.data.meshes.new(name)
        # Object data
        grid = bpy.data.objects.new(name, mesh)

        # Create bmesh to construct grid.
        bm = bmesh.new()

        # Add vertices
        # Front & Back (Z constant):
        for y in range(self.num_cams_y):
            for x in range(self.num_cams_x):
                bm.verts.new((-0.5 + x / (self.num_cams_x - 1),
                              0.5 - y / (self.num_cams_y - 1),
                              0.5))
                bm.verts.new((-0.5 + x / (self.num_cams_x - 1),
                              0.5 - y / (self.num_cams_y - 1),
                              -0.5))

        # Left & Right (X constant):
        for y in range(self.num_cams_y):
            for z in range(self.num_cams_z):
                bm.verts.new((-0.5,
                              0.5 - y / (self.num_cams_y - 1),
                              -0.5 + z / (self.num_cams_z - 1)))
                bm.verts.new((0.5,
                              0.5 - y / (self.num_cams_y - 1),
                              -0.5 + z / (self.num_cams_z - 1)))

        # Top & Bottom (Y constant):
        for z in range(self.num_cams_z):
            for x in range(self.num_cams_x):
                bm.verts.new((-0.5 + x / (self.num_cams_x - 1),
                              0.5,
                              -0.5 + z / (self.num_cams_z - 1)))
                bm.verts.new((-0.5 + x / (self.num_cams_x - 1),
                              -0.5,
                              -0.5 + z / (self.num_cams_z - 1)))

        bm.to_mesh(mesh)
        bm.free()

        grid.hide_render = True

        return grid

    def create_space(self):
        """
        Create visual that represents the space the lightfield is occupying.

        :return: Object.
        """
        name = self.construct_names()['space']
        bpy.ops.mesh.primitive_cube_add(location=(0.0, 0.0, 0.0))
        space = bpy.context.object
        space.scale = [0.5] * 3
        space.name = name

        space.data.name = name
        # Unlink the object from its current collection
        space.users_collection[0].objects.unlink(space)

        space_mat = bpy.data.materials.new(name)
        col = Color()
        col.hsv = (random.random(), 1.0, 0.8)
        space_mat.diffuse_color = col[:] + (0.1,)
        space.data.materials.append(space_mat)
        space.show_wire = True

        space.hide_render = True

        return space

    @staticmethod
    def construct_names():
        base = "LFCuboid"
        return {'lightfield': base,
                'camera': "{}_Camera".format(base),
                'grid': "{}_Grid".format(base),
                'space': "{}_Space".format(base),
                'front': "{}_Front".format(base)}

    def position_generator(self):
        # TODO: implement cube-map render
        sides = ['f', 'b', 'l', 'r', 'u', 'd']
        side_map = {'f': [self.num_cams_x, self.num_cams_y],
                    'b': [self.num_cams_x, self.num_cams_y],
                    'l': [self.num_cams_z, self.num_cams_y],
                    'r': [self.num_cams_z, self.num_cams_y],
                    'u': [self.num_cams_x, self.num_cams_z],
                    'd': [self.num_cams_x, self.num_cams_z], }
        for s in sides:
            local_x_dir = side_map[s][0]
            local_y_dir = side_map[s][1]
            for local_y in range(local_y_dir):
                for local_x in range(local_x_dir):
                    yield self.get_camera_pos(s, local_x, local_y)

    def get_camera_pos(self, side, x, y):
        base_x = 1 / (self.num_cams_x - 1)
        base_y = 1 / (self.num_cams_y - 1)
        base_z = 1 / (self.num_cams_z - 1)

        if side == 'f':
            return CameraPosition("view_{}{:04d}f".format(side, y * self.num_cams_x + x),
                                  -0.5 + x * base_x,
                                  0.5 - y * base_y,
                                  -0.5)

        elif side == 'b':
            return CameraPosition("view_{}{:04d}f".format(side, y * self.num_cams_x + x),
                                  0.5 - x * base_x,
                                  0.5 - y * base_y,
                                  0.5,
                                  theta=math.pi)

        elif side == 'l':
            return CameraPosition("view_{}{:04d}f".format(side, y * self.num_cams_z + x),
                                  -0.5,
                                  0.5 - y * base_y,
                                  0.5 - x * base_z,
                                  theta=math.pi / 2)

        elif side == 'r':
            return CameraPosition("view_{}{:04d}f".format(side, y * self.num_cams_z + x),
                                  0.5,
                                  0.5 - y * base_y,
                                  -0.5 + x * base_z,
                                  theta=-math.pi / 2)

        elif side == 'u':
            return CameraPosition("view_{}{:04d}f".format(side, y * self.num_cams_x + x),
                                  -0.5 + x * base_x,
                                  0.5,
                                  0.5 - y * base_z,
                                  alpha=math.pi / 2)

        elif side == 'd':
            return CameraPosition("view_{}{:04d}f".format(side, y * self.num_cams_x + x),
                                  -0.5 + x * base_x,
                                  -0.5,
                                  -0.5 + y * base_z,
                                  alpha=-math.pi / 2)
