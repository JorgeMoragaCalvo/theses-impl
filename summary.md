# MAIN.PY
## 1. Configuración inicial y dependencias
Imports principales
- FastAPI, Depends, HTTPException, status: para definir la API y las dependencias.
- SQLAlchemy `Session` y `text`: acceso a BD.
- Modelos de BD desde `.database`: `Student`, `Conversation`, `Message`, `Assessment`, `Feedback`, `UserRole`, `GradingSource`.
- Modelos Pydantic desde .models: request/response schemas (por ejemplo StudentCreate, ChatRequest, AssessmentGenerate, etc.).
- Auth desde .auth: funciones para hash de password, autenticación, crear tokens JWT y obtener usuario actual.
- Agentes de IA:
  - `get_linear_programming_agent`
  - `get_mathematical_modeling_agent`
- Servicios de dominio:
  - `get_conversation_service`
  - `get_assessment_service`
  - `get_grading_service`
- Router de admin: `.routers import admin`
- `settings`: configuración (modelo, host, puertos, etc.).

## 2. Registro de agentes de IA
```python
AGENT_REGISTRY = {
    "linear_programming": get_linear_programming_agent,
    "mathematical_modeling": get_mathematical_modeling_agent,
}
```

La función:
```python
def get_agent_for_topic(topic: str):
    ...
```
- Recibe un topic (ej. "linear_programming").
- Busca en `AGENT_REGISTRY`la función que devuelve el agente.
- Si no existe, hace fallback a `get_linear_programming_agent`.
- Devuelve una instancia de agente que luego se usa para generar respuestas en `/chat`.

## 3. Ciclo de vida de la app (lifespan)
```python
@asynccontextmanager
async def lifespan(_: FastAPI):
    ...
```

En el startup:
- Loguea inicio de la app, proveedor de LLM y modelo.
- Ejecuta `init_db()` para inicializar la base de datos.
- Si hay error, lo loguea y relanza la excepción.

En el shutdown:
- Loguea que la app se está cerrando.

Este lifespan se pasa al crear la app:
```python
app = FastAPI(..., lifespan=lifespan)
```

## 4. Configuración de la app FastAPI
```python
app = FastAPI(
    title="AI Tutoring System for Optimization Methods",
    description="Backend API ...",
    version=settings.version,
    debug=settings.debug,
    lifespan=lifespan
)
```

Luego:
- CORS abierto (para cualquier origen, método y header):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Incluye rutas de administración:
```python
app.include_router(admin.router)
```

## 5. Endpoint de salud /health
```python
@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
```

- Prueba la conexión a la BD con SELECT 1.
- Devuelve:
  - `status`: "healthy" o "degraded" según si la query funciona.
  - `version`: de `settings`
  - `llm_provider`
  - `database_connected`: `True/False`

## 6. Autenticación
### 6.1 Registro `/auth/register`
```python
@app.post("/auth/register", response_model=TokenResponse)
async def register(user_data: StudentRegister, db: Session = Depends(get_db)):
```
Flujo:
1. Comprueba si el email ya existe.
2. Crea un Student:
   - `name`, `email`
   - `password_hash` usando `get_password_hash`
   - `role = UserRole.USER`
   - `is_active = True`
   - `knowledge_levels` por defecto en “beginner” para varios temas.
3. Guarda en la BD.
4. Crea un JWT con `create_access_token`.
5. Devuelve `TokenResponse` con:
   - `access_token`
   - datos del usuario (`StudentResponse`).

### 6.2 Login `/auth/login
```python
@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: StudentLogin, db: Session = Depends(get_db)):
```

- Autentica con `authenticate_user(email, password)`.
- Si falla → `401 Unauthorized`.
- Si ok:
  - Actualiza `last_login`.
  - Crea token JWT.
  - Devuelve `TokenResponse`.

