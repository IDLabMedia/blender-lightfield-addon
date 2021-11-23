import math

import bpy
from . import utils


class OBJECT_OT_lightfield_add(bpy.types.Operator):
    """
    Operator to add a lightfield to the scene
    """
    bl_idname = 'object.lightfield_add'
    bl_label = "Lightfield"
    bl_description = "Add a lightfield setup to the scene"
    bl_options = {'REGISTER', 'UNDO'}

    action = bpy.props.EnumProperty(
        items=[
            ('PLANE', "Plane", ""),
            ('CUBOID', "Cuboid", ""),
            ('CYLINDER', "Cylinder", ""),
            ('SPHERE', "Sphere", "")]
    )

    def execute(self, context):
        scn = context.scene
        scn.lightfield_index = len(scn.lightfield)

        lf = (utils.get_lightfield_class(self.action))(scn.lightfield.add())
        lf.index = scn.lightfield_index
        lf.construct()
        return {'FINISHED'}


class LIGHTFIELD_OT_move(bpy.types.Operator):
    """Move items up and down"""
    bl_idname = "lightfield.list_move"
    bl_label = "List Move"
    bl_description = "Move items up and down"
    bl_options = {'REGISTER'}
    direction = bpy.props.EnumProperty(
        items=[
            ('UP', "Up", ""),
            ('DOWN', "Down", "")]
    )

    def invoke(self, context, event):
        scn = context.scene
        idx = scn.lightfield_index

        try:
            item = scn.lightfield[idx]
        except IndexError:
            pass
        else:
            if self.direction == 'DOWN' and idx < len(scn.lightfield) - 1:
                item_next = scn.lightfield[idx + 1]
                item.index += 1
                item_next.index -= 1
                scn.lightfield.move(idx, idx + 1)
                scn.lightfield_index += 1

            elif self.direction == 'UP' and idx >= 1:
                item_prev = scn.lightfield[idx - 1]
                item.index -= 1
                item_prev.index += 1
                scn.lightfield.move(idx, idx - 1)
                scn.lightfield_index -= 1
        return {"FINISHED"}

class LIGHTFIELD_OT_make_camera_active(bpy.types.Operator):
    """Make the camera of the selected light field the active one for the scene"""
    bl_idname = "lightfield.make_camera_active"
    bl_label = "Make Light Field camera active for scene"
    bl_description = "Make the camera of the selected light field active the active one for the scene"
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)
        context.scene.camera = lf.obj_camera
        render_settings = bpy.context.scene.render
        render_settings.resolution_x = lf.res_x
        render_settings.resolution_y = lf.res_y
        return {"FINISHED"}

class LIGHTFIELD_OT_select(bpy.types.Operator):
    """Select the current lightfield in the viewport"""
    bl_idname = "lightfield.select"
    bl_label = "Select in viewport"
    bl_description = "Select the current lightfield in the viewport"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = context.scene
        idx = scn.lightfield_index
        if idx == -1:
            return {'CANCELLED'}
        ob = scn.lightfield[idx].obj_empty
        bpy.ops.object.select_all(action='DESELECT')
        ob.select_set(True)
        context.view_layer.objects.active = ob

        return {"FINISHED"}


class LIGHTFIELD_OT_update(bpy.types.Operator):
    """Update the light field setup"""
    bl_idname = "lightfield.update"
    bl_label = """Update the light field setup"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        lf = utils.get_active_lightfield(context)
        collection = utils.get_lightfield_collection()

        name = None
        if lf.obj_grid:
            name = lf.obj_grid.name
            bpy.data.meshes.remove(lf.obj_grid.data)

        grid = lf.create_grid()
        lf.obj_grid = grid

        if name:
            grid.name = name
        collection.objects.link(grid)
        grid.parent = lf.obj_empty
        grid.hide_select = True

        bpy.context.view_layer.objects.active = lf.obj_empty

        scene = bpy.context.scene
        rb = scene.render
        if context.scene.camera == lf.obj_camera:
            # The camera is this one, update the resolution
            rb.resolution_x = lf.res_x
            rb.resolution_y = lf.res_y


        return {'FINISHED'}


class LIGHTFIELD_OT_update_preview(bpy.types.Operator):
    """Update the light field setup"""
    bl_idname = "lightfield.update_preview"
    bl_label = """Update the light field preview"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        if lf.lf_type == 'PLANE':
            # Percentage part in the x direction
            y_percentage_steps = 100.0 / lf.num_cams_y
            x_percentage = (lf.camera_preview_index % y_percentage_steps) / y_percentage_steps
            y_percentage = lf.camera_preview_index
            pos = lf.get_camera_pos(int(x_percentage * lf.num_cams_x),
                                    int(y_percentage * lf.num_cams_y / 101))
        elif lf.lf_type == 'CUBOID':
            side_map = {'f': [lf.num_cams_x, lf.num_cams_y],
                        'b': [lf.num_cams_x, lf.num_cams_y],
                        'l': [lf.num_cams_z, lf.num_cams_y],
                        'r': [lf.num_cams_z, lf.num_cams_y],
                        'u': [lf.num_cams_x, lf.num_cams_z],
                        'd': [lf.num_cams_x, lf.num_cams_z], }
            y_percentage_steps = 100.0 / lf.num_cams_y
            x_percentage = (lf.camera_preview_index % y_percentage_steps) / y_percentage_steps
            y_percentage = lf.camera_preview_index
            pos = lf.get_camera_pos(lf.camera_side,
                                    int(x_percentage * side_map[lf.camera_side][0]),
                                    int(y_percentage * side_map[lf.camera_side][1] / 101))
        elif lf.lf_type == 'CYLINDER':
            y_percentage_steps = 100.0 / lf.num_cams_y
            r_percentage = (lf.camera_preview_index % y_percentage_steps) / y_percentage_steps
            y_percentage = lf.camera_preview_index
            pos = lf.get_camera_pos(int(y_percentage * lf.num_cams_y / 101),
                                    int(r_percentage * lf.num_cams_radius))
        elif lf.lf_type == 'SPHERE':
            index = (lf.camera_preview_index / 100.0) * (len(lf.obj_grid.data.vertices) - 1)
            pos = lf.get_camera_pos(int(index))
        else:
            raise KeyError()

        lf.obj_camera.location = pos.location()
        lf.obj_camera.rotation_euler = pos.rotation()

        return {'FINISHED'}


