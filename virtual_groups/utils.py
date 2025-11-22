"""
Utilities module for Virtual Groups

Helper functions for:
- Tag manipulation on objects
- Object filtering and querying
- Scene tag enumeration
- Validation
"""

import json
import re


# ============================================================================
# Tag Management (Phase 2)
# ============================================================================

def get_tags_on_object(obj):
    """
    Get list of tags from an object.
    
    Args:
        obj: Blender object
        
    Returns:
        list: List of tag strings
    """
    tags_json = obj.get("vg_tags", "[]")
    try:
        return json.loads(tags_json)
    except json.JSONDecodeError:
        return []


def set_tags_on_object(obj, tags):
    """
    Set tags on an object.
    
    Args:
        obj: Blender object
        tags: List of tag strings
    """
    obj["vg_tags"] = json.dumps(tags)


def add_tag_to_object(obj, tag):
    """
    Add a tag to an object if not already present.
    
    Args:
        obj: Blender object
        tag: Tag string to add
    """
    tags = get_tags_on_object(obj)
    if tag not in tags:
        tags.append(tag)
        set_tags_on_object(obj, tags)


def remove_tag_from_object(obj, tag):
    """
    Remove a tag from an object if present.
    
    Args:
        obj: Blender object
        tag: Tag string to remove
    """
    tags = get_tags_on_object(obj)
    if tag in tags:
        tags.remove(tag)
        set_tags_on_object(obj, tags)


def validate_tag_name(tag):
    """
    Validate a tag name.
    
    Valid tags contain only alphanumeric characters, underscores, and hyphens.
    
    Args:
        tag: Tag string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not tag:
        return (False, "Tag name cannot be empty")
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', tag):
        return (False, "Tag name can only contain letters, numbers, underscores, and hyphens")
    
    return (True, "")


def get_all_scene_tags(scene):
    """
    Get all unique tags used in the scene.
    
    Args:
        scene: Blender scene
        
    Returns:
        list: Sorted list of unique tag strings
    """
    all_tags = set()
    for obj in scene.objects:
        tags = get_tags_on_object(obj)
        all_tags.update(tags)
    return sorted(all_tags)


# ============================================================================
# Object Filtering (Phase 3)
# ============================================================================

def get_objects_with_tags(scene, tags, mode='OR'):
    """
    Get objects that match the given tags.

    Args:
        scene: Blender scene
        tags: List of tag strings
        mode: 'OR' (any tag) or 'AND' (all tags)

    Returns:
        list: List of matching objects
    """
    matching = []
    tag_set = set(tags)

    # Empty tag list should return no objects
    if not tag_set:
        return []

    for obj in scene.objects:
        obj_tags = set(get_tags_on_object(obj))

        if mode == 'OR':
            # Object has ANY of the tags
            if obj_tags & tag_set:
                matching.append(obj)
        elif mode == 'AND':
            # Object has ALL of the tags
            if tag_set.issubset(obj_tags):
                matching.append(obj)

    return matching


# ============================================================================
# Context Helpers (Phase 3)
# ============================================================================

def has_viewport_selection(context):
    """
    Check if any objects are selected in the viewport.
    
    Args:
        context: Blender context
        
    Returns:
        bool: True if objects are selected
    """
    return len(context.selected_objects) > 0


def get_viewport_selection_count(context):
    """
    Get number of selected objects in viewport.

    Args:
        context: Blender context

    Returns:
        int: Number of selected objects
    """
    return len(context.selected_objects)


# ============================================================================
# View Object Resolution (v1 - Hybrid Model)
# ============================================================================

def get_objects_in_view(view, scene):
    """
    Get all objects that belong to a View (hybrid model).

    Objects are included if they match EITHER:
    1. The query (if query is not empty), OR
    2. Have explicit membership via view-{guid} tag

    This enables three use cases:
    - Pure query (dynamic): query set, no membership
    - Pure membership (explicit): no query, manual additions
    - Hybrid (best of both): query + manual exceptions/additions

    Args:
        view: VG_ViewProperty instance
        scene: Blender scene

    Returns:
        list: List of objects in this View
    """
    # Import query_parser (handle both package and direct import)
    try:
        from . import query_parser
    except ImportError:
        import query_parser

    matched_objects = set()

    # 1. Query-based inclusion (if query exists)
    if view.query.strip():
        query_matches = query_parser.get_objects_matching_query(view.query, scene)
        matched_objects.update(query_matches)

    # 2. Membership-based inclusion (via special tag)
    membership_tag = f"view-{view.guid}"
    for obj in scene.objects:
        if membership_tag in get_tags_on_object(obj):
            matched_objects.add(obj)

    return list(matched_objects)
