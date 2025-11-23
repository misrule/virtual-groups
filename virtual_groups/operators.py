"""
Operators module for Virtual Groups

Contains all operator classes (button actions):
- Tag management operators
- Tag Palette operators
- View management operators
- View operation operators
"""

import bpy
import uuid
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty, BoolProperty

# Import utilities (will be implemented in Phase 2+)
from . import utils
from . import query_parser


# ============================================================================
# Tag Management Operators (Phase 1)
# ============================================================================

class VG_OT_add_tag_to_selected(Operator):
    """Add tag to all selected objects"""
    bl_idname = "virtual_groups.add_tag_to_selected"
    bl_label = "Add Tag"
    bl_options = {'REGISTER', 'UNDO'}

    # Tag name as operator property (allows popup input)
    tag_name: StringProperty(
        name="Tag Name",
        description="Name of the tag to add",
        default=""
    )

    @classmethod
    def poll(cls, context):
        # Only enabled if objects are selected
        return len(context.selected_objects) > 0

    def invoke(self, context, event):
        # Always reset tag_name first (prevents persistence from last use)
        self.tag_name = ""

        # Pre-fill with text from the UI field if it exists
        props = context.scene.vg_props
        if props.new_tag_name.strip():
            self.tag_name = props.new_tag_name.strip()
            # Clear the UI field
            props.new_tag_name = ""

        # Show popup dialog with text input
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        tag = self.tag_name.strip()

        # Check if tag name is empty
        if not tag:
            self.report({'ERROR'}, "Tag name cannot be empty")
            return {'CANCELLED'}

        # Validate tag name
        is_valid, error_msg = utils.validate_tag_name(tag)
        if not is_valid:
            self.report({'ERROR'}, error_msg)
            return {'CANCELLED'}

        # Add tag to all selected objects
        count = 0
        for obj in context.selected_objects:
            utils.add_tag_to_object(obj, tag)
            count += 1

        # Force UI redraw to show new tag immediately
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Added tag '{tag}' to {count} object(s)")
        return {'FINISHED'}


class VG_OT_remove_tag_from_selected(Operator):
    """Remove tag from all selected objects"""
    bl_idname = "virtual_groups.remove_tag_from_selected"
    bl_label = "Remove Tag"
    bl_options = {'REGISTER', 'UNDO'}

    tag_name: StringProperty(
        name="Tag Name",
        description="Name of tag to remove"
    )

    @classmethod
    def poll(cls, context):
        # Only enabled if objects are selected
        return len(context.selected_objects) > 0

    def execute(self, context):
        if not self.tag_name:
            self.report({'ERROR'}, "No tag specified")
            return {'CANCELLED'}

        # Remove tag from all selected objects
        count = 0
        for obj in context.selected_objects:
            utils.remove_tag_from_object(obj, self.tag_name)
            count += 1

        # Force UI redraw to update tag list immediately
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Removed tag '{self.tag_name}' from {count} object(s)")
        return {'FINISHED'}


# ============================================================================
# Tag Palette Operators (Phase 2)
# ============================================================================

class VG_OT_toggle_tag_selection(Operator):
    """Toggle selection state of a tag in the Tag Palette"""
    bl_idname = "virtual_groups.toggle_tag_selection"
    bl_label = "Toggle Tag Selection"
    bl_options = {'INTERNAL'}

    tag_name: StringProperty(
        name="Tag Name",
        description="Tag to toggle selection"
    )

    def execute(self, context):
        props = context.scene.vg_props

        # Get current selected tags as a set
        selected_tags_str = props.selected_tags
        selected_tags = set(selected_tags_str.split(',')) if selected_tags_str else set()

        # Remove empty strings
        selected_tags.discard('')

        # Toggle the tag
        if self.tag_name in selected_tags:
            selected_tags.remove(self.tag_name)
        else:
            selected_tags.add(self.tag_name)

        # Save back to property as comma-separated string
        props.selected_tags = ','.join(sorted(selected_tags))

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        return {'FINISHED'}


class VG_OT_tag_palette_hide(Operator):
    """Hide all objects with selected tags"""
    bl_idname = "virtual_groups.tag_palette_hide"
    bl_label = "Hide"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled when tags are selected
        props = context.scene.vg_props
        return bool(props.selected_tags.strip())

    def execute(self, context):
        props = context.scene.vg_props
        selected_tags = [t for t in props.selected_tags.split(',') if t]

        # Get all objects with any of the selected tags (OR logic)
        objects = utils.get_objects_with_tags(context.scene, selected_tags, mode='OR')

        # Hide them
        for obj in objects:
            obj.hide_viewport = True

        # Auto-clear tag selection
        props.selected_tags = ""

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Hid {len(objects)} object(s)")
        return {'FINISHED'}


