# Info displayed in the add-on overview.
bl_info = {
    'name': "6D Lightfield Renderer",
    'description': "Create different configurations of lightfields for rendering out scenes",
    'author': "De Pauw Stijn",
    'version': (0, 1),
    'blender': (2, 80, 0),
    'location': "View3D > Tool Shelf > Lightfield",
    'wiki_url': '',
    'support': "COMMUNITY",
    'category': "Render"
}

if "bpy" in locals():
    print("Force reloading the plugin.")
    import importlib

    importlib.reload(lightfield)
    importlib.reload(lightfield_plane)
    importlib.reload(lightfield_cuboid)
    importlib.reload(lightfield_cylinder)
    importlib.reload(gui)
    importlib.reload(operators)
    importlib.reload(update)
else:
    from . import lightfield, \
        lightfield_plane, \
        lightfield_cuboid, \
        lightfield_cylinder, \
        gui, \
        operators, \
        update

import bpy


# -------------------------------------------------------------------
#   Register & Unregister
# -------------------------------------------------------------------
def make_annotations(cls):
    """Converts class fields to annotations if running with Blender 2.8"""
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


classes = (
    lightfield.LightfieldPropertyGroup,
    lightfield_plane.LightfieldPlane,
    lightfield_cuboid.LightfieldCuboid,
    lightfield_cylinder.LightfieldCylinder,
    gui.VIEW3D_MT_lightfield_delete,
    gui.VIEW3D_MT_lightfield_add,
    gui.DATA_PT_lightfield_setup,
    gui.DATA_PT_lightfield_camera,
    gui.DATA_PT_lightfield_dof,
    gui.DATA_PT_lightfield_dof_aperture,
    gui.DATA_PT_lightfield_rendering,
    gui.DATA_PT_lightfield_config,
    gui.LIGHTFIELD_UL_items,
    gui.VIEW3D_PT_lightfields,
    operators.OBJECT_OT_lightfield_add,
    operators.LIGHTFIELD_OT_select,
    operators.LIGHTFIELD_OT_move,
    operators.LIGHTFIELD_OT_delete_override,
    operators.OBJECT_OT_update_lightfield,
    operators.OBJECT_OT_update_lightfield_camera,
    operators.LIGHTFIELD_OT_render,
    operators.OBJECT_OT_lightfield_delete,
)


# Register all classes + the collection property for storing lightfields
def register():
    # import importlib
    # importlib.reload(lightfield)
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)
    bpy.types.Scene.lightfield = bpy.props.CollectionProperty(type=lightfield.LightfieldPropertyGroup)
    bpy.types.Scene.lightfield_index = bpy.props.IntProperty(default=-1)
    active_object = bpy.types.LayerObjects, "active"
    bpy.types.VIEW3D_MT_add.append(gui.add_lightfield)
    bpy.msgbus.subscribe_rna(key=active_object,
                             owner=bpy.types.Scene.lightfield_index,
                             args=(),
                             notify=update.update_lightfield_index)


# Unregister all classes + the collection property for storing lightfields
# This is done in reverse to 'pop the register stack'.
def unregister():
    bpy.msgbus.clear_by_owner(bpy.types.Scene.lightfield_index)
    bpy.types.VIEW3D_MT_add.remove(gui.add_lightfield)
    del bpy.types.Scene.lightfield_index
    del bpy.types.Scene.lightfield
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
