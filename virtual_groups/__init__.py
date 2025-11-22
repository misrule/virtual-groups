"""
Virtual Groups - Tag-based semantic grouping for Blender

This add-on provides a non-intrusive overlay for managing complex scenes
using semantic tags and dynamic query-based virtual collections.
"""

bl_info = {
    "name": "Virtual Groups",
    "author": "Your Name",
    "version": (0, 1, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > Virtual Groups",
    "description": "Tag-based semantic grouping and dynamic virtual collections",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy

# Import modules
from . import properties
from . import operators
from . import ui
from . import utils
from . import query_parser

# Module tuple for registration
modules = (
    properties,
    operators,
    ui,
)


def register():
    """Register all classes and properties."""
    # Register modules in order
    for module in modules:
        module.register()
    
    print("Virtual Groups registered")


def unregister():
    """Unregister all classes and properties."""
    # Unregister in reverse order
    for module in reversed(modules):
        module.unregister()
    
    print("Virtual Groups unregistered")


if __name__ == "__main__":
    register()