class VG_OT_tag_palette_show(Operator):
    """Show all objects with selected tags"""
    bl_idname = "virtual_groups.tag_palette_show"
    bl_label = "Show"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled when tags are selected
        props = context.scene.vg_props
        return bool(props.selected_tags.strip())

    def execute(self, context):
        props = context.scene.vg_props
        selected_tags = [t for t in props.selected_tags.split(',') if t]

        # Get all objects with any of the selected tags (OR logic)
        objects = utils.get_objects_with_tags(context.scene, selected_tags, mode='OR')

        # Show them
        for obj in objects:
            obj.hide_viewport = False

        # Auto-clear tag selection
        props.selected_tags = ""

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Showed {len(objects)} object(s)")
        return {'FINISHED'}


class VG_OT_tag_palette_toggle(Operator):
    """Toggle visibility of all objects with selected tags"""
    bl_idname = "virtual_groups.tag_palette_toggle"
    bl_label = "Toggle"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled when tags are selected
        props = context.scene.vg_props
        return bool(props.selected_tags.strip())

    def execute(self, context):
        props = context.scene.vg_props
        selected_tags = [t for t in props.selected_tags.split(',') if t]

        # Get all objects with any of the selected tags (OR logic)
        objects = utils.get_objects_with_tags(context.scene, selected_tags, mode='OR')

        # Toggle visibility
        for obj in objects:
            obj.hide_viewport = not obj.hide_viewport

        # Auto-clear tag selection
        props.selected_tags = ""

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Toggled visibility for {len(objects)} object(s)")
        return {'FINISHED'}


class VG_OT_tag_palette_select(Operator):
    """Select all objects with selected tags"""
    bl_idname = "virtual_groups.tag_palette_select"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled when tags are selected
        props = context.scene.vg_props
        return bool(props.selected_tags.strip())

    def execute(self, context):
        props = context.scene.vg_props
        selected_tags = [t for t in props.selected_tags.split(',') if t]

        # Get all objects with any of the selected tags (OR logic)
        objects = utils.get_objects_with_tags(context.scene, selected_tags, mode='OR')

        # Deselect all first
        bpy.ops.object.select_all(action='DESELECT')

        # Select matching objects
        for obj in objects:
            obj.select_set(True)

        # Auto-clear tag selection
        props.selected_tags = ""

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Selected {len(objects)} object(s)")
        return {'FINISHED'}


class VG_OT_tag_palette_add_tags(Operator):
    """Add selected tags to viewport-selected objects"""
    bl_idname = "virtual_groups.tag_palette_add_tags"
    bl_label = "Add Tags"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled when tags are selected AND objects are selected in viewport
        props = context.scene.vg_props
        has_tags = bool(props.selected_tags.strip())
        has_selection = len(context.selected_objects) > 0
        return has_tags and has_selection

    def execute(self, context):
        props = context.scene.vg_props
        selected_tags = [t for t in props.selected_tags.split(',') if t]

        # Add all selected tags to all selected objects
        for obj in context.selected_objects:
            for tag in selected_tags:
                utils.add_tag_to_object(obj, tag)

        # Auto-clear tag selection
        props.selected_tags = ""

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        tag_str = ', '.join(selected_tags)
        self.report({'INFO'}, f"Added tags [{tag_str}] to {len(context.selected_objects)} object(s)")
        return {'FINISHED'}


class VG_OT_tag_palette_remove_tags(Operator):
    """Remove selected tags from viewport-selected objects"""
    bl_idname = "virtual_groups.tag_palette_remove_tags"
    bl_label = "Remove Tags"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled when tags are selected AND objects are selected in viewport
        props = context.scene.vg_props
        has_tags = bool(props.selected_tags.strip())
        has_selection = len(context.selected_objects) > 0
        return has_tags and has_selection

    def execute(self, context):
        props = context.scene.vg_props
        selected_tags = [t for t in props.selected_tags.split(',') if t]

        # Remove all selected tags from all selected objects
        for obj in context.selected_objects:
            for tag in selected_tags:
                utils.remove_tag_from_object(obj, tag)

        # Auto-clear tag selection
        props.selected_tags = ""

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        tag_str = ', '.join(selected_tags)
        self.report({'INFO'}, f"Removed tags [{tag_str}] from {len(context.selected_objects)} object(s)")
        return {'FINISHED'}


