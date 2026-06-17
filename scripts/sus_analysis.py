"""Análisis del estudio de usabilidad SUS (System Usability Scale).

Lee el CSV exportado del Google Form (una fila por participante, columnas sus_1..sus_10)
y, opcionalmente, la hoja de registro del facilitador en formato largo
(docs/sus_study/hoja_registro.csv: una fila por participante-tarea con éxito/tiempo/SEQ).
Produce:
- Puntuación SUS por participante (0-100) y estadísticos globales (n, media, desv. est.,
  mediana, mín, máx) más interpretación frente al promedio de referencia (~68).
- Si hay datos por tarea: tasa de éxito, tiempo (mediana/rango) y SEQ medio por tarea.
- Histograma de puntuaciones SUS (PNG) y tabla de estadísticos en LaTeX para la tesis.

Formato esperado del CSV de SUS (Google Form):
    participant_id,sus_1,sus_2,sus_3,sus_4,sus_5,sus_6,sus_7,sus_8,sus_9,sus_10
    P1,4,2,5,1,4,2,5,1,4,2
    ...
Cada sus_i es 1-5. Los ítems impares son positivos; los pares, negativos.

Uso:
    python scripts/sus_analysis.py [ruta/sus_respuestas.csv] [ruta/hoja_registro.csv]
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ITEMS = [f"sus_{i}" for i in range(1, 11)]
IMPARES = [f"sus_{i}" for i in (1, 3, 5, 7, 9)]
PARES = [f"sus_{i}" for i in (2, 4, 6, 8, 10)]
PROMEDIO_REF = 68.0  # referencia de la literatura SUS


def puntuar_sus(df: pd.DataFrame) -> pd.Series:
    """Devuelve la puntuación SUS 0-100 por fila (participante)."""
    faltantes = [c for c in ITEMS if c not in df.columns]
    if faltantes:
        sys.exit(f"Faltan columnas en el CSV de SUS: {', '.join(faltantes)}")

    valores = df[ITEMS]
    if not valores.map(lambda v: 1 <= v <= 5).all().all():
        sys.exit("Todas las respuestas SUS deben estar en el rango 1-5.")

    impares = df[IMPARES].sub(1).sum(axis=1)  # respuesta - 1
    pares = (5 - df[PARES]).sum(axis=1)  # 5 - respuesta
    return (impares + pares) * 2.5


def estadisticos(serie: pd.Series) -> dict:
    return {
        "n": int(serie.count()),
        "media": round(serie.mean(), 1),
        "desv_est": round(serie.std(), 1),
        "mediana": round(serie.median(), 1),
        "min": round(serie.min(), 1),
        "max": round(serie.max(), 1),
    }


def interpretar(media: float) -> str:
    if media >= 80:
        return "bueno/excelente"
    if media >= PROMEDIO_REF:
        return "por encima del promedio"
    if media >= 50:
        return "por debajo del promedio"
    return "problemas serios de usabilidad"


def analizar_tareas(csv_path: Path) -> None:
    """Resumen por tarea desde la hoja de registro en formato largo."""
    df = pd.read_csv(csv_path)
    columnas = {"tarea", "exito_L_LD_F", "duracion_s", "seq_1a7"}
    if not columnas.issubset(df.columns):
        print(f"\n(Aviso) {csv_path.name} no tiene las columnas esperadas {columnas}; "
              "se omite el análisis por tarea.\n")
        return

    df = df.dropna(subset=["exito_L_LD_F"])
    if df.empty:
        print(f"\n(Aviso) {csv_path.name} no tiene datos de tareas registrados todavía; "
              "se omite el análisis por tarea.\n")
        return

    filas = []
    for tarea, g in df.groupby("tarea"):
        exito = g["exito_L_LD_F"].astype(str).str.upper()
        n = len(exito)
        logrado = exito.isin(["L", "LD"]).sum()
        dur = pd.to_numeric(g["duracion_s"], errors="coerce")
        seq = pd.to_numeric(g["seq_1a7"], errors="coerce")
        filas.append({
            "tarea": tarea,
            "n": n,
            "exito_%": round(100 * logrado / n, 0) if n else 0,
            "tiempo_mediana_s": round(dur.median(), 0) if dur.notna().any() else None,
            "tiempo_min_s": round(dur.min(), 0) if dur.notna().any() else None,
            "tiempo_max_s": round(dur.max(), 0) if dur.notna().any() else None,
            "seq_medio": round(seq.mean(), 1) if seq.notna().any() else None,
        })
    tabla = pd.DataFrame(filas).set_index("tarea")
    print("\n=== Metricas por tarea (exito / tiempo / SEQ) ===\n")
    print(tabla.to_string())


def main() -> None:
    sus_path = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/sus_study/sus_respuestas.csv")
    if not sus_path.exists():
        sys.exit(f"No se encontró el archivo de SUS: {sus_path}")

    df = pd.read_csv(sus_path)
    out_dir = sus_path.parent
    df["sus_score"] = puntuar_sus(df)

    id_col = "participant_id" if "participant_id" in df.columns else None
    print(f"\n=== Estudio SUS - {sus_path.name} ===\n")
    cols = ([id_col] if id_col else []) + ["sus_score"]
    print(df[cols].to_string(index=not id_col))

    stats = estadisticos(df["sus_score"])
    print(
        f"\nSUS global: media {stats['media']} (DE {stats['desv_est']}), "
        f"mediana {stats['mediana']}, rango {stats['min']}-{stats['max']}, n={stats['n']}\n"
        f"Interpretación: {interpretar(stats['media'])} "
        f"(referencia ~{PROMEDIO_REF:.0f}).\n"
    )

    # --- Tabla LaTeX ---
    tabla = pd.DataFrame([{"métrica": "SUS (0-100)", **stats}]).set_index("métrica")
    latex_path = out_dir / "sus_tabla.tex"
    latex_path.write_text(
        tabla.to_latex(
            caption="Puntuaciones del System Usability Scale (SUS).",
            label="table:sus",
        ),
        encoding="utf-8",
    )

    # --- Histograma ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(df["sus_score"], bins=10, range=(0, 100), edgecolor="black", alpha=0.8)
    ax.axvline(PROMEDIO_REF, color="red", linestyle="--",
               label=f"Promedio de referencia ({PROMEDIO_REF:.0f})")
    ax.axvline(stats["media"], color="orange", linestyle="-.",
               label=f"Media del estudio ({stats['media']})")
    ax.set_xlabel("Puntuación SUS")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de puntuaciones SUS")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "sus_histograma.png", dpi=150)

    print("Generados:\n"
          f"  {latex_path}\n"
          f"  {out_dir / 'sus_histograma.png'}")

    # --- Métricas por tarea (opcional) ---
    if len(sys.argv) > 2:
        tareas_path = Path(sys.argv[2])
        if tareas_path.exists():
            analizar_tareas(tareas_path)
        else:
            print(f"\n(Aviso) No se encontró la hoja de registro: {tareas_path}")


if __name__ == "__main__":
    main()