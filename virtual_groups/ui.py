"""
UI module for Virtual Groups

Defines all panel classes and UI drawing:
- Main panel
- Views subpanel
- Tags subpanel
- UIList for Views
"""

import bpy
from bpy.types import Panel, UIList

# Import utilities for UI operations
from . import utils


# ============================================================================
# Main Panel
# ============================================================================

class VG_PT_main_panel(Panel):
    """Main Virtual Groups panel in 3D View sidebar."""
    bl_label = "Virtual Groups"
    bl_idname = "VG_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Virtual Groups'
    
    def draw(self, context):
        layout = self.layout
        # Main panel is clean - subpanels contain all functionality


# ============================================================================
# Views Subpanel (Phase 5)
# ============================================================================

class VG_PT_views_subpanel(Panel):
    """Subpanel for managing Views."""
    bl_label = "Views"
    bl_idname = "VG_PT_views_subpanel"
    bl_parent_id = "VG_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.vg_props
        
        # Add View button
        layout.operator("virtual_groups.add_view", text="New", icon='ADD')

        # Separator
        layout.separator()
        
        # UIList of Views
        row = layout.row()
        row.template_list(
            "VG_UL_views",
            "",
            scene, "vg_views",
            scene, "vg_active_view_index",
            rows=4
        )
        
        # Active View details (shown when a View is selected)
        if scene.vg_active_view_index >= 0 and len(scene.vg_views) > 0:
            view = scene.vg_views[scene.vg_active_view_index]
            
            box = layout.box()

            # Name field
            box.prop(view, "name", text="Name")

            box.separator()

            # Membership controls (v1.2) - no label, just buttons
            row = box.row(align=True)
            row.operator("virtual_groups.add_to_view", text="Add", icon='ADD')
            row.operator("virtual_groups.remove_from_view", text="Remove", icon='REMOVE')
            row.operator("virtual_groups.clear_view_membership", text="Clear All", icon='X')

            box.separator()

            # Collapsible Advanced Query section (at bottom, out of the way)
            # Determine query preview text
            if view.query.strip():
                query_preview = "Advanced Query (…)"
            else:
                query_preview = "Advanced Query (none)"

            # Triangle icon (down if expanded, right if collapsed)
            icon = 'TRIA_DOWN' if view.show_query_section else 'TRIA_RIGHT'

            # Collapsible header (left-aligned)
            row = box.row()
            row.alignment = 'LEFT'
            row.prop(view, "show_query_section", text=query_preview, icon=icon, emboss=False)

            # Show query details if expanded
            if view.show_query_section:
                query_box = box.box()
                query_box.prop(view, "query", text="Query")
                query_box.operator("virtual_groups.apply_query", text="Apply Query", icon='FILE_REFRESH')


# ============================================================================
# Tags Subpanel (Phase 2+)
# ============================================================================

