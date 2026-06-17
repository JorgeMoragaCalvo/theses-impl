# Evaluación experta del andamiaje pedagógico (RNF6) — Tutor Multi-Agente de IO/Optimización

Este directorio contiene todo lo necesario para ejecutar una **sesión corta con el/la docente** del curso de Métodos de Optimización, en la que evalúa la **calidad del andamiaje pedagógico** del tutor inteligente (RNF6, §5.2.6 del Capítulo 5) mediante una **rúbrica de cuatro criterios**.

## Diseño en una línea

Sesión de **exploración libre moderada**: el/la docente interactúa con el tutor sobre un problema de ejemplo —incluyendo errores deliberados para provocar pistas y correcciones— y al final puntúa una **rúbrica de 4 criterios** en escala **1–4**. Umbral de aceptación: **promedio global ≥ 3,0/4 (75%)** y **ningún criterio con promedio < 3,0**.

## Archivos

| Archivo                  | Para quién             | Qué es                                                                                |
|--------------------------|------------------------|---------------------------------------------------------------------------------------|
| `protocolo_sesion.md`    | Facilitador            | Guion maestro de la sesión, reglas y tiempos.                                         |
| `guion_exploracion.md`   | Docente                | Problema de ejemplo y sugerencias de exploración que ejercitan los 4 criterios.       |
| `rubrica.md`             | Docente / Facilitador  | Instrumento: los 4 criterios con descriptores por nivel (1–4) y reglas de puntuación. |
| `hoja_registro.md`       | Facilitador            | Plantilla de captura en vivo: puntajes por criterio + evidencia observada.            |
| `rubrica_respuestas.csv` | Facilitador / Análisis | Puntajes en formato estructurado (una fila por ronda) que consume el script.          |

## Cómo ejecutar una sesión (resumen)

1. **Antes:** levanta la app (backend + frontend), ten lista una cuenta de prueba, abre el tutor en la página de Chat y deja a mano `rubrica.md` y la `hoja_registro`. Asigna un identificador de ronda (R1, R2…) si harás más de una.
2. **Durante:** sigue `protocolo_sesion.md`. El/la docente lee `guion_exploracion.md` e interactúa libremente con el tutor. A diferencia de una sesión de usabilidad, **aquí el evaluador conoce los criterios**: el facilitador puede asegurarse de que las cuatro conductas (guía, proporcionalidad, progresión, lenguaje) se ejerciten antes de puntuar.
3. **Al final:** el/la docente asigna un puntaje 1–4 a cada criterio (`rubrica.md`) y anota la evidencia. El facilitador los traslada a `rubrica_respuestas.csv`.
4. **Después:** ejecuta el script de análisis para obtener promedios, veredicto y la tabla LaTeX de §5.2.6.

> **Unidad de evaluación.** Cada *ronda* es una exploración completa (idealmente una por agente especialista, p. ej. Programación Lineal y Programación Entera) que produce una fila `c1..c4`. El script agrega los promedios sobre todas las rondas registradas; con una sola ronda también funciona (reporta esa única evaluación).

## Análisis automático (script)

`scripts/rubric_analysis.py` calcula todo a partir del CSV:

```bash
python scripts/rubric_analysis.py docs/rubric_study/rubrica_respuestas.csv
```

Produce: promedio por criterio y global, **veredicto RNF6** frente al umbral de 3,0/4 (75%),
`rubrica_tabla.tex` (tabla LaTeX lista para §5.2.6, con la etiqueta `table:rubric-results`) y
`rubrica_barras.png` (gráfico de barras por criterio con la línea de umbral).
`rubrica_respuestas.csv` viene con filas de ejemplos (R1–R5) para probar el script;
**reemplázalas con los puntajes reales** del/de la docente.

## Cómo se puntúa la rúbrica

Cada uno de los 4 criterios se puntúa **1–4** (1 = *muy deficiente* … 4 = *muy adecuado*), con los descriptores anclados en `rubrica.md`.

1. **Promedio por criterio:** media de los puntajes de ese criterio sobre todas las rondas.
2. **Cumplimiento (%) por criterio:** `promedio / 4 × 100`.
3. **Promedio global:** media de los cuatro promedios por criterio.
4. **Veredicto RNF6 — CUMPLE** si: promedio global ≥ **3,0/4 (75%)** **y** ningún criterio individual con promedio < 3,0.

> Ejemplo: promedios por criterio [3,5; 3,0; 3,0; 4,0] → global 3,375/4 = **84,4%**, mínimo 3,0 → **CUMPLE**.

**Interpretación:** el umbral del 75% proviene del enunciado del RNF6. A diferencia del SUS (muestra de usuarios), aquí el evaluador es un **único experto** (el/la docente del curso); se reportan los promedios descriptivos y el veredicto, sin inferencia estadística.

## Relación con §5.2.6 y con el estudio SUS

- La tabla generada (`rubrica_tabla.tex`) corresponde a `table:rubric-results` de §5.2.6: rellena las celdas hoy marcadas con `…`.
- Este kit es el análogo "experto" del kit de usabilidad de `docs/sus_study/` (RNF2/SUS): misma estructura de protocolo + instrumento + hoja de registro + script de análisis.