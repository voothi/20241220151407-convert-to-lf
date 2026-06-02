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
    traverse_directory,
    detect_encoding
)

class TestConvertToLF(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for file-based tests
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_detect_encoding(self):
        # UTF-8 without BOM
        utf8_file = os.path.join(self.test_dir, "utf8.txt")
        with open(utf8_file, "w", encoding="utf-8") as f:
            f.write("Hello World")
        self.assertEqual(detect_encoding(utf8_file), "utf-8")

        # UTF-8 with BOM
        utf8_bom_file = os.path.join(self.test_dir, "utf8_bom.txt")
        with open(utf8_bom_file, "w", encoding="utf-8-sig") as f:
            f.write("Hello World")
        self.assertEqual(detect_encoding(utf8_bom_file), "utf-8-sig")

        # UTF-16 LE
        utf16le_file = os.path.join(self.test_dir, "utf16le.txt")
        with open(utf16le_file, "w", encoding="utf-16-le") as f:
            f.write("\ufeffHello World") # writing BOM explicitly
        self.assertEqual(detect_encoding(utf16le_file), "utf-16-le")

        # UTF-16 BE
        utf16be_file = os.path.join(self.test_dir, "utf16be.txt")
        with open(utf16be_file, "w", encoding="utf-16-be") as f:
            f.write("\ufeffHello World") # writing BOM explicitly
        self.assertEqual(detect_encoding(utf16be_file), "utf-16-be")

        # CP1252 (legacy ANSI)
        cp1252_file = os.path.join(self.test_dir, "cp1252.txt")
        with open(cp1252_file, "wb") as f:
            f.write(b"Hello \xe9 (e with acute)")
        self.assertEqual(detect_encoding(cp1252_file), "cp1252")

        # Binary file
        binary_file = os.path.join(self.test_dir, "image.png")
        with open(binary_file, 'wb') as f:
            f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\xff\xff")
        self.assertIsNone(detect_encoding(binary_file))

    def test_convert_to_lf(self):
        # Test UTF-8 conversion
        utf8_file = os.path.join(self.test_dir, "test_utf8.txt")
        with open(utf8_file, 'wb') as f:
            f.write(b"Hello\r\nWorld\r\n")
        self.assertEqual(convert_to_lf(utf8_file), (True, False))
        with open(utf8_file, 'rb') as f:
            self.assertEqual(f.read(), b"Hello\nWorld\n")

        # Test UTF-16 LE conversion (crucial check for correct byte-level handling)
        utf16le_file = os.path.join(self.test_dir, "test_utf16le.txt")
        with open(utf16le_file, 'w', encoding='utf-16-le') as f:
            f.write("\ufeffHello\r\nWorld\r\n")
        self.assertEqual(convert_to_lf(utf16le_file), (True, False))
        with open(utf16le_file, 'r', encoding='utf-16-le') as f:
            self.assertEqual(f.read(), "\ufeffHello\nWorld\n")

        # Test CP1252 conversion
        cp1252_file = os.path.join(self.test_dir, "test_cp1252.txt")
        with open(cp1252_file, 'wb') as f:
            f.write(b"Hello\r\n\xe9\r\n")
        self.assertEqual(convert_to_lf(cp1252_file), (True, False))
        with open(cp1252_file, 'rb') as f:
            self.assertEqual(f.read(), b"Hello\n\xe9\n")

    def test_convert_to_lf_strip_bom(self):
        # 1. UTF-8 with BOM and CRLF, strip_bom=True -> writes as standard UTF-8 (no BOM), LF
        utf8_bom_crlf = os.path.join(self.test_dir, "bom_crlf.txt")
        with open(utf8_bom_crlf, 'wb') as f:
            f.write(b"\xef\xbb\xbfHello\r\nWorld\r\n")
        
        self.assertEqual(convert_to_lf(utf8_bom_crlf, strip_bom=True), (True, True))
        with open(utf8_bom_crlf, 'rb') as f:
            self.assertEqual(f.read(), b"Hello\nWorld\n")

        # 2. UTF-8 with BOM and LF, strip_bom=True -> writes as standard UTF-8 (no BOM), LF
        utf8_bom_lf = os.path.join(self.test_dir, "bom_lf.txt")
        with open(utf8_bom_lf, 'wb') as f:
            f.write(b"\xef\xbb\xbfHello\nWorld\n")
        
        self.assertEqual(convert_to_lf(utf8_bom_lf, strip_bom=True), (False, True))
        with open(utf8_bom_lf, 'rb') as f:
            self.assertEqual(f.read(), b"Hello\nWorld\n")

        # 3. UTF-8 with BOM and CRLF, strip_bom=False -> retains BOM, LF
        utf8_bom_keep = os.path.join(self.test_dir, "bom_keep.txt")
        with open(utf8_bom_keep, 'wb') as f:
            f.write(b"\xef\xbb\xbfHello\r\nWorld\r\n")
        
        self.assertEqual(convert_to_lf(utf8_bom_keep, strip_bom=False), (True, False))
        with open(utf8_bom_keep, 'rb') as f:
            self.assertEqual(f.read(), b"\xef\xbb\xbfHello\nWorld\n")

    def test_traverse_directory_listing_options(self):
        import io
        from unittest.mock import patch

        # Create files with different states:
        # - converted.txt (has CRLF, will convert)
        # - unchanged.txt (has LF, won't convert)
        # - binary.png (binary, skipped)
        
        converted_file = os.path.join(self.test_dir, "converted.txt")
        unchanged_file = os.path.join(self.test_dir, "unchanged.txt")
        binary_file = os.path.join(self.test_dir, "binary.png")

        def reset_files():
            with open(converted_file, 'wb') as f:
                f.write(b"Line1\r\nLine2\r\n")
            with open(unchanged_file, 'wb') as f:
                f.write(b"Line1\nLine2\n")
            with open(binary_file, 'wb') as f:
                f.write(b"\x89PNG\r\n\x1a\n\x00")

        # Test list_mode="changed" (default)
        reset_files()
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            traverse_directory(self.test_dir, [], [], list_mode="changed", auto_confirm=True)
            output = fake_out.getvalue()
            self.assertIn("[✓] Converted", output)
            self.assertNotIn("[-] Unchanged", output)
            self.assertNotIn("[S] Skipped/Binary", output)

        # Test list_mode="all"
        reset_files()
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            traverse_directory(self.test_dir, [], [], list_mode="all", auto_confirm=True)
            output = fake_out.getvalue()
            self.assertIn("[✓] Converted", output)
            self.assertIn("[-] Unchanged", output)
            self.assertIn("[S] Skipped/Binary", output)

        # Test list_mode="none"
        reset_files()
        with patch('sys.stdout', new=io.StringIO()) as fake_out:
            traverse_directory(self.test_dir, [], [], list_mode="none", auto_confirm=True)
            output = fake_out.getvalue()
            self.assertNotIn("[✓] Converted", output)
            self.assertNotIn("[-] Unchanged", output)
            self.assertNotIn("[S] Skipped/Binary", output)
            self.assertIn("Total files scanned:", output) # summary is still printed

    def test_is_text_file(self):
        # Text file
        text_file = os.path.join(self.test_dir, "doc.md")
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("Some standard text content")
        self.assertTrue(is_text_file(text_file))

        # Binary file
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
        traverse_directory(self.test_dir, exclude_dirs, exclude_files, auto_confirm=True)

        # Verify excluded files are untouched (still CRLF)
        for fpath in [git_file, node_file, build_file, log_file]:
            with open(fpath, 'rb') as f:
                self.assertEqual(f.read(), b"Line1\r\nLine2\r\n")

        # Verify targeted files are converted to LF
        for fpath in [py_file, txt_file]:
            with open(fpath, 'rb') as f:
                self.assertEqual(f.read(), b"Line1\nLine2\n")

    def test_get_config_options(self):
        # Create a temporary config.ini with Settings
        config_path = os.path.join(self.test_dir, "test_config.ini")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("[Settings]\nstrip_bom = true\nlist = all\nauto_confirm = true\n")
            
        config = get_config(config_path)
        self.assertTrue(config["strip_bom"])
        self.assertEqual(config["list"], "all")
        self.assertTrue(config["auto_confirm"])

    def test_traverse_directory_interactive_confirm_yes(self):
        from unittest.mock import patch
        import io
        
        # File needs conversion
        test_file = os.path.join(self.test_dir, "to_convert.txt")
        with open(test_file, 'wb') as f:
            f.write(b"Hello\r\nWorld\r\n")
            
        # Mock input to return 'y' (yes)
        with patch('builtins.input', return_value='y'), patch('sys.stdout', new=io.StringIO()):
            res = traverse_directory(self.test_dir, [], [], auto_confirm=False)
            self.assertTrue(res)
            
        with open(test_file, 'rb') as f:
            self.assertEqual(f.read(), b"Hello\nWorld\n")

    def test_traverse_directory_interactive_confirm_no(self):
        from unittest.mock import patch
        import io
        
        # File needs conversion
        test_file = os.path.join(self.test_dir, "to_convert.txt")
        with open(test_file, 'wb') as f:
            f.write(b"Hello\r\nWorld\r\n")
            
        # Mock input to return 'n' (no)
        with patch('builtins.input', return_value='n'), patch('sys.stdout', new=io.StringIO()):
            res = traverse_directory(self.test_dir, [], [], auto_confirm=False)
            self.assertFalse(res)
            
        # Verify file is UNTOUCHED (still has CRLF)
        with open(test_file, 'rb') as f:
            self.assertEqual(f.read(), b"Hello\r\nWorld\r\n")

if __name__ == "__main__":
    unittest.main()
