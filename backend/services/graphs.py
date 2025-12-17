from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# Папка вывода
GRAPHS_DIR = os.path.join("backend", "output", "graphs")

# Цвета
COLOR_DAF = "#0055A4"
COLOR_IVECO = "#003366"
COLOR_WAIT_HATCH_EDGE = "#808080"
COLOR_APPROACH = "#555555"

GRID_COLOR = "#D7DFEF"
LINE_COLOR = "#E6ECF5"
TITLE_COLOR = "#0D1B2A"
LABEL_COLOR = "#243B53"
TEXT_COLOR = "#4A4A4A"


# ─────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────

def _parse_hhmm(s: str) -> datetime:
    return datetime.strptime(s, "%H:%M")


def _floor_to_hour(dt: datetime) -> datetime:
    return dt.replace(minute=0, second=0, microsecond=0)


def _ceil_to_hour(dt: datetime) -> datetime:
    if dt.minute == 0:
        return dt
    return (dt + timedelta(hours=1)).replace(minute=0, second=0)


def _time_ticks(start_dt: datetime, end_dt: datetime):
    span_min = int((end_dt - start_dt).total_seconds() // 60)
    step = 15 if span_min <= 240 else 30 if span_min <= 480 else 60

    ticks, labels = [], []
    t = _floor_to_hour(start_dt)
    if t < start_dt:
        t += timedelta(hours=1)

    while t <= end_dt:
        ticks.append(t)
        labels.append(t.strftime("%H:%M"))
        t += timedelta(minutes=step)

    if not ticks or ticks[0] > start_dt:
        ticks.insert(0, start_dt)
        labels.insert(0, start_dt.strftime("%H:%M"))

    if ticks[-1] < end_dt:
        ticks.append(end_dt)
        labels.append(end_dt.strftime("%H:%M"))

    return ticks, labels


def _color_by_type(car_type: str) -> str:
    return COLOR_DAF if "DAF" in car_type.upper() else COLOR_IVECO


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _compute_section_waiting(schedule, sections):
    """Считает суммарное ожидание по секциям."""
    waiting = {s: 0 for s in sections}
    for row in schedule:
        sec = int(row["section"])
        waiting[sec] += float(row.get("waiting", 0))
    return waiting


def _draw_section_wait_labels(ax, waits, y_gap, left_dt, right_dt):
    """Рисует подпись 'Секция X — ожидание Y мин'."""
    for sec, w in waits.items():
        y = sec * y_gap + 0.45
        ax.text(
            left_dt + (right_dt - left_dt) / 2,
            y,
            f"Секция {sec} — ожидание: {round(w, 1)} мин",
            ha="center",
            va="bottom",
            fontsize=11,
            color=TEXT_COLOR,
            fontweight="bold",
        )


# ─────────────────────────────────────────
# ОСНОВНЫЕ БЛОКИ ГРАФИКОВ
# ─────────────────────────────────────────

def _plot_base_axes(ax, sections: List[int], left_dt: datetime, right_dt: datetime):
    ax.grid(True, axis="x", linestyle=":", color=GRID_COLOR, alpha=0.8)
    ax.set_axisbelow(True)

    y_gap = 1.4

    for sec in sections:
        y = sec * y_gap
        ax.axhline(y, color=LINE_COLOR, linewidth=1)
        ax.text(
            left_dt - timedelta(minutes=5),
            y,
            f"Секция {sec}",
            ha="right",
            va="center",
            fontsize=11,
            color=LABEL_COLOR,
        )

    y_approach = (max(sections) + 1.2) * y_gap
    ax.text(
        left_dt,
        y_approach + 0.2,
        "Подход автомобилей",
        fontsize=12,
        color=TITLE_COLOR,
        fontweight="bold"
    )

    return y_gap, y_approach


def _legend(ax):
    legend_elems = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR_APPROACH,
               markersize=6, label="Подход автомобилей"),
        Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=COLOR_WAIT_HATCH_EDGE,
                  hatch="////", label="Ожидание"),
        Rectangle((0, 0), 1, 1, facecolor=COLOR_DAF, label="Обслуживание (DAF)"),
        Rectangle((0, 0), 1, 1, facecolor=COLOR_IVECO, label="Обслуживание (IVECO)"),
    ]
    ax.legend(handles=legend_elems, loc="upper right", frameon=True)


# ─────────────────────────────────────────
# НЕРЕГУЛИРУЕМЫЙ ГРАФИК
# ─────────────────────────────────────────

