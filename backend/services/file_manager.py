import os
import json
from datetime import datetime

BASE_OUTPUT_PATH = os.path.join("backend", "output", "tables")


def ensure_output_folder_exists():
    """Гарантирует, что папка вывода существует"""
    os.makedirs(BASE_OUTPUT_PATH, exist_ok=True)


def generate_timestamp():
    """Генерирует дату-время для имени файла"""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def save_table(data, name_prefix):
    """
    Сохраняет таблицы JSON (регулируемый и нерегулируемый подвод)
    """
    ensure_output_folder_exists()
    timestamp = generate_timestamp()
    filename = f"{name_prefix}_{timestamp}.json"
    filepath = os.path.join(BASE_OUTPUT_PATH, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath


def save_results(results):
    """
    Сохраняет финансовые и вычислительные результаты
    """
    ensure_output_folder_exists()
    timestamp = generate_timestamp()
    filename = f"results_{timestamp}.json"
    filepath = os.path.join(BASE_OUTPUT_PATH, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return filepath