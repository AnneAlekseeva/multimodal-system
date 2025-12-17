# backend/services/regulation.py
from datetime import datetime, timedelta


# ----------------------------------------------------------
# 1) НЕРЕГУЛИРУЕМЫЙ ПОТОК С РЕАЛЬНЫМ ОЖИДАНИЕМ
# ----------------------------------------------------------
def compute_unregulated_with_waiting(unregulated_schedule, sections_count):
    """
    Добавляет WAITING в нерегулируемый поток.
    (!!! это то, чего у нас раньше НЕ БЫЛО !!!)

    Важное:
    - Машина идёт в ту секцию, которая указана в таблице случайных чисел (как раньше)
    - Но если секция занята — машина ждёт, пока она освободится.
    """

    result = []
    busy_until = [None] * sections_count  # реальные секции из модели случайных чисел

    for car in unregulated_schedule:
        sec = int(car["section"]) - 1  # индекс 0..N-1
        arrival_dt = datetime.strptime(car["arrival_time"], "%H:%M")
        service_time = car["service_time"]

        section_free_time = busy_until[sec]

        # ---- расчет ожидания ----
        if section_free_time is None or arrival_dt >= section_free_time:
            waiting = 0.0
            start_service = arrival_dt
        else:
            waiting = (section_free_time - arrival_dt).total_seconds() / 3600.0  # изменено на часы
            start_service = section_free_time

        # ---- окончание обслуживания ----
        departure_dt = start_service + timedelta(minutes=service_time)
        busy_until[sec] = departure_dt

        result.append(
            {
                "interval": car["interval"],
                "arrival_time": arrival_dt.strftime("%H:%M"),
                "car_type": car["car_type"],
                "service_time": service_time,
                "waiting": round(waiting, 2),
                "departure_time": departure_dt.strftime("%H:%M"),
                "section": sec + 1,
            }
        )

    return result


# ----------------------------------------------------------
# 2) РЕГУЛИРУЕМЫЙ ПОТОК (остался как раньше)
# ----------------------------------------------------------
def regulate_schedule(unregulated_schedule, sections_count):
    """
    Регулируемый подвод автомобилей:
    - Время прибытия и обслуживания такие же, как в нерегулируемом.
    - Но секцию выбирает диспетчер — та, что освободится раньше всех.
    """

    regulated = []
    busy_until = [None] * sections_count  # виртуальная загрузка секций

    for car in unregulated_schedule:
        arrival_dt = datetime.strptime(car["arrival_time"], "%H:%M")
        service_time = car["service_time"]

        # ---- выбираем секцию по минимальному времени освобождения ----
        free_times = []
        for t in busy_until:
            free_times.append(arrival_dt if t is None else t)

        chosen_index = free_times.index(min(free_times))
        section_ready = busy_until[chosen_index]

        # ---- ожидание ----
        if section_ready is None or arrival_dt >= section_ready:
            waiting = 0.0
            start_service = arrival_dt
        else:
            waiting = (section_ready - arrival_dt).total_seconds() / 3600.0  # изменено на часы
            start_service = section_ready

        # ---- окончание ----
        departure_dt = start_service + timedelta(minutes=service_time)
        busy_until[chosen_index] = departure_dt

        regulated.append(
            {
                "interval": car["interval"],
                "arrival_time": arrival_dt.strftime("%H:%M"),
                "car_type": car["car_type"],
                "service_time": service_time,
                "waiting": round(waiting, 2),
                "departure_time": departure_dt.strftime("%H:%M"),
                "section": chosen_index + 1,
            }
        )

    return regulated
