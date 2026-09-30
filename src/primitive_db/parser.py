import json


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
    prefix = "insert into "
    command = user_input.strip()
    if not command.lower().startswith(prefix):
        raise ValueError("Некорректный синтаксис insert")
    remainder = command[len(prefix):]
    marker = " values "
    marker_position = remainder.lower().find(marker)
    if marker_position == -1:
        raise ValueError("Некорректный синтаксис insert")
    table_name = remainder[:marker_position].strip()
    values_part = remainder[marker_position + len(marker):].strip()
    if (not table_name
        or not values_part.startswith("(")
        or not values_part.endswith(")")
       ):
        raise ValueError("Некорректный синтаксис insert")
    values_text = values_part[1:-1]
    try:
        values = json.loads(f"[{values_text}]")
    except json.JSONDecodeError as error:
        raise ValueError("Некорректные значения команды insert.") from error
    return table_name, values


def parse_select(user_input):
    """Разбирает команду select"""
    prefix = "select from "
    command = user_input.strip()
    if not command.lower().startswith(prefix):
        raise ValueError("Некорректный синтаксис select")
    remainder = command[len(prefix):].strip()
    if not remainder:
        raise ValueError("Некорректный синтаксис select")
    marker = " where "
    marker_position = remainder.lower().find(marker)
    if marker_position == -1:
        table_name = remainder.strip()
        if not table_name:
            raise ValueError("Некорректный синтаксис select")
        return table_name, None
    table_name = remainder[:marker_position].strip()
    condition_text = remainder[marker_position + len(marker):].strip()
    if not table_name or not condition_text:
        raise ValueError("Некорректный синтаксис select")
    where_clause = parse_condition(condition_text)
    return table_name, where_clause


def parse_update(user_input):
    """Разбирает команду update"""
    prefix = "update "
    command = user_input.strip()
    if not command.lower().startswith(prefix):
        raise ValueError("Некорректный синтаксис update")
    remainder = command[len(prefix):].strip()
    set_marker = " set "
    set_position = remainder.lower().find(set_marker)
    if set_position == -1:
        raise ValueError("Некорректный синтаксис update")
    table_name = remainder[:set_position].strip()
    after_set = remainder[set_position + len(set_marker):].strip()
    where_marker = " where "
    where_position = after_set.lower().find(where_marker)
    if where_position == -1:
        raise ValueError("Некорректный синтаксис update")
    set_text = after_set[:where_position].strip()
    where_text = after_set[where_position + len(where_marker):].strip()
    if (not table_name
        or not set_text
        or not where_text
       ):
        raise ValueError("Некорректный синтаксис update")
    set_clause = parse_condition(set_text)
    where_clause = parse_condition(where_text)
    return table_name, set_clause, where_clause



def parse_delete(user_input):
    """Разбирает команду delete"""
    prefix = "delete from "
    command = user_input.strip()
    if not command.lower().startswith(prefix):
        raise ValueError("Некорректный синтаксис delete")
    remainder = command[len(prefix):].strip()
    where_marker = " where "
    where_position = remainder.lower().find(where_marker)
    if where_position == -1:
        raise ValueError("Некорректный синтаксис delete")
    table_name = remainder[:where_position].strip()
    where_text = remainder[where_position + len(where_marker):].strip()
    if not table_name or not where_text:
        raise ValueError("Некорректный синтаксис delete")
    where_clause = parse_condition(where_text)
    return table_name, where_clause


def parse_info(user_input):
    """Разбирает команду info"""
    prefix = "info "
    command = user_input.strip()
    if not command.lower().startswith(prefix):
        raise ValueError("Некорректный синтаксис info")
    table_name = command[len(prefix):].strip()
    if not table_name:
        raise ValueError("Некорректный синтаксис info")
    if " " in table_name:
        raise ValueError("Некорректный синтаксис info")
    return table_name
