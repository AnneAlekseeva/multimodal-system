# backend/services/simulation.py
from datetime import datetime, timedelta

from .interval_model import calculate_intensity, calculate_erlang_interval
from .random_table import get_random, RANDOM_TABLE
from backend.models.input_models import InputData


def simulate_arrivals(data: InputData):
    """
    Моделирование прибытия автомобилей — НЕРЕГУЛИРУЕМЫЙ вариант.

    Логика строго по методичке:
    1) Формируем поток прибытия по закону Эрланга:
       - сначала период сгущённого подхода (с интенсивностью λ_peak),
       - затем обычный период (с интенсивностью λ_normal).
    2) Для каждой машины:
       - марка авто определяется 5-м столбцом таблицы случайных чисел;
       - секция — 7-м столбцом (случайно, без учёта занятости);
       - если выбранная секция занята, автомобиль ЖДЁТ ИМЕННО ЭТУ СЕКЦИЮ;
         простои считаем в поле "waiting".
    """

    if data.total_fleet > len(RANDOM_TABLE):
        raise ValueError(
            f"Ошибка: в таблице случайных чисел только {len(RANDOM_TABLE)} строк. "
            f"Вы запросили моделирование {data.total_fleet} автомобилей. "
        )

    schedule = []

    # Время начала работы склада
    current_arrival = datetime.strptime(data.start_time, "%H:%M")

    # Интенсивности в пике и вне пика
    lambda_peak = calculate_intensity(data.total_fleet, data.peak_share, data.peak_hours)
    lambda_normal = calculate_intensity(
        data.total_fleet,
        1 - data.peak_share,
        data.work_duration - data.peak_hours,
    )

    total_peak = int(data.total_fleet * data.peak_share)
    total_normal = data.total_fleet - total_peak

    # Время занятости каждой секции (для НЕрегулируемого варианта)
    busy_until = [None] * data.sections_count

    random_index = 0

    for car_index in range(data.total_fleet):
        # ---- 1. Интервал прибытия ----
        if car_index == 0:
            interval = 0
        elif car_index < total_peak:
            interval = calculate_erlang_interval(lambda_peak, data.k_peak, random_index)
        else:
            interval = calculate_erlang_interval(lambda_normal, data.k_normal, random_index)

        if car_index > 0:
            current_arrival += timedelta(minutes=interval)

        # ---- 2. Марка авто ----
        rnd_mark = get_random(random_index, 0)
        car_type = "DAF" if rnd_mark <= data.daf_share else "IVECO"
        service_time = data.daf_service_time if car_type == "DAF" else data.iveco_service_time

        # ---- 3. Секция по 7-му столбцу (случайный выбор) ----
        rnd_section = get_random(random_index, 1)
        section = int(rnd_section * data.sections_count) + 1
        sec_idx = section - 1

        # ---- 4. Учёт занятости СВОЕЙ секции (машина ждёт ИМЕННО ЕЁ) ----
        last_free_time = busy_until[sec_idx]

        if last_free_time is None or current_arrival >= last_free_time:
            waiting = 0.0
            start_service = current_arrival
        else:
            waiting = (last_free_time - current_arrival).total_seconds() / 60.0
            start_service = last_free_time

        departure = start_service + timedelta(minutes=service_time)
        busy_until[sec_idx] = departure

        schedule.append(
            {
                "interval": interval,
                "arrival_time": current_arrival.strftime("%H:%M"),
                "car_type": car_type,
                "service_time": service_time,
                "waiting": round(waiting, 2),
                "departure_time": departure.strftime("%H:%M"),
                "section": section,
            }
        )

        random_index += 1

    return schedule
