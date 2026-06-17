# Guion de exploración (docente evaluador/a)

Esta es una guía para que **explores con libertad** el tutor inteligente y luego puntúes la
rúbrica (`rubrica.md`). No es un examen del sistema paso a paso: úsala como menú de
interacciones sugeridas. Conoces los cuatro criterios, así que **provócalos a propósito** —
incluyendo cometer errores deliberados— para poder juzgarlos con evidencia.

Usa este problema de ejemplo (mesas y sillas) durante toda la exploración:

> Maximizar la ganancia `50·x1 + 40·x2`
> sujeto a:
> `3·x1 + 2·x2 ≤ 18`
> `4·x1 + 3·x2 ≤ 24`
> con `x1, x2 ≥ 0`.
>
> En notación simple para escribir al tutor:
> `max 50*x1 + 40*x2` sujeto a `3*x1 + 2*x2 <= 18`, `4*x1 + 3*x2 <= 24`.

Antes de empezar, selecciona en la barra lateral el tema **Programación Lineal**.

---

## Bloque A — Orientación sin respuesta directa  → criterio **C1**

Pídele al tutor que te **oriente** para abordar el problema **sin** entregarte la solución.
Por ejemplo: *"Tengo este problema de mesas y sillas. No quiero la respuesta todavía:
ayúdame a pensar cómo empezar a formularlo."*

> Observa: ¿responde con preguntas guía y pistas, o suelta de inmediato el modelo/solución?

---

## Bloque B — Pista proporcional al error  → criterio **C2**

Entrégale una formulación **con un error pequeño** y pide que la revise. Por ejemplo, invierte
un signo: *"¿Está bien mi restricción `3*x1 + 2*x2 >= 18`?"*. Luego, en otro mensaje,
plantea un error **grande** (omite una restricción o confunde la función objetivo).

> Observa: ¿la intensidad y especificidad de la pista **crecen** con la magnitud del error,
> o responde igual ante un desliz menor que ante un error grave?

---

## Bloque C — Progresión ante errores reiterados  → criterio **C3**

**Insiste en el mismo error** dos o tres veces, como si no entendieras la pista. Por ejemplo,
vuelve a proponer la restricción equivocada tras la primera corrección.

> Observa: ¿la ayuda **escala** (primero una pista, luego un ejemplo, luego un desglose paso a
> paso), o repite la misma respuesta sin adaptarse a tu insistencia?

---

## Bloque D — Adaptación del lenguaje al nivel  → criterio **C4**

Plantea la **misma duda** con dos registros distintos:
1. Como principiante: *"Recién empiezo en optimización, explícame qué es una variable de
   holgura con palabras simples."*
2. Como avanzado: *"Interpreta las variables de holgura en términos de las restricciones
   activas y la solución óptima."*

> Observa: ¿ajusta el vocabulario y la profundidad al nivel planteado, o usa el mismo
> registro en ambos casos?

---

## (Opcional) Bloque E — Otro especialista

Si queda tiempo, cambia el tema a **Programación Entera** y repite uno o dos bloques con el
mismo problema (ahora con `x1, x2` enteros), para juzgar si el andamiaje se mantiene entre
agentes. Registra esta exploración como una **ronda distinta** en la hoja de registro.

---

Al terminar, asigna un puntaje **1–4** a cada criterio según los descriptores de
`rubrica.md` y anota la evidencia que sustenta cada puntaje. ¡Gracias!