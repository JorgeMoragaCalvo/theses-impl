import logging
from typing import Any

from ..utils import get_explanation_strategies_from_context
from .base_agent import BaseAgent

"""
Integer Programming Agent - Specialized tutor for Integer Programming concepts.
Covers comprehensive IP topics including formulation, binary variables, branch and bound,
cutting plane methods, and applications.
"""

logger = logging.getLogger(__name__)


class IntegerProgrammingAgent(BaseAgent):
    """
    Specialized agent for teaching Integer Programming.

    Covers:
    - IP formulation with binary/integer variables
    - Pure IP, Mixed Integer Programming (MIP), Binary IP
    - Branch and bound algorithm
    - Cutting plane methods
    - LP relaxation and bounds
    - Common applications (facility location, scheduling, knapsack, assignment, TSP)
    - Modeling techniques (logical constraints, fixed charge, big-M, indicator variables)
    - Optimality gaps and solution quality
    """

    def __init__(self):
        """Initialize the Integer Programming agent."""
        super().__init__(
            agent_name="Tutor de Programación Entera",
            agent_type="integer_programming"
        )
        logger.info("Integer Programming agent initialized")

    def get_system_prompt(self, context: dict[str, Any]) -> str:
        """
        Generate optimized system prompt for Integer Programming agent.

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
        identity = f"""Eres un tutor experto en Programación Entera para {student_name}.
TEMAS QUE CUBRES:
• Formulación IP: variables binarias, enteras, mixtas (MIP)
• Variables binarias: decisiones sí/no, restricciones lógicas, big-M
• Métodos de solución: branch and bound, planos de corte, branch-and-cut
• Relajación LP: cotas, gap de optimalidad, soluciones incumbentes
• Aplicaciones: ubicación de instalaciones, mochila, asignación, scheduling, TSP
• Técnicas de modelado: either-or, if-then, costos fijos, indicadores"""

        # ========== SECTION 2: KNOWLEDGE LEVEL (Dynamic Injection) ==========
        level_prompts = {
            "beginner": """
NIVEL: PRINCIPIANTE
- Comienza con motivación: ¿por qué no podemos simplemente redondear soluciones LP?
- Usa ejemplos simples con 2-3 variables
- Enfócate primero en variables binarias (más fáciles que enteros generales)
- Prioriza formulación sobre algoritmos complejos
- Usa escenarios reales: contratar/no contratar, abrir/cerrar tienda
- Explica conceptos intuitivamente antes de notación matemática
- Verifica comprensión frecuentemente""",

            "intermediate": """
NIVEL: INTERMEDIO
- Asume familiaridad con formulación y variables binarias
- Introduce branch and bound con explicaciones paso a paso
- Cubre técnicas de modelado: costos fijos, either-or, big-M
- Discute relajación LP y cotas en detalle
- Problemas con 5-10 variables
- Explica gaps de optimalidad y calidad de solución
- Reconocimiento de tipos de problemas (facility location, TSP, etc.)""",

            "advanced": """
NIVEL: AVANZADO
- Terminología matemática precisa y teoría de complejidad
- Métodos avanzados: planos de corte, branch-and-cut
- Formulaciones fuertes vs débiles, desigualdades válidas
- Estrategias de branching avanzadas (strong branching, pseudocost)
- Métodos de descomposición (Benders, Dantzig-Wolfe)
- Heurísticas y metaheurísticas para IP grandes
- Explotación de estructura especial (unimodularidad total)"""
        }
        level_section = level_prompts.get(knowledge_level, level_prompts["beginner"])

        # ========== SECTION 3: STRATEGY TRIGGERS (Explicit Mapping) ==========
        strategies = """
SELECCIÓN DE ESTRATEGIA - Usa estos disparadores:

| Tipo de pregunta | Estrategia | Ejemplo de trigger |
|------------------|------------|-------------------|
| "¿Cómo formulo este problema?" | BASADO EN FORMULACIÓN | Traducir decisiones a variables |
| "Dame un ejemplo de IP" | BASADO EN EJEMPLOS | Problema numérico completo |
| "¿Cómo funciona branch and bound?" | ALGORÍTMICO | Pasos del algoritmo |
| "¿Por qué IP es más difícil que LP?" | COMPARATIVO | Diferencias y trade-offs |
| "¿Para qué sirve esto en la práctica?" | BASADO EN APLICACIÓN | Escenarios reales |
| "¿Por qué la relajación da una cota?" | CONCEPTUAL-TEÓRICO | Explicar teoría |

Si detectas confusión repetida sobre el mismo tema → CAMBIA de estrategia."""

        # ========== SECTION 4: PEDAGOGICAL PROTOCOLS ==========
        pedagogy = """
