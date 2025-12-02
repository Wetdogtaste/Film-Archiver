# Film Archiver

A desktop application for building a structured, searchable film photography archive. Film Archiver bridges your digital scans with physical negative storage through a thoughtful naming system and rich metadata embedding.

## The Archive Philosophy

Film Archiver creates a **dual-layer organization system** designed to work independently yet complement each other:

### Layer 1: Finder-Based Archive
Your film scans live in a structured folder hierarchy that you control—completely independent from any photo management software. This gives you:
- Direct access via Finder/file browser
- Easy backup and portability  
- Quick visual navigation by year/roll
- No lock-in to any specific application

### Layer 2: Metadata Integration  
EXIF metadata embedded in each file enables seamless integration with photo management apps (Lightroom, Capture One, Photo Mechanic, etc.):
- **Date metadata** keeps files chronologically organized in catalogs
- **Lens metadata** enables filtering and searching by lens
- Import into any DAM software and maintain organization automatically

**Recommended Practice:** Store your Film Archive folder separately from where your photo management app stores its managed files. This keeps your master archive navigable in Finder while still accessible to catalog software.

---

## Recommended Folder Structure

Set up a master archive folder with subfolders organized by year:

```
Film Archive/
├── 2023/
│   ├── 001-CLE-400D-JAN23/
│   │   ├── 001-01-CLE-400D.jpg
│   │   ├── 001-02-CLE-400D.jpg
│   │   └── ...
│   ├── 002-CLE-HP5-FEB23/
│   └── ...
├── 2024/
│   ├── 045-AE1P-PORTRA400-MAR24/
│   └── ...
└── 2025/
    └── ...
```

Opening any year folder shows every roll shot that year in chronological order, easily searchable by roll number, camera, or film stock.

---

## The Naming Format

### Folder Naming
```
{ROLL}-{CAMERA}-{STOCK}-{MONTH}{YR}
```

| Component | Purpose | Example |
|-----------|---------|---------|
| **ROLL** | Unique archive catalog number | `001`, `045`, `1000` |
| **CAMERA** | Camera body used | `CLE`, `AE1P`, `M6` |
| **STOCK** | Film stock | `400D`, `HP5`, `PORTRA400` |
| **MONTH+YR** | When the roll was shot | `JAN23`, `MAR24`, `NOV25` |

**Example:** `023-CANON_AE1P-PORTRA400-NOV25`

### File Naming
```
{ROLL}-{FRAME}-{CAMERA}-{STOCK}.ext
```

| Component | Purpose | Example |
|-----------|---------|---------|
| **ROLL** | Same catalog number as folder | `023` |
| **FRAME** | Frame number within roll | `01`, `15`, `36` |
| **CAMERA** | Camera body (redundant for safety) | `CANON_AE1P` |
| **STOCK** | Film stock (redundant for safety) | `PORTRA400` |

**Example:** `023-15-CANON_AE1P-PORTRA400.jpg`

### Optional Suffixes

For push/pull processing or shooting at a different ISO:

| Situation | Suffix | Example Filename |
|-----------|--------|------------------|
| Pushed +1 | `(+1)` | `023-15-CANON_AE1P-PORTRA400(+1).jpg` |
| Pulled -1 | `(-1)` | `023-15-CANON_AE1P-PORTRA400(-1).jpg` |
| Shot at ISO 800 | `(@800)` | `023-15-CANON_AE1P-PORTRA400(@800).jpg` |

---

## Why Duplicate Names Are Impossible

The naming scheme is designed so that **every file has a globally unique name**, even if files accidentally get moved to wrong folders:

1. **Roll number is unique** across your entire archive (you never reuse a roll number)
2. **Frame number is unique** within each roll (01-36 typically)
3. The combination of `ROLL-FRAME` creates a unique identifier that can never collide

Even if you moved `023-15-CANON_AE1P-PORTRA400.jpg` into the folder for roll 045, the filename itself contains roll 023 so there's no ambiguity about which negative it came from.

### Dynamic Roll Numbering

Film Archiver automatically adjusts padding based on your archive size:

| Archive Size | Padding | Examples |
|--------------|---------|----------|
| Rolls 1-999 | 3 digits | `001`, `023`, `999` |
| Rolls 1000+ | 4+ digits | `1000`, `1234`, `5432` |

