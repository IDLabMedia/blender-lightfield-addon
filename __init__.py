# Info displayed in the add-on overview.
bl_info = {
    'name': "6D Lightfield Renderer",
    'description': "Create different configurations of lightfields for rendering out scenes.",
    'author': "De Pauw Stijn",
    'version': (0, 1),
    'blender': (2, 80, 0),
    'location': "View3D > Tool Shelf > Lightfield || "
                "Properties > Data",
    'wiki_url': '',
    'support': "COMMUNITY",
    'category': "Render"
}

# Importing in this init file is a bit weird.
if "bpy" in locals():
    print("Force reloading the plugin.")
    import importlib

    importlib.reload(lightfield)
    importlib.reload(lightfield_plane)
    importlib.reload(lightfield_cuboid)
    importlib.reload(lightfield_cylinder)
    importlib.reload(lightfield_sphere)
    importlib.reload(gui)
    importlib.reload(operators)
    importlib.reload(update)
    importlib.reload(config)
    importlib.reload(utils)
else:
    from . import lightfield, \
        lightfield_plane, \
        lightfield_cuboid, \
        lightfield_cylinder, \
        lightfield_sphere, \
        gui, \
        operators, \
        update, \
        config, \
        utils

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

# All classes to register.
classes = (
    lightfield.LightfieldVisual,
    lightfield.LightfieldPropertyGroup,
    lightfield_plane.LightfieldPlane,
    lightfield_cuboid.LightfieldCuboid,
    lightfield_cylinder.LightfieldCylinder,
    lightfield_sphere.LightfieldSphere,
    gui.VIEW3D_MT_lightfield_add,
    gui.DATA_PT_lightfield_setup,
    gui.DATA_PT_lightfield_camera,
    gui.DATA_PT_lightfield_dof,
    gui.DATA_PT_lightfield_dof_aperture,
    gui.LIGHTFIELD_UL_items,
    gui.LIGHTFIELD_PT_list,
    gui.LIGHTFIELD_PT_rendering,
    gui.LIGHTFIELD_PT_preview,
    gui.LIGHTFIELD_PT_output,
    gui.LIGHTFIELD_PT_persistence,
    operators.OBJECT_OT_lightfield_add,
    operators.LIGHTFIELD_OT_select,
    operators.LIGHTFIELD_OT_move,
    operators.LIGHTFIELD_OT_delete_override,
    operators.LIGHTFIELD_OT_update,
    operators.LIGHTFIELD_OT_update_size,
    operators.LIGHTFIELD_OT_update_camera,
    operators.LIGHTFIELD_OT_update_preview,
    operators.LIGHTFIELD_OT_render,
    operators.OBJECT_OT_lightfield_delete,
    config.EXPORT_OT_lightfield_config,
    config.EXPORT_OT_lightfield_config_append,
)

# Handler for keeping lightfield list in sync with active selection.
@bpy.app.handlers.persistent
def load_handler(temp):
    active_object = bpy.types.LayerObjects, "active"

    bpy.msgbus.subscribe_rna(key=active_object,
                             owner=bpy.types.Scene.lightfield_index,
                             args=(),
                             notify=update.update_lightfield_index)

# Needed for updating the size correctly (no recursion).
@bpy.app.handlers.persistent
def update_depsgraph(scene):
    # Get the dependency graph.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    # Check if there is an object that was updated
    if depsgraph.id_type_updated('OBJECT'):
        # Check if it was the lightfield
        lf = utils.get_active_lightfield(bpy.context)
        if (lf is not None) and (
                lf.obj_empty.evaluated_get(depsgraph) in [_update.id for _update in depsgraph.updates]):
            # Update the lightfield.
            bpy.app.handlers.depsgraph_update_post.remove(update_depsgraph)
            update.update_size()
            bpy.app.handlers.depsgraph_update_post.append(update_depsgraph)

# Register all classes + the collection property for storing lightfields
def register():
    # Classes
    for cls in classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    # Properties
    bpy.types.Scene.lightfield = bpy.props.CollectionProperty(type=lightfield.LightfieldPropertyGroup)
    bpy.types.Scene.lightfield_index = bpy.props.IntProperty(default=-1)

    # Menus
    bpy.types.VIEW3D_MT_add.append(gui.add_lightfield)

    # Handlers
    # Handler for active object
    bpy.app.handlers.load_post.append(load_handler)
    # Handler for scaling.
    # Don't use for now.
    # bpy.app.handlers.depsgraph_update_post.append(update_depsgraph)


# Unregister all classes + the collection property for storing lightfields
# This is done in reverse to 'pop the register stack'.
def unregister():
    # Handlers
    # Don't use scaling for now
    # bpy.app.handlers.depsgraph_update_post.remove(update_depsgraph)
    bpy.app.handlers.load_post.remove(load_handler)

    # Unsubscribe from all possible subscriptions
    bpy.msgbus.clear_by_owner(bpy.types.Scene.lightfield_index)

    # Remove items from menu
    bpy.types.VIEW3D_MT_add.remove(gui.add_lightfield)

    # Remove properties
    del bpy.types.Scene.lightfield_index
    del bpy.types.Scene.lightfield

    # Unregister classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
