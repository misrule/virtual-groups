# Virtual Groups Unit Tests

This directory contains unit tests for the Virtual Groups Blender add-on.

## Overview

The test suite covers:
- **Query Parser** (`test_query_parser.py`) - Query validation, parsing, and evaluation logic
- **Utilities** (`test_utils.py`) - Tag manipulation, validation, and object filtering

Tests are written using Python's built-in `unittest` framework and use mock objects to avoid requiring Blender to be running.

## Running Tests

### Option 1: Using the test runner (recommended)

```bash
cd /path/to/virtual_groups_project
python tests/run_tests.py
```

### Option 2: Using Python's unittest module

```bash
cd /path/to/virtual_groups_project
python -m unittest discover tests
```

### Option 3: Running individual test files

```bash
cd /path/to/virtual_groups_project
python tests/test_query_parser.py
python tests/test_utils.py
```

### Option 4: Using pytest (if installed)

```bash
cd /path/to/virtual_groups_project
pytest tests/
```

## Test Coverage

### Query Parser Tests (test_query_parser.py)

**TestQueryValidation** - 11 tests
- Empty and whitespace queries
- Invalid syntax (no tag:, invalid characters, orphaned operators)
- Valid queries (single tag, AND, OR, NOT, complex)

**TestQueryEvaluation** - 12 tests
- Single tag matching
- AND operator (both tags present/missing)
- OR operator (either tag present/missing)
- NOT operator (tag exclusion)

**TestOperatorPrecedence** - 3 tests
- OR then AND precedence
- AND then OR precedence
- Complex mixed operators

**TestRealWorldScenarios** - 4 tests
- Hearth/desk props scenario (unintuitive precedence)
- Corrected hearth/desk props query (distributed AND)
- Hero objects excluding small ones
- Various real-world use cases

**TestEdgeCases** - 4 tests
- Empty query handling
- Malformed query safety
- Case-sensitive tags
- Tags with hyphens and underscores

**Total: 34 tests for query_parser.py**

### Utilities Tests (test_utils.py)

**TestTagManipulation** - 9 tests
- Get/set tags on objects
- Add tags (including duplicates)
- Remove tags (including nonexistent)
- Corrupted JSON handling

**TestTagValidation** - 8 tests
- Empty tags
- Valid alphanumeric, underscore, hyphen
- Invalid special characters and spaces
- Mixed case

**TestSceneTagEnumeration** - 4 tests
- Empty scene
- Tagged objects
- Sorted output
- Unique tags

**TestObjectFiltering** - 8 tests
- OR mode (single/multiple tags)
- AND mode (single/multiple tags)
- No matches
- Empty tag list

**Total: 29 tests for utils.py**

## Test Philosophy

These tests cover the **core business logic** that doesn't depend on Blender:

✅ **What's tested:**
- Query parsing and evaluation (complete coverage)
- Tag manipulation and validation (complete coverage)
- Object filtering by tags (complete coverage)

❌ **What's NOT tested (requires Blender integration):**
- Operators (button actions)
- UI panels and drawing
- Blender-specific property types
- Scene integration

For manual testing of operators and UI, see the main project documentation.

## Adding New Tests

When adding new tests:

1. **Create a new test class** inheriting from `unittest.TestCase`
2. **Name test methods** starting with `test_`
3. **Use descriptive names** - e.g., `test_and_both_tags_present`
4. **Add docstrings** to explain what's being tested
5. **Use mock objects** to avoid Blender dependencies

Example:

```python
class TestMyFeature(unittest.TestCase):
    """Test my new feature."""

    def test_something_specific(self):
        """Test that something specific works correctly."""
        # Arrange
        obj = MockObject("Test")

        # Act
        result = my_function(obj)

        # Assert
        self.assertTrue(result)
```

## CI/CD Integration

These tests can be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: python tests/run_tests.py
```

Exit codes:
- `0` - All tests passed
- `1` - One or more tests failed

## Troubleshooting

**Import errors:**
- Ensure you're running from the project root directory
- Check that `virtual_groups/` is a valid Python package

**Tests failing unexpectedly:**
- Check that you haven't modified the core logic in `query_parser.py` or `utils.py`
- Verify mock objects match the real Blender object API

**Need more verbose output:**
```bash
python tests/run_tests.py -v
```
