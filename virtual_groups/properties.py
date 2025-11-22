"""
Properties module for Virtual Groups

Defines all property classes for storing data:
- Scene properties (Views, Tag Palette state, etc.)
- View properties (name, query, cached count)
"""

import bpy
from bpy.props import (
    StringProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty,
)
from bpy.types import PropertyGroup


# ============================================================================
# Property Classes
# ============================================================================

class VG_ViewProperty(PropertyGroup):
    """Property group for a single View (virtual collection)."""

    name: StringProperty(
        name="View Name",
        description="Name of this View",
        default="New View"
    )

    guid: StringProperty(
        name="GUID",
        description="Unique identifier for this View (used for membership tracking)",
        default=""
    )

    query: StringProperty(
        name="Query",
        description="Tag query for this View (e.g., 'tag:candle AND tag:desk')",
        default=""
    )

    cached_count: IntProperty(
        name="Cached Count",
        description="Number of objects matching this query (cached)",
        default=0
    )


class VG_SceneProperties(PropertyGroup):
    """Scene-level properties for Virtual Groups."""
    
    # Tag Palette state
    selected_tags: StringProperty(
        name="Selected Tags",
        description="Comma-separated list of selected tags in Tag Palette",
        default=""
    )
    
    # Placeholder properties for v1
    view_search: StringProperty(
        name="View Search",
        description="Filter views by name",
        default=""
    )
    
    tag_search: StringProperty(
        name="Tag Search",
        description="Filter tags by name",
        default=""
    )
    
    tag_sort: EnumProperty(
        name="Sort Tags",
        description="How to sort tags",
        items=[
            ('ALPHA', "Alphabetical", "Sort tags alphabetically"),
            ('USAGE', "Usage", "Sort by number of objects using each tag"),
        ],
        default='ALPHA'
    )
    
    # Input field for adding new tags
    new_tag_name: StringProperty(
        name="New Tag",
        description="Name of tag to add to selected objects",
        default=""
    )


# ============================================================================
# Registration
# ============================================================================

classes = (
    VG_ViewProperty,
    VG_SceneProperties,
)


def register():
    """Register property classes and add to Scene."""
    # Register property group classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add properties to Scene
    bpy.types.Scene.vg_views = CollectionProperty(
        type=VG_ViewProperty,
        name="Virtual Groups Views"
    )
    
    bpy.types.Scene.vg_active_view_index = IntProperty(
        name="Active View Index",
        default=0
    )
    
    bpy.types.Scene.vg_props = PointerProperty(
        type=VG_SceneProperties,
        name="Virtual Groups Properties"
    )
    
    print("Virtual Groups properties registered")


def unregister():
    """Unregister property classes and remove from Scene."""
    # Remove properties from Scene
    del bpy.types.Scene.vg_props
    del bpy.types.Scene.vg_active_view_index
    del bpy.types.Scene.vg_views
    
    # Unregister property group classes
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("Virtual Groups properties unregistered")