def plot_unregulated(unregulated: List[Dict], sections_count, title="Нерегулируемый поток"):
    arrivals = [_parse_hhmm(x["arrival_time"]) for x in unregulated]
    ends = [_parse_hhmm(x["departure_time"]) for x in unregulated]

    left_dt = _floor_to_hour(min(arrivals))
    right_dt = _ceil_to_hour(max(ends) + timedelta(minutes=5))

    sections = list(range(1, sections_count + 1))

    # Ожидание всегда 0 — но выводим для симметрии
    waits = {s: 0.0 for s in sections}

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_title(title, fontsize=18, color=TITLE_COLOR, pad=16, fontweight="bold")

    y_gap, y_approach = _plot_base_axes(ax, sections, left_dt, right_dt)
    service_h = 0.40

    for row in unregulated:
        arr = _parse_hhmm(row["arrival_time"])
        dep = _parse_hhmm(row["departure_time"])
        sec = int(row["section"])
        y = sec * y_gap

        ax.plot([arr], [y_approach], marker="o", markersize=5, color=COLOR_APPROACH)

        ax.add_patch(Rectangle(
            (arr, y - service_h / 2),
            dep - arr,
            service_h,
            facecolor=_color_by_type(row["car_type"]),
            edgecolor="#222",
            linewidth=1.0
        ))

    # ← ДОБАВЛЯЕМ ПОДПИСИ ВРЕМЕНИ ОЖИДАНИЯ
    _draw_section_wait_labels(ax, waits, y_gap, left_dt, right_dt)

    ticks, labels = _time_ticks(left_dt, right_dt)
    ax.set_xlim(left_dt, right_dt)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=11)

    _legend(ax)
    plt.tight_layout()
    return fig, ax


# ─────────────────────────────────────────
# РЕГУЛИРУЕМЫЙ ГРАФИК
# ─────────────────────────────────────────

def plot_regulated(regulated: List[Dict], sections_count, title="Регулируемый поток"):
    arrivals = [_parse_hhmm(x["arrival_time"]) for x in regulated]
    ends = [_parse_hhmm(x["departure_time"]) for x in regulated]

    left_dt = _floor_to_hour(min(arrivals))
    right_dt = _ceil_to_hour(max(ends) + timedelta(minutes=5))

    sections = list(range(1, sections_count + 1))
    waits = _compute_section_waiting(regulated, sections)

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_title(title, fontsize=18, color=TITLE_COLOR, pad=16, fontweight="bold")

    y_gap, y_approach = _plot_base_axes(ax, sections, left_dt, right_dt)
    service_h = 0.40
    wait_h = 0.40

    for row in regulated:
        arr = _parse_hhmm(row["arrival_time"])
        dep = _parse_hhmm(row["departure_time"])
        sec = int(row["section"])
        wait = float(row.get("waiting", 0))
        y = sec * y_gap

        ax.plot([arr], [y_approach], marker="o", markersize=5, color=COLOR_APPROACH)

        if wait > 0:
            ax.add_patch(Rectangle(
                (arr, y - wait_h / 2),
                timedelta(minutes=wait),
                wait_h,
                facecolor="white",
                edgecolor=COLOR_WAIT_HATCH_EDGE,
                hatch="////",
                linewidth=1.0
            ))

        start_service = arr + timedelta(minutes=wait)

        ax.add_patch(Rectangle(
            (start_service, y - service_h / 2),
            dep - start_service,
            service_h,
            facecolor=_color_by_type(row["car_type"]),
            edgecolor="#222",
            linewidth=1.0
        ))

    _draw_section_wait_labels(ax, waits, y_gap, left_dt, right_dt)

    ticks, labels = _time_ticks(left_dt, right_dt)
    ax.set_xlim(left_dt, right_dt)
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels, fontsize=11)

    _legend(ax)
    plt.tight_layout()
    return fig, ax


# ─────────────────────────────────────────
# СОХРАНЕНИЕ ГРАФИКОВ
# ─────────────────────────────────────────

def save_graphs(unregulated, regulated, sections_count, unreg_title, reg_title):
    _ensure_dir(GRAPHS_DIR)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    fig1, ax1 = plot_unregulated(unregulated, sections_count, unreg_title)
    path1 = os.path.join(GRAPHS_DIR, f"unregulated_{ts}.png")
    fig1.savefig(path1, dpi=160)
    plt.close(fig1)

    fig2, ax2 = plot_regulated(regulated, sections_count, reg_title)
    path2 = os.path.join(GRAPHS_DIR, f"regulated_{ts}.png")
    fig2.savefig(path2, dpi=160)
    plt.close(fig2)

    return {
        "unregulated_graph": path1,
        "regulated_graph": path2
    }
