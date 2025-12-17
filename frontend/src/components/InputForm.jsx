import React, { useState } from "react";
import styles from "./InputForm.module.css";
import axios from "axios";

const InputForm = ({ onResults }) => {
  const [form, setForm] = useState({
    work_duration: 8,
    total_fleet: 40,
    daf_share: 0.4,
    iveco_share: 0.6,
    daf_service_time: 16,
    iveco_service_time: 11,
    peak_hours: 2,
    peak_share: 0.4,
    k_peak: 3,
    k_normal: 2,
    sections_count: 3,
    car_idle_cost: 1500,
    cargo_storage_cost: 300,
    daf_capacity: 15,
    iveco_capacity: 12,
    start_time: "08:00",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://localhost:8000/run", {
        ...form,
        work_duration: parseFloat(form.work_duration),
        total_fleet: parseInt(form.total_fleet),
        daf_share: parseFloat(form.daf_share),
        iveco_share: parseFloat(form.iveco_share),
        daf_service_time: parseFloat(form.daf_service_time),
        iveco_service_time: parseFloat(form.iveco_service_time),
        peak_hours: parseFloat(form.peak_hours),
        peak_share: parseFloat(form.peak_share),
        k_peak: parseInt(form.k_peak),
        k_normal: parseInt(form.k_normal),
        sections_count: parseInt(form.sections_count),
        car_idle_cost: parseFloat(form.car_idle_cost),
        cargo_storage_cost: parseFloat(form.cargo_storage_cost),
        daf_capacity: parseFloat(form.daf_capacity),
        iveco_capacity: parseFloat(form.iveco_capacity),
      });

      onResults(response.data);
    } catch (err) {
      console.error(err);
      setError("Ошибка при подключении к серверу. Проверьте, запущен ли backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.formContainer}>
      <h2>Параметры моделирования</h2>
      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.grid}>
          <label>
            Кол-во секций:
            <input
              type="number"
              name="sections_count"
              value={form.sections_count}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Продолжительность смены, ч:
            <input
              type="number"
              name="work_duration"
              value={form.work_duration}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Стоимость простоя, руб/ч:
            <input
              type="number"
              name="car_idle_cost"
              value={form.car_idle_cost}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Стоимость хранения, руб/т·ч:
            <input
              type="number"
              name="cargo_storage_cost"
              value={form.cargo_storage_cost}
              onChange={handleChange}
              required
            />
          </label>

          <label>
            Доля DAF:
            <input
              type="number"
              name="daf_share"
              value={form.daf_share}
              onChange={handleChange}
              step="0.1"
              min="0"
              max="1"
            />
          </label>

          <label>
            Доля IVECO:
            <input
              type="number"
              name="iveco_share"
              value={form.iveco_share}
              onChange={handleChange}
              step="0.1"
              min="0"
              max="1"
            />
          </label>

          <label>
            Время обслуживания DAF, мин:
            <input
              type="number"
              name="daf_service_time"
              value={form.daf_service_time}
              onChange={handleChange}
            />
          </label>

          <label>
            Время обслуживания IVECO, мин:
            <input
              type="number"
              name="iveco_service_time"
              value={form.iveco_service_time}
              onChange={handleChange}
            />
          </label>

          <label>
            Грузоподъемность DAF, т:
            <input
              type="number"
              name="daf_capacity"
              value={form.daf_capacity}
              onChange={handleChange}
            />
          </label>

          <label>
            Грузоподъемность IVECO, т:
            <input
              type="number"
              name="iveco_capacity"
              value={form.iveco_capacity}
              onChange={handleChange}
            />
          </label>

          <label>
            Всего машин:
            <input
              type="number"
              name="total_fleet"
              value={form.total_fleet}
              onChange={handleChange}
            />
          </label>

          <label>
            Время начала работы:
            <input
              type="time"
              name="start_time"
              value={form.start_time}
              onChange={handleChange}
            />
          </label>

          <label>
            Период сгущенного подхода, ч:
            <input
              type="number"
              name="peak_hours"
              value={form.peak_hours}
              onChange={handleChange}
            />
          </label>

          <label>
            Доля в пике:
            <input
              type="number"
              name="peak_share"
              value={form.peak_share}
              onChange={handleChange}
              step="0.1"
              min="0"
              max="1"
            />
          </label>

          <label>
            kₚ (Эрланг в пике):
            <input
              type="number"
              name="k_peak"
              value={form.k_peak}
              onChange={handleChange}
            />
          </label>

          <label>
            kₙ (Эрланг вне пика):
            <input
              type="number"
              name="k_normal"
              value={form.k_normal}
              onChange={handleChange}
            />
          </label>
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Расчет..." : "Запустить моделирование"}
        </button>
      </form>

      {error && <p className={styles.error}>{error}</p>}
    </div>
  );
};

export default InputForm;
