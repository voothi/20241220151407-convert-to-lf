import os
import sys
import argparse
import configparser

def get_config(config_path: str = "config.ini") -> dict:
    """
    Loads configuration settings from config_path.
    Falls back to sensible defaults if the file does not exist.
    """
    config = configparser.ConfigParser(interpolation=None)
    if os.path.exists(config_path):
        config.read(config_path, encoding="utf-8")

    exclude_dirs_str = config.get("Traversal", "exclude_dirs", fallback=".git, .history, .idea, node_modules")
    exclude_dirs = [d.strip() for d in exclude_dirs_str.split(",") if d.strip()]
    
    return {
        "exclude_dirs": exclude_dirs
    }

def convert_to_lf(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Replace CRLF (Windows) with LF (Unix)
    content = content.replace(b'\r\n', b'\n')

    with open(file_path, 'wb') as f:
        f.write(content)

def is_text_file(file_path):
    # A simple check to see if the file is text
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except:
        return False

def traverse_directory(directory, exclude_dirs):
    exclude_set = set(exclude_dirs)
    for root, dirs, files in os.walk(directory):
        # Modify dirs in-place to prevent traversing unwanted metadata/dependency directories
        dirs[:] = [d for d in dirs if d not in exclude_set]
        for file in files:
            file_path = os.path.join(root, file)
            if is_text_file(file_path):
                print(f'Converting {file_path} to LF line endings...')
                convert_to_lf(file_path)

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
        "-e", "--exclude", type=str,
        help="Comma-separated list of additional directories to exclude."
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

    if args.exclude:
        extra_excludes = [d.strip() for d in args.exclude.split(",") if d.strip()]
        exclude_dirs.update(extra_excludes)

    print(f"Scanning: {directory_to_scan}")
    print(f"Excluding directories: {', '.join(sorted(exclude_dirs))}")

    traverse_directory(directory_to_scan, exclude_dirs)
    print("Conversion complete!")

if __name__ == "__main__":
    main()