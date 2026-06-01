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
- **Flexible Globbing Exclusions**: Skips administrative metadata, development directories, and temporary files using standard wildcard glob patterns (e.g. `.*`, `*.log`, `node_modules`, `build`).

---

## Project Structure
```text
20241220151407-convert-to-lf/
├── config.ini             # Traversal glob/wildcard exclusion settings
├── config.ini.template    # Configuration template
├── .gitattributes         # Global LF normalization & asset protection settings
├── .gitignore             # Standard IDE and output file exclusions
├── LICENSE                # MIT License
├── README.md              # Detailed utility documentation
└── convert_to_lf.py       # Core recursive line ending converter script
```

---

## Configuration & Git Integration

### 1. The `config.ini` Settings
The utility automatically loads directories and files to ignore using glob/wildcard patterns.

Default `config.ini` configuration:
```ini
[Traversal]
# Comma-separated list of glob/wildcard patterns for directories to completely ignore
exclude_dirs = .*, node_modules, build, dist

# Comma-separated list of glob/wildcard patterns for files to ignore
exclude_files = .*, *.log, *.tmp
```

### 2. Git Attributes
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

### 1. Manual Invocation (CLI)
To run the utility, specify the directory you want to scan and convert as a positional argument:
```powershell
python convert_to_lf.py <directory-path>
```

For example:
```powershell
python convert_to_lf.py "U:\voothi\20241220151407-convert-to-lf"
```

### 2. Dynamic Traversal Keys (Arguments)
You can customize the exclusions and configurations dynamically via CLI arguments (keys):

* **Override Config File (`-c` / `--config`)**:
  Provide an explicit configuration file path:
  ```powershell
  python convert_to_lf.py "U:\voothi\20241220151407-convert-to-lf" --config "my-custom-config.ini"
  ```

* **Additional Directory Exclusions (`-e` / `--exclude-dirs`)**:
  Provide a comma-separated list of additional glob patterns for directories to skip:
  ```powershell
  python convert_to_lf.py "U:\voothi\20241220151407-convert-to-lf" --exclude-dirs "venv,tmp*,out"
  ```

* **Additional File Exclusions (`-f` / `--exclude-files`)**:
  Provide a comma-separated list of additional glob patterns for files to skip:
  ```powershell
  python convert_to_lf.py "U:\voothi\20241220151407-convert-to-lf" --exclude-files "*.bak,*.cache"
  ```

---

## How it Works

1. **Configure**: Resolves glob configurations from `config.ini`, then incorporates any dynamic CLI `--exclude-dirs` and `--exclude-files` arguments.
2. **Traverse**: The script uses `os.walk` recursively on the target directory, instantly pruning any directories matching the directory exclusion patterns using `fnmatch` matching.
3. **Filter**: Files are checked against the file glob patterns (like `.*` or `*.log`). If matched, they are completely bypassed.
4. **Detect**: `is_text_file` reads files to verify if they decode cleanly as UTF-8. Non-text/binary files are safely bypassed.
5. **Convert**: Normalizes CRLF (`\r\n`) sequences to Unix LF (`\n`) and rewrites the file in-place.

---

## License
MIT License. See LICENSE file for details.
