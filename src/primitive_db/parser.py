import json
import re


def parse_value(value_text):
    """Преобразует текстовое значение в Python-объект"""
    try:
        return json.loads(value_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"Некорректное значение: {value_text}") from error


def parse_condition(condition_text):
    """Преобразует 'age = 28' в {'age': 28}"""
    parts = condition_text.split("=", 1)
    if len(parts) != 2:
        raise ValueError(f"Некорректное условие: {condition_text}")
    column_name = parts[0].strip()
    value_text = parts[1].strip()
    if not column_name or not value_text:
        raise ValueError(f"Некорректное условие: {condition_text}")
    value = parse_value(value_text)
    return {column_name: value}


def parse_insert(user_input):
    """Разбирает команду insert"""
    pattern = (r"^insert\s+into\s+(\w+)\s+"
               r"values\s*\((.*)\)\s*$"
              )
    match = re.match(pattern, user_input, flags = re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный синтаксис insert")
    table_name = match.group(1)
    values_text = match.group(2)
    try:
        values = json.loads(f"[{values_text}]")
    except json.JSONDecodeError as error:
        raise ValueError("Некорректные значения команды insert") from error
    return table_name, values


def parse_select(user_input):
    """Разбирает команду select"""
    pattern = (r"^select\s+from\s+(\w+)"
               r"(?:\s+where\s+(.+))?\s*$"
              )
    match = re.match(pattern, user_input, flags = re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный синтаксис select")
    table_name = match.group(1)
    where_text = match.group(2)
    where_clause = None
    if where_text:
        where_clause = parse_condition(where_text)
    return table_name, where_clause


def parse_update(user_input):
    """Разбирает команду update"""
    pattern = (r"^update\s+(\w+)\s+set\s+(.+?)"
               r"\s+where\s+(.+)\s*$"
              )
    match = re.match(pattern, user_input, flags = re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный синтаксис update")
    table_name = match.group(1)
    set_clause = parse_condition(match.group(2))
    where_clause = parse_condition(match.group(3))
    return table_name, set_clause, where_clause


def parse_delete(user_input):
    """Разбирает команду delete"""
    pattern = (r"^delete\s+from\s+(\w+)"
               r"\s+where\s+(.+)\s*$"
              )
    match = re.match(pattern, user_input, flags = re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный синтаксис delete")
    table_name = match.group(1)
    where_clause = parse_condition(match.group(2))
    return table_name, where_clause


def parse_info(user_input):
    """Разбирает команду info"""
    pattern = r"^info\s+(\w+)\s*$"
    match = re.match(pattern, user_input, flags = re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный синтаксис info")
    return match.group(1)
