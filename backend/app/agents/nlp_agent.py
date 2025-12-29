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

# 2. Proactive Alternative Offering
#
#   From original (lines 213-214):
#   """
#   - Ofrecer opciones cuando un estudiante se bloquea:
#     "Puedo mostrarte un ejemplo, explicarte el algoritmo o explicarte la intuición"
#   """
#
#   Why it matters: Instead of just switching strategies internally, this explicitly empowers the student to choose their preferred learning path.
#
#   Recommendation: Add to the Scaffolding protocol:
#   ANDAMIAJE (Scaffolding):
#   1. Primero: pista orientadora
#   2. Si no avanza: pista más directa
#   3. Si sigue bloqueado: OFRECER OPCIONES EXPLÍCITAS:
#      "Puedo: (a) mostrarte un ejemplo numérico, (b) explicar el algoritmo paso a paso,
#       o (c) darte la intuición geométrica. ¿Qué prefieres?"
#   4. Último recurso: solución completa
#
#   ---
#   3. Mathematical Verification Step
#
#   From original (lines 248-249):
#   """
#   4. Verificar la optimalidad/corrección
#   """
#
#   Why it matters: For optimization problems, verifying the solution (checking KKT conditions, second-order conditions, etc.) is pedagogically important.
#
#   Recommendation: Add to the response structure guidelines:
#   ESTRUCTURA DE RESPUESTA MATEMÁTICA:
#   1. Plantear el problema
#   2. Resolver paso a paso
#   3. **VERIFICAR:** Comprobar condiciones de optimalidad
#      - ¿Se cumple ∇L = 0?
#      - ¿Son los multiplicadores ≥ 0?
#      - ¿Es el Hessiano definido positivo?
#   4. Interpretar el resultado
#   5. Pedir retroalimentación
#
#   ---
#   4. Richer Strategy Descriptions (Selective)
#
#   From original (lines 179-207): The original has detailed "Ideal for" and "Show" guidance for each strategy.
#
#   Recommendation: Expand the strategy table with a third column for key action:
#
#   | Tipo de pregunta | Estrategia | Acción clave |
#   |------------------|------------|--------------|
#   | "¿Cómo funciona [algo]?" | ALGORÍTMICO | Pseudocódigo numerado |
#   | "No entiendo por qué..." | CONCEPTUAL | Analogía → formalismo |
#   | "¿Cómo resuelvo...?" | EJEMPLO | Números reales, todos los pasos |
#   | "¿Diferencia entre X e Y?" | COMPARATIVO | Tabla pros/contras |
#   | Confusión post-matemática | GEOMÉTRICO | Describir superficie/contornos |
#   | "Demuéstrame que..." | CÁLCULO | Derivación formal rigurosa |
#
#   ---
#   5. Response Structure Template
#
#   From original (lines 244-251):
#   """
#   Ejemplo de estructura de respuesta:
#   1. Reconocer la pregunta/problema
#   2. Proporcionar una explicación
#   3. Mostrar la solución paso a paso
#   4. Verificar la optimalidad/corrección
#   5. Solicitar retroalimentación
#   6. Ofrecer práctica de seguimiento
#   """
#
#   Recommendation: Add a compact version to nlp_agent.py:
#   PLANTILLA DE RESPUESTA:
#   1. Reconocer → 2. Explicar → 3. Resolver → 4. Verificar → 5. "¿Te queda claro?" → 6. Sugerir práctica
#
#   ---
#   Part 2: New Recommendations for nlp_agent.py
#
#   6. Add Meta-Cognitive Prompts
#
#   Purpose: Help students develop problem-solving skills, not just get answers.
#
#   Recommendation:
#   DESARROLLO DE METACOGNICIÓN:
#   Ocasionalmente preguntar:
#   - "¿Qué tipo de problema es este? ¿Con o sin restricciones?"
#   - "¿Qué método elegirías y por qué?"
#   - "¿Qué pasaría si la función no fuera convexa?"
#   - "¿Cómo sabrías si tu solución es correcta?"
#
#   ---
#   7. Problem Classification Guide
#
#   Purpose: Help the tutor guide students in recognizing problem types.
#
#   Recommendation:
#   CLASIFICACIÓN DE PROBLEMAS (para guiar al estudiante):
#   | Características | Tipo | Método sugerido |
#   |-----------------|------|-----------------|
#   | Sin restricciones, f diferenciable | Unconstrained | Gradiente/Newton |
#   | Solo igualdades | Equality-constrained | Lagrange |
#   | Desigualdades presentes | Inequality-constrained | KKT |
#   | f o g no convexas | Non-convex | Múltiples inicios, cautela |
#   | Problema grande | Large-scale | L-BFGS, punto interior |
#
#   ---
#   8. Common Misconceptions Section
#
#   Purpose: Proactively address typical student errors.
#
#   Recommendation:
#   ERRORES COMUNES A ANTICIPAR:
#   1. Confundir mínimo local con global (recordar: solo garantizado si convexo)
#   2. Olvidar verificar λ ≥ 0 en KKT
#   3. Aplicar Lagrange a desigualdades directamente
#   4. Confundir condiciones necesarias vs suficientes
#   5. Ignorar calificación de restricciones (LICQ)
#
#   Cuando detectes estos errores → usar contraejemplo, no solo corregir
#
#   ---
#   9. Expanded Keyword Detection
#
#   Current is_nlp_related() in new version is better, but could add:
#
#   # Additional keywords to consider:
#   "wolfe", "backtracking", "armijo",  # Line search
#   "lagrangiano aumentado", "augmented lagrangian",
#   "nelder-mead", "simplex method",  # Derivative-free
#   "slsqp", "ipopt", "scipy.optimize",  # Solvers
#   "portafolio", "markowitz",  # Applications
#   "norma", "distancia", "mínimos cuadrados"  # Common problem types
#
#   ---
#   10. Practice Problem Offering Protocol
#
#   Purpose: Actively support skill development through exercises.
#
#   Recommendation:
#   OFRECIMIENTO DE PRÁCTICA:
#   Después de explicar un concepto nuevo, ofrecer:
#   "¿Quieres intentar un problema similar? Puedo darte uno de nivel [fácil/medio/difícil]."
#
#   Formato de ejercicio:
#   1. Enunciado claro
#   2. Pistas disponibles si lo pide
#   3. Verificación de respuesta
#   4. Explicación de errores comunes en ese tipo de problema
#
#   ---
#   Part 3: Consolidated Prompt Structure Recommendation
#
#   Here's how I'd restructure get_system_prompt() with all improvements:
#
#   1. IDENTIDAD Y ALCANCE (current - keep compact)
#   2. NIVEL DE CONOCIMIENTO (current - keep)
#   3. TABLA DE ESTRATEGIAS (enhanced with action column)
#   4. SEÑALES DE CONFUSIÓN (new - from original)
#   5. PROTOCOLOS PEDAGÓGICOS:
#      - Socrático (current)
#      - Andamiaje (enhanced with explicit offering)
#      - Corrección de errores (current)
#      - Longitud adaptativa (current)
#   6. CLASIFICACIÓN DE PROBLEMAS (new)
#   7. ERRORES COMUNES (new)
#   8. METACOGNICIÓN (new)
#   9. EJEMPLOS FEW-SHOT (current - critical, keep)
#   10. ESTILO Y NOTACIÓN (current + verification step)
#   11. PLANTILLA DE RESPUESTA (from original, compacted)
#
#   ---
#   Priority Implementation Order
#
#   | Priority  | Recommendation                    | Impact | Effort |
#   |-----------|-----------------------------------|--------|--------|
#   | 🔴 High   | Confusion signals (from original) | High   | Low    |
#   | 🔴 High   | Proactive alternative offering    | High   | Low    |
#   | 🟡 Medium | Mathematical verification step    | Medium | Low    |
#   | 🟡 Medium | Common misconceptions section     | High   | Medium |
#   | 🟡 Medium | Enhanced strategy table           | Medium | Low    |
#   | 🟢 Low    | Meta-cognitive prompts            | Medium | Low    |
#   | 🟢 Low    | Problem classification guide      | Medium | Medium |
#   | 🟢 Low    | Practice problem protocol         | High   | Medium |
#
#   ---
#   Would you like me to create a plan file with the specific edits to implement these recommendations in nlp_agent.py?

