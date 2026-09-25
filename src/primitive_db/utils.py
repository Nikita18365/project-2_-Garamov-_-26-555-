import json


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
