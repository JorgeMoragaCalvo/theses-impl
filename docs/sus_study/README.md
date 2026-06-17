# Estudio de usabilidad SUS — Tutor Multi-Agente de IO/Optimización

Este directorio contiene todo lo necesario para ejecutar **sesiones individuales de
usabilidad** con estudiantes y obtener una puntuación **System Usability Scale (SUS)**,
junto con evidencia ligera de eficacia/eficiencia (éxito por tarea, tiempo por tarea y
una pregunta de facilidad SEQ).

## Diseño en una línea

Sesiones **moderadas con pensamiento en voz alta** (think-aloud), **5–8 estudiantes**
(piloto), 5 tareas guiadas, cuestionario **SUS** en Google Forms al final.

## Archivos

| Archivo | Para quién | Qué es |
|---------|-----------|--------|
| `protocolo_sesion.md` | Facilitador | Guion maestro de la sesión, reglas y tiempos. |
| `guion_tareas.md` | Estudiante | Las 5 tareas tal como las lee el participante. |
| `cuestionario_sus.md` | Facilitador (arma el Form) | Texto fuente del Google Form: demografía, SEQ, 10 ítems SUS, comentario. |
| `hoja_registro.md` | Facilitador | Plantilla de captura en vivo: éxito + tiempo + SEQ + notas. |
| `hoja_registro.csv` | Facilitador | Misma plantilla en CSV para análisis. |

## Cómo ejecutar una sesión (resumen)

1. **Antes:** levanta la app (backend + frontend), crea/ten lista una cuenta de prueba,
   abre el Google Form, ten el cronómetro y la `hoja_registro` a mano. Asigna un ID
   anónimo al participante (P1…P8).
2. **Durante:** sigue `protocolo_sesion.md`. El estudiante lee `guion_tareas.md` y trabaja
   pensando en voz alta. Tú observas: marcas éxito/fallo, tomas el tiempo y el SEQ de cada
   tarea en `hoja_registro`. **No** ayudes ni demuestres.
3. **Al final:** el estudiante completa el Google Form (SUS + comentario) solo. Cierre con
   2–3 preguntas abiertas.
4. **Después:** exporta las respuestas del Form a CSV y une por ID con tu `hoja_registro`.

## Análisis automático (script)

`scripts/sus_analysis.py` calcula todo a partir de los CSV:

```bash
# Solo SUS (una fila por participante: participant_id, sus_1..sus_10)
python scripts/sus_analysis.py docs/sus_study/sus_respuestas.csv

# SUS + métricas por tarea (éxito/tiempo/SEQ desde la hoja de registro)
python scripts/sus_analysis.py docs/sus_study/sus_respuestas.csv docs/sus_study/hoja_registro.csv
```

Produce: puntuación por participante, estadísticos globales con interpretación,
`sus_tabla.tex` (tabla LaTeX para la tesis), `sus_histograma.png`, y —si pasas la hoja de
registro con datos— un resumen por tarea (% éxito, tiempo mediana/rango, SEQ medio).
`sus_respuestas.csv` viene con filas de ejemplo (P1–P5) para probar el script; reemplázalas
con el export real del Google Form.

## Cómo se puntúa el SUS

Cada uno de los 10 ítems se responde 1–5 (1 = Totalmente en desacuerdo … 5 = Totalmente de
acuerdo). Los ítems alternan polaridad (impares positivos, pares negativos).

1. **Ítems impares (1,3,5,7,9):** contribución = `respuesta − 1`.
2. **Ítems pares (2,4,6,8,10):** contribución = `5 − respuesta`.
3. Suma las 10 contribuciones (rango 0–40).
4. Multiplica por **2.5** → puntuación SUS final en **0–100**.

> Ejemplo: respuestas [4,2,4,2,4,2,4,2,4,2] → impares aportan (3+3+3+3+3)=15, pares aportan
> (3+3+3+3+3)=15, suma 30 × 2.5 = **75**.

**Interpretación:** ~**68** es el promedio de referencia de la literatura SUS. >80 se
considera bueno/excelente; <50 indica problemas serios de usabilidad. Con un piloto de 5–8
solo se reportan estadísticos descriptivos (media, desviación estándar, mín/máx).

### SEQ y métricas por tarea

- **SEQ** (1–7 por tarea): reporta media por tarea; identifica la tarea más difícil.
- **Éxito por tarea:** % de participantes que cumplieron el criterio de éxito.
- **Tiempo por tarea:** mediana/rango en segundos.

## Opcional: latencia objetiva (RNF7)

El proyecto ya registra latencias de respuesta vía la bandera `RNF7_LOG` en `.env`
(`frontend/pages/1_chat.py`, analizado por `scripts/rnf7_analysis.py`). Si la activas
durante las sesiones, obtienes tiempos de respuesta del tutor para complementar la
eficiencia percibida — **sin escribir código nuevo**. Es opcional y no forma parte del
protocolo SUS central.