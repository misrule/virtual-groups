# Virtual Groups - Blender Extension

Tag-based object organization system for Blender 4.2+

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/misrule/virtual-groups/releases/tag/v0.1.0)
[![License](https://img.shields.io/badge/license-GPL--3.0-green.svg)](LICENSE)
[![Blender](https://img.shields.io/badge/Blender-4.2+-orange.svg)](https://www.blender.org/)

## Overview

Virtual Groups is a Blender extension that provides flexible object management through semantic tags and query-based virtual collections. Organize complex scenes without modifying the Outliner structure.

## ✨ Features

### 🏷️ Tag System
- Tag objects using custom properties (non-intrusive, preserved with .blend files)
- Tag Palette for visual tag selection and bulk operations
- Validation ensures clean tag names (alphanumeric, underscore, hyphen)
- Filter and search tags across your scene
- Add/remove tags from multiple objects at once

### 📋 Tag Palette (Ad-hoc Operations)
- Multi-select tags with visual feedback
- **Visibility Operations**: Hide/Show/Toggle objects by tag
- **Selection Operations**: Select all objects with selected tags
- **Tag Operations**: Add or remove tags from viewport selection
- Auto-clears selection after operations for quick workflows

### 📂 Views (Virtual Collections)
- Create named Views with optional query logic
- **Query Syntax**: `tag:candle AND tag:desk OR NOT tag:small`
- **Hybrid Model (v1)**:
  - **Query-based**: Dynamically includes objects matching query
  - **Membership-based**: Manually add/remove specific objects
  - **Hybrid**: Combine both approaches for maximum flexibility
- **Compositional Operations**:
  - Toggle viewport visibility (👁️ eye icon)
  - Toggle selection (cursor icon)
  - Toggle render visibility (🎥 camera icon)
  - Operations are additive - compose across multiple Views
- **Smart Icons**: Icons show current state (all visible/hidden, etc.)
- **Automatic Cleanup**: Membership tags removed when View is deleted

### 🎨 UI/UX
- Clean sidebar panel in 3D View
- UIList interface matching Blender conventions
- Collapsible Advanced Query section
- Built-in search and sort in View list
- Dynamic state indicators on all icons

## 📦 Installation

### From Release (Recommended)

1. **Download** the latest `virtual_groups-0.1.0.zip` from [Releases](https://github.com/misrule/virtual-groups/releases)
2. Open Blender and go to **Edit > Preferences > Get Extensions**
3. Click the **⋮** menu (top right) > **Install from Disk**
4. Select the downloaded `.zip` file
5. Enable **Virtual Groups** in the extensions list

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/misrule/virtual-groups.git
cd virtual-groups/virtual_groups_project

# Build the extension package
/path/to/blender --command extension build \
  --output-dir ./dist \
  --source-dir ./virtual_groups

# Install for testing
/path/to/blender --command extension install-file \
  -r "user_default" \
  --enable ./dist/virtual_groups-0.1.0.zip
```

## 🚀 Quick Start

### 1. Access the Panel
Find Virtual Groups in: **3D View > Sidebar (N) > Virtual Groups**

### 2. Tag Your Objects
1. Select objects in the viewport
2. In the **Tags** section, type a tag name (e.g., `candle`)
3. Click **Add** (or press Enter)
4. Tags appear as pills below - click to select them

### 3. Use the Tag Palette
1. Click tag pills to select them (multi-select with additional clicks)
2. Use operation buttons:
   - **Hide/Show/Toggle**: Control visibility of tagged objects
   - **Select**: Select all objects with selected tags
   - **Add/Remove Tags**: Apply tags to currently selected objects

### 4. Create Views
1. In the **Views** section, click **[+ New]**
2. Enter a name (e.g., "Desk Area")
3. Add objects:
   - **Query Method**: Click ▸ Advanced Query, enter `tag:desk`, click Apply Query
   - **Membership Method**: Select objects, click **[Add]**
   - **Hybrid**: Combine both approaches
4. Use icons in the View list:
   - **👁️ Eye**: Toggle viewport visibility
   - **Cursor**: Toggle selection
   - **🎥 Camera**: Toggle render visibility

### 5. Compositional Workflow
Views operations are **compositional** - they add/remove objects from global state:

```
Example:
1. Manually select Chair_01 in viewport
2. Click "Window Area" View → Cursor icon
   → Result: Chair_01 + all window objects selected
3. Click "Desk Area" View → Cursor icon
   → Result: Chair_01 + windows + desk objects selected
4. Click "Window Area" View → Cursor icon again
   → Result: Chair_01 + desk objects (windows deselected)
```

## 📖 Documentation

### Query Syntax

Views support a simple query language:

```
tag:candle              # Single tag
tag:desk AND tag:props  # Both tags required (AND)
tag:desk OR tag:hearth  # Either tag matches (OR)
tag:hero AND NOT tag:small  # Tag presence with exclusion (NOT)
```

**Operator Precedence**: `NOT` > `AND` > `OR`

### Hybrid Views Explained

**Query-Only View**
- Set query: `tag:candle`
- Leave membership empty
- Objects automatically included when they match

**Membership-Only View**
- Leave query empty
- Manually add objects with **[Add]** button
- Full control over which objects are included

**Hybrid View** (Most Powerful!)
- Set query: `tag:props AND tag:desk`
- Query matches most objects
- Use **[Add]** to include exceptions (non-matching objects)
- Use **[Remove]** to exclude exceptions (matching objects you don't want)
- **[Clear All]** removes all membership tags (query still active)

### Internal Tags

Views use internal membership tags with format `view-{guid}`. These tags:
- Are automatically created when you add objects to a View
- Are filtered from all UI displays (Tag Palette, Selected Objects)
- Are automatically cleaned up when a View is deleted
- Are stored in object custom properties (preserved with .blend files)

## 🛠️ Development

### Project Structure

```
virtual_groups_project/
├── virtual_groups/          # Extension source
│   ├── __init__.py         # Registration and bl_info
│   ├── blender_manifest.toml # Extension metadata
│   ├── properties.py       # Property definitions (Views, Tags)
│   ├── operators.py        # All operator classes
│   ├── ui.py              # Panel layouts and UIList
│   ├── query_parser.py    # Query DSL parser and evaluator
│   └── utils.py           # Helper functions
├── tests/                  # Unit tests (not included in package)
│   ├── run_tests.py
│   ├── test_utils.py
│   ├── test_query_parser.py
│   └── test_hybrid_views.py
├── docs/                   # Documentation (not included in package)
└── dist/                   # Build output directory
```

### Running Tests

```bash
cd virtual_groups_project
python3 tests/run_tests.py
```

All 71 tests should pass ✅

### Building from Source

```bash
# Build extension package
blender --command extension build \
  --output-dir ./dist \
  --source-dir ./virtual_groups

# Output: dist/virtual_groups-0.1.0.zip
```

### Code Style

- Operator naming: `VG_OT_action_name`
- Properties prefixed with `vg_`
- Follow Blender Python API conventions
- Docstrings required for all classes

## 🗺️ Roadmap

### v0.1.0 (Current) ✅
- Tag system with custom properties
- Tag Palette with multi-select
- Query-based Views with AND/OR/NOT
- Hybrid Views (query + membership)
- Compositional operations
- UIList with dynamic state icons

### Future Versions
- Visual feedback system for tags (partial visibility indicators)
- Search and sort for tags
- Performance optimizations for large scenes
- Additional query operators
- Preset queries
- Export/import tag configurations

## 🐛 Known Issues

- Query operations may be slow on scenes with 10,000+ objects
- No undo support for tag operations (custom properties limitation)
- Query syntax doesn't support parentheses for grouping

## 📝 Version History

- **v0.1.0** (2025-11-23) - Initial release
  - Tag system with custom properties
  - Tag Palette with compositional operations
  - Hybrid Views (query + membership)
  - UIList interface with dynamic icons
  - Automatic membership tag cleanup

## 📄 License

GPL-3.0-or-later

Copyright (c) 2025 Sy Smythe

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

## 🤝 Contributing

Contributions are welcome! Please feel free to:

1. Report bugs via [Issues](https://github.com/misrule/virtual-groups/issues)
2. Suggest features or improvements
3. Submit pull requests

## 🔗 Links

- **GitHub Repository**: https://github.com/misrule/virtual-groups
- **Latest Release**: https://github.com/misrule/virtual-groups/releases/latest
- **Issue Tracker**: https://github.com/misrule/virtual-groups/issues
- **Blender Extensions**: https://extensions.blender.org/ (coming soon)

## ⭐ Support

If you find Virtual Groups useful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting features
- 📢 Sharing with others

---

Made with ❤️ for the Blender community
