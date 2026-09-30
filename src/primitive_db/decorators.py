import time


def handle_db_errors(func):
    """Централизованно обрабатывает ошибки операций базы данных через try-except"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                  "Ошибка: Файл данных не найден. "
                  "Возможно, база данных не инициализирована"
                 )
        except KeyError as error:
            print(
                  f"Ошибка: Таблица или столбец "
                  f"{error} не найден"
                 )
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None
    return wrapper


def confirm_action(action_name):
    """Функция запрашивает подтверждение перед опасной операцией"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить '
                           f'"{action_name}"? [y/n]: '
                          ).strip().lower()
            if answer != "y":
                print("Операция отменена")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator


# @wraps(func) нужен чтобы декторатор не затирал имя исходной функции
# Без него log_time, отладка и документация могли бы вместо insert видеть имя wrapper
def log_time(func):
    """Измеряет время выполнения функции"""
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_time = time.monotonic() - start_time
            print(
                  f"Функция {func.__name__} выполнилась "
                  f"за {elapsed_time:.3f} секунд"
                 )
    return wrapper


def create_cacher():
    """Создаёт замыкание для кэширования результатов"""
    cache = {}
    def cache_result(key, value_func):
        if key in cache:
            return cache[key]
        value = value_func()
        cache[key] = value
        return value
    return cache_result