# Yes, I understand completely. You have 5 standalone tutoring agents (Linear Programming, Integer Programming, Nonlinear Programming, Mathematical Modeling, Operations Research) and the student must manually select which one to use. This is indeed a basic architecture that doesn't demonstrate sophisticated multi-agent coordination.
#
#   For a thesis project, you need to show intelligent orchestration. Here are approaches from simpler to more advanced:
#
#   ---
#   Current State (Basic)
#
#   Student → Manual Selection → Agent 1
#                             → Agent 2
#                             → Agent 3
#                             → Agent 4
#                             → Agent 5
#
#   Problems:
#   - Student must know which topic their question belongs to
#   - No handling of cross-domain questions
#   - No coherent learning path
#   - No demonstration of multi-agent coordination
#
#   ---
#   Option 1: Intelligent Router Agent
#
#   Student → Router Agent → Specialist Agent → Response
#                 ↓
#           (Analyzes question,
#            selects best agent)
#
#   How it works:
#   - A lightweight "router" agent analyzes the student's question
#   - Uses classification (keywords, embeddings, or LLM) to select the appropriate specialist
#   - Routes transparently - student doesn't need to choose
#
#   Thesis value: Demonstrates automatic intent classification and agent selection.
#
#   ---
#   Option 2: Orchestrator with Context Awareness
#
#   Student → Orchestrator Agent → Specialist Agent(s)
#                 ↓                       ↓
#           Maintains session      Returns response
#           context, learning           ↓
#           history, decides     Orchestrator synthesizes
#           routing + follow-up        final response
#
#   How it works:
#   - Orchestrator maintains conversation state and student model
#   - Decides which specialist(s) to consult
#   - Can ask clarifying questions before routing
#   - Synthesizes responses if multiple agents contribute
#
#   Thesis value: Demonstrates stateful coordination, context-aware routing.
#
#   ---
#   Option 3: Hierarchical Multi-Agent System (Recommended for Thesis)
#
#                       ┌─────────────────────┐
#                       │   Meta-Tutor Agent  │
#                       │  (Orchestration +   │
#                       │   Pedagogy Control) │
#                       └──────────┬──────────┘
#                                  │
#             ┌────────────────────┼────────────────────┐
#             ↓                    ↓                    ↓
#       ┌───────────┐       ┌───────────┐       ┌───────────┐
#       │  Router   │       │ Student   │       │ Learning  │
#       │  Agent    │       │ Modeler   │       │ Path      │
#       │           │       │           │       │ Planner   │
#       └─────┬─────┘       └───────────┘       └───────────┘
#             │
#       ┌─────┴─────┬───────────┬───────────┬───────────┐
#       ↓           ↓           ↓           ↓           ↓
#     ┌───┐       ┌───┐       ┌───┐       ┌───┐       ┌───┐
#     │LP │       │IP │       │NLP│       │MM │       │OR │
#     └───┘       └───┘       └───┘       └───┘       └───┘
#
#   Components:
#
#   | Agent                 | Responsibility                                  |
#   |-----------------------|-------------------------------------------------|
#   | Meta-Tutor            | High-level orchestration, pedagogical decisions |
#   | Router                | Classifies questions, selects specialist(s)     |
#   | Student Modeler       | Tracks knowledge state, confusion, progress     |
#   | Learning Path Planner | Suggests next topics, identifies gaps           |
#   | Specialists (5)       | Deep domain expertise                           |
#
#   Thesis value: Full multi-agent architecture with clear separation of concerns.
#
#   ---
#   Option 4: Collaborative Agents with Cross-Consultation
#
#   Student: "How do I model this scheduling problem?"
#
#   Meta-Tutor → Router: "This involves modeling + integer programming"
#             → Calls Mathematical Modeling Agent: "Formulate the model"
#             → Calls Integer Programming Agent: "Explain binary variables for scheduling"
#             → Synthesizes both responses coherently
#
#   Key feature: Agents can be consulted in sequence or parallel for multi-domain questions.
#
#   Thesis value: Demonstrates agent collaboration, not just selection.
#
#   ---
#   My Recommendation for Your Thesis
#
#   I recommend Option 3 (Hierarchical) with elements of Option 4 (Collaboration). Here's why:
#
#   Academic Justification
#
#   | Aspect                   | How it strengthens your thesis                        |
#   |--------------------------|-------------------------------------------------------|
#   | Multi-agent coordination | Clear orchestration logic, not just manual selection  |
#   | Adaptive learning        | Student Modeler enables personalization               |
#   | Pedagogical control      | Meta-Tutor makes teaching decisions                   |
#   | Cross-domain handling    | Router + collaboration handles real student questions |
#   | Measurable outcomes      | Can evaluate routing accuracy, learning gains         |
#
#   Minimum Viable Architecture
#
#   For a practical thesis implementation, I'd suggest at minimum:
#
#   ┌─────────────────────────────────────────────────┐
#   │                 Orchestrator Agent              │
#   │  - Routes questions to specialists              │
#   │  - Maintains conversation context               │
#   │  - Tracks student knowledge state               │
#   │  - Makes pedagogical decisions (hints vs full)  │
#   └───────────────────────┬─────────────────────────┘
#                           │
#           ┌───────┬───────┼───────┬───────┐
#           ↓       ↓       ↓       ↓       ↓
#         [LP]    [IP]    [NLP]   [MM]    [OR]
#
#   This gives you:
#   1. Automatic routing (no manual selection)
#   2. Context-aware responses
#   3. Cross-domain question handling
#   4. Student modeling for adaptation
#   5. Clear thesis contribution: "Orchestrated multi-agent ITS for Operations Research"
#
#   ---
#   Questions to Clarify Your Direction
#
#   Before I create a detailed implementation plan, I need to understand:
#
#   1. Scope constraint: How much time do you have to implement this?
#     - Quick (1-2 weeks): Option 1 (Router only)
#     - Medium (3-4 weeks): Option 2 (Orchestrator)
#     - Full (5+ weeks): Option 3 (Hierarchical)
#   2. Cross-domain questions: How important is handling questions that span multiple topics (e.g., "How do I model this problem as an IP?")?
#   3. Student modeling depth: Do you want to track detailed knowledge per topic, or just basic routing?
#   4. Current infrastructure: Are you using LangChain, LangGraph, or plain Python for your agents?
#
# Yes, I understand perfectly! Right now your "agents" are essentially LLM wrappers with different prompts - they can only generate text. True agents have tools that let them take actions, compute results, and interact with the environment.
#
#   This is a critical improvement for your thesis. Let me map out appropriate tools for each agent:
#
#   ---
#   What Makes a "Real" Agent
#
#   Current State:                    True Agent:
#   ┌─────────────┐                  ┌─────────────────────────────┐
#   │   Prompt    │                  │         Agent               │
#   │      +      │       →          │  ┌─────────┐  ┌──────────┐  │
#   │    LLM      │                  │  │ Reasoning│  │  Tools   │  │
#   │             │                  │  │ (LLM)    │→ │ (Actions)│  │
#   └─────────────┘                  │  └─────────┘  └──────────┘  │
#      "Chatbot"                     └─────────────────────────────┘
#                                           "Agent"
#
#   ---
#   Tool Recommendations by Agent
#
#   1. Linear Programming Agent
#
#   | Tool                 | Purpose                                      | Implementation                       |
#   |----------------------|----------------------------------------------|--------------------------------------|
#   | solve_lp             | Solve LP problems, return optimal solution   | scipy.optimize.linprog or PuLP       |
#   | graphical_method     | Visualize 2D feasible region + optimal point | matplotlib polygon plotting          |
#   | simplex_tableau      | Step-by-step simplex iterations              | Custom implementation showing pivots |
#   | sensitivity_analysis | Analyze shadow prices, reduced costs, ranges | Post-solve analysis from solver      |
#   | dual_problem         | Generate and solve the dual LP               | Automatic dual formulation           |
#
#   Example interaction:
#   Student: "Solve max 3x + 2y subject to x + y ≤ 4, x ≤ 2, y ≤ 3"
#
#   Agent: [THINKS] This is a 2D LP, I'll use graphical_method for visualization
#          and solve_lp for the solution.
#
#          [CALLS solve_lp] → Returns: x*=2, y*=2, z*=10
#          [CALLS graphical_method] → Returns: Image of feasible region
#
#          "La solución óptima es x=2, y=2 con valor objetivo z=10.
#           [Shows graph] El punto óptimo está en el vértice donde
#           se intersectan x=2 y x+y=4."
#
#   ---
#   2. Integer Programming Agent
#
#   | Tool                  | Purpose                                   | Implementation                |
#   |-----------------------|-------------------------------------------|-------------------------------|
#   | solve_ip              | Solve IP/MIP problems                     | PuLP, OR-Tools, or scipy.milp |
#   | lp_relaxation         | Solve LP relaxation, show integrality gap | Compare LP vs IP solutions    |
#   | branch_and_bound_tree | Visualize B&B tree structure              | Custom tree visualization     |
#   | formulation_checker   | Validate IP formulation correctness       | Constraint analysis           |
#   | big_m_calculator      | Calculate appropriate Big-M values        | Based on variable bounds      |
#
#   Example interaction:
#   Student: "¿Por qué la relajación LP da x=1.5 pero necesito x entero?"
#
#   Agent: [CALLS lp_relaxation] → Shows LP solution with fractional values
#          [CALLS solve_ip] → Shows IP solution
#
#          "La relajación LP ignora la restricción de integralidad.
#           [Shows comparison table]
#           La brecha de integralidad es 12% en este caso."
#
#   ---
#   3. Nonlinear Programming Agent
#
#   | Tool                   | Purpose                                        | Implementation              |
#   |------------------------|------------------------------------------------|-----------------------------|
#   | solve_nlp              | Solve unconstrained/constrained NLP            | scipy.optimize.minimize     |
#   | compute_gradient       | Calculate gradient symbolically or numerically | sympy or finite differences |
#   | compute_hessian        | Calculate Hessian matrix                       | sympy or numerical          |
#   | check_convexity        | Verify if function is convex                   | Hessian eigenvalue analysis |
#   | plot_contours          | Visualize objective function landscape         | matplotlib contour plots    |
#   | verify_kkt             | Check KKT conditions for a point               | Symbolic verification       |
#   | gradient_descent_steps | Show step-by-step gradient descent             | Iterative visualization     |
#
#   Example interaction:
#   Student: "Minimiza f(x,y) = x² + y² - 2x - 4y"
#
#   Agent: [CALLS compute_gradient] → ∇f = [2x-2, 2y-4]
#          [CALLS compute_hessian] → H = [[2,0],[0,2]]
#          [CALLS check_convexity] → "Convex (H positive definite)"
#          [CALLS solve_nlp] → x*=1, y*=2, f*=-5
#          [CALLS plot_contours] → Shows contour plot with optimum
#
#          "Esta función es convexa (Hessiano definido positivo),
#           por lo que el punto estacionario es el mínimo global.
#           [Shows contour plot with gradient vectors]"
#
#   ---
#   4. Mathematical Modeling Agent
#
#   | Tool                | Purpose                                       | Implementation               |
#   |---------------------|-----------------------------------------------|------------------------------|
#   | validate_model      | Check model consistency (dimensions, indices) | Constraint/variable analysis |
#   | model_template      | Provide templates for common problems         | Template database            |
#   | latex_formatter     | Format model in publication-quality LaTeX     | String formatting            |
#   | constraint_analyzer | Identify constraint types and structure       | Pattern matching             |
#   | example_database    | Retrieve similar modeling examples            | Vector search or keyword     |
#
#   Example interaction:
#   Student: "Tengo trabajadores, turnos y demanda. ¿Cómo modelo esto?"
#
#   Agent: [CALLS model_template("scheduling")] → Returns scheduling template
#          [CALLS example_database("worker scheduling")] → Similar examples
#
#          "Este es un problema de programación de turnos.
#           La estructura típica es:
#           [Shows LaTeX formatted model template]
#
#           ¿Tienes restricciones adicionales como descansos o
#           habilidades de trabajadores?"
#
#   ---
#   5. Operations Research Agent (General/Router)
#
#   | Tool                 | Purpose                                   | Implementation         |
#   |----------------------|-------------------------------------------|------------------------|
#   | classify_problem     | Identify problem type (LP, IP, NLP, etc.) | LLM + keyword analysis |
#   | recommend_method     | Suggest appropriate solution approach     | Decision tree          |
#   | concept_explainer    | Retrieve concept explanations             | Knowledge base         |
#   | prerequisite_checker | Check if student has prerequisites        | Student model query    |
#
#   ---
#   6. Shared Tools (All Agents)
#
#   | Tool                | Purpose                                   | Implementation          |
#   |---------------------|-------------------------------------------|-------------------------|
#   | calculator          | Basic arithmetic and matrix operations    | numpy                   |
#   | symbolic_math       | Symbolic manipulation (derivatives, etc.) | sympy                   |
#   | generate_exercise   | Create practice problems                  | Parameterized templates |
#   | check_solution      | Verify student's proposed solution        | Compare with solver     |
#   | step_by_step_solver | Show solution process pedagogically       | Custom per method       |
#
#   ---
#   Architecture with Tools
#
#   ┌────────────────────────────────────────────────────────────────┐
#   │                      Orchestrator Agent                        │
#   │                                                                │
#   │  Tools: [classify_problem, recommend_method, route_to_agent]   │
#   └───────────────────────────┬────────────────────────────────────┘
#                               │
#          ┌──────────┬─────────┼─────────┬──────────┐
#          ↓          ↓         ↓         ↓          ↓
#   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
#   │ LP Agent │ │ IP Agent │ │NLP Agent │ │MM Agent  │ │OR Agent  │
#   ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤ ├──────────┤
#   │solve_lp  │ │solve_ip  │ │solve_nlp │ │validate  │ │classify  │
#   │graphical │ │relaxation│ │gradient  │ │template  │ │recommend │
#   │simplex   │ │branch_bb │ │hessian   │ │latex     │ │explain   │
#   │sensitivity│ │big_m    │ │convexity │ │examples  │ │prereq    │
#   │dual      │ │formulate │ │contours  │ │analyze   │ │          │
#   └──────────┘ └──────────┘ │kkt_check │ └──────────┘ └──────────┘
#                             │gd_steps  │
#                             └──────────┘
#
#   Shared Tools: [calculator, symbolic_math, generate_exercise,
#                  check_solution, step_by_step_solver]
#
#   ---
#   Priority Tools for Thesis Impact
#
#   If you have limited time, implement these high-impact tools first:
#
#   | Priority    | Tool                            | Agent       | Why                                          |
#   |-------------|---------------------------------|-------------|----------------------------------------------|
#   | 🔴 Critical | solve_lp / solve_ip / solve_nlp | LP, IP, NLP | Core functionality - actually solve problems |
#   | 🔴 Critical | graphical_method                | LP          | Visual learning, very impressive for demos   |
#   | 🔴 Critical | plot_contours                   | NLP         | Visualize optimization landscape             |
#   | 🟡 High     | check_solution                  | All         | Verify student work - key for ITS            |
#   | 🟡 High     | compute_gradient                | NLP         | Essential for teaching NLP                   |
#   | 🟡 High     | simplex_tableau                 | LP          | Step-by-step pedagogy                        |
#   | 🟢 Medium   | verify_kkt                      | NLP         | Demonstrate condition checking               |
#   | 🟢 Medium   | sensitivity_analysis            | LP          | Advanced LP understanding                    |
#   | 🟢 Medium   | generate_exercise               | All         | Adaptive practice                            |
#
#   ---
#   Questions for Implementation Planning
#
#   1. Tech stack preference?
#     - LangChain/LangGraph (built-in tool support)
#     - Plain Python with function calling
#     - Other framework?
#   2. Visualization output:
#     - Return image files?
#     - Interactive plots (Plotly)?
#     - ASCII/text representations?
#   3. Solver preferences:
#     - Open source only (SciPy, PuLP, OR-Tools)?
#     - Commercial allowed (Gurobi, CPLEX)?
#   4. Which agents are highest priority? Should all 5 have tools, or focus on 2-3?