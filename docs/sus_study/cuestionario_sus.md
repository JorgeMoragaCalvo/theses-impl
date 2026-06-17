# Cuestionario SUS — texto fuente para Google Forms

Este archivo es la **fuente de verdad** para construir el Google Form. Copia las secciones en este orden. Idioma: español. Anota siempre el **ID anónimo** (P1…P8) como primer campo para poder unir con la `hoja_registro`.

---

## Sección 0 — Identificación

- **ID de participante** (lo asigna el facilitador, ej. P1): _respuesta corta_

---

## Sección 1 — Demografía (3 preguntas)

1. **Carrera / curso actual:** _respuesta corta_
2. **Conocimiento previo de Investigación de Operaciones / Optimización:**
   - Ninguno
   - Básico (algo de clases)
   - Intermedio (he resuelto problemas de LP/IP)
   - Avanzado
3. **Familiaridad con herramientas de IA (ChatGPT, Gemini, etc.):**
   - Nunca las uso
   - Ocasionalmente
   - Frecuentemente

---

## Sección 2 — Facilidad por tarea (SEQ)

> El facilitador captura el SEQ en vivo en la `hoja_registro`. Esta sección en el Form es
> **opcional/respaldo**; si la incluyes, una pregunta por tarea con escala 1–7.

Para cada tarea (1 a 5): *"En general, completar esta tarea fue…"* Escala lineal **1 = Muy difícil … 7 = Muy fácil**.

- SEQ Tarea 1 — Entrar y elegir especialista
- SEQ Tarea 2 — Pedir orientación
- SEQ Tarea 3 — Resolución paso a paso (símplex)
- SEQ Tarea 4 — Visualizar región factible
- SEQ Tarea 5 — Practicar y evaluarse

---

## Sección 3 — System Usability Scale (10 ítems, obligatorio)

Escala **Likert 1–5** para los 10 ítems:
**1 = Totalmente en desacuerdo · 2 = En desacuerdo · 3 = Neutral · 4 = De acuerdo ·
5 = Totalmente de acuerdo**

> Importante: respeta el orden y la polaridad (ítems impares positivos, pares negativos); de esto depende la fórmula de puntuación.

1. Creo que me gustaría usar este sistema con frecuencia.
2. Encontré el sistema innecesariamente complejo.
3. Pensé que el sistema era fácil de usar.
4. Creo que necesitaría el apoyo de una persona técnica para poder usar este sistema.
5. Encontré que las diversas funciones del sistema estaban bien integradas.
6. Pensé que había demasiada inconsistencia en el sistema.
7. Imagino que la mayoría de las personas aprenderían a usar este sistema muy rápidamente.
8. Encontré el sistema muy engorroso de usar.
9. Me sentí muy seguro/a usando el sistema.
10. Necesité aprender muchas cosas antes de poder empezar a usar el sistema.

---

## Sección 4 — Comentario abierto (1 pregunta)

- **Si pudieras cambiar una cosa del tutor, ¿cuál sería?** _párrafo_

---

## Nota de puntuación (recordatorio)

- Ítems impares (1,3,5,7,9): `respuesta − 1`.
- Ítems pares (2,4,6,8,10): `5 − respuesta`.
- Suma (0–40) × **2.5** = puntuación SUS (0–100).
- Referencia: ~68 = promedio. Ver `README.md` para el detalle.