# Rúbrica de andamiaje pedagógico (RNF6) — instrumento

Instrumento de evaluación experta de la **calidad del andamiaje pedagógico** del tutor.
Cuatro criterios, cada uno en escala **1–4**. El/la docente asigna un puntaje por criterio
al final de la exploración, sustentándolo con evidencia observada.

**Escala:** 1 = *muy deficiente* · 2 = *deficiente* · 3 = *adecuado* · 4 = *muy adecuado*.

---

## C1. Guía vs. respuesta directa

*¿El tutor conduce al estudiante mediante preguntas y pistas en lugar de entregar la
solución completa de inmediato?*

| Nivel | Descriptor |
|-------|-----------|
| 4 — Muy adecuado | Evita dar la solución completa cuando no corresponde; conduce con preguntas y pistas y solo entrega la respuesta cuando el estudiante la pide explícitamente o tras haberlo guiado. |
| 3 — Adecuado | Predomina la guía, aunque ocasionalmente adelanta parte de la solución sin que se la pidan. |
| 2 — Deficiente | Tiende a entregar la respuesta directa; la guía es escasa o superficial. |
| 1 — Muy deficiente | Entrega siempre la solución completa, sin intentar guiar el razonamiento. |

## C2. Proporcionalidad de la pista al error

*¿La intensidad y especificidad de la pista aumentan en proporción a la magnitud del error
cometido?*

| Nivel | Descriptor |
|-------|-----------|
| 4 — Muy adecuado | Ajusta finamente la pista: ante un error menor da una indicación leve; ante un error grave, una corrección más específica y estructurada. |
| 3 — Adecuado | Distingue en general errores leves de graves, con algún ajuste impreciso. |
| 2 — Deficiente | Responde de forma similar sin importar la gravedad del error. |
| 1 — Muy deficiente | La pista no guarda relación con el error (excesiva ante un desliz, o nula ante un error grave). |

## C3. Progresión de la ayuda ante errores reiterados

*Si el estudiante persiste en el error, ¿la ayuda escala (pista → ejemplo → desglose paso a
paso)?*

| Nivel | Descriptor |
|-------|-----------|
| 4 — Muy adecuado | Ante la insistencia en el error, la ayuda escala con claridad: pista, luego ejemplo, luego desglose paso a paso. |
| 3 — Adecuado | Ofrece ayuda adicional ante la reiteración, aunque la progresión no siempre es clara. |
| 2 — Deficiente | Repite respuestas similares con poca adaptación a la insistencia. |
| 1 — Muy deficiente | Repite exactamente la misma respuesta sin reconocer el error reiterado. |

## C4. Adaptación del lenguaje al nivel del problema

*¿El registro del lenguaje (técnico vs. coloquial) se ajusta a la dificultad y al nivel del
estudiante?*

| Nivel | Descriptor |
|-------|-----------|
| 4 — Muy adecuado | Adapta con claridad el vocabulario y la profundidad al nivel planteado (simple para principiante, técnico para avanzado). |
| 3 — Adecuado | Adapta el registro en general, con algún desajuste puntual. |
| 2 — Deficiente | Apenas varía el registro entre niveles distintos. |
| 1 — Muy deficiente | Usa siempre el mismo registro, inadecuado para el nivel planteado. |

---

## Puntuación y veredicto

- **Promedio por criterio:** media de los puntajes del criterio sobre todas las rondas.
- **Cumplimiento (%):** `promedio / 4 × 100`.
- **Promedio global:** media de los cuatro promedios por criterio.
- **Veredicto RNF6 — CUMPLE** si: promedio global ≥ **3,0/4 (75%)** **y** ningún criterio
  individual < 3,0.

El cálculo y la tabla LaTeX los genera `scripts/rubric_analysis.py` a partir de
`rubrica_respuestas.csv`.

## Hoja de respuesta (por ronda)

| Criterio | Puntaje (1–4) | Evidencia observada |
|----------|---------------|---------------------|
| C1. Guía vs. respuesta directa | | |
| C2. Proporcionalidad de la pista | | |
| C3. Progresión ante errores reiterados | | |
| C4. Adaptación del lenguaje | | |