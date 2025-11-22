"""
Unit tests for hybrid view model (v1.2).

Tests the get_objects_in_view() function which combines
query-based and membership-based object inclusion.
"""

import unittest
import sys
from pathlib import Path
import json

# Add virtual_groups directory to path to import modules directly
# This avoids importing __init__.py which requires bpy (Blender)
virtual_groups_path = Path(__file__).parent.parent / "virtual_groups"
sys.path.insert(0, str(virtual_groups_path))

# Import utils module directly
import utils


class MockObject:
    """Mock Blender object for testing."""

    def __init__(self, name):
        self.name = name
        self._props = {}

    def __setitem__(self, key, value):
        """Mock custom property setter."""
        self._props[key] = value

    def __getitem__(self, key):
        """Mock custom property getter."""
        return self._props[key]

    def get(self, key, default=None):
        """Mock custom property get with default."""
        return self._props.get(key, default)

    def __repr__(self):
        return f"<MockObject '{self.name}'>"


class MockScene:
    """Mock Blender scene for testing."""

    def __init__(self, objects=None):
        self.objects = objects or []


class MockView:
    """Mock View property group for testing."""

    def __init__(self, name="Test View", query="", guid="test-guid-12345"):
        self.name = name
        self.query = query
        self.guid = guid


class TestMembershipTagOperations(unittest.TestCase):
    """Test membership tag operations (basic functionality)."""

    def setUp(self):
        """Set up test objects."""
        self.obj1 = MockObject("TestObject1")
        self.obj2 = MockObject("TestObject2")
        self.obj3 = MockObject("TestObject3")
        utils.set_tags_on_object(self.obj1, ["tag1", "tag2"])
        utils.set_tags_on_object(self.obj2, ["tag3"])
        utils.set_tags_on_object(self.obj3, [])

    def test_membership_tag_format(self):
        """Test that membership tags follow correct format."""
        view_guid = "abc-123-def-456"
        membership_tag = f"view-{view_guid}"

        # Add membership tag
        utils.add_tag_to_object(self.obj1, membership_tag)

        # Verify tag is stored correctly
        tags = utils.get_tags_on_object(self.obj1)
        self.assertIn(membership_tag, tags)

    def test_membership_tag_persists_with_regular_tags(self):
        """Test that membership tags coexist with regular tags."""
        membership_tag = "view-test-guid"

        # Add membership tag
        utils.add_tag_to_object(self.obj1, membership_tag)

        # Verify both regular and membership tags exist
        tags = utils.get_tags_on_object(self.obj1)
        self.assertIn(membership_tag, tags)
        self.assertIn("tag1", tags)
        self.assertIn("tag2", tags)

    def test_multiple_membership_tags_on_same_object(self):
        """Test object can have membership in multiple views."""
        tag1 = "view-guid-1"
        tag2 = "view-guid-2"
        tag3 = "view-guid-3"

        # Add multiple membership tags
        utils.add_tag_to_object(self.obj1, tag1)
        utils.add_tag_to_object(self.obj1, tag2)
        utils.add_tag_to_object(self.obj1, tag3)

        # Verify all membership tags exist
        tags = utils.get_tags_on_object(self.obj1)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertIn(tag3, tags)

    def test_remove_membership_tag_leaves_others(self):
        """Test removing one membership tag doesn't affect others."""
        tag1 = "view-guid-1"
        tag2 = "view-guid-2"

        # Add two membership tags
        utils.add_tag_to_object(self.obj1, tag1)
        utils.add_tag_to_object(self.obj1, tag2)

        # Remove one
        utils.remove_tag_from_object(self.obj1, tag1)

        # Verify only tag1 is gone
        tags = utils.get_tags_on_object(self.obj1)
        self.assertNotIn(tag1, tags)
        self.assertIn(tag2, tags)
        self.assertIn("tag1", tags)  # Regular tags unaffected
        self.assertIn("tag2", tags)

    def test_membership_tag_on_object_without_tags(self):
        """Test adding membership tag to object with no existing tags."""
        membership_tag = "view-guid-empty"

        # Add to object with no tags
        utils.add_tag_to_object(self.obj3, membership_tag)

        # Verify tag was added
        tags = utils.get_tags_on_object(self.obj3)
        self.assertEqual(len(tags), 1)
        self.assertIn(membership_tag, tags)


class TestMembershipOperations(unittest.TestCase):
    """Test membership tag operations (add/remove)."""

    def setUp(self):
        """Set up test objects."""
        self.obj = MockObject("TestObject")
        utils.set_tags_on_object(self.obj, ["tag1", "tag2"])

    def test_add_membership_tag(self):
        """Test adding view membership tag."""
        membership_tag = "view-guid-12345"

        # Add membership tag
        utils.add_tag_to_object(self.obj, membership_tag)

        # Verify tag was added
        tags = utils.get_tags_on_object(self.obj)
        self.assertIn(membership_tag, tags)

        # Verify original tags are preserved
        self.assertIn("tag1", tags)
        self.assertIn("tag2", tags)

    def test_remove_membership_tag(self):
        """Test removing view membership tag."""
        membership_tag = "view-guid-12345"

        # Add then remove membership tag
        utils.add_tag_to_object(self.obj, membership_tag)
        utils.remove_tag_from_object(self.obj, membership_tag)

        # Verify tag was removed
        tags = utils.get_tags_on_object(self.obj)
        self.assertNotIn(membership_tag, tags)

        # Verify original tags are preserved
        self.assertIn("tag1", tags)
        self.assertIn("tag2", tags)

    def test_add_membership_tag_idempotent(self):
        """Test that adding same membership tag twice doesn't duplicate."""
        membership_tag = "view-guid-12345"

        # Add tag twice
        utils.add_tag_to_object(self.obj, membership_tag)
        utils.add_tag_to_object(self.obj, membership_tag)

        # Verify tag appears only once
        tags = utils.get_tags_on_object(self.obj)
        self.assertEqual(tags.count(membership_tag), 1)


if __name__ == '__main__':
    unittest.main()
