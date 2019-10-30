import random
import bpy
from .camera_position import CameraPosition

from mathutils import Color, Vector, Matrix
from .lightfield import LightfieldPropertyGroup


class LightfieldSphere(LightfieldPropertyGroup):

    def construct(self):
        visuals = self.default_construct()
        self.lf_type = 'SPHERE'
        self.obj_empty.empty_display_type = 'SPHERE'

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

        # Remember selected objects
        # selected = bpy.context.selected_objects

        # Object data
        bpy.ops.mesh.primitive_ico_sphere_add(location=(0.0, 0.0, 0.0), subdivisions=self.num_cams_subdiv, radius=0.5)
        grid = bpy.context.active_object
        bpy.ops.object.editmode_toggle()

        bpy.ops.mesh.delete(type='EDGE_FACE')
        bpy.ops.object.editmode_toggle()
        grid.name = name
        # Unlink the object from its current collection
        grid.users_collection[0].objects.unlink(grid)

        grid.hide_render = True

        return grid

    def create_space(self):
        """
        Create visual that represents the space the lightfield is occupying.

        :return: Object.
        """

        name = self.construct_names()['space']
        bpy.ops.mesh.primitive_ico_sphere_add(location=(0.0, 0.0, 0.0), subdivisions=self.num_cams_subdiv, radius=0.5)
        space = bpy.context.object
        bpy.ops.object.shade_smooth()
        space.name = name

        space.data.name = name
        # Unlink the object from its current collection
        space.users_collection[0].objects.unlink(space)

        space_mat = bpy.data.materials.new(name)
        col = Color()
        col.hsv = (random.random(), 1.0, 0.8)
        space_mat.diffuse_color = col[:] + (0.3,)
        space.data.materials.append(space_mat)

        space.hide_render = True

        return space

    @staticmethod
    def construct_names():
        base = "LFSphere"
        return {'lightfield': base,
                'camera': "{}_Camera".format(base),
                'grid': "{}_Grid".format(base),
                'space': "{}_Space".format(base),
                'front': "{}_Front".format(base),
                'edges': "{}_Edges".format(base)}

    def position_generator(self):
        # TODO: implement cube-map render
        for index in range(len(self.obj_grid.data.vertices)):
            yield self.get_camera_pos(index)

    def get_camera_pos(self, index):
        vertex = self.obj_grid.data.vertices[index]

        normal = vertex.normal
        z = Vector([0.0, 1.0, 0.0])
        side = z.cross(normal)
        if side.length > 0.0001:
            up = side.cross(normal)

            basis = Matrix.Identity(3)
            basis.col[0] = -side
            basis.col[1] = -up
            basis.col[2] = -normal
            # basis = basis.to_4x4()
            euler = basis.to_euler()
        else:
            euler = vertex.normal.to_track_quat('-Z', 'Y').to_euler()
            euler[2] = 0

        return CameraPosition("view_{:04d}f".format(index),
                              vertex.co[0],
                              vertex.co[1],
                              vertex.co[2],
                              alpha=euler[0],
                              theta=euler[1],
                              phi=euler[2])
