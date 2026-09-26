"""Тесты для application/bruteforce.py"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from subdomain_enum.application.bruteforce import bruteforce, load_wordlist


class TestBruteforce(unittest.TestCase):
    @patch("subdomain_enum.application.bruteforce.resolve_domain")
    def test_simple(self, mock_resolve):
        #Простейший случай: 3 слова, все резолвятся
        mock_resolve.side_effect = [
            ["1.1.1.1"],
            ["2.2.2.2"],
            ["3.3.3.3"],
        ]

        result = bruteforce("example.com", ["www", "mail", "api"])

        self.assertEqual(result, [
            ("www.example.com", ["1.1.1.1"]),
            ("mail.example.com", ["2.2.2.2"]),
            ("api.example.com", ["3.3.3.3"]),
        ])

    @patch("subdomain_enum.application.bruteforce.resolve_domain")
    def test_full_names(self, mock_resolve):
        #Полные имена формируются как word.domain
        mock_resolve.return_value = None

        bruteforce("example.com", ["www", "api"])

        called_names = [c.args[0] for c in mock_resolve.call_args_list]
        self.assertEqual(called_names, ["www.example.com", "api.example.com"])

    @patch("subdomain_enum.application.bruteforce.resolve_domain")
    def test_not_resolve(self, mock_resolve):
        #Часть слов не резолвится их ip = None
        mock_resolve.side_effect = [
            ["1.1.1.1"],
            None,
            ["3.3.3.3"],
        ]

        result = bruteforce("example.com", ["www", "mail", "api"])

        self.assertEqual(result, [
            ("www.example.com", ["1.1.1.1"]),
            ("mail.example.com", None),
            ("api.example.com", ["3.3.3.3"]),
        ])

    @patch("subdomain_enum.application.bruteforce.resolve_domain")
    def test_empty_words(self, mock_resolve):
        #Пустой список слов, пустой результат
        result = bruteforce("example.com", [])

        self.assertEqual(result, [])
        mock_resolve.assert_not_called()

    @patch("subdomain_enum.application.bruteforce.resolve_domain")
    def test_order_preserved(self, mock_resolve):
        #Порядок сохраняется, даже если резолв медленный
        mock_resolve.return_value = ["1.1.1.1"]

        result = bruteforce("example.com", ["c", "a", "b"])

        names = [name for name, _ in result]
        self.assertEqual(names, ["c.example.com", "a.example.com", "b.example.com"])

    @patch("subdomain_enum.application.bruteforce.resolve_domain")
    def test_timeout_passed(self, mock_resolve):
        #Параметр timeout доходит до resolve_domain
        mock_resolve.return_value = None

        bruteforce("example.com", ["www"], timeout=5.0)

        _, kwargs = mock_resolve.call_args
        self.assertEqual(kwargs.get("timeout"), 5.0)

    @patch("subdomain_enum.application.bruteforce.resolve_domain")
    def test_many_words(self, mock_resolve):
        #Работает с большим количеством слов
        mock_resolve.return_value = ["1.1.1.1"]

        words = [f"sub{i}" for i in range(100)]
        result = bruteforce("example.com", words, max_workers=10)

        self.assertEqual(len(result), 100)
        self.assertEqual(result[0][0], "sub0.example.com")
        self.assertEqual(result[-1][0], "sub99.example.com")

class TestLoadWordlist(unittest.TestCase):

    def _write_temp(self, content: str) -> str:
        #Вспомогательный метод: пишет content во временный файл, возвращает путь
        tmp = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".txt",
            delete=False,
        )
        tmp.write(content)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)  # удалит файл после теста
        return tmp.name

    def test_simple(self):
        #Обычный файл слова возвращаются в порядке появления
        path = self._write_temp("www\nmail\napi\n")
        self.assertEqual(load_wordlist(path), ["www", "mail", "api"])

    def test_skips_empty_lines(self):
        #Пустые строки пропускаются
        path = self._write_temp("www\n\n\nmail\n\n")
        self.assertEqual(load_wordlist(path), ["www", "mail"])

    def test_skips_comments(self):
        #Строки, начинающиеся с #, пропускаются
        path = self._write_temp("# comment\nwww\n# another\nmail\n")
        self.assertEqual(load_wordlist(path), ["www", "mail"])

    def test_strips_whitespace(self):
        #Пробелы и \\n убираются с концов строк
        path = self._write_temp("  www  \n\tmail\t\n")
        self.assertEqual(load_wordlist(path), ["www", "mail"])

    def test_empty_file(self):
        #Пустой файл пустой список
        path = self._write_temp("")
        self.assertEqual(load_wordlist(path), [])

    def test_only_comments_and_empty(self):
        #Только комментарии и пустые строки пустой список
        path = self._write_temp("# c1\n\n# c2\n\n")
        self.assertEqual(load_wordlist(path), [])

    def test_utf8(self):
        #Кириллица читается корректно
        path = self._write_temp("тест\nпример\n")
        self.assertEqual(load_wordlist(path), ["тест", "пример"])

    def test_file_not_found(self):
        #Несуществующий файл FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            load_wordlist("/this/path/definitely/does/not/exist.txt")

if __name__ == "__main__":
    unittest.main()