import bpy


def update_num_cameras(self, context):
    bpy.ops.scene.update_lightfield('EXEC_DEFAULT')


def update_cube_camera(self, context):
    bpy.ops.scene.update_lightfield_camera('EXEC_DEFAULT')


def update_lightfield_index():
    ob = bpy.context.active_object
    if (not ob) or (not ob.type == 'EMPTY'):
        return
    scn = bpy.context.scene
    lf = scn.lightfield
    for lightfield in lf:
        if lightfield.obj_empty == ob:
            scn.lightfield_index = lightfield.index
            break
