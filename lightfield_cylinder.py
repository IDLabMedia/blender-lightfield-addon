import random
import math
import bpy
import bmesh
from .camera_position import CameraPosition

from mathutils import Color
from .lightfield import LightfieldPropertyGroup


class LightfieldCylinder(LightfieldPropertyGroup):

    def construct(self):
        visuals = self.default_construct()
        self.lf_type = 'CYLINDER'
        self.obj_empty.empty_display_type = 'CIRCLE'

        # Update lightfield references
        self.obj_visuals.add().obj_visual = visuals[0]
        self.obj_visuals.add().obj_visual = visuals[1]
        self.obj_visuals.add().obj_visual = visuals[2]
        self.obj_visuals.add().obj_visual = visuals[3]

        self.obj_grid = visuals[1]
        self.set_camera_to_first_view()

    def construct_visuals(self, collection):
        grid = self.create_grid()
        space, edges = self.create_space()
        front = self.create_front()

        # Add to lightfield collection
        collection.objects.link(grid)
        collection.objects.link(space)
        collection.objects.link(front)
        collection.objects.link(edges)

        return [space, grid, front, edges]


    def create_space(self):
        """
        Create visual that represents the space the lightfield is occupying.

        :return: Object.
        """

        # Used to clean up after making a mess with meshes.
        dumped_meshes = []

        # Top and bottom circle colored
        bpy.ops.mesh.primitive_circle_add(location=(0.0, 0.0,  1.0), fill_type='NGON')
        c2 = bpy.context.object
        bpy.ops.mesh.primitive_circle_add(location=(0.0, 0.0, -1.0), fill_type='NGON')
        c1 = bpy.context.object
        dumped_meshes.append(c2.data)
        dumped_meshes.append(c1.data)

        # Cylinder
        name = self.construct_names()['space']
        bpy.ops.mesh.primitive_cylinder_add(location=(0.0, 0.0, 0.0), end_fill_type='NGON')
        bpy.ops.object.shade_smooth()
        space = bpy.context.object
        space.name = name
        c1.select_set(True)
        c2.select_set(True)
        bpy.ops.object.join()
        space.scale = [0.5] * 3

        space.data.name = name
        # Unlink the object from its current collection
        space.users_collection[0].objects.unlink(space)

        space_mat = bpy.data.materials.new(name)
        col = Color()
        col.hsv = (random.random(), 1.0, 0.8)
        space_mat.diffuse_color = col[:] + (0.1,)
        space.data.materials.append(space_mat)

        space.hide_render = True

        # Top and bottom circle
        bpy.ops.mesh.primitive_circle_add(location=(0.0, 0.0,  1.0))
        c2 = bpy.context.object
        bpy.ops.mesh.primitive_circle_add(location=(0.0, 0.0, -1.0))
        c1 = bpy.context.object
        c1.name = self.construct_names()['edges']
        c1.data.name = c1.name
        c2.select_set(True)

        dumped_meshes.append(c2.data)

        bpy.ops.object.join()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
        c1.scale = [0.5] * 3
        c1.users_collection[0].objects.unlink(c1)

        # Delete all unused mesh data.
        for mesh in dumped_meshes:
            bpy.data.meshes.remove(mesh)

        return space, c1

    @staticmethod
    def construct_names():
        base = "LFCylinder"
        return {'lightfield': base,
                'camera': "{}_Camera".format(base),
                'grid': "{}_Grid".format(base),
                'space': "{}_Space".format(base),
                'front': "{}_Front".format(base),
                'edges': "{}_Edges".format(base)}

    def position_generator(self):
        # TODO: implement cube-map render
        for y in range(self.num_cams_y):
            for r in range(self.num_cams_radius):
                yield self.get_camera_pos(y, r)

    def get_camera_pos(self, y, r):
        base_y = 1 / (self.num_cams_y - 1)
        angle = r * 2 * math.pi / self.num_cams_radius
        return CameraPosition("view_{:04d}f".format(y * self.num_cams_radius + r),
                               0.5 * math.sin(angle),
                               0.5 * math.cos(angle),
                               0.5 - y * base_y,
                              alpha=0.5*math.pi,
                              phi=-angle + (math.pi if self.face_inside else 0))
