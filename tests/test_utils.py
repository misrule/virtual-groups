"""
Unit tests for utils module.

Tests tag manipulation, validation, and object filtering logic.
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


class MockScene:
    """Mock Blender scene for testing."""

    def __init__(self, objects=None):
        self.objects = objects or []


class TestTagManipulation(unittest.TestCase):
    """Test tag manipulation functions."""

    def test_get_tags_on_new_object(self):
        """Get tags on object with no tags should return empty list."""
        obj = MockObject("Cube")
        tags = utils.get_tags_on_object(obj)
        self.assertEqual(tags, [])

    def test_set_and_get_tags(self):
        """Set tags and retrieve them."""
        obj = MockObject("Cube")
        utils.set_tags_on_object(obj, ["candle", "desk"])

        tags = utils.get_tags_on_object(obj)
        self.assertEqual(tags, ["candle", "desk"])

    def test_get_tags_with_corrupted_json(self):
        """Corrupted JSON should return empty list."""
        obj = MockObject("Cube")
        obj["vg_tags"] = "not valid json["

        tags = utils.get_tags_on_object(obj)
        self.assertEqual(tags, [])

    def test_add_tag_to_object(self):
        """Add tag to object."""
        obj = MockObject("Cube")
        utils.add_tag_to_object(obj, "candle")

        tags = utils.get_tags_on_object(obj)
        self.assertIn("candle", tags)

    def test_add_duplicate_tag(self):
        """Adding duplicate tag should not create duplicates."""
        obj = MockObject("Cube")
        utils.add_tag_to_object(obj, "candle")
        utils.add_tag_to_object(obj, "candle")

        tags = utils.get_tags_on_object(obj)
        self.assertEqual(tags.count("candle"), 1)

    def test_add_multiple_tags(self):
        """Add multiple tags to object."""
        obj = MockObject("Cube")
        utils.add_tag_to_object(obj, "candle")
        utils.add_tag_to_object(obj, "desk")
        utils.add_tag_to_object(obj, "props")

        tags = utils.get_tags_on_object(obj)
        self.assertEqual(len(tags), 3)
        self.assertIn("candle", tags)
        self.assertIn("desk", tags)
        self.assertIn("props", tags)

    def test_remove_tag_from_object(self):
        """Remove tag from object."""
        obj = MockObject("Cube")
        utils.set_tags_on_object(obj, ["candle", "desk", "props"])

        utils.remove_tag_from_object(obj, "desk")

        tags = utils.get_tags_on_object(obj)
        self.assertNotIn("desk", tags)
        self.assertIn("candle", tags)
        self.assertIn("props", tags)

    def test_remove_nonexistent_tag(self):
        """Removing nonexistent tag should not error."""
        obj = MockObject("Cube")
        utils.set_tags_on_object(obj, ["candle"])

        # Should not raise exception
        utils.remove_tag_from_object(obj, "desk")

        tags = utils.get_tags_on_object(obj)
        self.assertEqual(tags, ["candle"])

    def test_remove_all_tags(self):
        """Remove all tags from object."""
        obj = MockObject("Cube")
        utils.set_tags_on_object(obj, ["candle", "desk"])

        utils.remove_tag_from_object(obj, "candle")
        utils.remove_tag_from_object(obj, "desk")

        tags = utils.get_tags_on_object(obj)
        self.assertEqual(tags, [])


class TestTagValidation(unittest.TestCase):
    """Test tag name validation."""

    def test_empty_tag(self):
        """Empty tag should be invalid."""
        is_valid, error = utils.validate_tag_name("")
        self.assertFalse(is_valid)
        self.assertIn("empty", error.lower())

    def test_valid_alphanumeric_tag(self):
        """Alphanumeric tag should be valid."""
        is_valid, error = utils.validate_tag_name("candle123")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_valid_tag_with_underscore(self):
        """Tag with underscore should be valid."""
        is_valid, error = utils.validate_tag_name("main_character")
        self.assertTrue(is_valid)

    def test_valid_tag_with_hyphen(self):
        """Tag with hyphen should be valid."""
        is_valid, error = utils.validate_tag_name("hero-large")
        self.assertTrue(is_valid)

    def test_invalid_tag_with_space(self):
        """Tag with space should be invalid."""
        is_valid, error = utils.validate_tag_name("my tag")
        self.assertFalse(is_valid)

    def test_invalid_tag_with_special_char(self):
        """Tag with special characters should be invalid."""
        is_valid, error = utils.validate_tag_name("tag@123")
        self.assertFalse(is_valid)

        is_valid, error = utils.validate_tag_name("tag!name")
        self.assertFalse(is_valid)

        is_valid, error = utils.validate_tag_name("tag.name")
        self.assertFalse(is_valid)

    def test_valid_mixed_case_tag(self):
        """Mixed case tag should be valid."""
        is_valid, error = utils.validate_tag_name("MyTag")
        self.assertTrue(is_valid)


class TestSceneTagEnumeration(unittest.TestCase):
    """Test scene tag enumeration."""

    def test_empty_scene(self):
        """Empty scene should return empty tag list."""
        scene = MockScene([])
        tags = utils.get_all_scene_tags(scene)
        self.assertEqual(tags, [])

    def test_scene_with_tagged_objects(self):
        """Scene with tagged objects should return all unique tags."""
        obj1 = MockObject("Obj1")
        utils.set_tags_on_object(obj1, ["candle", "desk"])

        obj2 = MockObject("Obj2")
        utils.set_tags_on_object(obj2, ["props", "desk"])

        scene = MockScene([obj1, obj2])
        tags = utils.get_all_scene_tags(scene)

        self.assertEqual(len(tags), 3)
        self.assertIn("candle", tags)
        self.assertIn("desk", tags)
        self.assertIn("props", tags)

    def test_scene_tags_are_sorted(self):
        """Tags should be returned in sorted order."""
        obj1 = MockObject("Obj1")
        utils.set_tags_on_object(obj1, ["zebra", "apple", "mouse"])

        scene = MockScene([obj1])
        tags = utils.get_all_scene_tags(scene)

        self.assertEqual(tags, ["apple", "mouse", "zebra"])

    def test_scene_tags_are_unique(self):
        """Duplicate tags across objects should only appear once."""
        obj1 = MockObject("Obj1")
        utils.set_tags_on_object(obj1, ["candle"])

        obj2 = MockObject("Obj2")
        utils.set_tags_on_object(obj2, ["candle"])

        obj3 = MockObject("Obj3")
        utils.set_tags_on_object(obj3, ["candle"])

        scene = MockScene([obj1, obj2, obj3])
        tags = utils.get_all_scene_tags(scene)

        self.assertEqual(tags, ["candle"])


class TestObjectFiltering(unittest.TestCase):
    """Test object filtering by tags."""

    def setUp(self):
        """Set up test objects."""
        self.obj1 = MockObject("Obj1")
        utils.set_tags_on_object(self.obj1, ["candle", "desk"])

        self.obj2 = MockObject("Obj2")
        utils.set_tags_on_object(self.obj2, ["props", "desk"])

        self.obj3 = MockObject("Obj3")
        utils.set_tags_on_object(self.obj3, ["candle"])

        self.obj4 = MockObject("Obj4")
        utils.set_tags_on_object(self.obj4, [])

        self.scene = MockScene([self.obj1, self.obj2, self.obj3, self.obj4])

    def test_or_mode_single_tag(self):
        """OR mode with single tag should return all objects with that tag."""
        objects = utils.get_objects_with_tags(self.scene, ["candle"], mode='OR')

        self.assertEqual(len(objects), 2)
        self.assertIn(self.obj1, objects)
        self.assertIn(self.obj3, objects)

    def test_or_mode_multiple_tags(self):
        """OR mode should return objects with any of the tags."""
        objects = utils.get_objects_with_tags(self.scene, ["candle", "props"], mode='OR')

        self.assertEqual(len(objects), 3)
        self.assertIn(self.obj1, objects)  # has candle
        self.assertIn(self.obj2, objects)  # has props
        self.assertIn(self.obj3, objects)  # has candle

    def test_or_mode_no_matches(self):
        """OR mode with no matching tags should return empty list."""
        objects = utils.get_objects_with_tags(self.scene, ["nonexistent"], mode='OR')
        self.assertEqual(len(objects), 0)

    def test_and_mode_single_tag(self):
        """AND mode with single tag should behave like OR mode."""
        objects = utils.get_objects_with_tags(self.scene, ["desk"], mode='AND')

        self.assertEqual(len(objects), 2)
        self.assertIn(self.obj1, objects)
        self.assertIn(self.obj2, objects)

    def test_and_mode_multiple_tags(self):
        """AND mode should return only objects with all tags."""
        objects = utils.get_objects_with_tags(self.scene, ["candle", "desk"], mode='AND')

        self.assertEqual(len(objects), 1)
        self.assertIn(self.obj1, objects)

    def test_and_mode_no_matches(self):
        """AND mode with impossible combination should return empty list."""
        objects = utils.get_objects_with_tags(self.scene, ["candle", "props"], mode='AND')
        self.assertEqual(len(objects), 0)

    def test_empty_tag_list(self):
        """Empty tag list should return empty results."""
        objects = utils.get_objects_with_tags(self.scene, [], mode='OR')
        self.assertEqual(len(objects), 0)

        objects = utils.get_objects_with_tags(self.scene, [], mode='AND')
        self.assertEqual(len(objects), 0)


if __name__ == '__main__':
    unittest.main()
