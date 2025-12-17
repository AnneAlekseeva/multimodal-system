import math
from .random_table import get_random

def calculate_intensity(total_fleet: int, share: float, hours: float) -> float:
    """
    Расчёт средней часовой интенсивности λ (формула 1.2 из ПЗ):
    λ = (N * α) / T
    N — общий парк автомобилей
    α — доля обслуживаемых в период (%)
    T — время периода (часы)
    """
    return (total_fleet * share) / hours


def calculate_erlang_interval(lambda_value: float, k: int, row_index: int) -> int:
    """
    Расчёт интервала между прибытием автомобилей по закону Эрланга (формула 1.1):
    τ = − (60 / (λ * k)) * ln(Π R_i)
    где R_i — случайные числа из таблицы случайных чисел (мы берём из get_random)
    """
    product = 1.0
    for i in range(k):
        # В ПЗ таблица используется последовательно по строкам, берём случайные числа
        r = get_random(row_index + i, 0)  # используем 5-й столбец (марка), как источник R
        product *= r

    tau = - (60 / (lambda_value * k)) * math.log(product)

    return max(1, round(tau))  # интервал не может быть меньше 1 минуты