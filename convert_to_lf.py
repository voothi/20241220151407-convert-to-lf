import os
import sys

def convert_to_lf(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Replace CRLF (Windows) with LF (Unix)
    content = content.replace(b'\r\n', b'\n')

    with open(file_path, 'wb') as f:
        f.write(content)

def is_text_file(file_path):
    # A simple check to see if the file is text; you may want to improve this.
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except:
        return False

def traverse_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_text_file(file_path):
                print(f'Converting {file_path} to LF line endings...')
                convert_to_lf(file_path)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert_to_lf.py <directory>")
        sys.exit(1)

    directory_to_scan = sys.argv[1]
    if not os.path.isdir(directory_to_scan):
        print(f"Error: {directory_to_scan} is not a valid directory.")
        sys.exit(1)

    traverse_directory(directory_to_scan)
    print("Conversion complete!")