class LIGHTFIELD_OT_update_camera(bpy.types.Operator):
    """Update the light field setup camera"""
    bl_idname = "lightfield.update_camera"
    bl_label = """Update the light field camera"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        lf = utils.get_active_lightfield(context)
        if lf.cube_camera:
            lf.dummy_focal_length = lf.data_camera.lens
            lf.data_camera.angle = math.pi / 2
        else:
            lf.data_camera.lens = lf.dummy_focal_length

        return {'FINISHED'}


class LIGHTFIELD_OT_update_size(bpy.types.Operator):
    """Update the light field setup size"""
    bl_idname = "lightfield.update_size"
    bl_label = """Update the light field size"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        lf = utils.get_active_lightfield(context)
        collection = utils.get_lightfield_collection()

        return {'FINISHED'}


class LIGHTFIELD_OT_render(bpy.types.Operator):
    """Update the light field setup"""
    bl_idname = "lightfield.render"
    bl_label = """Render the lightfield"""
    bl_options = {'REGISTER'}

    def execute(self, context):
        lf = context.scene.lightfield[context.scene.lightfield_index]
        lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.render()
        return {'FINISHED'}


class OBJECT_OT_lightfield_delete(bpy.types.Operator):
    """
    Operator to delete a lightfield from the scene
    """
    bl_idname = 'object.lightfield_delete'
    bl_label = "Delete"
    bl_description = "Delete lightfield"
    bl_options = {'REGISTER', 'UNDO'}

    index = bpy.props.IntProperty(default=-1)
    confirm = bpy.props.BoolProperty(name="Confirm", description="Prompt for confirmation", default=True)

    def execute(self, context):
        if self.index == -1:
            lf = utils.get_active_lightfield(context)
            if lf is None:
                return
        else:
            lf = context.scene.lightfield[self.index]
            lf = (utils.get_lightfield_class(lf.lf_type))(lf)

        lf.deconstruct()
        lightfields = context.scene.lightfield
        for i in range(lf.index + 1, len(lightfields)):
            lightfields[i].index -= 1
        lightfields.remove(lf.index)
        if context.scene.lightfield_index >= len(lightfields):
            context.scene.lightfield_index = len(lightfields) - 1

        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.confirm:
            return self.execute(context)
        else:
            return context.window_manager.invoke_confirm(self, event)


class LIGHTFIELD_OT_delete_override(bpy.types.Operator):
    """
    Operator to delete a lightfield from the scene
    """
    bl_idname = 'object.delete'
    bl_label = "Delete"
    bl_description = "Delete"
    bl_options = {'REGISTER', 'UNDO'}

    use_global = bpy.props.BoolProperty(name="Delete Globally", description="Remove object from all scenes")
    confirm = bpy.props.BoolProperty(name="Confirm", description="Prompt for confirmation", default=True)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        lfs = [lf.obj_empty for lf in context.scene.lightfield]
        for o in context.selected_objects:
            if o in lfs:
                bpy.ops.object.lightfield_delete('EXEC_DEFAULT',
                                                 index=context.scene.lightfield[lfs.index(o)].index,
                                                 confirm=self.confirm)
            else:
                bpy.data.objects.remove(o, do_unlink=True)

        self.confirm = True

        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.confirm:
            return self.execute(context)
        else:
            return context.window_manager.invoke_confirm(self, event)
