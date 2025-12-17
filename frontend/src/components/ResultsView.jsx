import React from "react";

function ResultsView({ data, onBack }) {
  if (!data) return null;

  const { tables, results, graphs, report_url } = data;
  const { waiting_time, costs, performance } = results || {};

  // Универсальный рендер таблицы
  const renderTable = (rows, { title, regulated = false }) => {
    if (!rows || rows.length === 0) {
      return (
        <>
          <h3 style={{ marginTop: "24px" }}>{title}</h3>
          <p style={{ opacity: 0.7 }}>Нет данных для отображения.</p>
        </>
      );
    }

    return (
      <>
        <h3 style={{ marginTop: "24px" }}>
          {title} <span style={{ opacity: 0.6, fontWeight: 400 }}>({rows.length} строк)</span>
        </h3>

        <table
          style={{
            margin: "12px auto 24px",
            borderCollapse: "collapse",
            width: "90%",
            backgroundColor: "#f9f9f9",
          }}
        >
          <thead style={{ backgroundColor: "#e3f2fd" }}>
            <tr>
              <th>#</th>
              <th>Тип авто</th>
              <th>Интервал, мин</th>
              <th>Время прибытия</th>
              {/* В регулируемой таблице покажем колонку ожидания */}
              {regulated && <th>Ожид., мин</th>}
              <th>Время выезда</th>
              <th>Секция</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td>{row.car_type}</td>
                <td>{row.interval}</td>
                <td>{row.arrival_time}</td>
                {regulated && <td>{row.waiting ?? 0}</td>}
                <td>{row.departure_time}</td>
                <td>{row.section}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </>
    );
  };

  return (
    <div style={{ padding: "40px", textAlign: "center" }}>
      <h2 style={{ color: "#002b5c" }}>Результаты моделирования</h2>

      {/* === 1. Таблицы движения автомобилей === */}
      <h3 style={{ marginTop: "30px" }}>1. Таблицы движения автомобилей</h3>

      {renderTable(tables?.unregulated, { title: "1.1 Нерегулируемый поток", regulated: false })}
      {renderTable(tables?.regulated, { title: "1.2 Регулируемый поток", regulated: true })}

      {/* === 2. Итоговые показатели === */}
      <h3 style={{ marginTop: "30px" }}>2. Итоговые показатели</h3>
      <div
        style={{
          display: "inline-block",
          textAlign: "left",
          backgroundColor: "#f4f8ff",
          padding: "20px 30px",
          borderRadius: "10px",
          margin: "20px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          lineHeight: "1.8",
          minWidth: 420,
        }}
      >
        <p>
          <b>Общее количество автомобилей (регулируемый поток):</b>{" "}
          {tables?.regulated?.length ?? 0}
        </p>
        <p>
          <b>Среднее ожидание на автомобиль:</b>{" "}
          {waiting_time?.average_waiting_per_car_min ?? "—"} мин
        </p>
        <p>
          <b>Общее время ожидания:</b>{" "}
          {waiting_time?.regulated_min ?? "—"} мин
        </p>
        <p>
          <b>Суммарные потери при регулировании:</b>{" "}
          {costs?.loss_regulated_rub ?? "—"} руб
        </p>
        <p>
          <b>Экономический эффект (сокращение потерь):</b>{" "}
          <span style={{ color: "green", fontWeight: "bold" }}>
            +{costs?.economic_effect_rub ?? "—"} руб
          </span>
        </p>
        <p>
          <b>Средняя грузоподъёмность:</b>{" "}
          {performance?.average_capacity_tons ?? "—"} т
        </p>
        <p>
          <b>Грузооборот за смену:</b>{" "}
          {performance?.throughput_tons ?? "—"} т
        </p>
        <p>
          <b>Производительность склада:</b>{" "}
          {performance?.productivity_cars_per_hour ?? "—"} авт/ч
        </p>
      </div>

      {/* === 3. Графики === */}
      <h3 style={{ marginTop: "30px" }}>3. Графики</h3>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "30px",
          flexWrap: "wrap",
          marginTop: "20px",
        }}
      >
        {graphs && graphs.length > 0 ? (
          graphs.map((graph, idx) => (
            <img
              key={idx}
              src={`http://127.0.0.1:8000${graph.startsWith("/") ? graph : "/" + graph}`}
              alt={`График ${idx + 1}`}
              style={{
                width: "600px",
                borderRadius: "8px",
                boxShadow: "0 0 10px rgba(0,0,0,0.2)",
              }}
              onError={(e) => {
                e.currentTarget.style.display = "none";
                console.warn("График не найден:", graph);
              }}
            />
          ))
        ) : (
          <p>Графики не найдены.</p>
        )}
      </div>

      {/* === 4. Кнопки === */}
      <div style={{ marginTop: "40px" }}>
        <button
          onClick={onBack}
          style={{
            background: "#002b5c",
            color: "white",
            border: "none",
            borderRadius: "5px",
            padding: "10px 20px",
            marginRight: "20px",
            cursor: "pointer",
          }}
        >
          ← Назад
        </button>

        {report_url && (
          <a
            href={report_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              background: "#003366",
              color: "white",
              textDecoration: "none",
              borderRadius: "5px",
              padding: "10px 20px",
            }}
          >
            📄 Скачать отчёт (PDF)
          </a>
        )}
      </div>
    </div>
  );
}

export default ResultsView;
