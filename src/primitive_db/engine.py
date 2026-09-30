import shlex

import prompt
from prettytable import PrettyTable

from src.primitive_db.constants import META_FILE
from src.primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
    validate_clause,
)
from src.primitive_db.parser import (
    parse_delete,
    parse_info,
    parse_insert,
    parse_select,
    parse_update,
)
from src.primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Выводит справку по командам"""
    print("\n***Операции с данными***")
    print("\nУправление таблицами:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
        )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nCRUD-операции:")
    print(
        "<command> insert into <имя_таблицы> "
        "values (<значение1>, <значение2>, ...) - создать запись"
        )
    print(
        "<command> select from <имя_таблицы> "
        "where <столбец> = <значение> - прочитать записи"
        )
    print(
        "<command> select from <имя_таблицы> "
        "- прочитать все записи"
        )
    print(
        "<command> update <имя_таблицы> "
        "set <столбец> = <значение> "
        "where <столбец> = <значение> - обновить записи"
        )
    print(
        "<command> delete from <имя_таблицы> "
        "where <столбец> = <значение> - удалить записи"
        )
    print(
        "<command> info <имя_таблицы> "
        "- вывести информацию о таблице"
        )

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_table(metadata, table_name, rows):
    """Красиво выводит записи таблицы"""
    columns = metadata[table_name]["columns"]
    column_names = [column["name"] for column in columns]
    table = PrettyTable()
    table.field_names = column_names
    for row in rows:
        table.add_row([row.get(column_name)
        for column_name in column_names
                       ]
                      )
    print(table)


def print_info(metadata, table_name, table_data):
    """Выводит информацию о таблице"""
    columns = metadata[table_name]["columns"]
    columns_text = ", ".join(
        f'{column["name"]}:{column["type"]}'
        for column in columns
                             )
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns_text}")
    print(f"Количество записей: {len(table_data)}")


def run():
    """Запускает основной цикл базы данных"""
    print_help()
    while True:
        metadata = load_metadata(META_FILE)
        user_input = prompt.string(">>>Введите команду: ")
        try:
            args = shlex.split(user_input)
        except ValueError:
            print(
                  f"Некорректное значение: {user_input}. "
                  "Попробуйте снова"
                 )
            continue

        if not args:
            continue

        command = args[0].lower()

        try:
            if command == "create_table":
                if len(args) < 3:
                    raise ValueError("Для создания таблицы нужны имя и столбцы")

                table_name = args[1]
                columns = args[2:]

                updated_metadata = create_table(metadata,
                                                table_name,
                                                columns
                                                )
                if updated_metadata is None:
                    continue
                if updated_metadata != metadata:
                    save_metadata(META_FILE,
                                  updated_metadata
                                  )
                    save_table_data(table_name, [])

            elif command == "drop_table":
                if len(args) != 2:
                    raise ValueError("Некорректный синтаксис drop_table")

                table_name = args[1]

                updated_metadata = drop_table(metadata,
                                              table_name
                                              )
                # Теперь у нас будет обработчик соглашений (y/n)
                if updated_metadata is None:
                    continue
                if updated_metadata != metadata:
                    save_metadata(META_FILE, updated_metadata)
                    delete_table_data(table_name)

            elif command == "list_tables":
                list_tables(metadata)

            elif command == "insert":
                table_name, values = parse_insert(user_input)

                table_data = load_table_data(table_name)

                updated_data = insert(metadata,
                                      table_name,
                                      values,
                                      table_data
                                      )

                if updated_data is not None:
                    save_table_data(table_name,
                                    updated_data
                                    )

            elif command == "select":
                table_name, where_clause = parse_select(user_input)

                if table_name not in metadata:
                    print(
                          f'Ошибка: Таблица "{table_name}" '
                          "не существует"
                         )
                    continue

                if (
                    where_clause is not None
                    and not validate_clause(metadata,
                                            table_name,
                                            where_clause
                                            )
                    ):
                    continue

                table_data = load_table_data(table_name)

                rows = select(table_data, where_clause)
                # На случай если handle_db_errors поймает исключение
                if rows is None:
                    continue
                print_table(metadata,
                            table_name,
                            rows
                            )

            elif command == "update":
                (table_name,
                 set_clause,
                 where_clause
                 ) = parse_update(user_input)

                if not validate_clause(metadata,
                                       table_name,
                                       set_clause
                                       ):
                    continue

                if not validate_clause(metadata,
                                       table_name,
                                       where_clause
                                       ):
                    continue

                table_data = load_table_data(table_name)

                update_result = update(table_data,
                                       set_clause,
                                       where_clause
                                      )

                if update_result is None:
                    continue

                updated_data, updated_ids = update_result

                save_table_data(table_name, updated_data)

                if not updated_ids:
                    print("Записи не найдены.")
                else:
                    for record_id in updated_ids:
                        print(
                              f"Запись с ID={record_id} "
                              f'в таблице "{table_name}" '
                              "успешно обновлена."
                             )

            elif command == "delete":
                table_name, where_clause = parse_delete(user_input)

                if not validate_clause(metadata,
                                       table_name,
                                       where_clause
                                       ):
                    continue

                table_data = load_table_data(table_name)

                delete_result = delete(table_data,
                                       where_clause
                                      )

                if delete_result is None:
                    continue

                updated_data, deleted_ids = delete_result

                save_table_data(table_name,
                                updated_data
                                )

                if not deleted_ids:
                    print("Записи не найдены.")
                else:
                    for record_id in deleted_ids:
                        print(
                              f"Запись с ID={record_id} "
                              f'успешно удалена из таблицы '
                              f'"{table_name}".'
                             )

            elif command == "info":
                table_name = parse_info(user_input)

                if table_name not in metadata:
                    print(
                          f'Ошибка: Таблица "{table_name}" '
                          "не существует"
                         )
                    continue

                table_data = load_table_data(table_name)

                print_info(metadata,
                           table_name,
                           table_data
                           )

            elif command == "help":
                print_help()

            elif command == "exit":
                break

            else:
                print(
                      f'Функции "{command}" нет. '
                      "Попробуйте снова"
                     )

        except ValueError as error:
            print(f"Ошибка: {error}")