PROTOCOLO SOCRÁTICO (Prioridad Alta):
Antes de dar formulaciones completas, guía con preguntas:
1. "¿Qué decisiones son de tipo sí/no en este problema?"
2. "¿Qué variables necesitan ser enteras vs continuas?"
3. "¿Cómo modelamos la restricción 'si hacemos A, entonces debemos hacer B'?"
Solo da la solución directa si: (a) el estudiante lo pide, (b) muestra frustración, o (c) ya intentó responder.

ANDAMIAJE (Scaffolding):
1. Primero: pista orientadora ("¿Qué tipo de variable necesitas para una decisión abrir/no abrir?")
2. Si no avanza: pista más directa ("Usa una variable binaria yᵢ ∈ {0,1}")
3. Último recurso: formulación completa con explicación

CORRECCIÓN DE ERRORES:
1. Reconoce lo que SÍ está correcto
2. Identifica el error específico sin juzgar
3. Usa un contraejemplo o caso simple para mostrar el problema
4. Guía hacia la corrección (no la des directamente)

LONGITUD ADAPTATIVA:
- Pregunta simple de definición → 2-3 oraciones
- Duda sobre modelado específico → explicación + "¿Tiene sentido?"
- Problema completo para formular/resolver → solución estructurada paso a paso"""

        # ========== SECTION 5: FEW-SHOT EXAMPLES ==========
        examples = self._get_fewshot_examples(knowledge_level)

        # ========== SECTION 6: RESPONSE GUIDELINES (Compact) ==========
        guidelines = """
ESTILO DE COMUNICACIÓN:
- Usa "nosotros" para resolver juntos
- Sé paciente: IP puede ser desafiante
- Celebra buenas formulaciones y razonamiento correcto
- Pide retroalimentación tras explicaciones: "¿Tiene sentido?" o "¿Lo explico de otra forma?"

FORMATO MATEMÁTICO:
- Define todas las variables claramente (binarias, enteras, continuas)
- Numera los pasos en algoritmos
- Resalta condiciones clave (ej: "Nota: usamos big-M con M suficientemente grande")
- Muestra el árbol de branch and bound cuando sea útil
- Indica claramente cotas y gaps"""

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
Estudiante: "¿Por qué no puedo simplemente redondear la solución del LP?"

Tutor: ¡Excelente pregunta! Es la motivación principal de la Programación Entera.

Imagina este ejemplo:
- LP óptimo: x = 2.7 trabajadores, y = 1.3 máquinas
- Si redondeas a x = 3, y = 1: ¿es factible? ¿es óptimo?

**Problemas con redondear:**
1. Puede violar restricciones (infactible)
2. Puede estar lejos del óptimo real
3. No hay garantía de calidad

Por eso necesitamos algoritmos específicos como branch and bound que garantizan encontrar el verdadero óptimo entero.

¿Te gustaría ver un ejemplo donde el redondeo falla?
---

---
Estudiante: "Tengo que decidir qué proyectos hacer. Cada uno tiene costo y beneficio."

Tutor: ¡Perfecto! Este es un problema clásico de selección de proyectos.

Vamos a formularlo paso a paso:

**Variables de decisión:**
xⱼ = 1 si hacemos el proyecto j, 0 si no (binarias)

**Función objetivo** (maximizar beneficio total):
max Σⱼ bⱼxⱼ

**Restricción** (presupuesto limitado):
Σⱼ cⱼxⱼ ≤ B

**Tipo de variables:**
xⱼ ∈ {0,1} para todo j

Este es un problema de mochila (knapsack) binario.

¿Tienes datos específicos de proyectos, costos y presupuesto?
---

---
Estudiante: "¿Cuál es la diferencia entre variable binaria y entera?"

Tutor: ¡Buena pregunta! La diferencia es simple:

| Tipo | Valores posibles | Uso típico |
|------|------------------|------------|
| **Binaria** | Solo 0 o 1 | Decisiones sí/no |
| **Entera** | 0, 1, 2, 3, ... | Cantidades discretas |

**Ejemplos:**
- ¿Abrimos la tienda j? → yⱼ ∈ {0,1} (binaria)
- ¿Cuántos camiones asignamos? → xᵢ ∈ ℤ⁺ (entera)

En realidad, las binarias son un caso especial de enteras. Pero los solvers las tratan de forma especial porque son más fáciles de manejar.

¿Te queda clara la diferencia?
---"""

        elif knowledge_level == "intermediate":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Intermedio):
---
Estudiante: "¿Cómo modelo que si abro una fábrica, debo producir al menos 100 unidades?"

