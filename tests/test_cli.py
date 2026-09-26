"""Тесты для cli.py"""

import io
import unittest
from contextlib import redirect_stderr
from unittest import TestCase

from subdomain_enum.cli import parse_args


class TestParseArgsCommands(TestCase):
    #Парсинг subcommands

    def test_crt_command(self):
        args = parse_args(["crt", "example.com"])
        self.assertEqual(args.command, "crt")
        self.assertEqual(args.domain, "example.com")

    def test_crt_ru_command(self):
        args = parse_args(["crt-ru", "yandex.ru"])
        self.assertEqual(args.command, "crt-ru")
        self.assertEqual(args.domain, "yandex.ru")

    def test_brute_command(self):
        args = parse_args(["brute", "example.com"])
        self.assertEqual(args.command, "brute")
        self.assertEqual(args.domain, "example.com")

    def test_unif_command(self):
        args = parse_args(["unif", "example.com"])
        self.assertEqual(args.command, "unif")
        self.assertEqual(args.domain, "example.com")

    def test_unknown_command(self):
        #Неизвестная команда SystemExit
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                parse_args(["unknown", "example.com"])

    def test_no_command(self):
        #Без команды SystemExit
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                parse_args([])

    def test_no_domain(self):
        #Команда без домена SystemExit
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                parse_args(["crt"])


class TestParseArgsDefaults(TestCase):
    #Значения по умолчанию для общих аргументов

    def test_timeout_default(self):
        args = parse_args(["crt", "example.com"])
        self.assertEqual(args.timeout, 2.0)

    def test_workers_default(self):
        args = parse_args(["crt", "example.com"])
        self.assertEqual(args.workers, 30)

    def test_json_default_false(self):
        args = parse_args(["crt", "example.com"])
        self.assertFalse(args.json)

    def test_output_default_none(self):
        args = parse_args(["crt", "example.com"])
        self.assertIsNone(args.output)

    def test_log_level_default(self):
        args = parse_args(["crt", "example.com"])
        self.assertEqual(args.log_level, "WARNING")

    def test_log_file_default_none(self):
        args = parse_args(["crt", "example.com"])
        self.assertIsNone(args.log_file)


class TestParseArgsFlags(TestCase):
    #Парсинг флагов

    def test_timeout_custom(self):
        args = parse_args(["crt", "example.com", "--timeout", "5.5"])
        self.assertEqual(args.timeout, 5.5)

    def test_timeout_short(self):
        args = parse_args(["crt", "example.com", "-t", "1.0"])
        self.assertEqual(args.timeout, 1.0)

    def test_workers_custom(self):
        args = parse_args(["crt", "example.com", "--workers", "50"])
        self.assertEqual(args.workers, 50)

    def test_json_flag(self):
        args = parse_args(["crt", "example.com", "--json"])
        self.assertTrue(args.json)

    def test_output(self):
        args = parse_args(["crt", "example.com", "--output", "result.txt"])
        self.assertEqual(args.output, "result.txt")

    def test_log_level_info(self):
        args = parse_args(["crt", "example.com", "--log-level", "INFO"])
        self.assertEqual(args.log_level, "INFO")

    def test_log_level_debug(self):
        args = parse_args(["crt", "example.com", "--log-level", "DEBUG"])
        self.assertEqual(args.log_level, "DEBUG")

    def test_log_level_invalid(self):
        #Неверный уровень SystemExit
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                parse_args(["crt", "example.com", "--log-level", "VERBOSE"])

    def test_log_file(self):
        args = parse_args(["crt", "example.com", "--log-file", "app.log"])
        self.assertEqual(args.log_file, "app.log")

    def test_combined_flags(self):
        args = parse_args([
            "crt", "example.com",
            "--timeout", "3.0",
            "--workers", "20",
            "--json",
            "--output", "out.json",
            "--log-level", "INFO",
            "--log-file", "app.log",
        ])
        self.assertEqual(args.timeout, 3.0)
        self.assertEqual(args.workers, 20)
        self.assertTrue(args.json)
        self.assertEqual(args.output, "out.json")
        self.assertEqual(args.log_level, "INFO")
        self.assertEqual(args.log_file, "app.log")


class TestParseArgsWordlist(TestCase):
    #Парсинг --wordlist для brute и unif

    def test_brute_has_wordlist(self):
        args = parse_args(["brute", "example.com"])
        self.assertTrue(hasattr(args, "wordlist"))

    def test_unif_has_wordlist(self):
        args = parse_args(["unif", "example.com"])
        self.assertTrue(hasattr(args, "wordlist"))

    def test_wordlist_default(self):
        args = parse_args(["brute", "example.com"])
        self.assertEqual(args.wordlist, "wordlists/subdomains-5000.txt")

    def test_wordlist_custom(self):
        args = parse_args(["brute", "example.com", "-w", "custom.txt"])
        self.assertEqual(args.wordlist, "custom.txt")

    def test_wordlist_long_flag(self):
        args = parse_args(["brute", "example.com", "--wordlist", "custom.txt"])
        self.assertEqual(args.wordlist, "custom.txt")

    def test_crt_no_wordlist_attribute(self):
        #У команды crt нет атрибута wordlist
        args = parse_args(["crt", "example.com"])
        # wordlist не определён для crt, поэтому обращение к нему AttributeError
        self.assertFalse(hasattr(args, "wordlist"))

    def test_crt_ru_no_wordlist_attribute(self):
        args = parse_args(["crt-ru", "yandex.ru"])
        self.assertFalse(hasattr(args, "wordlist"))


class TestParseArgsHelp(TestCase):
    #--help работает для всех команд

    def test_help_top_level(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                parse_args(["--help"])

    def test_help_crt(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                parse_args(["crt", "--help"])

    def test_help_brute(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(io.StringIO()):
                parse_args(["brute", "--help"])


if __name__ == "__main__":
    unittest.main()