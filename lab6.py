import logging
from functools import wraps
import os
import yaml
import random

class FileNotFound(Exception):
    pass


class FileCorrupted(Exception):
    pass

def logged(exception, mode='console', log_file="logs/app.log"):
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(f"lab_logger_{mode}_{exception.__name__}")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        logger.handlers.clear()

    if mode == "console":
        handler = logging.StreamHandler()
    elif mode == "file":
        handler = logging.FileHandler(log_file, encoding="utf-8")
    else:
        raise ValueError("mode має бути 'console' або 'file'")

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                logger.error(f"{exception.__name__}: {e}")
                raise
        return wrapper
    return decorator

class YamlWorker:
    def __init__(self, filepath):
        folder = os.path.dirname(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        self.filepath = filepath

    @logged(FileNotFound, mode="console")
def read(self):
    if not os.path.exists(self.filepath):
        raise FileNotFound(f"Файл {self.filepath} не існує")

    try:
        with open(self.filepath, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        raise FileCorrupted(f"Помилка читання файлу {self.filepath}: {e}")

    @logged(FileCorrupted, mode="file")
    def write(self, new_data):
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, "r", encoding="utf-8") as f:
                    existing_data = yaml.safe_load(f) or {}
            else:
                existing_data = {}

            existing_data[f"temp{len(existing_data) + 1}"] = new_data

            sorted_students = sorted(existing_data.values(), key=lambda s: s["grade"])
            renumbered_data = {
                f"student{i+1}": student for i, student in enumerate(sorted_students)
            }

            with open(self.filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump(renumbered_data, f, allow_unicode=True)

        except Exception as e:
            raise FileCorrupted(f"Помилка запису у файл {self.filepath}: {e}")

    def add_student(self, name, subject, grade):
        student_data = {
            "name": name,
            "subject": subject,
            "grade": grade
        }
        self.write(student_data)

if __name__ == "__main__":
    worker = YamlWorker("data/test.yaml")

    random_names = [
        "Андрій Синиця", "Марія Левченко", "Олександр Гнатюк",
        "Софія Кравець", "Петро Дорошенко"
    ]
    subjects = ["Математика", "Фізика", "Історія", "Програмування", "Хімія"]

    for _ in range(5):
        name = random.choice(random_names)
        subject = random.choice(subjects)
        grade = random.randint(60, 100)
        worker.add_student(name, subject, grade)

    result = worker.read()
    print("Прочитані дані (відсортовані):")
    for key, student in result.items():
        print(f"{key}: {student}")