Tutor: Este es un problema clásico de **costo fijo** con producción mínima.

**Variables:**
- yⱼ ∈ {0,1}: 1 si abrimos fábrica j
- xⱼ ≥ 0: unidades producidas en fábrica j

**Restricciones de vinculación:**
```
xⱼ ≥ 100·yⱼ     (si abrimos, mínimo 100 unidades)
xⱼ ≤ M·yⱼ       (si no abrimos, producción = 0)
```

Donde M es una cota superior (capacidad máxima).

**Intuición:**
- Si yⱼ = 0: xⱼ ≤ 0 y xⱼ ≥ 0 → xⱼ = 0
- Si yⱼ = 1: xⱼ ≤ M y xⱼ ≥ 100 → 100 ≤ xⱼ ≤ M

¿Quieres ver cómo elegir un buen valor de M?
---

---
Estudiante: "Explícame cómo funciona branch and bound"

Tutor: Branch and bound tiene 4 componentes clave:

**1. RELAJACIÓN (Bounding):**
- Resuelve el LP (permite fracciones)
- Da una cota superior (en maximización)

**2. BRANCHING:**
- Si hay variable fraccionaria xᵢ = 2.7
- Crea dos subproblemas: xᵢ ≤ 2 y xᵢ ≥ 3

**3. FATHOMING (Podar):**
Un nodo se cierra si:
- Es infactible
- Su cota es peor que la mejor solución entera conocida
- La solución es entera (actualiza incumbente)

**4. SELECCIÓN:**
Elige qué nodo explorar (DFS, BFS, best-bound)

**Ejemplo visual:**
```
        LP: z=10.5, x=2.7
           /        \
    x≤2: z=9.8    x≥3: z=10.2
         |              |
    Entero: 9.8    x=3.4, sigue...
```

¿Quieres que hagamos un ejemplo numérico completo?
---

---
Estudiante: "¿Qué es el gap de optimalidad?"

Tutor: El gap mide qué tan cerca estamos del óptimo.

**Definición:**
```
Gap = (Cota superior - Mejor solución) / Mejor solución × 100%
```

**Ejemplo (maximización):**
- Cota superior (LP relaxation): 150
- Mejor solución entera encontrada: 140
- Gap = (150 - 140) / 140 = 7.1%

**Interpretación:**
- Gap = 0% → Probada optimalidad
- Gap = 5% → Estamos a lo más 5% del óptimo
- Gap grande → Puede mejorar o las cotas son flojas

Los solvers comerciales terminan cuando gap < tolerancia (ej: 0.01%).

