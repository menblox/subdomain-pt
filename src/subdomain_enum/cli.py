"""CLI-интерфейс утилиты поиска поддоменов"""

import argparse
import logging
import sys

from subdomain_enum.application.bruteforce import load_wordlist
from subdomain_enum.application.unification import unification_names
from subdomain_enum.application.wildcard import detect_wildcard
from subdomain_enum.infrastructure.ctlogs import fetch_subdomains
from subdomain_enum.infrastructure.ctlogs_ru import fetch_subdomains_ru
from subdomain_enum.presentation.present import format_json, format_text, save_in_file

logger = logging.getLogger(__name__)

def _setup_logging(level: str) -> None:
    #Настройки logging
    numeric_level = getattr(logging, level.upper(), logging.WARNING)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr
    )

def _add_common_args(parser: argparse.ArgumentParser) -> None:
    #Добавляет общие аргументы, которые есть у всех subcommands
    parser.add_argument(
        "domain",
        help="Целевой домен"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=2.0,
        help="Таймаут DNS-запроса в секундах"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=30,
        help="Количество параллельных потоков"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Вывод результата в JSON"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Сохранить результат в файл"
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Уровень логирования"
    )
    parser.add_argument(
        "--log-file",
        default=None,
        help="Файл для записи логов (по умолчанию: stderr)"
    )

def _add_wordlist_arg(parser: argparse.ArgumentParser) -> None:
    #Добавляет аргумент --wordlist
    parser.add_argument(
        "-w", "--wordlist",
        default="wordlists/subdomains-5000.txt",
        help="Путь к файлу словарю"
    )

def _setup_logging(level: str, log_file: str | None = None) -> None:
    handlers: list[logging.Handler] = []

    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    else:
        handlers.append(logging.StreamHandler(sys.stderr))

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    #Парсит аргументы командной строки
    parser = argparse.ArgumentParser(
        prog="subdomain_pt",
        description="CLI утилита для поиска поддоменов"
    )

    subparser = parser.add_subparsers(dest="command", required=True)

    # ==================================
    # crt: глобальные CT логи
    # ==================================
    ctr_parser = subparser.add_parser(
        "crt",
        help="Поиск через глобальные CT логи"
    )
    _add_common_args(ctr_parser)

    # ==================================
    # crt-ru: РФ CT логи
    # ==================================
    crt_ru_parser = subparser.add_parser(
        "crt-ru",
        help="Поиск через российские CT логи"
    )
    _add_common_args(crt_ru_parser)

    # ==================================
    # brute: брутфорс по словарю
    # ==================================
    brute_parser = subparser.add_parser(
        "brute",
        help="Брутфорс по словарю"
    )
    _add_common_args(brute_parser)
    _add_wordlist_arg(brute_parser)

    # ==================================
    # unif все источники
    # ==================================
    unif_parser = subparser.add_parser(
        "unif",
        help="Все источники: глобальные + российские CT + брутфорс"
    )
    _add_common_args(unif_parser)
    _add_wordlist_arg(unif_parser)

    return parser.parse_args(argv)

def _collect_names(args: argparse.Namespace) -> list[str]:
    #Собирает имена из выбранных источников
    names: set[str] = set()

    if args.command in ("crt", "unif"):
        logger.info("Запрос глобальных CT логов")
        global_names = fetch_subdomains(args.domain, args.timeout)
        logger.info("Глобальные CT логи: %d имен", len(global_names))
        names.update(global_names)

    if args.command in ("crt-ru", "unif"):
        logger.info("Запрос рф CT логов")
        ru_names = fetch_subdomains_ru(args.domain, args.timeout)
        logger.info("РФ CT логи: %d имен", len(ru_names))
        names.update(ru_names)

    if args.command in ("brute", "unif"):
        logger.info("Загружаю словарь: %s", args.wordlist)
        words = load_wordlist(args.wordlist)
        logger.info("Слов в словаре: %d", len(words))
        names.update(f"{word}.{args.domain}" for word in words)

    return sorted(names)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _setup_logging(args.log_level, args.log_file)

    try:
        names = _collect_names(args)
    except FileNotFoundError:
        logger.error("Файл словаря не найден: %s", args.wordlist)
        return 1
    except PermissionError:
        logger.error("Нет доступа к файлу: %s", args.wordlist)
        return 1

    logger.info("Всего имён: %d", len(names))

    if not names:
        logger.warning("Не найдено ни одного имени")
        return 0

    logger.info("Проверка wildcard...")
    wildcard_ip = detect_wildcard(args.domain, args.timeout)
    if wildcard_ip:
        logger.warning("Обнаружен wildcard: %s", wildcard_ip)

    logger.info("Резолв %d имён...", len(names))
    results = unification_names(
        names,
        timeout=args.timeout,
        max_workers=args.workers,
        wildcard_ip=wildcard_ip
    )

    output = format_json(results) if args.json else format_text(results)

    if args.output:
        try:
            save_in_file(output, args.output)
            logger.info("Результат сохранён в %s", args.output)
        except OSError as e:
            logger.error("Ошибка записи в файл: %s", e)
            return 1
    else:
        print(output)

    found = sum(1 for _, ip in results if ip)
    logger.info("Найдено: %d из %d", found, len(results))

    return 0