# ============================================================================
# View Management Operators (Phase 5)
# ============================================================================

class VG_OT_add_view(Operator):
    """Create a new View"""
    bl_idname = "virtual_groups.add_view"
    bl_label = "Add View"
    bl_options = {'REGISTER', 'UNDO'}

    view_name: StringProperty(
        name="View Name",
        description="Name for the new View",
        default="New View"
    )

    def invoke(self, context, event):
        # Show popup dialog with text input
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        name = self.view_name.strip()

        if not name:
            self.report({'ERROR'}, "View name cannot be empty")
            return {'CANCELLED'}

        # Create new View
        scene = context.scene
        new_view = scene.vg_views.add()
        new_view.name = name
        new_view.guid = str(uuid.uuid4())
        new_view.query = ""
        new_view.cached_count = 0

        # Set as active
        scene.vg_active_view_index = len(scene.vg_views) - 1

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Created View '{name}'")
        return {'FINISHED'}


class VG_OT_delete_view(Operator):
    """Delete the selected View"""
    bl_idname = "virtual_groups.delete_view"
    bl_label = "Delete View"
    bl_options = {'REGISTER', 'UNDO'}

    view_index: IntProperty(
        name="View Index",
        description="Index of view to delete (use -1 for active view)",
        default=-1
    )

    @classmethod
    def poll(cls, context):
        # Only enabled if there's at least one view
        scene = context.scene
        return len(scene.vg_views) > 0

    def execute(self, context):
        scene = context.scene

        # Use view_index if provided, otherwise use active index
        if self.view_index >= 0:
            index = self.view_index
        else:
            index = scene.vg_active_view_index

        if index < 0 or index >= len(scene.vg_views):
            self.report({'ERROR'}, "No View selected")
            return {'CANCELLED'}

        view_name = scene.vg_views[index].name
        scene.vg_views.remove(index)

        # Adjust active index
        if scene.vg_active_view_index >= len(scene.vg_views):
            scene.vg_active_view_index = len(scene.vg_views) - 1

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Deleted View '{view_name}'")
        return {'FINISHED'}


class VG_OT_apply_query(Operator):
    """Evaluate the View query and update cached count"""
    bl_idname = "virtual_groups.apply_query"
    bl_label = "Apply Query"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled if there's a view selected
        scene = context.scene
        return len(scene.vg_views) > 0 and 0 <= scene.vg_active_view_index < len(scene.vg_views)

    def execute(self, context):
        scene = context.scene
        index = scene.vg_active_view_index

        if index < 0 or index >= len(scene.vg_views):
            self.report({'ERROR'}, "No View selected")
            return {'CANCELLED'}

        view = scene.vg_views[index]

        # Validate query (if present)
        if view.query.strip():
            is_valid, error_msg = query_parser.validate_query(view.query)
            if not is_valid:
                self.report({'ERROR'}, f"Invalid query: {error_msg}")
                return {'CANCELLED'}

        # Get matching objects (hybrid: query + membership)
        matching_objects = utils.get_objects_in_view(view, scene)

        # Update cached count
        view.cached_count = len(matching_objects)

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Query matched {len(matching_objects)} object(s)")
        return {'FINISHED'}


# ============================================================================
# View Membership Operators (v1.2)
# ============================================================================

class VG_OT_add_to_view(Operator):
    """Add selected objects to this View (explicit membership)"""
    bl_idname = "virtual_groups.add_to_view"
    bl_label = "Add to View"
    bl_description = "Add selected objects to this View. Objects will remain in View even if query changes."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled if there's a view selected AND objects are selected
        scene = context.scene
        if len(scene.vg_views) == 0 or not (0 <= scene.vg_active_view_index < len(scene.vg_views)):
            return False
        return utils.has_viewport_selection(context)

    def execute(self, context):
        scene = context.scene
        view = scene.vg_views[scene.vg_active_view_index]

        if not view.guid:
            self.report({'ERROR'}, "View has no GUID (legacy View?). Please recreate the View.")
            return {'CANCELLED'}

        membership_tag = f"view-{view.guid}"
        count = 0

        # Add membership tag to all selected objects
        for obj in context.selected_objects:
            utils.add_tag_to_object(obj, membership_tag)
            count += 1

        # Update cached count
        matching_objects = utils.get_objects_in_view(view, scene)
        view.cached_count = len(matching_objects)

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Added {count} object(s) to View '{view.name}'")
        return {'FINISHED'}


