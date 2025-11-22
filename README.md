# Virtual Groups - Blender Add-on

Tag-based semantic grouping and dynamic virtual collections for Blender 4.5+

## Overview

Virtual Groups is a non-intrusive Blender add-on that provides flexible object management through semantic tags and query-based virtual collections. Manage complex scenes without modifying the Outliner structure.

## Features

### Tag System
- Add semantic tags to objects (e.g., `candle`, `desk`, `hero`, `props`)
- Tags stored in object custom properties
- Tag validation (alphanumeric, underscore, hyphen)

### Tag Palette (Ad-hoc Operations)
- Multi-select tags for quick operations
- Hide/Show/Toggle visibility
- Select objects by tags
- Add/Remove tags from selected objects
- Visual feedback showing visibility state
- Search and sort functionality

### Views (Virtual Collections)
- Create named Views with optional queries
- Query syntax: `tag:candle AND tag:desk OR tag:props`
- **Hybrid Model (v1)**:
  - Query-based (dynamic): Auto-includes matching objects
  - Membership-based (explicit): Manually add/remove specific objects
  - Hybrid: Combine both approaches
- View operations: Show/Hide/Toggle/Select
- Persistent in .blend files

## Installation

1. Download or clone this repository
2. Open Blender 4.5+
3. Go to Edit > Preferences > Add-ons
4. Click "Install..." and select the `virtual_groups` directory
5. Enable "Virtual Groups" in the add-ons list
6. Find the panel in 3D View sidebar (N-panel) under "Virtual Groups" tab

## Usage

### Tagging Objects
1. Select objects in viewport
2. In Virtual Groups panel, go to Tags section
3. Type tag name and click "Add"
4. Tags appear on selected objects

### Tag Palette Operations
1. Click tag pills to select them (multi-select supported)
2. Use operation buttons:
   - **Hide/Show/Toggle**: Control visibility
   - **Select**: Select objects with selected tags
   - **Add/Remove Tags**: Apply tags to viewport selection

### Creating Views
1. Click "Add View" in Views section
2. Enter view name
3. (Optional) Enter query: `tag:candle AND tag:desk`
4. Click "Apply Query" to evaluate

### Hybrid Views (v1)
- **Query-only**: Leave membership empty, objects match dynamically
- **Membership-only**: Leave query empty, manually add objects with [Add] button
- **Hybrid**: Use query + manually add exceptions with [Add]/[Remove]

## Development

### Running Tests
```bash
python3 tests/run_tests.py
```

### Project Structure
```
virtual_groups_project/
├── virtual_groups/          # Add-on source
│   ├── __init__.py         # Registration
│   ├── properties.py       # Data model
│   ├── operators.py        # Button actions
│   ├── ui.py              # Panel layouts
│   ├── query_parser.py    # Query evaluation
│   └── utils.py           # Helper functions
└── tests/                 # Unit tests
    ├── test_utils.py
    ├── test_query_parser.py
    └── test_hybrid_views.py
```

## Version History

- **v0.1** - Initial release with tags, Tag Palette, and query-based Views
- **v1.0** - Hybrid View model (query + membership), visual feedback system

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
