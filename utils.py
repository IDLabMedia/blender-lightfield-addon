import bpy
from .lightfield_plane import LightfieldPlane
from .lightfield_cuboid import LightfieldCuboid
from .lightfield_cylinder import LightfieldCylinder
from .lightfield_sphere import LightfieldSphere


# from .lightfield_sphere import LightfieldSphere

def get_active_lightfield(context):
    """
    Get the active lightfield object, or None if not active
    :return: lightfield/None
    """
    obj = bpy.context.active_object
    if not obj:
        return None

    for lightfield in bpy.context.scene.lightfield:
        if lightfield.obj_empty == obj:
            if lightfield.lf_type == 'PLANE':
                lf = (LightfieldPlane)(lightfield)
            elif lightfield.lf_type == 'CUBOID':
                lf = (LightfieldCuboid)(lightfield)
            elif lightfield.lf_type == 'CYLINDER':
                lf = (LightfieldCylinder)(lightfield)
            elif lightfield.lf_type == 'SPHERE':
                lf = (LightfieldSphere)(lightfield)
            else:
                return None
            return lf
    return None


def get_lightfield_class(enum_name):
    """Return the lightfield class of the corresponding name."""
    if enum_name == 'PLANE':
        return LightfieldPlane
    elif enum_name == 'CUBOID':
        return LightfieldCuboid
    elif enum_name == 'CYLINDER':
        return LightfieldCylinder
    elif enum_name == 'SPHERE':
        return LightfieldSphere
    else:
        raise LookupError()


def get_lightfield_collection():
    """Return the collection containing the lightfields."""
    LIGHTFIELD_COLLECTION = 'Lightfields'
    if LIGHTFIELD_COLLECTION in bpy.data.collections:
        collection = bpy.data.collections[LIGHTFIELD_COLLECTION]
    else:
        collection = bpy.data.collections.new(LIGHTFIELD_COLLECTION)
        bpy.context.scene.collection.children.link(collection)

    return collection
