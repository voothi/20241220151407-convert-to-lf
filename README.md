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
- **Safe Traversal Exclusions**: Skips administrative metadata and massive dependency folders (e.g. `.git`, `.idea`, `.history`, `node_modules`) to avoid repository corruption.

---

## Project Structure
```text
20241220151407-convert-to-lf/
├── config.ini             # Traversal exclusion settings
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
The utility automatically loads directories to exclude from the `config.ini` file located next to the script.

Default `config.ini` configuration:
```ini
[Traversal]
# Comma-separated list of directory names to completely ignore during recursive scanning
exclude_dirs = .git, .history, .idea, node_modules
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

* **Additional Directory Exclusions (`-e` / `--exclude`)**:
  Provide a comma-separated list of additional directories to skip on-the-fly:
  ```powershell
  python convert_to_lf.py "U:\voothi\20241220151407-convert-to-lf" --exclude "venv,dist,build"
  ```

---

## How it Works

1. **Configure**: Resolves configurations from `config.ini`, then incorporates any dynamic CLI `--exclude` arguments.
2. **Traverse**: The script uses `os.walk` recursively on the target directory, instantly pruning any directories matching the exclusion list.
3. **Detect**: `is_text_file` reads files to verify if they decode cleanly as UTF-8. Non-text/binary files are safely bypassed.
4. **Convert**: Normalizes CRLF (`\r\n`) sequences to Unix LF (`\n`) and rewrites the file in-place.

---

## License
MIT License. See LICENSE file for details.
