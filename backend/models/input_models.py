from pydantic import BaseModel, Field
from typing import Optional

class InputData(BaseModel):
    # Основные параметры из таблицы ПЗ 1
    work_duration: float = Field(..., description="Продолжительность работы автотранспорта, часы")
    total_fleet: int = Field(..., description="Общий автопарк автомобилей, обслуживаемый у склада, шт")
    daf_share: float = Field(..., description="Доля автомобилей DAF, от 0 до 1")  # например 0.6
    iveco_share: float = Field(..., description="Доля автомобилей IVECO, от 0 до 1")
    daf_service_time: float = Field(..., description="Время обслуживания DAF, мин")
    iveco_service_time: float = Field(..., description="Время обслуживания IVECO, мин")
    
    # Моделирование интервалов (ПЗ 1)
    peak_hours: float = Field(..., description="Период сгущенного подхода автомобилей, ч")
    peak_share: float = Field(..., description="Доля автомобилей в период сгущенного подхода, от 0 до 1")
    k_peak: int = Field(..., description="Параметр Эрланга в период сгущённого подхода")
    k_normal: int = Field(..., description="Параметр Эрланга в обычный период")

    # Секции склада
    sections_count: int = Field(..., description="Количество секций склада")

    # Экономика (ПЗ условие)
    car_idle_cost: float = Field(..., description="Стоимость автомобиле-часа простоя, руб/ч")
    cargo_storage_cost: float = Field(..., description="Стоимость хранения груза, руб/т·ч")
    daf_capacity: float = Field(..., description="Грузоподъемность DAF, т")
    iveco_capacity: float = Field(..., description="Грузоподъемность IVECO, т")
    
    # Дополнительно
    start_time: Optional[str] = Field(default="08:00", description="Время начала работы автотранспорта")