# Guía del estudiante: cómo sacarle el máximo al tutor

Esta guía explica la forma ideal de interactuar con el tutor de IA para Investigación de Operaciones / Optimización Matemática. Léela una vez antes de empezar: cambia mucho cómo aprovechas el sistema.

## 1. Cómo "piensa" el tutor (lo más importante)

El tutor **no es un solucionador que te entrega la respuesta de inmediato**. Está diseñado con un *protocolo socrático*: primero te guía con preguntas y pistas, y solo entrega la solución completa cuando **tú la pides**, cuando muestras frustración, o cuando ya intentaste resolverla.

Cuando sí resuelve, la solución la calcula una **herramienta verificada** (no se los inventa) y te los explica **paso a paso**, no como un volcado de datos.

**Implicación práctica:** si quieres aprender, deja que te guíe. Si solo quieres la respuesta, pídela explícitamente ("resuélveme esto").

## 2. Empieza eligiendo el tema correcto

En la página **💬 Chat**, **eliges manualmente el tema** en el selector de la barra lateral. Esa elección decide qué especialista te responde: **no hay detección automática del tema** a partir de lo que escribes.

| Tema                         | Especialista | Para qué                                                     |
|------------------------------|--------------|--------------------------------------------------------------|
| Programación Lineal          | Tutor LP     | formulación, método gráfico, símplex, dualidad, sensibilidad |
| Programación Entera          | Tutor IP     | binarias/enteras, branch & bound, relajación LP              |
| Programación No Lineal       | Tutor NLP    | KKT, convexidad, optimización no lineal                      |
| Modelamiento Matemático      | Tutor MM     | traducir un problema verbal a un modelo                      |
| Investigación de Operaciones | Tutor OR     | panorama general, clasificación de problemas                 |

Cada agente está **acotado a su tema**. Si el **primer mensaje** de una conversación nueva no parece relacionado con el tema elegido, el agente te avisa amablemente que está fuera de su alcance y te recuerda en qué puede ayudarte, pero **no cambia de tema por ti**. Para hablar con otro especialista, elige otro tema en el selector.

## 3. Tu nivel de conocimiento

El tutor está **diseñado** para adaptar su lenguaje a tres niveles:

- **Principiante:** analogías, números pequeños, comienza por el método gráfico.
- **Intermedio:** mecánica del símplex, dualidad, precios sombra, problemas de 3+ variables.
- **Avanzado:** notación formal, demostraciones, degeneración, branch-and-cut, métodos de punto interior.

**Importante (estado actual):** por ahora todos los estudiantes quedan fijados en el nivel **Principiante**. Todavía no existe una forma —ni manual ni automática— de cambiar tu nivel, así que las explicaciones del tutor serán de nivel principiante. (El selector de dificultad de la página de **Evaluaciones** es independiente: solo fija la dificultad de esa evaluación, no tu nivel en el chat.)

## 4. Qué escribir para activar cada capacidad

El tutor decide automáticamente qué herramienta usar según cómo formules la frase. Usando un ejercicio de ejemplo (mesas y sillas: `max 50x₁ + 40x₂` sujeto a `3x₁ + 2x₂ ≤ 18`, `4x₁ + 3x₂ ≤ 24`, con `x₁, x₂` enteros):

- **Para que te guíe (recomendado para aprender):** *"¿Cómo abordo este problema?"*, *"¿Por dónde empiezo?"* → te hace preguntas y andamiaje.
- **Solución numérica (el óptimo):** *"Resuélveme este problema"*, *"¿cuál es la solución óptima?"* → calcula el óptimo verificado y te lo explica gradualmente.
- **Paso a paso / método símplex (LP):** *"Resuélvelo paso a paso"*, *"muéstrame el método símplex / los tableaus"* → iteraciones, variable entrante/saliente, prueba del cociente mínimo, pivoteo.
- **Branch & bound (IP):** *"Muéstrame el árbol de branch and bound"*, *"ramificación y acotamiento paso a paso"* → árbol completo con cotas y poda.
- **Gráfico de región factible (solo 2 variables):** *"Grafícame la región factible"*, *"explícame el método gráfico"* → imagen con restricciones, vértices y (en IP) puntos enteros factibles.
- **Revisar TU formulación antes de resolver:** *"¿Está bien mi modelo?"*, *"revisa mi formulación"* → validación, no solo la respuesta.

> **Truco:** nombra el método que quieres ver ("símplex", "branch and bound", "gráfico"). Eso garantiza que el tutor invoque la herramienta correcta en lugar de improvisar.

## 5. Practica con ejercicios pre-construidos

Los ejercicios pre-construidos (lp_01…lp_06, ip_01…ip_06, y los de NLP, MM y OR) se practican desde la página **📝 Evaluaciones**, no por el chat:

1. Elige el modo **"Practicar con ejercicio existente"**.
2. Filtra por tema y selecciona un ejercicio de la lista. Los ejercicios se **desbloquean por dificultad**: debes completar los de un rango para acceder al siguiente, y verás cuáles ya completaste.
3. Pulsa **"Comenzar evaluación"** para rendirlo; al enviarlo recibes corrección automática y retroalimentación.

En el **💬 Chat**, en cambio, lo natural es traer **tu propio problema** y pedir pistas, una resolución paso a paso, o que el tutor **revise tu formulación** (ver sección 4).

## 6. Flujo de aprendizaje recomendado

1. **Intenta formular tú primero** (variables, objetivo, restricciones) y pídele que la **revise**.
2. **Resuelve guiado**: pide pistas y resuelve paso a paso antes de ver la respuesta.
3. **Verifica**: pide la solución numérica y compárala con la tuya.
4. **Visualiza** (si son 2 variables) para ganar intuición geométrica.
5. **Evalúate**: ve a **📝 Evaluaciones** para generar y rendir una evaluación (autocorregida, escala 1.0–7.0).
6. **Revisa tu avance** en **📊 Progreso** (dominio por concepto, taxonomía de Bloom). El sistema agenda repasos espaciados en segundo plano y el tutor puede traer a colación, dentro del chat, los temas que toca repasar.

## 7. Buenos hábitos

- **Sé específico:** "no entiendo por qué x₂ = 0 en el óptimo" rinde mucho más que "no entiendo".
- **Pide otra estrategia** si algo no te queda: *"explícamelo de otra forma"*, *"con un ejemplo"*, *"compáralo con…"*.
- **Haz seguimiento:** la conversación tiene memoria; puedes decir *"ahora cambia la restricción de madera a ≤ 30"*.
- **Responde a sus preguntas de comprobación** ("¿Tiene sentido?"): el tutor ajusta su explicación según lo que le contestes en la conversación.
- **Escribe en español** y, para modelos, usa notación simple: `3*x1 + 2*x2 <= 18`.

## 8. Qué *no* esperar

- No resuelve problemas enormes (límite aproximado de **20 variables / 50 restricciones** en las herramientas).
- El gráfico de región factible solo funciona con **exactamente 2 variables**.
- No hará tu tarea sin enseñarte: por diseño, prioriza guiarte antes que darte la respuesta.