class VG_OT_remove_from_view(Operator):
    """Remove selected objects from this View (explicit membership)"""
    bl_idname = "virtual_groups.remove_from_view"
    bl_label = "Remove from View"
    bl_description = "Remove selected objects from this View. Objects matched by query will remain."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled if there's a view selected AND objects are selected
        scene = context.scene
        if len(scene.vg_views) == 0 or not (0 <= scene.vg_active_view_index < len(scene.vg_views)):
            return False
        return utils.has_viewport_selection(context)

    def execute(self, context):
        scene = context.scene
        view = scene.vg_views[scene.vg_active_view_index]

        if not view.guid:
            self.report({'ERROR'}, "View has no GUID (legacy View?). Please recreate the View.")
            return {'CANCELLED'}

        membership_tag = f"view-{view.guid}"
        count = 0

        # Remove membership tag from all selected objects
        for obj in context.selected_objects:
            utils.remove_tag_from_object(obj, membership_tag)
            count += 1

        # Update cached count
        matching_objects = utils.get_objects_in_view(view, scene)
        view.cached_count = len(matching_objects)

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Removed {count} object(s) from View '{view.name}'")
        return {'FINISHED'}


class VG_OT_clear_view_membership(Operator):
    """Clear all explicit membership from this View"""
    bl_idname = "virtual_groups.clear_view_membership"
    bl_label = "Clear All Membership"
    bl_description = "Remove all objects from this View's explicit membership. Query-matched objects will remain."
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # Only enabled if there's a view selected
        scene = context.scene
        if len(scene.vg_views) == 0 or not (0 <= scene.vg_active_view_index < len(scene.vg_views)):
            return False
        return True

    def execute(self, context):
        scene = context.scene
        view = scene.vg_views[scene.vg_active_view_index]

        if not view.guid:
            self.report({'ERROR'}, "View has no GUID (legacy View?). Please recreate the View.")
            return {'CANCELLED'}

        membership_tag = f"view-{view.guid}"
        count = 0

        # Remove membership tag from ALL objects in scene
        for obj in scene.objects:
            if membership_tag in utils.get_tags_on_object(obj):
                utils.remove_tag_from_object(obj, membership_tag)
                count += 1

        # Update cached count
        matching_objects = utils.get_objects_in_view(view, scene)
        view.cached_count = len(matching_objects)

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        self.report({'INFO'}, f"Cleared {count} object(s) from membership in View '{view.name}'")
        return {'FINISHED'}


# ============================================================================
# Compositional View Operations (v1 - Compositional)
# ============================================================================

class VG_OT_toggle_view_visibility(Operator):
    """Toggle viewport visibility for all objects in this View"""
    bl_idname = "virtual_groups.toggle_view_visibility"
    bl_label = "Toggle View Visibility"
    bl_description = "Toggle viewport visibility for all objects in this View (compositional)"
    bl_options = {'REGISTER', 'UNDO'}

    view_index: IntProperty(
        name="View Index",
        description="Index of view to toggle visibility",
        default=-1
    )

    @classmethod
    def poll(cls, context):
        # Only enabled if there's at least one view
        scene = context.scene
        return len(scene.vg_views) > 0

    def execute(self, context):
        scene = context.scene

        # Use view_index if provided, otherwise use active index
        if self.view_index >= 0:
            index = self.view_index
        else:
            index = scene.vg_active_view_index

        if index < 0 or index >= len(scene.vg_views):
            self.report({'ERROR'}, "No View selected")
            return {'CANCELLED'}

        view = scene.vg_views[index]

        # Get objects in this View
        objects = utils.get_objects_in_view(view, scene)

        if not objects:
            self.report({'WARNING'}, "View has no objects")
            return {'CANCELLED'}

        # Check current state - are all objects visible?
        all_visible = all(not obj.hide_viewport for obj in objects)

        # Toggle: if all visible, hide all; otherwise show all
        for obj in objects:
            obj.hide_viewport = all_visible

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        action = "Hid" if all_visible else "Showed"
        self.report({'INFO'}, f"{action} {len(objects)} object(s) in View '{view.name}'")
        return {'FINISHED'}