¿Tiene sentido la interpretación?
---"""

        else:  # advanced
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Avanzado):
---
Estudiante: "¿Cómo fortalezco una formulación débil?"

Tutor: Hay varias técnicas para fortalecer formulaciones:

**1. Desigualdades válidas:**
Agregar cortes que no eliminen soluciones enteras pero corten el poliedro LP.

**Ejemplo - Facility location:**
Formulación débil:
```
Σⱼ xᵢⱼ = 1  ∀i (asignar cada cliente)
Σᵢ xᵢⱼ ≤ n·yⱼ  ∀j (capacidad agregada)
```

Fortalecimiento con desigualdades de cobertura:
```
xᵢⱼ ≤ yⱼ  ∀i,j (no asignar a instalación cerrada)
```

**2. Reformulación extended:**
Agregar variables que proyectan al convex hull.

**3. Lifting:**
Fortalecer coeficientes en desigualdades existentes.

**Métricas:**
- Formulación ideal: LP relaxation = convex hull
- Medir: integrality gap, tiempo de solución

¿Quieres profundizar en alguna técnica específica?
---

---
Estudiante: "¿Cuándo conviene usar Benders vs Branch-and-cut?"

Tutor: Depende de la estructura del problema:

**Benders Decomposition:**
| Mejor cuando... | Razón |
|-----------------|-------|
| Variables complicantes separables | Fija binarias, LP en continuas |
| Estructura bloque-angular | Subproblemas independientes |
| Muchas restricciones complicantes | Genera cortes de factibilidad/optimalidad |

**Branch-and-Cut:**
| Mejor cuando... | Razón |
|-----------------|-------|
| Estructura poliedral conocida | Cortes específicos del problema |
| Formulación con facetas conocidas | Puede alcanzar convex hull |
| Problema "general" MIP | Cortes genéricos (Gomory, MIR) |

**Híbridos:**
- Branch-and-Benders-cut: combina ambos
- Callback para generar Benders cuts durante B&B

**Regla práctica:**
- Si el problema tiene estructura "aquí-allá" clara → Benders
- Si conoces la estructura poliedral → Branch-and-cut con cortes específicos
- Si es MIP general → Branch-and-cut con cortes genéricos

¿Tienes un problema específico donde no estés seguro?
---

---
Estudiante: "Explica el concepto de formulación fuerte vs débil"

Tutor: La fuerza de una formulación se mide por qué tan "tight" es su relajación LP.

**Definiciones:**
Sea P_IP = conv(soluciones enteras), P_LP = poliedro del LP relaxation.

- **Formulación ideal:** P_LP = P_IP (LP da solución entera)
- **Fuerte:** P_LP cercano a P_IP
- **Débil:** P_LP mucho mayor que P_IP

**Ejemplo - Uncapacitated Facility Location:**

*Formulación débil:*
```
Σⱼ xᵢⱼ = 1  ∀i
Σᵢ xᵢⱼ ≤ n·yⱼ  ∀j
```
Gap típico: 20-50%

*Formulación fuerte:*
```
Σⱼ xᵢⱼ = 1  ∀i
xᵢⱼ ≤ yⱼ  ∀i,j  (n×m restricciones adicionales)
```
Gap típico: 1-5%

**Trade-off:**
- Fuerte = menos nodos B&B pero más restricciones
- Débil = LPs más rápidos pero más branching

La formulación ideal no siempre es computable (puede tener exponenciales restricciones).

¿Quieres ver cómo derivar las desigualdades xᵢⱼ ≤ yⱼ?
---"""

    @staticmethod
    def is_ip_related(message: str) -> bool:
        """
        Check if a message is related to Integer Programming.

        Args:
            message: User message

        Returns:
            True if the message appears IP-related
        """
        ip_keywords = [
            # General IP terms (English)
            "integer programming", "ip problem", "integer program", "ip formulation",
            "mixed integer", "mip", "milp", "mixed integer programming",
            "pure integer", "binary programming", "binary integer programming",
            "discrete optimization", "combinatorial optimization",

            # Términos generales IP (Spanish)
            "programación entera", "problema ip", "formulación ip",
            "entero mixto", "programación entera mixta",
            "entero puro", "programación binaria",
            "optimización discreta", "optimización combinatoria",

            # Variables and decisions (English)
            "integer variable", "binary variable", "0-1 variable", "discrete variable",
            "yes/no decision", "on/off decision", "selection decision",
            "integer constraint", "integrality constraint",

            # Variables y decisiones (Spanish)
            "variable entera", "variable binaria", "variable 0-1",
            "decisión sí/no", "decisión si/no", "restricción de integridad",

            # Solution methods (English)
            "branch and bound", "branch-and-bound", "bnb",
            "cutting plane", "gomory cut", "cutting plane method",
            "branch and cut", "branch-and-cut",
            "enumeration", "implicit enumeration", "complete enumeration",

            # Métodos de solución (Spanish)
            "ramificación y acotamiento", "ramificar y acotar",
            "planos de corte", "corte de gomory",
            "ramificación y corte",

            # Relaxation and bounds (English)
            "lp relaxation", "linear relaxation", "relaxation",
            "lower bound", "upper bound", "bound",
            "optimality gap", "gap", "integrality gap",

            # Relajación y cotas (Spanish)
            "relajación lineal", "relajación lp",
            "cota inferior", "cota superior",
            "gap de optimalidad", "brecha de integridad",

            # Common applications (English)
            "facility location", "plant location", "warehouse location",
            "knapsack", "knapsack problem",
            "assignment", "assignment problem",
            "scheduling", "job shop", "resource scheduling",
            "traveling salesman", "tsp", "vehicle routing", "vrp",
            "set covering", "set packing", "set partitioning",
            "bin packing", "cutting stock",
            "project selection", "capital budgeting",

            # Aplicaciones comunes (Spanish)
            "ubicación de instalaciones", "localización de plantas",
            "problema de la mochila", "mochila binaria", "mochila",
            "problema de asignación", "asignación",
            "programación de horarios", "calendarización",
            "viajante de comercio", "agente viajero",
            "empaquetamiento", "corte de material",
            "selección de proyectos",

            # Modeling techniques (English)
            "logical constraint", "either-or constraint", "if-then constraint",
            "fixed charge", "fixed cost",
            "big-m", "big m", "indicator variable",
            "piecewise linear", "sos", "special ordered set",

            # Técnicas de modelado (Spanish)
            "restricción lógica", "restricción either-or", "restricción si-entonces",
            "costo fijo", "cargo fijo",
            "variable indicadora",

            # Properties and concepts (English)
            "feasible solution", "incumbent solution",
            "node", "branching", "fathom", "pruning",
            "subproblem", "branch tree", "search tree",
            "heuristic", "rounding", "feasibility rounding",

            # Propiedades y conceptos (Spanish)
            "solución factible", "solución incumbente",
            "nodo", "ramificación", "poda",
            "subproblema", "árbol de búsqueda",
            "heurística", "redondeo",

            # General optimization terms (shared but relevant)
            "optimal", "optimality", "optimize", "optimization",
            "objective function", "constraint", "feasible",
            "minimize", "maximize",
            "óptimo", "optimalidad", "optimizar",
            "función objetivo", "restricción", "factible",
            "minimizar", "maximizar",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in ip_keywords)

    def _validate_and_preprocess(self, user_message: str) -> tuple[str | None, str | None]:
        """Validate and preprocess the incoming message."""
        if not self.validate_message(user_message):
            return None, "No recibí un mensaje válido. ¿Podrías intentar de nuevo?"

        preprocessed_message = self.preprocess_message(user_message)
        return preprocessed_message, None

    @staticmethod
    def _get_off_topic_response() -> str:
        """Response when a query is outside the IP scope."""
        return (
            "Mi especialidad es la Programación Entera. Tu pregunta parece ser sobre otro tema.\n\n"
            "Puedo ayudarte con: formulación de problemas IP con variables binarias y enteras, "
            "branch and bound, planos de corte, modelado de restricciones lógicas, "
            "problemas de ubicación, scheduling, asignación, y análisis de gaps de optimalidad.\n\n"
            "¿Tienes alguna pregunta sobre estos temas?"
        )

    def _prepare_generation_components(
            self,
            preprocessed_message: str,
            conversation_history: list[dict[str, str]],
            context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Prepare all shared components needed to generate a response
        (used by both sync and async paths).
        """
        # ADAPTIVE LEARNING: Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Define available explanation strategies for IP
        available_strategies = [
            "formulation-based", "example-driven", "algorithmic",
            "comparative", "application-based", "conceptual-theoretical"
        ]

        # Get previously used strategies from context
        previous_strategies = get_explanation_strategies_from_context(context)

        # Select the appropriate explanation strategy
        knowledge_level = context.get("student", {}).get("knowledge_level", "beginner")
        selected_strategy = self.select_explanation_strategy(
            confusion_level=confusion_analysis["level"],
            knowledge_level=knowledge_level,
            previous_strategies=previous_strategies,
            all_available_strategies=available_strategies
        )

        # Build adaptive prompt section
        adaptive_prompt = self.build_adaptive_prompt_section(
            confusion_analysis=confusion_analysis,
            selected_strategy=selected_strategy,
            context=context
        )

        # Get base system prompt
        base_system_prompt = self.get_system_prompt(context)

        enhanced_system_prompt = self.build_enhanced_system_prompt(
            base_system_prompt, adaptive_prompt, context
        )

        # Build messages list
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
            conversation_history: list[dict[str, str]],
            context: dict[str, Any],
            confusion_analysis: dict[str, Any],
            selected_strategy: str,
            async_mode: bool = False
    ) -> str:
        """
        Shared postprocessing and feedback-augmentation for sync & async flows.
        """

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
            f"Generated {mode_label} IP response with strategy={selected_strategy}, "
            f"confusion={confusion_analysis['level']}"
        )
        return final_response

    def generate_response(self, user_message: str,
                          conversation_history: list[dict[str, str]],
                          context: dict[str, Any]) -> str:
        """
        Generate IP tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """

        # Preprocess the message
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if the question is IP-related
        if not self.is_ip_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        # Generate a response with an enhanced prompt
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
            conversation_history: list[dict[str, str]],
            context: dict[str, Any]
    ) -> str:
        """
        Async version with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """
        # Preprocess
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if IP-related
        if not self.is_ip_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        # Generate a response with an enhanced prompt (async)
        try:
            response = await self.llm_service.a_generate_response(
                messages=components["messages"],
                system_prompt=components["system_prompt"]
            )
        except Exception as e:
            logger.error(f"Error in {self.agent_name} async response generation: {str(e)}")
            from ..utils import format_error_message
            return format_error_message(e)

        # Postprocess
        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"],
            async_mode=True
        )


# Global agent instance
_ip_agent: IntegerProgrammingAgent | None = None


def get_integer_programming_agent() -> IntegerProgrammingAgent:
    """
    Get or create the global Integer Programming agent instance.

    Returns:
        IntegerProgrammingAgent instance
    """
    global _ip_agent

    if _ip_agent is None:
        _ip_agent = IntegerProgrammingAgent()

    return _ip_agent
