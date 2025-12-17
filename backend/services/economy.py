# backend/services/economy.py
from datetime import timedelta


def calculate_waiting_time(schedule):
    """
    Суммарное время ожидания автомобилей в очереди (минуты).
    Принимает ЛЮБОЕ расписание (регулируемое или нет),
    берёт поле "waiting" у каждой записи.
    """
    return sum(car.get("waiting", 0) for car in schedule)


def calculate_average_waiting(schedule):
    """
    Среднее ожидание на один автомобиль (минуты).
    """
    if not schedule:
        return 0.0
    total_waiting = calculate_waiting_time(schedule)
    return round(total_waiting / len(schedule), 2)


def calculate_idle_cost(total_waiting_minutes, cost_per_hour):
    """
    Потери от простоев автомобилей (руб).
    t_час = t_мин / 60
    Потери = t_час * C_простоя
    """
    total_hours = total_waiting_minutes / 60.0
    return round(total_hours * cost_per_hour, 2)


def calculate_average_capacity(daf_share, iveco_share, daf_capacity, iveco_capacity):
    """
    Средневзвешенная грузоподъёмность автомобиля, т.
    q_ср = q_DAF * α_DAF + q_IVECO * α_IVECO.
    """
    avg_capacity = daf_capacity * daf_share + iveco_capacity * iveco_share
    return round(avg_capacity, 2)


def calculate_shift_throughput(avg_capacity, total_fleet):
    """
    Грузооборот за смену, т.
    G = q_ср * N.
    """
    return round(avg_capacity * total_fleet, 2)


def calculate_productivity(total_fleet, work_hours):
    """
    Производительность склада, авт/ч.
    П = N / T.
    """
    if work_hours == 0:
        return 0.0
    return round(total_fleet / work_hours, 2)


def calculate_economic_effect(idle_loss_unregulated, idle_loss_regulated):
    """
    Экономический эффект регулирования, руб.
    Э = Потери при НЕРЕГУЛИРУЕМОМ подводе − Потери при РЕГУЛИРУЕМОМ.
    Положительное значение — выгода от диспетчеризации.
    """
    return round(idle_loss_unregulated - idle_loss_regulated, 2)
