import shlex

import prompt

from src.primitive_db.core import create_table, drop_table, list_tables
from src.primitive_db.utils import load_metadata, save_metadata

METADATA_FILE = "db_meta.json"


def print_help():
    """Выводит справку по командам."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print(
        "<command> create_table <имя_таблицы> "
        "<столбец1:тип> <столбец2:тип> .. - создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def print_invalid_value(value):
    """Выводит сообщение о некорректном значении."""
    print(f"Некорректное значение: {value}. Попробуйте снова.")


def run():
    """Запускает основной цикл базы данных."""
    print_help()

    while True:
        metadata = load_metadata(METADATA_FILE)
        user_input = prompt.string(">>>Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print_invalid_value(user_input)
            continue

        if not args:
            continue

        command = args[0]
        command_args = args[1:]

        if command == "create_table":
            if len(command_args) < 2:
                print_invalid_value(user_input)
                continue

            table_name = command_args[0]
            columns = command_args[1:]

            updated_metadata = create_table(metadata, table_name, columns)

            if updated_metadata != metadata:
                save_metadata(METADATA_FILE, updated_metadata)

        elif command == "drop_table":
            if len(command_args) != 1:
                print_invalid_value(user_input)
                continue

            table_name = command_args[0]
            updated_metadata = drop_table(metadata, table_name)

            if updated_metadata != metadata:
                save_metadata(METADATA_FILE, updated_metadata)

        elif command == "list_tables":
            if command_args:
                print_invalid_value(user_input)
                continue

            list_tables(metadata)

        elif command == "help":
            if command_args:
                print_invalid_value(user_input)
                continue

            print_help()

        elif command == "exit":
            if command_args:
                print_invalid_value(user_input)
                continue

            break

        else:
            print(f"Функции {command} нет. Попробуйте сначала.")
