# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .models.input_models import InputData
from .services.simulation import simulate_arrivals

# ВАЖНО — ИСПОЛЬЗУЕМ НОВЫЕ ФУНКЦИИ
from .services.regulation import (
    compute_unregulated_with_waiting,
    regulate_schedule
)

from .services.economy import (
    calculate_waiting_time,
    calculate_average_waiting,
    calculate_idle_cost,
    calculate_average_capacity,
    calculate_shift_throughput,
    calculate_productivity,
    calculate_economic_effect,
)

from .services.file_manager import save_table, save_results
from .services.graphs import save_graphs
from .services.report import generate_pdf_report

import os


# === Настройки приложения ===
app = FastAPI(
    title="Мультимодальные транспортные системы – расчет эффективности склада",
    description="API для расчета графиков обработки автомобилей и экономической эффективности регулирования",
    version="1.0",
)

# --- Пути ---
BASE_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
GRAPHS_DIR = os.path.join(OUTPUT_DIR, "graphs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "API работает! Подключение успешно ✅"}


# === Основной расчёт ===
@app.post("/run")
def run_model(data: InputData):

    # -----------------------------------------------------------
    # 1. Генерация нерегулируемого потока (без ожидания)
    # -----------------------------------------------------------
    schedule_raw = simulate_arrivals(data)

    # -----------------------------------------------------------
    # 2. Добавляем ожидание в НЕРЕГУЛИРУЕМЫЙ поток!
    # -----------------------------------------------------------
    schedule_unregulated = compute_unregulated_with_waiting(
        schedule_raw,
        data.sections_count
    )

    # -----------------------------------------------------------
    # 3. Регулируемый поток (диспетчер)
    # -----------------------------------------------------------
    schedule_regulated = regulate_schedule(
        schedule_raw,
        data.sections_count
    )

    # -----------------------------------------------------------
    # 4. Расчёты
    # -----------------------------------------------------------
    total_wait_unregulated = calculate_waiting_time(schedule_unregulated)
    total_wait_regulated = calculate_waiting_time(schedule_regulated)

    idle_loss_unregulated = calculate_idle_cost(total_wait_unregulated, data.car_idle_cost)
    idle_loss_regulated = calculate_idle_cost(total_wait_regulated, data.car_idle_cost)

    avg_capacity = calculate_average_capacity(
        data.daf_share,
        data.iveco_share,
        data.daf_capacity,
        data.iveco_capacity,
    )

    throughput = calculate_shift_throughput(avg_capacity, data.total_fleet)
    productivity = calculate_productivity(data.total_fleet, data.work_duration)

    economic_effect = calculate_economic_effect(
        idle_loss_unregulated,
        idle_loss_regulated,
    )

    # -----------------------------------------------------------
    # 5. Сохранение таблиц (CSV)
    # -----------------------------------------------------------
    path_unregulated = save_table(schedule_unregulated, "unregulated")
    path_regulated = save_table(schedule_regulated, "regulated")

    # -----------------------------------------------------------
    # 6. Сохранение JSON результатов
    # -----------------------------------------------------------
    path_results = save_results(
        {
            "total_waiting_unregulated_min": total_wait_unregulated,
            "total_waiting_regulated_min": total_wait_regulated,
            "idle_loss_unregulated_rub": idle_loss_unregulated,
            "idle_loss_regulated_rub": idle_loss_regulated,
            "economic_effect_rub": economic_effect,
            "average_capacity_tons": avg_capacity,
            "throughput_tons": throughput,
            "productivity_cars_per_hour": productivity,
        }
    )

    # -----------------------------------------------------------
    # 7. Графики
    # -----------------------------------------------------------
    graphs_paths = save_graphs(
        schedule_unregulated,
        schedule_regulated,
        data.sections_count,
        "Нерегулируемый поток обслуживания",
        "Регулируемый поток с очередностью"
    )

    graph_list = [
        f"/output/graphs/{os.path.basename(path)}"
        for path in graphs_paths.values()
    ]

    # -----------------------------------------------------------
    # 8. PDF отчёт
    # -----------------------------------------------------------
    try:
        pdf_path = generate_pdf_report(
            schedule_unregulated=schedule_unregulated,
            schedule_regulated=schedule_regulated,
            metrics={
                "avg_service_time": round(
                    sum(car["service_time"] for car in schedule_unregulated)
                    / len(schedule_unregulated),
                    2,
                ),
                "avg_idle_time": calculate_average_waiting(schedule_regulated),
                "total_cost": round(idle_loss_regulated, 2),
                "economic_effect": round(economic_effect, 2),
            },
            graph_paths=list(graphs_paths.values()),
            output_dir=OUTPUT_DIR,
        )
    except Exception as e:
        print(f"[!] Ошибка при создании PDF: {e}")
        pdf_path = None

    # -----------------------------------------------------------
    # 9. Ответ фронту
    # -----------------------------------------------------------
    return {
        "status": "✅ Расчёт выполнен успешно",
        "tables": {
            "unregulated": schedule_unregulated,
            "regulated": schedule_regulated,
        },
        "results": {
            "waiting_time": {
                "unregulated_min": total_wait_unregulated,
                "regulated_min": total_wait_regulated,
                "average_waiting_per_car_min": calculate_average_waiting(schedule_regulated),
            },
            "costs": {
                "loss_unregulated_rub": idle_loss_unregulated,
                "loss_regulated_rub": idle_loss_regulated,
                "economic_effect_rub": economic_effect,
            },
            "performance": {
                "average_capacity_tons": avg_capacity,
                "throughput_tons": throughput,
                "productivity_cars_per_hour": productivity,
            },
        },
        "saved_files": {
            "unregulated_table": path_unregulated,
            "regulated_table": path_regulated,
            "results": path_results,
            "report": os.path.basename(pdf_path) if pdf_path else None,
        },
        "graphs": graph_list,
        "report_url": "http://127.0.0.1:8000/output/report.pdf",
    }


# === Эндпоинт скачивания PDF ===
@app.get("/download/report")
def download_report():
    pdf_path = os.path.join(OUTPUT_DIR, "report.pdf")
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type="application/pdf", filename="report.pdf")
    return {"error": "Отчет еще не создан"}
