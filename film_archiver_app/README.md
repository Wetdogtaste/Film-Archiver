# Film Archiver

A tool for organizing and renaming film photography scans.

## Features

- Automatically rename scanned film photos with customizable naming scheme
- Drag and drop support for easy file import
- Preview images before processing
- Save frequently used camera models, film stocks, and lenses
- Update file dates to match capture dates
- Store lens metadata in EXIF data for each photo
- Apply different lenses to individual photos within the same roll
- Reverse file order when needed
- Dark mode support
- Dynamic roll numbering (supports archives of any size)

## Installation

1. Download the latest Film_Archiver.dmg
2. Open the DMG file
3. Drag "Film Archiver" to your Applications folder
4. Double-click to launch

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

## Usage Tips

1. Click "Add Files" or drag and drop files directly to add your scanned photos
2. Enter roll number, camera model, film type, and lens model (if applicable)
3. Use the calendar to set the capture date
4. Toggle "Reverse File Order" if needed (useful when labs scan rolls in reverse)
5. To set different lenses for individual photos:
   - Select one or multiple photos in the file list
   - Click on the lens cell (with dropdown indicator) for any selected photo
   - Choose a lens from the dropdown menu or enter a new one
   - The lens will be applied to all selected photos
6. Click "Process Files" to organize your photos

## Version History

### 1.2.0 (2025-11-30)
- Added drag and drop support for adding files
- Added dynamic roll number padding (supports 1000+ rolls)
- Improved dark mode theming and UI consistency
- Fixed image preview display issues
- Fixed tooltip behavior
- Fixed calendar date picker issues
- Fixed input parameter type box behavior
- Various UI refinements for Light/Dark mode

### 1.1.0 (2025-03-29)
- Added lens metadata support
- Store lens information in EXIF data
- Apply different lenses to individual photos
- Save frequently used lenses
- Improved selection behavior in file list

### 1.0.0 (2024-02-08)
- Initial release
- Basic file renaming and organization
- Camera and film stock management
- Image preview functionality
- Date modification support

## Author

Created by **Michael Ziebell**

GitHub: [@Wetdogtaste](https://github.com/Wetdogtaste)

## License

MIT License - © 2024-2025 Michael Ziebell