class VG_OT_toggle_view_selection(Operator):
    """Toggle selection for all objects in this View (recursive)"""
    bl_idname = "virtual_groups.toggle_view_selection"
    bl_label = "Toggle View Selection"
    bl_description = "Toggle selection for all objects in this View, including children (compositional)"
    bl_options = {'REGISTER', 'UNDO'}

    view_index: IntProperty(
        name="View Index",
        description="Index of view to toggle selection",
        default=-1
    )

    @classmethod
    def poll(cls, context):
        # Only enabled if there's at least one view
        scene = context.scene
        return len(scene.vg_views) > 0

    def execute(self, context):
        scene = context.scene

        # Use view_index if provided, otherwise use active index
        if self.view_index >= 0:
            index = self.view_index
        else:
            index = scene.vg_active_view_index

        if index < 0 or index >= len(scene.vg_views):
            self.report({'ERROR'}, "No View selected")
            return {'CANCELLED'}

        view = scene.vg_views[index]

        # Get objects in this View
        objects = utils.get_objects_in_view(view, scene)

        if not objects:
            self.report({'WARNING'}, "View has no objects")
            return {'CANCELLED'}

        # Get all objects including children (recursive)
        all_objects = []
        for obj in objects:
            all_objects.append(obj)
            all_objects.extend(obj.children_recursive)

        # Check current state - are all objects selected?
        all_selected = all(obj.select_get() for obj in all_objects)

        # Toggle (compositional - add or remove from selection)
        for obj in all_objects:
            obj.select_set(not all_selected)

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        action = "Deselected" if all_selected else "Selected"
        self.report({'INFO'}, f"{action} {len(all_objects)} object(s) from View '{view.name}'")
        return {'FINISHED'}


class VG_OT_toggle_view_render_visibility(Operator):
    """Toggle render visibility for all objects in this View"""
    bl_idname = "virtual_groups.toggle_view_render_visibility"
    bl_label = "Toggle View Render Visibility"
    bl_description = "Toggle render visibility for all objects in this View (compositional)"
    bl_options = {'REGISTER', 'UNDO'}

    view_index: IntProperty(
        name="View Index",
        description="Index of view to toggle render visibility",
        default=-1
    )

    @classmethod
    def poll(cls, context):
        # Only enabled if there's at least one view
        scene = context.scene
        return len(scene.vg_views) > 0

    def execute(self, context):
        scene = context.scene

        # Use view_index if provided, otherwise use active index
        if self.view_index >= 0:
            index = self.view_index
        else:
            index = scene.vg_active_view_index

        if index < 0 or index >= len(scene.vg_views):
            self.report({'ERROR'}, "No View selected")
            return {'CANCELLED'}

        view = scene.vg_views[index]

        # Get objects in this View
        objects = utils.get_objects_in_view(view, scene)

        if not objects:
            self.report({'WARNING'}, "View has no objects")
            return {'CANCELLED'}

        # Check current state - are all objects render-visible?
        all_render_visible = all(not obj.hide_render for obj in objects)

        # Toggle: if all render-visible, hide from render; otherwise show in render
        for obj in objects:
            obj.hide_render = all_render_visible

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        action = "Hid from render" if all_render_visible else "Enabled for render"
        self.report({'INFO'}, f"{action} {len(objects)} object(s) in View '{view.name}'")
        return {'FINISHED'}


# ============================================================================
# Registration
# ============================================================================

classes = (
    # Tag Management
    VG_OT_add_tag_to_selected,
    VG_OT_remove_tag_from_selected,
    # Tag Palette
    VG_OT_toggle_tag_selection,
    VG_OT_tag_palette_hide,
    VG_OT_tag_palette_show,
    VG_OT_tag_palette_toggle,
    VG_OT_tag_palette_select,
    VG_OT_tag_palette_add_tags,
    VG_OT_tag_palette_remove_tags,
    # View Management
    VG_OT_add_view,
    VG_OT_delete_view,
    VG_OT_apply_query,
    # View Membership (v1.2)
    VG_OT_add_to_view,
    VG_OT_remove_from_view,
    VG_OT_clear_view_membership,
    # Compositional View Operations (v1 - Compositional)
    VG_OT_toggle_view_visibility,
    VG_OT_toggle_view_selection,
    VG_OT_toggle_view_render_visibility,
)


def register():
    """Register all operator classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("Virtual Groups operators registered")


def unregister():
    """Unregister all operator classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("Virtual Groups operators unregistered")