### 6.3 Usuario actual `/auth/me`
```python
@app.get("/auth/me", response_model=StudentResponse)
async def get_me(current_user: Student = Depends(get_current_user)):
```
- Usa la dependencia `get_current_user` (lee y valida JWT del header).
- Devuelve el usuario actual.

## 7. Endpoints de estudiantes
### Crear estudiante (sin auth) `/students` (POST)
```python
@app.post("/students", response_model=StudentResponse)
async def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
```
- Similar al registro, pero:
  - No maneja password ni roles.
  - Usa `knowledge_levels` y `preferences` enviados o defaults “beginner”.

```note
Ojo: este endpoint no está protegido; si se usa en producción, quizá debería requerir admin o integrarse con /auth/register.
```

### Obtener estudiante por ID /students/{student_id} (GET)
Protegido por `get_current_user`. Lógica de autorización:
- Si el usuario actual **no es** el `student_id` y **no es** `admin → 403`.
Si existe el estudiante → lo devuelve; si no → 404.

### Actualizar estudiante `/students/{student_id}` (PUT)
- Solo el propio usuario puede actualizar su perfil (no se permite ni para admin aquí).
- Actualiza campos opcionales: name, email, knowledge_levels, preferences.

### Listar estudiantes `/students (GET)`
- Devuelve lista paginada (skip, limit).
- Comentado el `current_admin`: está pensado para ser solo admin, pero ahora mismo no está restringido (podría ser un detalle a corregir).

## 8. Chat con el tutor IA `/chat`
```python
@app.post("/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, db: Session = Depends(get_db), current_user: Student = Depends(get_current_user)):
```
Flujo completo:
1. Usa el current_user.id como student_id.
2. Si viene conversation_id, intenta recuperar esa conversación activa (`is_active == 1`).
3. Si no existe, crea una nueva Conversation con:
   - `student_id`
   - `topic` (enum de `chat_request.topic`)
4. Verifica que la conversación pertenece al usuario actual → si no, 403.
5. Guarda el mensaje del usuario en Message:
   - `role="user"`
   - `content=chat_request.message`
6. Obtiene el agente adecuado:
    ```python
    topic_value = chat_request.topic.value
    agent = get_agent_for_topic(topic_value)
    ```
7. `Usa conversation_service` para:
   - Obtener histórico de la conversación.
   - Obtener contexto del estudiante para ese topic.
8. Llama a `agent.generate_response(...)` para producir el texto de IA.
9. Manejo de errores:
   - Si algo falla, responde con texto de error “genérico” y agent_type="error".
10. Guarda el mensaje de la IA en Message:
    - `role="assistant"`
    - `content=response_text`
    - `agent_type` (tipo de agente usado).
11. Devuelve `ChatResponse` con:
    - `conversation_id`
    - `message_id`
    - `response`
    - `agent_type`
    - `topic`
    - `timestamp`

## 9. Conversaciones
### Obtener una conversación `/conversations/{conversation_id}`
- Busca la `Conversation`.
- Si no existe → `404`.
- Autoriza:
  - Solo el dueño o un admin puede verla.
  - Recupera todos los `Message` ordenados por tiempo.
- Devuelve `ConversationResponse` con la lista de mensajes.

### Conversaciones de un estudiante `/students/{student_id}/conversations`
- Autoriza: el propio estudiante o admin.
- Devuelve todas las conversaciones del estudiante ordenadas por started_at descendente.

## 10. Feedback `/feedback`
```python
@app.post("/feedback", response_model=FeedbackResponse)
async def create_feedback(feedback_data: FeedbackCreate, ...)
```
- Verifica que el `Message` existe.
- Crea un `Feedback`:
  - `message_id`
  - `student_id = current_user.id`
  - `rating`
  - `is_helpful` (mapea booleano a 0/1/None)
  - `comment`
- Devuelve `FeedbackResponse`.

Sirve para evaluar la calidad de las respuestas de la IA.

