"""Análisis de latencias del experimento RNF7.

Lee el CSV generado por la instrumentación del chat (RNF7_LOG=true) y produce:
- Estadísticos globales y por tema (n, media, desv. estándar, mediana, P90, P95, máx)
- Veredicto RNF7: P95 <= 15000 ms
- Histograma y boxplot por tema (PNG)
- Tabla de estadísticos en LaTeX para la tesis

Uso:
    python scripts/rnf7_analysis.py [ruta/al/rnf7_latencias.csv]
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

UMBRAL_MS = 15000


def estadisticos(serie: pd.Series) -> dict:
    return {
        "n": int(serie.count()),
        "media_ms": round(serie.mean(), 1),
        "desv_est_ms": round(serie.std(), 1),
        "mediana_ms": round(serie.median(), 1),
        "p90_ms": round(serie.quantile(0.90), 1),
        "p95_ms": round(serie.quantile(0.95), 1),
        "max_ms": round(serie.max(), 1),
    }


def main() -> None:
    csv_path = Path(sys.argv[1] if len(sys.argv) > 1 else "rnf7_latencias.csv")
    if not csv_path.exists():
        sys.exit(f"No se encontró el archivo: {csv_path}")

    df = pd.read_csv(csv_path)
    lat = df["latencia_ms"]
    out_dir = csv_path.parent

    # --- Estadísticos ---
    filas = [{"tema": "GLOBAL", **estadisticos(lat)}]
    for tema, grupo in df.groupby("tema"):
        filas.append({"tema": tema, **estadisticos(grupo["latencia_ms"])})
    tabla = pd.DataFrame(filas).set_index("tema")

    print(f"\n=== RNF7 - Analisis de latencias ({csv_path.name}) ===\n")
    print(tabla.to_string())

    p95 = lat.quantile(0.95)
    cumple = p95 <= UMBRAL_MS
    print(
        f"\nP95 global: {p95:.1f} ms ({p95 / 1000:.2f} s) | "
        f"umbral RNF7: {UMBRAL_MS} ms -> {'CUMPLE' if cumple else 'NO CUMPLE'}\n"
    )

    # --- Tabla LaTeX ---
    latex_path = out_dir / "rnf7_tabla.tex"
    latex_path.write_text(
        tabla.to_latex(
            caption="Estadísticos de latencia de respuesta del agente (RNF7).",
            label="table:rnf7",
        ),
        encoding="utf-8",
    )

    # --- Histograma ---
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(lat / 1000, bins=15, edgecolor="black", alpha=0.8)
    ax.axvline(UMBRAL_MS / 1000, color="red", linestyle="--", label="Umbral RNF7 (15 s)")
    ax.axvline(p95 / 1000, color="orange", linestyle="-.", label=f"P95 ({p95 / 1000:.1f} s)")
    ax.set_xlabel("Latencia (s)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Distribución de latencias de respuesta (RNF7)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "rnf7_histograma.png", dpi=150)

    # --- Boxplot por tema ---
    fig, ax = plt.subplots(figsize=(9, 5))
    grupos = [g["latencia_ms"] / 1000 for _, g in df.groupby("tema")]
    ax.boxplot(grupos, tick_labels=list(df.groupby("tema").groups.keys()))
    ax.axhline(UMBRAL_MS / 1000, color="red", linestyle="--", label="Umbral RNF7 (15 s)")
    ax.set_ylabel("Latencia (s)")
    ax.set_title("Latencia de respuesta por tema (RNF7)")
    ax.legend()
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(out_dir / "rnf7_boxplot.png", dpi=150)

    print(
        "Generados:\n"
        f"  {latex_path}\n"
        f"  {out_dir / 'rnf7_histograma.png'}\n"
        f"  {out_dir / 'rnf7_boxplot.png'}"
    )


if __name__ == "__main__":
    main()