This ensures proper alphabetical sorting regardless of how large your archive grows.

---

## Metadata Benefits

### EXIF Date Embedding
Film Archiver sets these date fields in each file:
- `DateTimeOriginal` — when the photo was taken
- `DateTimeDigitized` — synced to the same date
- `DateTime` — file modification date
- macOS creation date (on Mac)

**Result:** Import files into any photo management app and they automatically sort chronologically, regardless of when they were scanned.

### Lens Metadata
Store the lens used for each frame in the EXIF `LensModel` field:
- Filter photos by lens in your catalog software
- Track which lenses you use most
- Apply different lenses to individual frames within a roll

---

## Cross-Referencing Physical ↔ Digital

The roll number is your **universal catalog ID** linking digital files to physical negatives.

### Finding the Negative for a Digital File
1. Note the roll number from the filename (e.g., `023-15-...` → Roll 023)
2. Find physical negative sleeve labeled `023`
3. Locate frame 15 on the sleeve

### Finding Digital Files for a Physical Negative
1. Note the roll number on the sleeve (e.g., `023`)
2. In Finder: search for `023-` in your Film Archive
3. In your photo app: filter by filename containing `023-`

---

## Features

- **Image preview** with thumbnail caching
- **Favorites** for cameras, films, and lenses
- **Per-file lens assignment** for rolls shot with multiple lenses
- **Reverse file order** toggle (labs often scan in reverse)
- **Date picker** with calendar widget
- **Push/Pull notation** or custom shot-at ISO
- **Dark mode** support (follows macOS system setting)
- **RAW format support** (CR2, CR3, NEF, ARW, DNG, etc.)
- **Auto-increment roll number** after processing for streamlined multi-roll workflow

---

## System Requirements

### macOS Compatibility

Film Archiver is built for macOS and supports a wide range of versions:

| macOS Version | Support Status | Notes |
|---------------|----------------|-------|
| 10.13 High Sierra | ✅ Supported | Light theme only (no system dark mode) |
| 10.14 Mojave | ✅ Supported | Full functionality including dark mode |
| 10.15 Catalina | ✅ Supported | Full functionality |
| 11.0 Big Sur | ✅ Supported | Full functionality |
| 12.0 Monterey | ✅ Supported | Full functionality (Intel & Apple Silicon) |
| 13.0 Ventura | ✅ Supported | Full functionality |
| 14.0 Sonoma | ✅ Supported | Full functionality |
| 15.0 Sequoia | ✅ Supported | Full functionality |

**Architecture Support:**
- ✅ Intel Macs (x64)
- ✅ Apple Silicon Macs (M1/M2/M3/M4 - ARM64)

### Known Limitations

**Drag and Drop:** In the packaged DMG version, drag-and-drop is disabled due to compatibility issues with the bundled runtime. Use the **Add Files** button to select images instead. This does not affect any other functionality.

**Dark Mode:** Automatic dark mode detection requires macOS 10.14 Mojave or later. On older versions, the app will use the light theme.

### Gatekeeper Notice

Since Film Archiver is not yet notarized with Apple, macOS may display a security warning on first launch. To open the app:

1. **Right-click** (or Control-click) on Film Archiver in Applications
2. Select **Open** from the context menu
3. Click **Open** in the dialog that appears

You only need to do this once—subsequent launches will work normally.

Alternatively: System Preferences → Security & Privacy → General → click "Open Anyway"

---

## Getting Started

See the detailed [Installation & Usage Guide](film_archiver_app/README.md) in the app directory.

**Quick Start:**
1. Download the latest `.dmg` from [Releases](https://github.com/Wetdogtaste/Film-Archiver/releases)
2. Drag Film Archiver to Applications
3. Add your scanned files
4. Fill in roll number, camera, film, and date
5. Click **Process Files** and choose your output folder

---

## Version

**Current version: 1.2.3**

See [Changelog](film_archiver_app/README.md#version-history) for release history.

---

## Author

Created by **Michael Ziebell**

GitHub: [@Wetdogtaste](https://github.com/Wetdogtaste)

## License

MIT License — © 2024-2025 Michael Ziebell
