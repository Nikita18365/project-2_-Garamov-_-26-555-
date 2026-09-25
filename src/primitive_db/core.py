SUPPORTED_TYPES = {"int", "str", "bool"}


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
