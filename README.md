# LF Line Ending Converter Utility

[![Version](https://img.shields.io/badge/version-v1.0.0-green)](https://github.com/voothi/20241220151407-convert-to-lf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A premium, lightweight Python command-line utility to recursively traverse a specified directory, automatically detect text files, and seamlessly normalize Windows-style CRLF line endings to Unix-standard LF line endings.

## Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Configuration & Git Integration](#configuration--git-integration)
- [Usage](#usage)
- [How it Works](#how-it-works)
- [License](#license)

---

## Features
- **Recursive Traversal**: Scans all subdirectories and nested folders automatically from a specified root directory.
- **Intelligent Text Detection**: Performs a clean UTF-8 validation check to automatically isolate text files (like `.md`, `.txt`, `.py`, `.js`, etc.) and prevent any corruption of binary assets (like images, archives, or PDFs).
- **In-Place Normalization**: Replaces CRLF (`\r\n`) line endings with Unix-style LF (`\n`) directly in the files safely.
- **Modern Gitattributes Integration**: Complements `.gitattributes` configuration to ensure consistent multi-platform Line Ending settings.

---

## Project Structure
```text
20241220151407-convert-to-lf/
├── .gitattributes         # Global LF normalization & asset protection settings
├── .gitignore             # Standard IDE and output file exclusions
├── LICENSE                # MIT License
├── README.md              # Detailed utility documentation
└── convert_to_lf.py       # Core recursive line ending converter script
```

---

## Configuration & Git Integration

The project includes an optimized `.gitattributes` file to enforce global LF normalization for text files while preserving binary assets.

Default `.gitattributes` configuration highlights:
```gitattributes
# Default Handling: Auto-detect text files and enforce Unix-style LF
* text=auto eol=lf

# Plain Text & Markdown (Obsidian Vault Essentials)
*.md text eol=lf
*.txt text eol=lf

# Development & Scripting Languages
*.py text eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
```

---

## Usage

### Manual Invocation (CLI)
To run the utility, specify the directory you want to scan and convert as an argument:
```powershell
python convert_to_lf.py <directory-path>
```

For example, to normalize all files in a project vault or workspace:
```powershell
python convert_to_lf.py "U:\voothi\20241220151407-convert-to-lf"
```

---

## How it Works

1. **Traverse**: The script uses `os.walk` to recursively inspect every file in the target directory.
2. **Detect**: `is_text_file` reads the file to verify if it can be successfully decoded with UTF-8 encoding. If it succeeds, it's considered a text file.
3. **Convert**: For each text file, `convert_to_lf` reads the raw binary representation, replaces all raw occurrences of CRLF (`\r\n`) with LF (`\n`), and writes it back in-place.

---

## License
MIT License. See LICENSE file for details.