## 11. Progreso del estudiante `/students/{student_id}/progress`
- Autoriza: el propio estudiante o admin.
- Verifica que el estudiante existe.
- Usa `conversation_service.compute_student_progress(student_id)` para generar métricas agregadas (por ejemplo, número de sesiones, dificultades, etc., según se defina en el servicio).
- Devuelve un `ProgressResponse`.

## 12. Evaluaciones (Assessments)
### 12.1 Listar evaluaciones de un estudiante
`GET /students/{student_id}/assessments`
- Autoriza: propio estudiante o admin.
- Opcionalmente filtra por `topic`.
- Usa paginación (`skip`, `limit`).
- Devuelve lista de `AssessmentResponse`.

### 12.2 Obtener una evaluación
`GET /assessments/{assessment_id}`
- Verifica que existe.
- Solo dueño o admin puede verla.
- Devuelve `AssessmentResponse`.

### 12.3 Generar evaluación
`POST /assessments/generate`
- Solo para usuario autenticado; usa `current_user.id`.
- Opcionalmente, asocia una conversación (`conversation_id`):
  - Verifica que exista.
  - Verifica que pertenezca al usuario.
- Usa `assessment_service.generate_personalized_assessment(...)` con:
  - `student_id`
  - `topic`
  - `difficulty` (string desde enum)
  - `conversation_id` (para personalizar según chat previo).
- Espera un `dict` con:
  - `question`
  - `correct_answer`
  - `rubric`
  - `metadata`
- Si falla, crea una pregunta de fallback simple.
- Crea Assessment con:
  - `max_score` = 7.0 por defecto.
  - `extra_data = metadata + difficulty`.
- Devuelve `AssessmentResponse`.

### 12.4 Enviar respuesta de evaluación (auto‐corregida)
`POST /assessments/{assessment_id}/submit`
- Verifica que la evaluación exista.
- Solo el dueño puede enviar (`student_id == current_user.id`).
- Si ya fue enviada (`submitted_at` no es `None`) → error.
- Guarda:
  - `student_answer`
  - `submitted_at = now()`
- Luego intenta auto-calificar:
  - Usa `grading_service.grade_assessment(assessment)` → (score, feedback).
  - Guarda `score, feedback, graded_at, graded_by = GradingSource.AUTO`.
- Si falla el grading:
  - Deja la evaluación enviada pero sin calificar.

### 12.5 Calificar / sobrescribir calificación (admin)
POST `/assessments/{assessment_id}/grade`

- Solo admin (`get_current_admin_user`).
- Verifica existencia y que ya esté enviada.
- Permite:
  - Establecer `score`
  - Opcionalmente cambiar `max_score`
  - Opcionalmente `feedback`
- Marca:
  - `graded_by = GradingSource.ADMIN`
  - `graded_at = now()`
- Si ya estaba calificada y fue auto (AUTO), registra `overridden_at = now()`.

## 13. Endpoint raíz /
Devuelve un JSON simple:
```json
{
  "message": "AI Tutoring System for Optimization Methods",
  "version": ...,
  "docs": "/docs",
  "health": "/health"
}
```

Facilita descubrir la API.

## 14. Ejecución directa con Uvicorn
Al final:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=settings.debug
    )
```

Permite ejecutar la app con `python -m app.main` (o similar) sin tener que llamar a uvicorn manualmente.

## 15. Resumen conceptual
En pocas palabras, el `main.py`:

- Orquesta todo el backend:
  - Autenticación y usuarios,
  - Chat con agentes de IA específicos por tema,
  - Gestión de conversaciones y feedback,
  - Seguimiento de progreso,
  - Generación y corrección (auto y manual) de evaluaciones.
- Se apoya en:
  - Modelos Pydantic para requests/responses limpios.
  - SQLAlchemy para persistencia.
  - Servicios (`conversation_service`, `assessment_service`, `grading_service`) para encapsular lógica compleja.
  - Agentes LLM para generar respuestas y evaluaciones personalizadas.