from src.decorators import (
	confirm_action,
	create_cacher,
	handle_db_errors,
	log_time,
)

SUPPORTED_TYPES = {"int", "str", "bool"}

_select_cache = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
	"""Функция создаёт таблицу и возвращает обновленные метаданные"""
	if table_name in metadata:
		print(f"Ошибка: Таблица {table_name} уже существует")
		return metadata

	parsed_columns = []
	column_names = set()

	for column in columns:
		if column.count(":") != 1:
			print(f"1. Некорректное значение {column}. Попробуйте сначала.")
			return metadata

		column_name, column_type = column.split(":", 1)

		if not column_name or column_type not in SUPPORTED_TYPES:
			print(f"2. Некорректное значение: {column}. Попробуйте сначала.")
			return metadata

		normalized_name = column_name.lower()

		if normalized_name in column_names:
			print(f"3. Некорректное значение: {column}. Попробуйте сначала.")
			return metadata

		column_names.add(normalized_name)

		if normalized_name == "id":
			if column_type != "int":
				print(f"4. Некорректное значение: {column}. Попробуйте сначала.")
				return metadata

			parsed_columns.append({"name": "ID", "type": "int"})

		else:
			parsed_columns.append({"name": column_name, "type": column_type})

	has_id = any(column["name"] == "ID" for column in parsed_columns)

	if not has_id:
		parsed_columns.insert(0,{"name": "ID", "type": "int"})
	else:
		parsed_columns.sort(key = lambda column: column["name"] != "ID")

	updated_metadata = metadata.copy()
	updated_metadata[table_name] = {"columns": parsed_columns}
	columns_text = ", ".join(
    f'{column["name"]}:{column["type"]}'
    for column in parsed_columns
)
	print(
		f'Таблица "{table_name}" успешно создана '
		f"со столбцами: {columns_text}"
	)

	return updated_metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу и возвращает обновлённые метаданные."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata
    updated_metadata = metadata.copy()
    del updated_metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return updated_metadata


def list_tables(metadata):
    """Выводит список существующих таблиц."""
    if not metadata:
        print("В базе данных нет таблиц.")
        return
    for table_name in metadata:
        print(f"- {table_name}")


def is_valid_type(value, expected_type):
    """Проверяет соответствие Python-значения типу столбца (int, str, bool)"""
    if expected_type == "int":
        return type(value) is int
    if expected_type == "str":
        return type(value) is str
    if expected_type == "bool":
        return type(value) is bool
    return False


def get_column_type(metadata, table_name, column_name):
    """Возвращает тип столбца таблицы"""
    columns = metadata[table_name]["columns"]
    for column in columns:
        if column["name"] == column_name:
            return column["type"]
    return None


@handle_db_errors
def validate_clause(metadata, table_name, clause):
    """Проверяет столбец и тип значения условия"""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует')
        return False
    column_name, value = next(iter(clause.items()))
    column_type = get_column_type(metadata, table_name, column_name,)
    if column_type is None:
        print(
              f'Ошибка: Столбец "{column_name}" '
              f'не существует в таблице "{table_name}"'
             )
        return False
    if not is_valid_type(value, column_type):
        print(
              f'Ошибка: Значение столбца "{column_name}" '
              f"должно иметь тип {column_type}"
             )
        return False
    return True


# handle_db_errors -> log_time -> insert
@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data = None):
    """Добавляет новую запись в таблицу"""

    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует')
        return None

    if table_data is None:
        table_data = []

    columns = metadata[table_name]["columns"]
    user_columns = [column for column in columns
                    if column["name"] != "ID"
                    ]
    if len(values) != len(user_columns):
        print(
              "Ошибка: Количество значений не соответствует "
              "количеству столбцов."
              )
        return None

    for column, value in zip(user_columns, values):
        expected_type = column["type"]
        if not is_valid_type(value, expected_type):
            print(
                  f'Ошибка: Значение для столбца "{column["name"]}" '
                  f" должно иметь тип {expected_type}"
                 )
            return None

    if table_data:
        new_id = max(row["ID"] for row in table_data) + 1
    else:
        new_id = 1

    new_row = {"ID": new_id}

    for column, value in zip(user_columns, values):
        new_row[column["name"]] = value

    updated_data = table_data.copy()
    updated_data.append(new_row)

    print(
          f'Запись с ID={new_id} успешно добавлена '
          f'в таблицу "{table_name}"'
         )
    return updated_data


@handle_db_errors
@log_time
def select(table_data, where_clause = None):
    """Возвращает записи с использованием кэша"""
    cache_key = (repr(table_data), repr(where_clause))
    def get_result():
        if where_clause is None:
            return table_data
        column_name, expected_value = next(iter(where_clause.items()))
        return [row for row in table_data
                if row.get(column_name) == expected_value
               ]
    return _select_cache(cache_key, get_result)


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Обновляет записи по условию"""
    where_column, where_value = next(iter(where_clause.items()))
    updated_data = [row.copy() for row in table_data]
    updated_ids = []

    for row in updated_data:
        if row.get(where_column) == where_value:
            for column_name, new_value in set_clause.items():
                row[column_name] = new_value
            updated_ids.append(row["ID"])

    return updated_data, updated_ids


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    """Удаляет записи по условию"""
    column_name, expected_value = next(iter(where_clause.items()))
    deleted_ids = [row["ID"] for row in table_data
                   if row.get(column_name) == expected_value
                   ]
    updated_data = [row for row in table_data
                    if row.get(column_name) != expected_value
                    ]
    return updated_data, deleted_ids
