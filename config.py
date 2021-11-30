import bpy
import csv
import os

from . import utils, file_utils


# Export configuration of current setup for later use.
class EXPORT_OT_lightfield_config(bpy.types.Operator):
    bl_idname = "lightfield.export_config"
    bl_label = """Export lightfield configuration"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        with open(bpy.path.abspath(lf.path_config_file), mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')

            cam = lf.data_camera

            camera_meta_fields = ["type"]
            camera_meta = [cam.type]
            if cam.type == 'PANO':
                engine = context.engine
                if engine == 'CYCLES':
                    ccam = cam.cycles
                    camera_meta_fields.append("panorama_type")
                    camera_meta.append(ccam.panorama_type)
                    if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
                        camera_meta_fields.append("fisheye_fov")
                        camera_meta.append(ccam.fisheye_fov)
                    elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
                        camera_meta_fields.append("fisheye_lens")
                        camera_meta_fields.append("fisheye_fov")
                        camera_meta.append(ccam.fisheye_lens)
                        camera_meta.append(ccam.fisheye_fov)
                    elif ccam.panorama_type == 'EQUIRECTANGULAR':
                        camera_meta_fields.append("latitude_min")
                        camera_meta_fields.append("latitude_max")
                        camera_meta_fields.append("longitude_min")
                        camera_meta_fields.append("longitude_max")
                        camera_meta.append(ccam.latitude_min)
                        camera_meta.append(ccam.latitude_max)
                        camera_meta.append(ccam.longitude_min)
                        camera_meta.append(ccam.longitude_max)
                else:
                    raise Exception("Panoramic lenses only supported in Cycles")
            else:
                camera_meta_fields.append("lens_unit")
                camera_meta.append(cam.lens_unit)
                if cam.lens_unit == 'MILLIMETERS':
                    camera_meta_fields.append("lens")
                    camera_meta.append(cam.lens)
                elif cam.lens_unit == 'FOV':
                    camera_meta_fields.append("angle")
                    camera_meta.append(cam.angle)
            writer.writerow(camera_meta_fields)
            writer.writerow(camera_meta)


            projection_matrix = lf.obj_camera.calc_matrix_camera(
                context.evaluated_depsgraph_get(),
                x=context.scene.render.resolution_x,
                y=context.scene.render.resolution_y,
                scale_x=context.scene.render.pixel_aspect_x,
                scale_y=context.scene.render.pixel_aspect_y)
            writer.writerow([lf.lf_type])
            writer.writerow([lf.res_x, lf.res_y])
            for i in range(0, 4):
                writer.writerow([projection_matrix[i][0],
                                 projection_matrix[i][1],
                                 projection_matrix[i][2],
                                 projection_matrix[i][3]])

        return {'FINISHED'}


# Export part of a configuration to be appended, for later use.
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
