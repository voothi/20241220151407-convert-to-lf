import os
import sys
import unittest
import tempfile
import shutil

# Add the parent directory to the path so we can import the script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from convert_to_lf import (
    convert_to_lf,
    is_text_file,
    should_exclude,
    get_config,
    traverse_directory
)

class TestConvertToLF(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for file-based tests
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_convert_to_lf(self):
        test_file = os.path.join(self.test_dir, "test.txt")
        # Write CRLF text
        with open(test_file, 'wb') as f:
            f.write(b"Hello\r\nWorld\r\n")

        # Convert
        convert_to_lf(test_file)

        # Verify it converted to LF
        with open(test_file, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b"Hello\nWorld\n")

    def test_is_text_file(self):
        # Text file
        text_file = os.path.join(self.test_dir, "doc.md")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("Some standard text content")
        self.assertTrue(is_text_file(text_file))

        # Binary file (contains invalid UTF-8 sequences)
        binary_file = os.path.join(self.test_dir, "image.png")
        with open(binary_file, 'wb') as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\xff\xff")
        self.assertFalse(is_text_file(binary_file))

    def test_should_exclude_glob(self):
        patterns = [".*", "node_modules", "build", "*.log", "*.tmp"]

        # Directories/Files matching globs
        self.assertTrue(should_exclude(".git", patterns))
        self.assertTrue(should_exclude("node_modules", patterns))
        self.assertTrue(should_exclude("error.log", patterns))
        self.assertTrue(should_exclude("test.tmp", patterns))

        # Non-matching
        self.assertFalse(should_exclude("src", patterns))
        self.assertFalse(should_exclude("README.md", patterns))

    def test_should_exclude_regex(self):
        patterns = [r"re:^build_\d+$", r"re:^cache_[a-f0-9]{5}\.json$", "normal_glob"]

        # Matching regexes
        self.assertTrue(should_exclude("build_123", patterns))
        self.assertTrue(should_exclude("cache_a1b2c.json", patterns))
        self.assertTrue(should_exclude("normal_glob", patterns))

        # Non-matching
        self.assertFalse(should_exclude("build_abc", patterns))
        self.assertFalse(should_exclude("cache_g1g2g.json", patterns))
        self.assertFalse(should_exclude("build_", patterns))

    def test_traverse_directory_exclusions(self):
        # Setup nested structure in temp dir:
        # self.test_dir/
        # ├── .git/
        # │   └── config (should be ignored)
        # ├── node_modules/
        # │   └── index.js (should be ignored)
        # ├── build_99/
        # │   └── bundle.js (should be ignored due to regex build_\d+)
        # ├── src/
        # │   ├── main.py (should be converted)
        # │   └── test.log (should be ignored due to *.log)
        # └── normal.txt (should be converted)

        git_dir = os.path.join(self.test_dir, ".git")
        node_dir = os.path.join(self.test_dir, "node_modules")
        build_dir = os.path.join(self.test_dir, "build_99")
        src_dir = os.path.join(self.test_dir, "src")

        os.makedirs(git_dir)
        os.makedirs(node_dir)
        os.makedirs(build_dir)
        os.makedirs(src_dir)

        git_file = os.path.join(git_dir, "config")
        node_file = os.path.join(node_dir, "index.js")
        build_file = os.path.join(build_dir, "bundle.js")
        log_file = os.path.join(src_dir, "test.log")
        py_file = os.path.join(src_dir, "main.py")
        txt_file = os.path.join(self.test_dir, "normal.txt")

        for fpath in [git_file, node_file, build_file, log_file, py_file, txt_file]:
            with open(fpath, 'wb') as f:
                f.write(b"Line1\r\nLine2\r\n")

        # Run traversal with glob & regex exclusions
        exclude_dirs = [".*", "node_modules", r"re:^build_\d+$"]
        exclude_files = ["*.log"]
        traverse_directory(self.test_dir, exclude_dirs, exclude_files)

        # Verify excluded files are untouched (still CRLF)
        for fpath in [git_file, node_file, build_file, log_file]:
            with open(fpath, 'rb') as f:
                self.assertEqual(f.read(), b"Line1\r\nLine2\r\n")

        # Verify targeted files are converted to LF
        for fpath in [py_file, txt_file]:
            with open(fpath, 'rb') as f:
                self.assertEqual(f.read(), b"Line1\nLine2\n")

if __name__ == "__main__":
    unittest.main()
