"""Análisis de la Sección 2 (Percepción de eficacia) del cuestionario de evaluación (6.1).

Lee el CSV exportado del Google Form (una fila por participante, columnas item_1..item_6,
escala Likert 1-5, todos los ítems de polaridad positiva) y produce estadísticos
descriptivos por ítem para sustentar las secciones 6.2, 6.3 y 6.4 de la tesis.

Cada ítem se ancla a una dificultad del problema (§1.2) o a un propósito (§1.3.2);
esa trazabilidad se incluye en la salida y en la tabla LaTeX.

Produce:
- Estadísticos por ítem: n, media, desv. est., mediana, mín, máx y % de acuerdo (respuestas 4-5).
- Media global de percepción de eficacia (promedio de las medias por ítem).
- Tabla de estadísticos en LaTeX para la tesis (eval_tabla.tex).
- Gráfico de barras de la media por ítem con la banda de "acuerdo" (eval_barras.png).

Formato esperado del CSV (Google Form):
    participant_id,item_1,item_2,item_3,item_4,item_5,item_6
    E1,4,5,4,5,4,5
    ...
Cada item_i es 1-5.

Uso:
    python scripts/eval_analysis.py [ruta/eval_respuestas.csv]
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ITEMS = [f"item_{i}" for i in range(1, 7)]

# Etiqueta corta + ancla en el Capítulo 1 (para tabla y gráfico).
DIMENSIONES = {
    "item_1": ("Modelado", "§1.2 dif. 1 — problema"),
    "item_2": ("Procedimiento paso a paso", "§1.2 dif. 2 — problema"),
    "item_3": ("Retroalimentación inmediata", "§1.2 dif. 3 — problema"),
    "item_4": ("Personalización", "§1.2 dif. 4 / §1.3.2.1"),
    "item_5": ("Conceptos complejos", "§1.3.2.2 — propósito"),
    "item_6": ("Disponibilidad / autonomía", "§1.3.2.1 — propósito"),
}
UMBRAL_ACUERDO = 4  # respuestas 4-5 se cuentan como "de acuerdo"


def validar(df: pd.DataFrame) -> pd.DataFrame:
    """Verifica columnas y rango 1-5; devuelve solo las columnas de ítems."""
    faltantes = [c for c in ITEMS if c not in df.columns]
    if faltantes:
        sys.exit(f"Faltan columnas en el CSV: {', '.join(faltantes)}")

    valores = df[ITEMS]
    if valores.isna().any().any():
        sys.exit("Hay respuestas vacías; la Sección 2 es obligatoria (1-5).")
    if not valores.map(lambda v: 1 <= v <= 5).all().all():
        sys.exit("Todas las respuestas deben estar en el rango 1-5.")
    return valores


def estadisticos_item(serie: pd.Series) -> dict:
    n = int(serie.count())
    acuerdo = int((serie >= UMBRAL_ACUERDO).sum())
    return {
        "n": n,
        "media": round(serie.mean(), 2),
        "desv_est": round(serie.std(), 2),
        "mediana": round(serie.median(), 1),
        "min": int(serie.min()),
        "max": int(serie.max()),
        "acuerdo_n": acuerdo,
        "acuerdo_%": round(100 * acuerdo / n, 0) if n else 0,
    }


def tabla_por_item(valores: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for item in ITEMS:
        etiqueta, ancla = DIMENSIONES[item]
        filas.append({
            "ítem": item.replace("item_", ""),
            "dimensión": etiqueta,
            "ancla": ancla,
            **estadisticos_item(valores[item]),
        })
    return pd.DataFrame(filas).set_index("ítem")


def main() -> None:
    csv_path = Path(
        sys.argv[1] if len(sys.argv) > 1 else "docs/eval_study/eval_respuestas.csv"
    )
    if not csv_path.exists():
        sys.exit(f"No se encontró el archivo: {csv_path}")

    df = pd.read_csv(csv_path)
    out_dir = csv_path.parent
    valores = validar(df)

    tabla = tabla_por_item(valores)
    print(f"\n=== Sección 2 · Percepción de eficacia — {csv_path.name} ===\n")
    print(tabla.to_string())

    media_global = round(valores.mean().mean(), 2)
    acuerdo_global = round(100 * (valores >= UMBRAL_ACUERDO).mean().mean(), 0)
    print(
        f"\nMedia global de eficacia percibida: {media_global} / 5 "
        f"({acuerdo_global:.0f}% de respuestas de acuerdo, n={len(df)} participantes).\n"
    )

    # --- Tabla LaTeX ---
    latex_path = out_dir / "eval_tabla.tex"
    latex_path.write_text(
        tabla.to_latex(
            caption="Percepción de eficacia por ítem (Sección 2 del cuestionario de evaluación).",
            label="table:eval_eficacia",
        ),
        encoding="utf-8",
    )

    # --- Gráfico de barras: media por ítem ---
    etiquetas = [DIMENSIONES[i][0] for i in ITEMS]
    medias = [tabla.loc[i.replace("item_", ""), "media"] for i in ITEMS]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(etiquetas, medias, edgecolor="black", alpha=0.8)
    ax.axhline(UMBRAL_ACUERDO, color="green", linestyle="--",
               label=f"Umbral de acuerdo ({UMBRAL_ACUERDO})")
    ax.axhline(media_global, color="orange", linestyle="-.",
               label=f"Media global ({media_global})")
    ax.set_ylim(1, 5)
    ax.set_ylabel("Media (escala 1-5)")
    ax.set_title("Percepción de eficacia por ítem")
    ax.tick_params(axis="x", rotation=30)
    for lbl in ax.get_xticklabels():
        lbl.set_ha("right")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "eval_barras.png", dpi=150)

    print("Generados:\n"
          f"  {latex_path}\n"
          f"  {out_dir / 'eval_barras.png'}")


if __name__ == "__main__":
    main()