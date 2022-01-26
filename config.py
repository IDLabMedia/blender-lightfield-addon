import bpy
import csv
import os
import json

from . import utils, file_utils


# Export configuration of current setup for later use.
class EXPORT_OT_lightfield_config(bpy.types.Operator):
    bl_idname = "lightfield.export_config"
    bl_label = """Export lightfield configuration"""
    bl_options = {'REGISTER'}

    frame_number = bpy.props.IntProperty()

    def execute(self, context):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        os.makedirs(lf.get_output_directory(), exist_ok=True)

        with open(lf.get_path_config_file_json(self.frame_number), mode='w', newline='') as json_file:
            cam = lf.data_camera
            sensor_size = []
            if cam.sensor_fit == 'AUTO':
                size = cam.sensor_width
                res = max(lf.res_x, lf.res_y)
                sensor_size = [size * lf.res_x / res, size * lf.res_y / res]
            elif cam.sensor_fit == 'HORIZONTAL':
                size = cam.sensor_width
                sensor_size = [size, size * lf.res_y / lf.res_x]
            elif cam.sensor_fit == 'VERTICAL':
                size = cam.sensor_height
                sensor_size = [size * lf.res_x / lf.res_y, size]
            else:
                raise Exception("Unknown sensor fit")

            cfg = {
                'camera': {
                    'type': cam.type,
                },
                'lf_type': lf.lf_type,
                'resolution': [lf.res_x, lf.res_y],
                'sensor_size': sensor_size,
            }
            if cam.type == 'PANO':
                engine = context.engine
                if engine == 'CYCLES':
                    ccam = cam.cycles
                    cfg['camera']['panorama_type'] = ccam.panorama_type
                    if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
                        cfg['camera']['fisheye_fov'] = ccam.fisheye_fov
                    elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
                        cfg['camera']['fisheye_lens'] = ccam.fisheye_lens
                        cfg['camera']['fisheye_fov'] = ccam.fisheye_fov
                    elif ccam.panorama_type == 'EQUIRECTANGULAR':
                        cfg['camera']['latitude_min'] = ccam.latitude_min
                        cfg['camera']['latitude_max'] = ccam.latitude_max
                        cfg['camera']['longitude_min'] = ccam.longitude_min
                        cfg['camera']['longitude_max'] = ccam.longitude_max
                else:
                    raise Exception("Panoramic lenses only supported in Cycles")
            elif cam.type == 'PERSP':
                cfg['camera']['lens_unit'] = ccam.lens_unit
                if cam.lens_unit == 'MILLIMETERS':
                    cfg['camera']['focal_length'] = ccam.lens
                elif cam.lens_unit == 'FOV':
                    cfg['camera']['angle'] = ccam.angle

                projection_matrix = lf.obj_camera.calc_matrix_camera(
                    context.evaluated_depsgraph_get(),
                    x=context.scene.render.resolution_x,
                    y=context.scene.render.resolution_y,
                    scale_x=context.scene.render.pixel_aspect_x,
                    scale_y=context.scene.render.pixel_aspect_y)

                cfg['camera']['projection_matrix'] = projection_matrix

            cfg['frames'] = []

            json.dump(cfg, json_file, indent=2)



        with open(lf.get_path_config_file(self.frame_number), mode='w', newline='') as csv_file:
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
            writer.writerow(["sensor_width", "sensor_height"])
            if cam.sensor_fit == 'AUTO':
                size = cam.sensor_width
                res = max(lf.res_x, lf.res_y)
                writer.writerow([size * lf.res_x / res, size * lf.res_y / res])
            elif cam.sensor_fit == 'HORIZONTAL':
                size = cam.sensor_width
                writer.writerow([size, size * lf.res_y / lf.res_x])
            elif cam.sensor_fit == 'VERTICAL':
                size = cam.sensor_height
                writer.writerow([size * lf.res_x / lf.res_y, size])
            else:
                raise Exception("Unknown sensor fit")

            writer.writerow(["projection_matrix"])
            for i in range(0, 4):
                writer.writerow([projection_matrix[i][0],
                                 projection_matrix[i][1],
                                 projection_matrix[i][2],
                                 projection_matrix[i][3]])
            writer.writerow(["name", "x", "y", "z", "rot_x", "rot_y", "rot_z"])

        return {'FINISHED'}


# Export part of a configuration to be appended, for later use.
class EXPORT_OT_lightfield_config_append(bpy.types.Operator):
    bl_idname = "lightfield.export_config_append"
    bl_label = """Append a camera position to the lightfield configuration"""
    bl_options = {'REGISTER'}

    frame_number = bpy.props.IntProperty()
    filename = bpy.props.StringProperty()

    def execute(self, context):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        with open(lf.get_path_config_file(self.frame_number), mode='a', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            x, y, z = lf.obj_camera.matrix_world.to_translation()
            rx, ry, rz = lf.obj_camera.matrix_world.to_euler()
            writer.writerow([self.filename, x, y, z, rx, ry, rz])

        with open(lf.get_path_config_file_json(self.frame_number), mode='r', newline='') as json_file:
            cfg = json.load(json_file)
        with open(lf.get_path_config_file_json(self.frame_number), mode='w', newline='') as json_file:
            x, y, z = lf.obj_camera.matrix_world.to_translation()
            rx, ry, rz = lf.obj_camera.matrix_world.to_euler()
            cfg['frames'].append({
                'name': self.filename,
                'position': [x, y, z],
                'rotation': [rx, ry, rz],
                'world_matrix': lf.obj_camera.matrix_world,
            })
            json.dump(cfg, json_file)

        return {'FINISHED'}
