import os
import sys
import argparse
import configparser
import fnmatch
import re

def get_config(config_path: str = "config.ini") -> dict:
    """
    Loads configuration settings from config_path.
    Falls back to sensible defaults if the file does not exist.
    """
    config = configparser.ConfigParser(interpolation=None)
    if os.path.exists(config_path):
        config.read(config_path, encoding="utf-8")

    exclude_dirs_str = config.get("Traversal", "exclude_dirs", fallback=".*, node_modules, build, dist")
    exclude_files_str = config.get("Traversal", "exclude_files", fallback=".*, *.log, *.tmp")
    
    exclude_dirs = [d.strip() for d in exclude_dirs_str.split(",") if d.strip()]
    exclude_files = [f.strip() for f in exclude_files_str.split(",") if f.strip()]
    
    return {
        "exclude_dirs": exclude_dirs,
        "exclude_files": exclude_files
    }

def detect_encoding(file_path):
    """
    Detects the encoding of the file by reading BOMs or analyzing a block.
    Returns the encoding string (e.g. 'utf-8', 'utf-16-le', 'cp1252') or None if binary/unknown.
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
    except IOError:
        return None

    if not chunk:
        return 'utf-8' # Empty file is treated as utf-8

    # 1. Check for BOMs
    if chunk.startswith(b'\xef\xbb\xbf'):
        return 'utf-8-sig'
    if chunk.startswith(b'\xff\xfe\x00\x00'):
        return 'utf-32-le'
    if chunk.startswith(b'\x00\x00\xfe\xff'):
        return 'utf-32-be'
    if chunk.startswith(b'\xff\xfe'):
        return 'utf-16-le'
    if chunk.startswith(b'\xfe\xff'):
        return 'utf-16-be'

    # 2. Check for null bytes (likely binary or UTF-16/32 without BOM)
    if b'\x00' in chunk:
        # Check if it could be UTF-16 without BOM
        for enc in ('utf-16-le', 'utf-16-be'):
            try:
                decoded = chunk.decode(enc)
                # Count control characters to make sure it's not binary
                control_chars = sum(1 for c in decoded if c < ' ' and c not in '\r\n\t')
                if len(decoded) > 0 and control_chars / len(decoded) < 0.1:
                    return enc
            except UnicodeDecodeError as e:
                if e.reason == 'unexpected end of data' and e.end == len(chunk):
                    try:
                        decoded = chunk[:e.start].decode(enc)
                        control_chars = sum(1 for c in decoded if c < ' ' and c not in '\r\n\t')
                        if len(decoded) > 0 and control_chars / len(decoded) < 0.1:
                            return enc
                    except Exception:
                        pass
        return None # Considered binary

    # 3. Try to decode as UTF-8
    try:
        chunk.decode('utf-8')
        return 'utf-8'
    except UnicodeDecodeError as e:
        if e.reason == 'unexpected end of data' and e.end == len(chunk):
            return 'utf-8'

    # 4. Fallback to CP1252 / ANSI (common legacy Windows text encoding)
    try:
        decoded = chunk.decode('cp1252', errors='replace')
        control_chars = sum(1 for c in decoded if c < ' ' and c not in '\r\n\t')
        if len(decoded) > 0 and control_chars / len(decoded) < 0.1:
            return 'cp1252'
    except Exception:
        pass

    return None

def convert_to_lf(file_path, encoding=None, strip_bom=False):
    if encoding is None:
        encoding = detect_encoding(file_path)
    if not encoding:
        return False

    try:
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            content = f.read()
    except (UnicodeDecodeError, LookupError):
        return False
    
    # Check if conversion is needed
    has_crlf = '\r\n' in content
    has_bom = (encoding == 'utf-8-sig')

    if not has_crlf and not (has_bom and strip_bom):
        return False

    if has_crlf:
        content = content.replace('\r\n', '\n')

    write_encoding = 'utf-8' if (has_bom and strip_bom) else encoding

    try:
        with open(file_path, 'w', encoding=write_encoding, newline='\n') as f:
            f.write(content)
    except (UnicodeEncodeError, LookupError):
        return False
    return True

def is_text_file(file_path):
    return detect_encoding(file_path) is not None

def should_exclude(name, patterns):
    """
    Checks if a name matches any of the glob/wildcard patterns or regular expressions.
    Patterns starting with 're:' or 'regex:' are treated as regular expressions.
    """
    for pattern in patterns:
        if pattern.startswith("re:") or pattern.startswith("regex:"):
            regex_pattern = pattern.split(":", 1)[1]
            try:
                if re.search(regex_pattern, name):
                    return True
            except re.error as exc:
                print(f"[!] Warning: Invalid regex pattern '{pattern}': {exc}", file=sys.stderr)
        else:
            if fnmatch.fnmatch(name, pattern):
                return True
    return False

def traverse_directory(directory, exclude_dirs, exclude_files, strip_bom=False, list_mode="changed"):
    total_files = 0
    converted_files = 0
    skipped_files = 0

    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to prevent traversing unwanted metadata/dependency directories
        dirs[:] = [d for d in dirs if not should_exclude(d, exclude_dirs)]
        for file in files:
            # Skip excluded files
            if should_exclude(file, exclude_files):
                continue
            file_path = os.path.join(root, file)
            total_files += 1
            encoding = detect_encoding(file_path)
            
            if encoding:
                changed = convert_to_lf(file_path, encoding, strip_bom=strip_bom)
                if changed:
                    converted_files += 1
                    if list_mode in ('changed', 'all'):
                        enc_str = f"{encoding} -> utf-8" if (encoding == "utf-8-sig" and strip_bom) else encoding
                        print(f'[✓] Converted: {file_path} ({enc_str})')
                else:
                    skipped_files += 1
                    if list_mode == 'all':
                        print(f'[-] Unchanged: {file_path} ({encoding})')
            else:
                skipped_files += 1
                if list_mode == 'all':
                    print(f'[S] Skipped/Binary: {file_path}')

    print("\n--- Summary ---")
    print(f"Total files scanned:    {total_files}")
    print(f"Files normalized (LF):  {converted_files}")
    print(f"Files unchanged/binary: {skipped_files}")

def main():
    parser = argparse.ArgumentParser(
        description="LF Line Ending Converter — recursively normalizes text files to standard Unix LF endings."
    )
    parser.add_argument(
        "directory", type=str, nargs="?",
        help="The target directory to scan and normalize."
    )
    parser.add_argument(
        "-c", "--config", type=str, default="config.ini",
        help="Path to config.ini configuration file (default: config.ini next to the script)."
    )
    parser.add_argument(
        "-e", "--exclude-dirs", type=str,
        help="Comma-separated list of additional glob patterns or 're:'-prefixed regexes for directories to exclude."
    )
    parser.add_argument(
        "-f", "--exclude-files", type=str,
        help="Comma-separated list of additional glob patterns or 're:'-prefixed regexes for files to exclude."
    )
    parser.add_argument(
        "--strip-bom", action="store_true",
        help="Convert UTF-8 files with Byte Order Mark (BOM) signature to standard UTF-8 (without BOM)."
    )
    parser.add_argument(
        "-l", "--list", type=str, choices=["changed", "all", "none"], default="changed",
        help="Flexible listing options: 'changed' lists only converted files (default), 'all' lists everything, 'none' suppresses individual output."
    )
    
    args = parser.parse_args()

    if not args.directory:
        parser.print_help()
        sys.exit(0)

    directory_to_scan = args.directory
    if not os.path.isdir(directory_to_scan):
        print(f"Error: {directory_to_scan} is not a valid directory.")
        sys.exit(1)

    # Resolve config relative to the script file
    config_path = args.config
    if not os.path.isabs(config_path):
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)

    config = get_config(config_path)
    
    exclude_dirs = set(config["exclude_dirs"])
    exclude_files = set(config["exclude_files"])

    if args.exclude_dirs:
        extra_dir_excludes = [d.strip() for d in args.exclude_dirs.split(",") if d.strip()]
        exclude_dirs.update(extra_dir_excludes)

    if args.exclude_files:
        extra_file_excludes = [f.strip() for f in args.exclude_files.split(",") if f.strip()]
        exclude_files.update(extra_file_excludes)

    print(f"Scanning: {directory_to_scan}")
    print(f"Excluding directories matching patterns: {', '.join(sorted(exclude_dirs))}")
    print(f"Excluding files matching patterns:       {', '.join(sorted(exclude_files))}")

    traverse_directory(
        directory_to_scan, exclude_dirs, exclude_files,
        strip_bom=args.strip_bom, list_mode=args.list
    )
    print("Conversion complete!")

if __name__ == "__main__":
    main()