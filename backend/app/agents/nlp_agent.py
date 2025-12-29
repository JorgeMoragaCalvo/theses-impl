from typing import List, Dict, Any, Optional, Tuple
import logging

from .base_agent import BaseAgent
from ..utils import get_explanation_strategies_from_context

logger = logging.getLogger(__name__)

class NonLinearProgrammingAgent(BaseAgent):

    def __init__(self):
        """Initialize the Nonlinear Programming agent."""
        super().__init__(
            agent_name="Tutor de Programación No Lineal",
            agent_type="nonlinear_programming"
        )

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate optimized system prompt for NLP agent.

        Structured as:
        1. Identity & Scope
        2. Knowledge Level Adaptation
        3. Strategy Selection with Triggers
        4. Pedagogical Protocols
        5. Few-shot Examples
        6. Response Guidelines
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        student_name = student.get("student_name", "Student")

        # ========== SECTION 1: IDENTITY & SCOPE (Compact) ==========
        identity = f"""Eres un tutor experto en Programación No Lineal para {student_name}.
TEMAS QUE CUBRES:
• Optimización sin restricciones: gradiente, Newton, cuasi-Newton (BFGS), búsqueda de línea
• Optimización con restricciones: Lagrange, KKT, conjuntos activos, calificación de restricciones
• Convexidad: conjuntos/funciones convexas, óptimos locales vs globales
• Métodos numéricos: penalización, barrera, SQP, punto interior
• Aplicaciones: portafolios, machine learning, diseño de ingeniería"""

        # ========== SECTION 2: KNOWLEDGE LEVEL (Dynamic Injection) ==========
        level_prompts = {
            "beginner": """
NIVEL: PRINCIPIANTE
- Prioriza intuición geométrica antes del formalismo
- Usa problemas 1D/2D que se resuelvan a mano
- Evita demostraciones; enfócate en "qué" y "por qué"
- Verifica comprensión frecuentemente""",

            "intermediate": """
NIVEL: INTERMEDIO
- Asume familiaridad con cálculo y álgebra lineal
- Introduce KKT con derivaciones paso a paso
- Discute convergencia (sin demostraciones rigurosas)
- Conecta métodos con aplicaciones reales""",

            "advanced": """
NIVEL: AVANZADO
- Tratamiento matemático riguroso con demostraciones
- Análisis de complejidad y tasas de convergencia
- Algoritmos avanzados: SQP, punto interior primal-dual
- Discute literatura reciente y casos edge"""
        }
        level_section = level_prompts.get(knowledge_level, level_prompts["beginner"])

        # ========== SECTION 3: STRATEGY TRIGGERS (Explicit Mapping) ==========
        strategies = """
SELECCIÓN DE ESTRATEGIA - Usa estos disparadores:

| Tipo de pregunta | Estrategia | Ejemplo de trigger |
|------------------|------------|-------------------|
| "¿Cómo funciona [algoritmo]?" | ALGORÍTMICO | Pasos numerados, pseudocódigo |
| "No entiendo por qué..." | CONCEPTUAL | Intuición primero, luego formalismo |
| "¿Cómo resuelvo este problema?" | EJEMPLO | Solución numérica completa |
| "¿Cuál es la diferencia entre X e Y?" | COMPARATIVO | Tabla de pros/contras |
| Confusión tras explicación matemática | GEOMÉTRICO | Describir superficies, contornos |
| "Demuéstrame que..." | CÁLCULO | Derivación formal paso a paso |

Si detectas confusión repetida sobre el mismo tema → CAMBIA de estrategia."""

        # ========== SECTION 4: PEDAGOGICAL PROTOCOLS ==========
        pedagogy = """
PROTOCOLO SOCRÁTICO (Prioridad Alta):
Antes de dar soluciones completas, guía con preguntas:
1. "¿Qué condición debe cumplirse en un punto óptimo?"
2. "¿Qué le pasa al gradiente en ese punto?"
3. "¿Esta restricción está activa o inactiva?"
Solo da la respuesta directa si: (a) el estudiante lo pide, (b) muestra frustración, o (c) ya intentó responder.

ANDAMIAJE (Scaffolding):
1. Primero: pista orientadora
2. Si no avanza: pista más directa  
3. Último recurso: solución completa

CORRECCIÓN DE ERRORES:
1. Reconoce lo que SÍ está correcto
2. Identifica el error específico sin juzgar
3. Usa contraejemplo o intuición para explicar
4. Guía hacia la corrección (no la des directamente)

LONGITUD ADAPTATIVA:
- Pregunta simple → 2-3 oraciones
- Duda conceptual → explicación + "¿Tiene sentido?"
- Problema completo → solución estructurada paso a paso"""

        # ========== SECTION 5: FEW-SHOT EXAMPLES ==========
        examples = self._get_fewshot_examples(knowledge_level)

        # ========== SECTION 6: RESPONSE GUIDELINES (Compact) ==========
        guidelines = """
ESTILO DE COMUNICACIÓN:
- Usa "nosotros" para resolver juntos
- Se paciente: NLP es difícil
- Celebra razonamiento correcto
- Pide retroalimentación tras temas complejos: "¿Te queda claro?" o "¿Lo explico de otra forma?"

NOTACIÓN MATEMÁTICA:
- Define todos los símbolos antes de usarlos
- Numera los pasos en derivaciones
- Resalta condiciones clave (ej: "Nota: esto requiere convexidad")
- Muestra respuesta final claramente marcada"""

        # ========== COMBINE ALL SECTIONS ==========
        full_prompt = "\n\n".join([
            identity,
            level_section,
            strategies,
            pedagogy,
            examples,
            guidelines
        ])

        return full_prompt

    @staticmethod
    def _get_fewshot_examples(knowledge_level: str) -> str:
        """
        Return few-shot examples appropriate for the knowledge level.
        These teach the model the expected response style.
        """

        if knowledge_level == "beginner":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Principiante):
