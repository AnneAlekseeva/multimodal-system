import React, { useState } from "react";
import InputForm from "./components/InputForm";
import ResultsView from "./components/ResultsView";
import "./App.css";

function App() {
  const [results, setResults] = useState(null);

  // 🔙 функция для возврата к форме
  const handleBack = () => setResults(null);

  return (
    <div
      style={{
        backgroundColor: "#f2f6fa",
        minHeight: "100vh",
        paddingBottom: "50px",
      }}
    >
      <h1
        style={{
          textAlign: "center",
          color: "#002b5c",
          marginTop: "40px",
          fontWeight: "700",
        }}
      >
        Симуляция мультимодальной транспортной системы
      </h1>

      {/* Если нет результатов — показываем форму */}
      {!results && <InputForm onResults={setResults} />}

      {/* Если есть результаты — показываем страницу отчёта */}
      {results && <ResultsView data={results} onBack={handleBack} />}
    </div>
  );
}

export default App;
