# LF Line Ending Converter Utility - Release Notes (v1.0.2)

A premium, production-ready release bringing absolute safety controls, configurable exclusions, standard wildcard glob matching, advanced regex filters, dynamic CLI parameters, and extensive automated test coverage to ensure line ending conversions remain fast, reliable, and risk-free.

## 🚀 Key Improvements & Features

### 1. Hardened VCS & Metadata Protection
* **Safety Pruning**: Upgraded recursive directory traversal to modify `dirs[:]` in-place inside `os.walk`.
* **Zero Corruption Risk**: Administrative, dependency, and backup directories (such as `.git`, `.idea`, `node_modules`, and `.history`) are now entirely bypassed, protecting internal databases from accidental normalizations.

### 2. Externalized Traversal Exclusions (`config.ini`)
* **Flexible Configurations**: Extracted excluded paths into a standard INI configuration layout.
* **Template Provided**: Included `config.ini.template` for clean settings distribution.
* Default exclusions are shipped out-of-the-box for common development environments:
  ```ini
  [Traversal]
  exclude_dirs = .*, node_modules, build, dist
  exclude_files = .*, *.log, *.tmp
  ```

### 3. Smart Wildcard Globbing Exclusions
* Integrated Python's standard `fnmatch` wildcard pattern matcher.
* You can now safely skip patterns like `*.log`, `*.tmp`, or `.history` files using clean glob semantics.

### 4. Advanced Regular Expression Engines
* Added true Regex matching capability! By prefixing any exclusion pattern with the `re:` or `regex:` prefix, the system compiles and processes the constraint as a full Python regular expression pattern:
  * Directory pattern: `re:^build_\d+$` (avoids folders matching specific numeric build patterns)
  * File pattern: `re:^cache_[a-f0-9]{5}\.json$`

### 5. Standardized Command-Line Keys (Argparse)
* Introduced a complete CLI argument parsing schema for high-speed dynamic runs:
  * **`-c` / `--config`**: Manually specify the location of the `config.ini` configuration.
  * **`-e` / `--exclude-dirs`**: Pass one or more comma-separated directory glob or regex patterns.
  * **`-f` / `--exclude-files`**: Pass one or more comma-separated file glob or regex patterns.

### 6. Comprehensive Test Suite
* Added 5 automated unit test suites covering the core pipeline:
  * Normalizing CRLF to LF in-place
  * UTF-8 decodability text file checks vs binary images
  * Wildcard glob exclusion filters
  * `re:`-prefixed regex pattern matching
  * Nested mock directory structure traversal testing
* The tests execute with **100% coverage and zero warnings**.

---

## 📂 Release Assets
```text
20241220151407-convert-to-lf/
├── config.ini             # Active traversal configurations
├── config.ini.template    # Configuration blueprints
├── convert_to_lf.py       # Refactored robust traversal utility
├── README.md              # Beautiful premium user guide
└── tests/
    └── test_convert_to_lf.py # Automated test suites
```
