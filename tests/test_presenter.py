"""Тесты для presentation/present.py"""

import json
import tempfile
import unittest
from pathlib import Path

from subdomain_enum.presentation.present import format_json, format_text, save_in_file


class TestFormatText(unittest.TestCase):
    def test_ip(self):
        result = [("www.example.com", ["1.2.3.4", "5.6.7.8"])]
        text = format_text(result)
        self.assertEqual(text, "www.example.com\t1.2.3.4, 5.6.7.8")

    def test_without_ip(self):
        result = [("api.example.com", None)]
        text = format_text(result)
        self.assertEqual(text, "api.example.com\tN/A")

    def test_multiple(self):
        result = [("www.example.com", ["1.2.3.4"]), ("api.example.com", None)]
        text = format_text(result)
        self.assertEqual(text, "www.example.com\t1.2.3.4\napi.example.com\tN/A")

    def test_none(self):
        self.assertEqual(format_text([]), "")


class TestFormatJson(unittest.TestCase):
    def test_ip(self):
        result = [("www.example.com", ["1.2.3.4"])]
        text = format_json(result)
        data = json.loads(text)
        self.assertEqual(data, [{"name": "www.example.com", "ip": ["1.2.3.4"]}])

    def test_without_ip(self):
        result = [("api.example.com", None)]
        text = format_json(result)
        data = json.loads(text)
        self.assertEqual(data, [{"name": "api.example.com", "ip": []}])

    def test_none(self):
        text = format_json([])
        data = json.loads(text)
        self.assertEqual(data, [])

    def test_valid_json(self):
        result = [("www.example.com", ["1.2.3.4"])]
        text = format_json(result)
        json.loads(text)


class TestSaveInFile(unittest.TestCase):
    def test_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.txt"
            save_in_file("hello", str(path))
            self.assertTrue(path.exists())
            self.assertEqual(path.read_text(encoding="utf-8"), "hello")

    def test_save_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.txt"
            save_in_file("привет", str(path))
            self.assertEqual(path.read_text(encoding="utf-8"), "привет")

    def test_save_invalid_path(self):
        with self.assertRaises(OSError):
            save_in_file("data", "/assfafafaqwer/file.txt")


if __name__ == "__main__":
    unittest.main()