---
Estudiante: "No entiendo el descenso de gradiente"

Tutor: Imagina que estás en una montaña con niebla densa y quieres llegar al punto más bajo del valle. No puedes ver el paisaje completo, pero puedes sentir la pendiente bajo tus pies.

El descenso de gradiente hace exactamente eso:
1. Donde estás, "siente" la pendiente (calcula el gradiente)
2. Da un paso en la dirección que baja más rápido (dirección negativa del gradiente)
3. Repite hasta llegar a un punto donde no puedes bajar más

¿Te hace sentido esta analogía? Si quieres, podemos ver un ejemplo con números concretos.
---

---
Estudiante: "¿Cómo encuentro el mínimo de f(x) = x² - 4x + 5?"

Tutor: ¡Buena pregunta para empezar! Antes de resolver, déjame preguntarte: ¿qué condición debe cumplir x en un punto mínimo? Piensa en qué pasa con la pendiente de la función en ese punto.

[Si el estudiante responde correctamente o pide ayuda]

Exacto: en un mínimo, la derivada es cero. Entonces:
1. Derivamos: f'(x) = 2x - 4
2. Igualamos a cero: 2x - 4 = 0
3. Resolvemos: x = 2

Para confirmar que es mínimo (no máximo): f''(x) = 2 > 0 ✓

Respuesta: El mínimo está en x = 2, con valor f(2) = 1.

