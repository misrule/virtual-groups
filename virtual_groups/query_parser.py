"""
Query Parser module for Virtual Groups

Implements parsing and evaluation of tag queries:
- Parse query syntax: tag:name AND/OR/NOT tag:name
- Evaluate queries against objects
- Get objects matching a query

This will be fully implemented in Phase 4.
"""

import re
from . import utils


# ============================================================================
# Query Parsing (Phase 4)
# ============================================================================

def parse_query(query_string):
    """
    Parse a query string into a structured representation.
    
    Query syntax:
        tag:tagname
        tag:tag1 AND tag:tag2
        tag:tag1 OR tag:tag2
        tag:tag1 AND NOT tag:tag2
    
    Args:
        query_string: Query string to parse
        
    Returns:
        Structured representation of the query
        
    Note: Full implementation in Phase 4
    """
    # TODO: Implement in Phase 4
    pass


def validate_query(query_string):
    """
    Validate query syntax.

    Args:
        query_string: Query string to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    if not query_string.strip():
        return (False, "Query cannot be empty")

    # Check for at least one tag: clause
    if "tag:" not in query_string:
        return (False, "Query must contain at least one 'tag:' clause")

    # Check for valid tag names (alphanumeric, underscore, hyphen)
    tag_pattern = r'tag:([a-zA-Z0-9_-]+)'
    matches = re.findall(tag_pattern, query_string)

    if not matches:
        return (False, "No valid tag names found (use alphanumeric, underscore, or hyphen)")

    # Check for orphaned operators
    if query_string.strip().startswith(('AND ', 'OR ')):
        return (False, "Query cannot start with AND or OR")

    if query_string.strip().endswith((' AND', ' OR', ' NOT')):
        return (False, "Query cannot end with an operator")

    # Check for NOT without following tag
    if re.search(r'NOT\s*$', query_string):
        return (False, "NOT operator must be followed by a tag")

    return (True, "")


def evaluate_query(query_string, obj):
    """
    Evaluate a query against a single object.

    Supports AND/OR/NOT operators with proper precedence:
    - OR has lowest precedence (evaluated first by splitting)
    - AND has higher precedence (binds tighter)
    - NOT modifies the immediate next tag term

    Examples:
        tag:candle                       → object has "candle" tag
        tag:desk AND tag:candle          → object has both tags
        tag:desk OR tag:props            → object has either tag
        tag:hero AND NOT tag:small       → object has "hero" but not "small"
        tag:a AND tag:b OR tag:c         → (a AND b) OR c

    Args:
        query_string: Query string to evaluate
        obj: Blender object to test

    Returns:
        bool: True if object matches query
    """
    if not query_string.strip():
        return False

    obj_tags = set(utils.get_tags_on_object(obj))

    # Split by OR (lowest precedence)
    # If any OR clause is true, the whole query is true
    or_clauses = query_string.split(' OR ')

    for or_clause in or_clauses:
        if _evaluate_and_clause(or_clause.strip(), obj_tags):
            return True

    return False


def _evaluate_and_clause(clause, obj_tags):
    """
    Evaluate a single AND clause (may contain multiple AND terms with NOT modifiers).

    Args:
        clause: String like "tag:desk AND tag:candle" or "tag:hero AND NOT tag:small"
        obj_tags: Set of tags on the object

    Returns:
        bool: True if all AND terms in the clause are satisfied
    """
    # Split by AND (higher precedence)
    and_terms = clause.split(' AND ')

    # All AND terms must be true
    for term in and_terms:
        if not _evaluate_term(term.strip(), obj_tags):
            return False

    return True


def _evaluate_term(term, obj_tags):
    """
    Evaluate a single term (tag:xxx or NOT tag:xxx).

    Args:
        term: String like "tag:candle" or "NOT tag:small"
        obj_tags: Set of tags on the object

    Returns:
        bool: True if the term is satisfied
    """
    term = term.strip()

    # Check for NOT modifier
    if term.startswith('NOT '):
        # NOT tag:xxx - tag must NOT be present
        tag_match = re.match(r'NOT\s+tag:([a-zA-Z0-9_-]+)', term)
        if tag_match:
            tag = tag_match.group(1)
            return tag not in obj_tags
        # Invalid syntax, fail safe
        return False
    else:
        # tag:xxx - tag must be present
        tag_match = re.match(r'tag:([a-zA-Z0-9_-]+)', term)
        if tag_match:
            tag = tag_match.group(1)
            return tag in obj_tags
        # Invalid syntax, fail safe
        return False


def get_objects_matching_query(query_string, scene):
    """
    Get all objects in scene that match the query.

    Args:
        query_string: Query string to evaluate
        scene: Blender scene

    Returns:
        list: List of matching objects
    """
    matching = []

    for obj in scene.objects:
        if evaluate_query(query_string, obj):
            matching.append(obj)

    return matching
