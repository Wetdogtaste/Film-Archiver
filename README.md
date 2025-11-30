# Film Archiver

A desktop application for organizing and renaming film photography scans with metadata support.

## Overview

Film Archiver helps film photographers organize their scanned negatives by:

- Renaming files with a consistent naming scheme
- Storing metadata like camera model, film stock, and lens information
- Embedding lens information in EXIF data
- Managing favorites for cameras, films, and lenses
- Supporting per-file lens assignment for rolls shot with multiple lenses

## Features

- Intuitive user interface with image preview
- Drag and drop support for easy file import
- Customizable file naming
- EXIF metadata embedding
- Lens metadata support with per-file assignment
- Favorites management for cameras, films, and lenses
- Dark mode support

## Archive Organization System

Film Archiver creates a structured, searchable archive system that bridges your digital scans with physical negative storage.

### Folder Structure

Each processed roll creates a folder formatted as:

```
{ROLL#}-{CAMERA}-{FILM}-{MONTH+YEAR}
```

**Example:** `023-CANON_AE-1P-PORTRA_400-NOV25`

### File Structure

Files within each folder follow the naming convention:

```
{ROLL#}-{FRAME#}-{CAMERA}-{FILM}.ext
```

**Example:** `023-01-CANON_AE-1P-PORTRA_400.jpg`

### Dynamic Roll Numbering

The roll number automatically adjusts padding based on your archive size:
- Rolls 1-999: 3 digits (e.g., `001`, `023`, `999`)
- Rolls 1000+: 4+ digits (e.g., `1000`, `5432`)

This ensures proper sorting regardless of archive size.

### Why This Matters

The naming convention serves as a **cross-referenceable catalog system**:

| Component | Purpose |
|-----------|---------|
| **Roll Number** | Unique catalog ID - matches your physical negative sleeves |
| **Camera Model** | Filter/search by camera body |
| **Film Stock** | Filter/search by film type |
| **Date** | Temporal context for chronological organization |

### Cross-Referencing Your Archive

**Digital → Physical:**
1. Find a photo in your digital archive (e.g., `023-15-CANON_AE-1P-PORTRA_400.jpg`)
2. Note the roll number (`023`)
3. Locate physical negative sleeve labeled `023`
4. Find frame 15 on the sleeve

**Physical → Digital:**
1. Pick up negative sleeve `023`
2. Search your digital archive for files starting with `023-`
3. All scans from that roll are instantly accessible

## Getting Started

See the detailed README in the `film_archiver_app` directory for installation and usage instructions.

## Version

Current version: 1.2.0

## Author

Created by **Michael Ziebell**

GitHub: [@Wetdogtaste](https://github.com/Wetdogtaste)

## License

MIT License - © 2024-2025 Michael Ziebell
