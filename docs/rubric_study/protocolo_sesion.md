# Protocolo de sesión (facilitador)

Documento maestro para conducir la **sesión de evaluación experta del andamiaje pedagógico
(RNF6)** con el/la docente del curso. Modalidad: **exploración libre moderada**. Duración
objetiva: **30–40 min**. Lee este guion antes de la sesión y ten a mano `rubrica.md` y la
`hoja_registro`.

## Antes de empezar (checklist)

- [ ] Backend y frontend levantados y funcionando (prueba tú mismo una conversación).
- [ ] Cuenta de prueba creada y con sesión iniciada en la página de **Chat**.
- [ ] `rubrica.md` impresa o en pantalla aparte para el/la docente.
- [ ] `hoja_registro` (md) abierta; identificador de ronda asignado (R1, R2…).
- [ ] Problema de ejemplo de `guion_exploracion.md` a la vista.
- [ ] (Opcional) `RNF7_LOG` activado en `.env` si quieres registrar latencias en paralelo.
- [ ] Grabación (audio/pantalla) solo si hay consentimiento.

## Rol del facilitador (modalidad experta)

A diferencia de una sesión de usabilidad con estudiantes, **aquí el evaluador es un experto
que conoce los criterios**. Por tanto:

1. **Sí puedes** explicar la rúbrica, el problema de ejemplo y cómo escribir al tutor; el
   objetivo no es medir si el docente sabe usar la interfaz, sino que **juzgue la calidad
   pedagógica** del tutor.
2. **Asegura la cobertura de los 4 criterios.** Si al explorar libremente no se provocó
   alguna conducta (p. ej. nunca cometió un error para ver la progresión de la ayuda),
   sugiérele una interacción que la dispare —ver mapa de conductas abajo— **antes** de que
   puntúe.
3. **No defiendas al sistema.** Si el docente señala una debilidad, regístrala como
   evidencia; no la justifiques ni induzcas un puntaje.
4. **El puntaje lo asigna el/la docente**, criterio por criterio, al final.

## Estructura de la sesión

| Fase | Tiempo | Acción del facilitador |
|------|--------|------------------------|
| 1. Bienvenida y contexto | 3 min | Explica objetivo (evaluar la *manera* de enseñar del tutor, no su exactitud numérica) y la rúbrica. |
| 2. Lectura de la rúbrica | 4 min | El/la docente lee `rubrica.md` y resuelve dudas sobre los descriptores. |
| 3. Exploración libre | 18–22 min | El/la docente interactúa con el tutor siguiendo `guion_exploracion.md`. Tú observas y aseguras cobertura de los 4 criterios. |
| 4. Puntuación | 5 min | El/la docente asigna 1–4 a cada criterio y anota evidencia. |
| 5. Cierre | 3 min | 3 preguntas abiertas (abajo). |

## Guion de bienvenida (léelo en voz alta)

> "Gracias por participar. Vamos a evaluar **cómo acompaña el tutor el aprendizaje**: si guía
> en lugar de dar la respuesta directa, si sus pistas son proporcionales al error, si la
> ayuda progresa cuando el estudiante insiste en equivocarse, y si adapta el lenguaje al
> nivel. No evaluamos aquí la exactitud del resultado (eso se midió aparte). Te pediré que
> interactúes con el tutor con libertad —incluso cometiendo errores a propósito— y al final
> puntúes cuatro criterios de 1 a 4. Puedes pensar en voz alta; tomaré nota de lo que
> observes."

## Mapa de conductas a provocar (para asegurar cobertura)

Si la exploración libre no las cubrió, sugiere estas interacciones antes de puntuar:

| Criterio | Cómo provocarlo |
|----------|-----------------|
| **C1 — Guía vs. respuesta directa** | Pedir ayuda **sin** querer la solución: *"No me des la respuesta, oriéntame para empezar"*. |
| **C2 — Proporcionalidad de la pista** | Entregar una formulación con un error **pequeño** (un signo) y luego otra con un error **grande** (restricción ausente); comparar la intensidad de la pista. |
| **C3 — Progresión ante errores reiterados** | Repetir el **mismo** error 2–3 veces y observar si la ayuda escala (pista → ejemplo → desglose paso a paso). |
| **C4 — Adaptación del lenguaje** | Plantear la misma duda primero como *"recién empiezo, explícamelo simple"* y luego en registro técnico avanzado. |

## Durante la exploración — qué registrar (en `hoja_registro`)

- **Agente especialista** usado en la ronda (PL, PE, etc.).
- **Evidencia por criterio:** citas textuales o descripción de la respuesta del tutor que
  sustente el puntaje (p. ej. "ante el error de signo, respondió con una pregunta guía, no
  con la corrección directa").
- **Debilidades observadas:** cualquier conducta que baje el puntaje.

## Preguntas de cierre (entrevista corta)

1. ¿En qué se parece o se diferencia el tutor de **cómo guiarías tú** a un estudiante?
2. ¿Cuál fue el criterio donde el tutor estuvo **más débil**?
3. Si pudieras **mejorar una cosa** del comportamiento pedagógico, ¿cuál sería?

## Después de la sesión

- Verifica que la `hoja_registro` tenga los 4 puntajes (1–4) de la ronda y su evidencia.
- Traslada los puntajes a `rubrica_respuestas.csv` (una fila por ronda).
- Ejecuta `python scripts/rubric_analysis.py docs/rubric_study/rubrica_respuestas.csv`.