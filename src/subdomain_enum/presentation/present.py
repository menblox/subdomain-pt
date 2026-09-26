"""Форматирование и вывод результатов"""

import json


def format_text(results: list[tuple[str, list[str] | None]]) -> str:
    # форматирует результаты в текстовый вид
    lines: list[str] = []

    for name, ip in results:
        if ip:
            lines.append(f"{name}\t{', '.join(ip)}")
        else:
            lines.append(f"{name}\tN/A")

    return "\n".join(lines)


def format_json(results: list[tuple[str, list[str] | None]]) -> str:
    # Форматирует результаты в JSON
    data = []

    for name, ip in results:
        data.append({"name": name, "ip": ip if ip else []})

    return json.dumps(data, indent=2, ensure_ascii=False)


def save_in_file(content: str, path: str) -> None:
    # Сохраняет строку в файл
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