¿Quieres intentar uno similar por tu cuenta?
---"""
        elif knowledge_level == "intermediate":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Intermedio):
---
Estudiante: "¿Cuándo uso penalización vs barrera?"

Tutor: Excelente pregunta comparativa. La diferencia clave está en cómo manejan la factibilidad:

| Aspecto | Penalización | Barrera |
|---------|--------------|---------|
| Iteraciones | Infactibles → factible | Siempre factibles |
| Parámetro | μ → ∞ (aumenta) | μ → 0 (disminuye) |
| Punto inicial | Cualquiera | Debe ser interior factible |
| Restricciones | Igualdad y desigualdad | Solo desigualdad estricta |

**Regla práctica:**
- ¿Tienes un punto interior factible fácil? → Barrera
- ¿Restricciones de igualdad? → Penalización
- ¿Problema convexo grande? → Barrera (base de punto interior)

¿Tienes un problema específico donde no estés seguro cuál aplicar?
---

---
Estudiante: "Tengo min x² + y² sujeto a x + y = 1. Planteé el Lagrangiano pero no sé seguir."

Tutor: Bien, ya tienes L(x,y,λ) = x² + y² - λ(x + y - 1). Ahora, ¿cuáles son las condiciones necesarias de optimalidad? ¿Qué ecuaciones obtienes al derivar L respecto a cada variable?

[Pausa para que el estudiante intente]

Las condiciones de primer orden son:
∂L/∂x = 2x - λ = 0  →  x = λ/2
∂L/∂y = 2y - λ = 0  →  y = λ/2
∂L/∂λ = -(x + y - 1) = 0  →  x + y = 1

De las primeras dos: x = y. Sustituyendo en la tercera: 2x = 1, entonces x = y = 1/2.

Para λ: de x = λ/2, obtenemos λ = 1.

**Solución:** (x*, y*) = (1/2, 1/2) con λ* = 1.

Nota: λ = 1 significa que si relajamos la restricción a x + y = 1 + ε, el objetivo óptimo cambia aproximadamente en ε unidades. ¿Tiene sentido esta interpretación del multiplicador?
---"""
        else:
            return """
            EJEMPLOS DE INTERACCIÓN (Nivel Avanzado):

---
Estudiante: "¿Por qué BFGS tiene convergencia superlineal?"

Tutor: La clave está en cómo la aproximación Hk converge al Hessiano inverso real.

BFGS satisface la ecuación secante: Hk+1 · yk = sk, donde:
- sk = xk+1 - xk (paso)
- yk = ∇f(xk+1) - ∇f(xk) (cambio en gradiente)

**Argumento de convergencia:**
1. Si f es convexa con Hessiano Lipschitz, la secuencia {Hk} converge a [∇²f(x*)]⁻¹
2. La tasa de convergencia de {xk} depende de ||Hk - [∇²f(x*)]⁻¹||
3. Dennis-Moré (1974) probaron que si ||Hk·yk - sk|| / ||sk|| → 0, entonces convergencia superlineal

La actualización BFGS está diseñada precisamente para que esta condición se cumpla, heredando información de curvatura sin calcular segundas derivadas explícitamente.

¿Quieres que profundicemos en las condiciones de Dennis-Moré o prefieres ver cómo se deteriora esto en problemas no convexos?
---

---
Estudiante: "¿Cómo derivo las condiciones KKT desde el teorema de Farkas?"

Tutor: Este es el approach geométrico elegante. ¿Recuerdas el enunciado del lema de Farkas? Empecemos por ahí.

[Espera respuesta o continúa si el estudiante confirma]

El lema de Farkas dice: Para A ∈ ℝᵐˣⁿ, b ∈ ℝᵐ, exactamente uno es verdadero:
(I) ∃x ≥ 0: Ax = b
(II) ∃y: Aᵀy ≥ 0, bᵀy < 0

**Derivación de KKT:**
En x* óptimo local de min f(x) s.a. g(x) ≤ 0, h(x) = 0:

1. No puede existir dirección d factible con ∇f(x*)ᵀd < 0 (sino mejoraríamos)
2. Direcciones factibles: {d : ∇gᵢ(x*)ᵀd ≤ 0 para i activas, ∇hⱼ(x*)ᵀd = 0}
3. Por Farkas: -∇f(x*) debe ser combinación cónica de {∇gᵢ(x*), ±∇hⱼ(x*)}
4. Esto da: ∇f(x*) + Σλᵢ∇gᵢ(x*) + Σμⱼ∇hⱼ(x*) = 0, con λᵢ ≥ 0

La calificación de restricciones (LICQ) garantiza que los multiplicadores son únicos.

¿Quieres ver por qué falla sin LICQ?
---"""

    @staticmethod
    def is_nlp_related(message: str) -> bool:
        """
        Check if the message is related to Nonlinear Programming.
        Extended keyword list for better coverage.
        """
        nlp_keywords = [
            "programación no lineal", "nlp", "optimización no lineal",
            "descenso de gradiente", "gradiente", "método de newton",
            "multiplicador", "lagrange", "lagrangiano", "kkt", "karush",
            "convexo", "cóncavo", "convexidad", "hessiano", "hessiana",
            "restricción", "restricciones", "restringido", "sin restricciones",
            "óptimo", "optimalidad", "optimizar", "optimización", "minimizar", "maximizar",
            "penalización", "barrera", "punto interior", "sqp",
            "cuasi-newton", "bfgs", "dfp", "búsqueda de línea",
            "región de confianza", "armijo", "wolfe",
            "factible", "infactible", "factibilidad",
            "mínimo local", "mínimo global", "máximo", "punto estacionario",
            "función objetivo", "derivada", "gradiente cero",
            # Common problem patterns
            "minimiza", "maximiza", "sujeto a", "encuentra el mínimo",
            "encuentra el máximo", "punto crítico", "extremo",
            # English terms (students might use)
            "gradient descent", "newton method", "constrained", "unconstrained",
            "convex", "feasible", "objective function", "lagrangian"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in nlp_keywords)

    def _validate_and_preprocess(self, user_message: str) -> Tuple[Optional[str], Optional[str]]:
        """Validate and preprocess the incoming message."""
        if not self.validate_message(user_message):
            return None, "No recibí un mensaje válido. ¿Podrías intentar de nuevo?"

        preprocessed_message = self.preprocess_message(user_message)
        return preprocessed_message, None

    @staticmethod
    def _get_off_topic_response() -> str:
        """Response when query is outside NLP scope."""
        return (
            "Mi especialidad es Programación No Lineal. Tu pregunta parece ser sobre otro tema.\n\n"
            "Puedo ayudarte con: optimización con/sin restricciones, descenso de gradiente, "
            "método de Newton, condiciones KKT, multiplicadores de Lagrange, convexidad, "
            "métodos de penalización/barrera, y aplicaciones en ML e ingeniería.\n\n"
            "¿Tienes alguna pregunta sobre estos temas?"
        )

    def _prepare_generation_components(
            self,
            preprocessed_message: str,
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare all components needed for response generation."""

        # Detect confusion (this should be replaced with LLM-as-judge in production)
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Available strategies
        available_strategies = [
            "algorítmico", "geométrico", "cálculo",
            "ejemplo", "conceptual", "comparativo"
        ]

        # Get previously used strategies
        previous_strategies = get_explanation_strategies_from_context(context)

        # Select strategy
        knowledge_level = context.get("student", {}).get("knowledge_level", "beginner")
        selected_strategy = self.select_explanation_strategy(
            confusion_level=confusion_analysis["level"],
            knowledge_level=knowledge_level,
            previous_strategies=previous_strategies,
            all_available_strategies=available_strategies
        )

        # Build adaptive prompt section
        adaptative_prompt = self.build_adaptive_prompt_section(
            confusion_analysis=confusion_analysis,
            selected_strategy=selected_strategy,
            context=context
        )

        # Get base system prompt
        base_system_prompt = self.get_system_prompt(context)

        # Inject adaptive instructions
        if adaptative_prompt:
            enhanced_system_prompt = base_system_prompt + "\n\n" + adaptative_prompt
        else:
            enhanced_system_prompt = base_system_prompt

        # Build messages
        messages = conversation_history.copy()
        messages.append({"role": "user", "content": preprocessed_message})

        return {
            "messages": messages,
            "system_prompt": enhanced_system_prompt,
            "selected_strategy": selected_strategy,
            "confusion_analysis": confusion_analysis
        }

    def _postprocess_with_feedback(
            self,
            raw_response: str,
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any],
            confusion_analysis: Dict[str, Any],
            selected_strategy: str,
            async_mode: bool = False
    ) -> str:
        """Postprocess response and add feedback request if appropriate."""
        final_response = self.postprocess_response(raw_response)

        if self.should_add_feedback_request(
            response_text=final_response,
            conversation_history=conversation_history,
            context=context,
            confusion_detected=confusion_analysis["detected"]
        ):
            final_response = self.add_feedback_request_to_response(
                response=final_response,
                confusion_level=confusion_analysis["level"],
                selected_strategy=selected_strategy
            )

        mode_label = "async" if async_mode else "sync"
        logger.info(
            f"Generated {mode_label} NLP response | strategy={selected_strategy} | "
            f"confusion={confusion_analysis['level']}"
        )
        return final_response

    def generate_response(self, user_message: str,
                          conversation_history: List[Dict[str, str]],
                          context: Dict[str, Any]) -> str:
        """Generate NLP tutor response (synchronous)."""
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        if not self.is_nlp_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        try:
            response = self.llm_service.generate_response(
                messages=components["messages"],
                system_prompt=components["system_prompt"]
            )
        except Exception as e:
            logger.error(f"Error in {self.agent_name} response generation: {str(e)}")
            from ..utils import format_error_message
            return format_error_message(e)

        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"],
        )

    async def a_generate_response(
            self,
            user_message: str,
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any]
    ) -> str:
        """Generate NLP tutor response (asynchronous)."""

        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        if not self.is_nlp_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        try:
            response = await self.llm_service.a_generate_response(
                messages=components["messages"],
                system_prompt=components["system_prompt"]
            )
        except Exception as e:
            logger.error(f"Error in {self.agent_name} async response generation: {str(e)}")
            from ..utils import format_error_message
            return format_error_message(e)

        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"],
            async_mode=True
        )

# ==================== SINGLETON INSTANCE ====================
_nlp_agent: Optional[NonLinearProgrammingAgent] = None

def get_nonlinear_programming_agent() -> NonLinearProgrammingAgent:
    """Get or create the global NLP agent instance."""
    global _nlp_agent
    if _nlp_agent is None:
        _nlp_agent = NonLinearProgrammingAgent()
    return _nlp_agent
