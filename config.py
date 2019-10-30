import bpy
import csv
import os

from . import utils, file_utils


class EXPORT_OT_lightfield_config(bpy.types.Operator):
    bl_idname = "lightfield.export_config"
    bl_label = """Export lightfield configuration"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        with open(bpy.path.abspath(lf.path_config_file), mode='w', newline='') as csv_file:
            # TODO: write projection-matrix
            writer = csv.writer(csv_file, delimiter=',')

            projection_matrix = lf.obj_camera.calc_matrix_camera(
                context.evaluated_depsgraph_get(),
                x=context.scene.render.resolution_x,
                y=context.scene.render.resolution_y,
                scale_x=context.scene.render.pixel_aspect_x,
                scale_y=context.scene.render.pixel_aspect_y)
            writer.writerow([lf.lf_type])
            for i in range(0, 4):
                writer.writerow([projection_matrix[i][0],
                                 projection_matrix[i][1],
                                 projection_matrix[i][2],
                                 projection_matrix[i][3]])

        return {'FINISHED'}


class EXPORT_OT_lightfield_config_append(bpy.types.Operator):
    bl_idname = "lightfield.export_config_append"
    bl_label = """Append a camera position to the lightfield configuration"""
    bl_options = {'REGISTER'}

    filename = bpy.props.StringProperty()

    def execute(self, context):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        with open(bpy.path.abspath(lf.path_config_file), mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            x, y, z = lf.obj_camera.matrix_world.to_translation()
            rx, ry, rz = lf.obj_camera.matrix_world.to_euler()
            writer.writerow([self.filename, x, y, z, rx, ry, rz])

        csv_file.close()

        return {'FINISHED'}