class VG_PT_tags_subpanel(Panel):
    """Subpanel for tag management and Tag Palette."""
    bl_label = "Tags"
    bl_idname = "VG_PT_tags_subpanel"
    bl_parent_id = "VG_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.vg_props
        
        # Search bar (placeholder for v1)
        row = layout.row()
        row.enabled = False
        row.prop(props, "tag_search", text="", icon='VIEWZOOM', placeholder="Search tags...")
        
        # Sort dropdown (placeholder for v1)
        row = layout.row()
        row.enabled = False
        row.prop(props, "tag_sort", text="Sort")
        
        # Separator
        layout.separator()
        
        # Viewport Selection Indicator
        box = layout.box()
        num_selected = len(context.selected_objects)
        if num_selected > 0:
            box.label(text=f"🎯 {num_selected} objects selected in viewport", icon='NONE')
        else:
            box.label(text="🎯 No objects selected in viewport", icon='NONE')
        
        # Separator
        layout.separator()
        
        # Scene Tags section (Tag Palette)
        layout.label(text="Scene Tags", icon='BOOKMARKS')

        # Get all scene tags and filter out view-* tags (internal membership tags)
        all_tags = utils.get_all_scene_tags(scene)
        display_tags = [tag for tag in all_tags if not tag.startswith('view-')]

        if display_tags:
            # Get selected tags for highlighting
            selected_tags_str = props.selected_tags
            selected_tags = selected_tags_str.split(',') if selected_tags_str else []

            # Grid layout for tag pills (toggle buttons)
            flow = layout.grid_flow(row_major=True, columns=3, align=True)
            for tag in display_tags:
                # Create toggle button that appears pressed when selected
                is_selected = tag in selected_tags
                op = flow.operator(
                    "virtual_groups.toggle_tag_selection",
                    text=tag,
                    depress=is_selected,
                    emboss=True
                )
                op.tag_name = tag
        else:
            # No tags in scene yet
            layout.label(text="No tags in scene", icon='INFO')

        # Separator
        layout.separator()

        # Operation Ribbon
        box = layout.box()
        col = box.column(align=False)

        # Check context for enabling/disabling buttons
        has_tag_selection = bool(props.selected_tags)
        has_viewport_selection = num_selected > 0

        # Tag Operations section (only when viewport has selection)
        if has_viewport_selection:
            col.label(text="Tag Operations", icon='MODIFIER')
            row = col.row(align=True)
            row.operator("virtual_groups.tag_palette_add_tags", text="Add Tags")
            row.enabled = has_tag_selection

            row = col.row(align=True)
            row.operator("virtual_groups.tag_palette_remove_tags", text="Remove Tags")
            row.enabled = has_tag_selection

            col.separator()

        # Visibility Operations section (always shown)
        col.label(text="Visibility", icon='HIDE_OFF')
        row = col.row(align=True)
        row.operator("virtual_groups.tag_palette_hide", text="Hide")
        row.enabled = has_tag_selection

        row = col.row(align=True)
        row.operator("virtual_groups.tag_palette_show", text="Show")
        row.enabled = has_tag_selection

        row = col.row(align=True)
        row.operator("virtual_groups.tag_palette_toggle", text="Toggle")
        row.enabled = has_tag_selection

        col.separator()

        # Selection Operations section (always shown)
        col.label(text="Selection", icon='RESTRICT_SELECT_OFF')
        row = col.row(align=True)
        row.operator("virtual_groups.tag_palette_select", text="Select")
        row.enabled = has_tag_selection

        # Separator
        layout.separator()
        
        # Selected Objects section (collapsible)
        box = layout.box()
        
        # Header row with collapse icon
        row = box.row()
        row.label(text=f"Selected Objects ({num_selected})", icon='OBJECT_DATA')
        
        # Only show content if objects are selected
        if num_selected > 0:
            box.label(text="Tags on selected objects", icon='INFO')
            
            # Get tags from selected objects (union of all tags)
            selected_obj_tags = set()
            for obj in context.selected_objects:
                obj_tags = utils.get_tags_on_object(obj)
                selected_obj_tags.update(obj_tags)

            # Filter out view-* tags (internal membership tags)
            display_selected_tags = {tag for tag in selected_obj_tags if not tag.startswith('view-')}

            if display_selected_tags:
                # Show tags as removable pills
                # Using a column of rows instead of grid_flow for better compatibility
                col = box.column(align=True)
                for tag in sorted(display_selected_tags):
                    row = col.row(align=True)
                    row.label(text=tag, icon='BOOKMARKS')
                    op = row.operator(
                        "virtual_groups.remove_tag_from_selected",
                        text="",
                        icon='X',
                        emboss=False
                    )
                    op.tag_name = tag
            else:
                box.label(text="No tags on selected objects", icon='INFO')
            
            # Separator
            box.separator()
            
            # Add tag section
            box.label(text="Add Tags", icon='ADD')
            
            # Input field for new tag
            row = box.row(align=True)
            row.prop(props, "new_tag_name", text="")
            row.operator("virtual_groups.add_tag_to_selected", text="Add", icon='ADD')


# ============================================================================
# UILists (Phase 5)
# ============================================================================

class VG_UL_views(UIList):
    """UIList for displaying Views."""
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Draw a single View item in the list."""
        view = item

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            # Create a row for the entire item
            row = layout.row(align=True)

            # Get objects in this View to determine icon states
            view_objects = utils.get_objects_in_view(view, context.scene)

            # Visibility toggle (dynamic icon based on state)
            all_visible = all(not obj.hide_viewport for obj in view_objects) if view_objects else True
            vis_icon = 'RESTRICT_VIEW_OFF' if all_visible else 'HIDE_ON'
            op_vis = row.operator(
                "virtual_groups.toggle_view_visibility",
                text="",
                icon=vis_icon,
                emboss=False
            )
            op_vis.view_index = index

            # Selection toggle
            op_sel = row.operator(
                "virtual_groups.toggle_view_selection",
                text="",
                icon='RESTRICT_SELECT_OFF',
                emboss=False
            )
            op_sel.view_index = index

            # Render visibility toggle (dynamic icon based on state)
            all_render_visible = all(not obj.hide_render for obj in view_objects) if view_objects else True
            render_icon = 'RESTRICT_RENDER_OFF' if all_render_visible else 'RESTRICT_RENDER_ON'
            op_render = row.operator(
                "virtual_groups.toggle_view_render_visibility",
                text="",
                icon=render_icon,
                emboss=False
            )
            op_render.view_index = index

            # View name (clickable to select)
            row.prop(view, "name", text="", emboss=False)

            # Object count
            row.label(text=f"({view.cached_count})")

            # Delete button
            op_delete = row.operator(
                "virtual_groups.delete_view",
                text="",
                icon='X',
                emboss=False
            )
            op_delete.view_index = index

        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon='BOOKMARKS')


# ============================================================================
# Registration
# ============================================================================

classes = (
    VG_PT_main_panel,
    VG_PT_views_subpanel,
    VG_PT_tags_subpanel,
    VG_UL_views,
)


def register():
    """Register all UI classes."""
    for cls in classes:
        bpy.utils.register_class(cls)
    
    print("Virtual Groups UI registered")


def unregister():
    """Unregister all UI classes."""
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    print("Virtual Groups UI unregistered")
