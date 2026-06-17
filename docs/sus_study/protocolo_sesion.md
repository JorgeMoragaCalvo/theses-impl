# Protocolo de sesión (facilitador)

Documento maestro para conducir una sesión individual de usabilidad **moderada con pensamiento en voz alta**. Duración objetiva: **45–55 min**. Lee este guion antes de cada sesión y ten a mano la `hoja_registro` y el Google Form.

## Antes de empezar (checklist)

- [ ] Backend y frontend levantados y funcionando (prueba tú mismo las 5 tareas — ver "Ensayo" en el README).
- [ ] Cuenta de prueba creada (o flujo de registro listo para la Tarea 1).
- [ ] Cronómetro / temporizador disponible.
- [ ] `hoja_registro` (md o csv) abierta; ID anónimo asignado (P1…P8).
- [ ] Google Form abierto en una pestaña para el final.
- [ ] (Opcional) `RNF7_LOG` activado en `.env` para latencias objetivas.
- [ ] Grabación (audio/pantalla) solo si hay consentimiento.

## Reglas del facilitador (críticas)

1. **No enseñes ni demuestres.** No muestres cómo formular las frases ni dónde hacer clic. Cómo el estudiante descubre la interfaz **es lo que estamos midiendo**.
2. **Prompts neutrales únicamente:** *"¿Qué estás pensando ahora?"*, *"¿Qué esperabas que pasara?"*, *"¿Qué intentarías a continuación?"*. Nunca *"deberías…"* ni *"haz clic en…"*.
3. **Silencio productivo:** deja que el estudiante luche un poco; el silencio incómodo es parte del método.
4. **Criterio de fallo:** si tras **~3–4 min** sigue atascado en una tarea, márcala como *fallida*, anota el motivo y pasa a la siguiente (puedes dejarle la tarea ya iniciada para no bloquear las siguientes).
5. **No interpretes la escala SUS** por el estudiante; el cuestionario lo responde solo.

## Estructura de la sesión

| Fase                           | Tiempo    | Acción del facilitador                                                                          |
|--------------------------------|-----------|-------------------------------------------------------------------------------------------------|
| 1. Bienvenida y consentimiento | 5 min     | Guion de bienvenida (abajo). Registra consentimiento.                                           |
| 2. Contexto / demografía       | 3 min     | El estudiante responde la sección de demografía del Form (o al inicio).                         |
| 3. Orientación breve           | 2 min     | Tour de 60 s: páginas **Chat**, **Evaluaciones**, **Progreso**. Sin enseñar a formular prompts. |
| 4. Tareas (think-aloud)        | 25–30 min | El estudiante lee `guion_tareas.md` y trabaja. Tú registras éxito + tiempo + SEQ por tarea.     |
| 5. Cuestionario SUS            | 5 min     | El estudiante completa el Form (10 ítems SUS + comentario) solo.                                |
| 6. Cierre / entrevista         | 3–5 min   | 3 preguntas abiertas (abajo).                                                                   |

## Guion de bienvenida (léelo en voz alta)

> "Gracias por participar. Hoy vamos a evaluar **el sistema, no a ti**: no hay respuestas
> correctas ni incorrectas, y nada de lo que hagas está bien o mal. Te pediré que
> **pienses en voz alta**: di lo que estás mirando, lo que esperas que pase y lo que te
> confunde. Yo no puedo ayudarte durante las tareas porque quiero ver cómo funciona el
> sistema por sí solo, así que si te quedas en silencio te recordaré que sigas narrando.
> Puedes detenerte cuando quieras. ¿Tienes alguna pregunta antes de empezar?"

Confirma consentimiento (y de grabación, si aplica) antes de continuar.

## Durante las tareas — qué registrar (en `hoja_registro`)

Para cada una de las 5 tareas:
- **Tiempo de inicio / fin** (o duración en segundos).
- **Éxito** según el criterio definido en `guion_tareas.md`: Logrado / Logrado con dificultad / Fallido.
- **SEQ:** justo al terminar la tarea, pregunta: *"En general, esta tarea fue…"* y registra **1 (Muy difícil) – 7 (Muy fácil)**.
- **Notas de observación:** dónde dudó, qué frase usó para activar la herramienta, errores, citas textuales útiles.

## Preguntas de cierre (entrevista corta)

1. ¿Qué fue **lo más confuso** o frustrante de usar el tutor?
2. ¿Qué te resultó **más útil**?
3. Si pudieras **cambiar una cosa**, ¿cuál sería?

## Después de la sesión

- Verifica que la `hoja_registro` esté completa (5 tareas × éxito/tiempo/SEQ).
- Confirma que el Form se envió.
- Une por ID anónimo (P1…P8) las respuestas del Form con tu `hoja_registro`.