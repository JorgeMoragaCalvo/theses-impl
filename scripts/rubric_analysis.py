"""Análisis de la evaluación experta del andamiaje pedagógico (RNF6).

Lee el CSV con los puntajes de la rúbrica aplicada por el/la docente
(docs/rubric_study/rubrica_respuestas.csv: una fila por ronda de exploración, columnas
c1..c4 en escala 1-4) y produce:
- Promedio por criterio y promedio global, con porcentaje de cumplimiento (promedio/4*100).
- Veredicto RNF6: promedio global >= 3.0/4 (75%) y ningún criterio individual < 3.0.
- Tabla de resultados en LaTeX (table:rubric-results, para §5.2.6) y gráfico de barras por
  criterio (PNG) con la línea de umbral.

Formato esperado del CSV:
    ronda,agente,c1,c2,c3,c4,notas
    R1,linear_programming,4,3,3,4,...
Cada c_i es un entero 1-4. Las columnas ronda/agente/notas son opcionales para el cálculo.

Uso:
    python scripts/rubric_analysis.py [ruta/rubrica_respuestas.csv]
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

CRITERIOS = [f"c{i}" for i in range(1, 5)]
ETIQUETAS = {
    "c1": "C1. Guía vs. respuesta directa",
    "c2": "C2. Proporcionalidad de la pista al error",
    "c3": "C3. Progresión ante errores reiterados",
    "c4": "C4. Adaptación del lenguaje al nivel",
}
MAX_PUNTAJE = 4
UMBRAL = 3.0  # 75% del puntaje máximo (3.0 sobre 4)


def main() -> None:
    csv_path = Path(
        sys.argv[1] if len(sys.argv) > 1 else "docs/rubric_study/rubrica_respuestas.csv"
    )
    if not csv_path.exists():
        sys.exit(f"No se encontró el archivo: {csv_path}")

    df = pd.read_csv(csv_path)
    faltantes = [c for c in CRITERIOS if c not in df.columns]
    if faltantes:
        sys.exit(f"Faltan columnas en el CSV: {', '.join(faltantes)}")

    valores = df[CRITERIOS]
    if not valores.map(lambda v: 1 <= v <= MAX_PUNTAJE).all().all():
        sys.exit(f"Todas las puntuaciones deben estar en el rango 1-{MAX_PUNTAJE}.")

    out_dir = csv_path.parent
    medias = valores.mean()
    global_media = float(valores.to_numpy().mean())

    # --- Tabla de resultados ---
    filas = [
        {
            "Criterio": ETIQUETAS[c],
            "Promedio (1-4)": round(medias[c], 2),
            "Cumplimiento (%)": round(medias[c] / MAX_PUNTAJE * 100, 1),
        }
        for c in CRITERIOS
    ]
    filas.append(
        {
            "Criterio": "Global",
            "Promedio (1-4)": round(global_media, 2),
            "Cumplimiento (%)": round(global_media / MAX_PUNTAJE * 100, 1),
        }
    )
    tabla = pd.DataFrame(filas).set_index("Criterio")

    print(f"\n=== RNF6 - Evaluación del andamiaje pedagógico ({csv_path.name}) ===\n")
    print(f"n = {len(df)} ronda(s) de evaluación\n")
    print(tabla.to_string())

    min_criterio = float(medias.min())
    cumple = global_media >= UMBRAL and min_criterio >= UMBRAL
    print(
        f"\nPromedio global: {global_media:.2f}/4 ({global_media / MAX_PUNTAJE * 100:.1f}%) | "
        f"mínimo por criterio: {min_criterio:.2f}/4 | umbral RNF6: {UMBRAL}/4 (75%) -> "
        f"{'CUMPLE' if cumple else 'NO CUMPLE'}\n"
    )

    # --- Tabla LaTeX ---
    latex_path = out_dir / "rubrica_tabla.tex"
    latex_path.write_text(
        tabla.to_latex(
            caption="Resultados de la evaluación experta del andamiaje pedagógico (RNF6).",
            label="table:rubric-results",
        ),
        encoding="utf-8",
    )

    # --- Gráfico de barras por criterio ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar([c.upper() for c in CRITERIOS], [medias[c] for c in CRITERIOS],
           edgecolor="black", alpha=0.8)
    ax.axhline(UMBRAL, color="red", linestyle="--", label=f"Umbral RNF6 ({UMBRAL}/4)")
    ax.set_ylim(0, MAX_PUNTAJE)
    ax.set_ylabel("Promedio (1-4)")
    ax.set_title("Evaluación experta del andamiaje pedagógico por criterio (RNF6)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "rubrica_barras.png", dpi=150)

    print(
        "Generados:\n"
        f"  {latex_path}\n"
        f"  {out_dir / 'rubrica_barras.png'}"
    )


if __name__ == "__main__":
    main()