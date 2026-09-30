import json
import os

from src.primitive_db.constants import DATA_DIR


def load_metadata(filepath):
    """Загрузка метаданных базы данных (БД) из *.json файла"""
    try:
        with open(filepath, encoding = "utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    """Функция сохраняет метаданные БД в json файл"""
    with open(filepath, "w", encoding = "utf-8") as file:
        json.dump(data, file, ensure_ascii = False, indent = 4)


def load_table_data(table_name):
    """Загружает данные таблицы из data/<table_name>.json"""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name, data):
    """Сохраняет данные таблицы в data/<table_name>.json"""
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    with open(filepath, "w", encoding = "utf-8") as file:
        json.dump(data, file, ensure_ascii = False, indent = 4)


def delete_table_data(table_name):
    """Удаляет файл с данными таблицы"""
    filepath = os.path.join(DATA_DIR, f"{table_name}.json")
    try:
        os.remove(filepath)
    except FileNotFoundError:
        pass
