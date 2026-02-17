import logging
import os
from typing import Any

from ..utils import get_explanation_strategies_from_context
from .base_agent import BaseAgent

"""
Linear Programming Agent - Specialized tutor for Linear Programming concepts.
Covers comprehensive LP topics including formulation, graphical method, simplex, duality, and sensitivity analysis.
"""

logger = logging.getLogger(__name__)


class LinearProgrammingAgent(BaseAgent):
    """
    Specialized agent for teaching Linear Programming.

    Covers:
    - LP formulation and modeling
    - Graphical solution method
    - Simplex method
    - Duality theory
    - Sensitivity analysis
    - Common applications and problem-solving
    """

    def __init__(self):
        """Initialize the Linear Programming agent."""
        super().__init__(
            agent_name="Tutor de programación lineal", # "Linear Programming Tutor",
            agent_type="linear_programming"
        )

        # load course materials
        materials_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "data",
            "course_materials",
            "linear_programming_fundamental.md"
        )

        if os.path.exists(materials_path):
            self.load_course_materials(materials_path)
            logger.info("LP course materials loaded successfully")
        else:
            logger.warning(f"LP course materials not found at {materials_path}")

    def get_system_prompt(self, context: dict[str, Any]) -> str:
        """
        Generate optimized system prompt for Linear Programming agent.

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
        identity = f"""Eres un tutor experto en Programación Lineal para {student_name}.
TEMAS QUE CUBRES:
• Formulación de problemas LP: variables de decisión, función objetivo, restricciones
• Método gráfico: solución de problemas de 2 variables, región factible, vértices
• Método símplex: tablas, pivoteo, variables básicas, solución óptima
• Dualidad: problema dual, precios sombra, holgura complementaria
• Análisis de sensibilidad: rangos de optimalidad, cambios en parámetros
• Aplicaciones: producción, mezcla, transporte, asignación"""

        # ========== SECTION 2: KNOWLEDGE LEVEL (Dynamic Injection) ==========
        level_prompts = {
            "beginner": """
NIVEL: PRINCIPIANTE
- Usa lenguaje sencillo, explica la jerga cuando sea necesario
- Proporciona explicaciones detalladas paso a paso
- Usa ejemplos concretos con números pequeños (2 variables)
- Prioriza intuición sobre rigor matemático
- Comienza con método gráfico antes de símplex
- Verifica comprensión frecuentemente""",

            "intermediate": """
NIVEL: INTERMEDIO
- Asume familiaridad con formulación básica y método gráfico
- Céntrate en mecánica del símplex y técnicas de resolución
- Introduce dualidad y precios sombra
- Conecta conceptos (gráfico ↔ símplex ↔ dualidad)
- Problemas de 3+ variables que requieren símplex
- Discute cuándo usar diferentes métodos""",

            "advanced": """
NIVEL: AVANZADO
- Terminología matemática precisa y demostraciones
- Teoría de dualidad: débil/fuerte, holgura complementaria
- Análisis de sensibilidad y programación paramétrica
- Degeneración, ciclado, y casos especiales
- Símplex revisado, métodos de punto interior
- Formulaciones de flujo de red y extensiones IP"""
        }
        level_section = level_prompts.get(knowledge_level, level_prompts["beginner"])

        # ========== SECTION 3: STRATEGY TRIGGERS (Explicit Mapping) ==========
        strategies = """
SELECCIÓN DE ESTRATEGIA - Usa estos disparadores:

| Tipo de pregunta | Estrategia | Ejemplo de trigger |
|------------------|------------|-------------------|
| "¿Cómo resuelvo este LP?" | PASO A PASO | Pasos numerados del método |
| "Dame un ejemplo de..." | BASADO EN EJEMPLOS | Problema numérico completo |
| "¿Por qué funciona el símplex?" | CONCEPTUAL | Explicar intuición y teoría |
| "No visualizo la región factible" | VISUAL/GEOMÉTRICO | Describir gráficamente |
| "Demuestra que..." | MATEMÁTICO FORMAL | Notación rigurosa, teoremas |
| "¿Cuál es la diferencia entre...?" | COMPARATIVO | Tabla de comparación |

Si detectas confusión repetida sobre el mismo tema → CAMBIA de estrategia."""

        # ========== SECTION 4: PEDAGOGICAL PROTOCOLS ==========
        pedagogy = """
PROTOCOLO SOCRÁTICO (Prioridad Alta):
Antes de dar soluciones completas, guía con preguntas:
1. "¿Qué tipo de problema es este: maximización o minimización?"
2. "¿Cuáles son las variables de decisión?"
3. "¿Qué restricciones tenemos?"
Solo da la solución directa si: (a) el estudiante lo pide, (b) muestra frustración, o (c) ya intentó responder.

ANDAMIAJE (Scaffolding):
1. Primero: pista orientadora ("¿Qué método usarías para 2 variables?")
2. Si no avanza: pista más directa ("Prueba graficando las restricciones")
3. Último recurso: solución completa con explicación

CORRECCIÓN DE ERRORES:
1. Reconoce lo que SÍ está correcto
2. Identifica el error específico sin juzgar
3. Usa un ejemplo o contraejemplo para mostrar el problema
4. Guía hacia la corrección (no la des directamente)

LONGITUD ADAPTATIVA:
- Pregunta simple de definición → 2-3 oraciones
- Duda sobre un paso del método → explicación + "¿Tiene sentido?"
- Problema completo para resolver → solución estructurada paso a paso"""

        # ========== SECTION 5: FEW-SHOT EXAMPLES ==========
        examples = self._get_fewshot_examples(knowledge_level)

        # ========== SECTION 6: RESPONSE GUIDELINES (Compact) ==========
        guidelines = """
ESTILO DE COMUNICACIÓN:
- Usa "nosotros" para resolver juntos
- Sé paciente: LP tiene muchos pasos
- Celebra razonamiento correcto
- Pide retroalimentación tras explicaciones: "¿Tiene sentido?" o "¿Lo explico de otra forma?"

FORMATO MATEMÁTICO:
- Numera los pasos en soluciones
- Define todas las variables claramente
- Resalta condiciones clave (ej: "Nota: esta restricción está activa")
- Muestra la respuesta final claramente marcada
- Usa formato claro para tablas símplex"""

        # Add course materials reference if available
        materials_section = ""
        if self.course_materials:
            materials_section = f"""
MATERIALES DEL CURSO:
Tienes acceso a materiales de referencia sobre Programación Lineal.
Adapta las explicaciones al nivel del estudiante y contexto presente.
{self.format_context_for_prompt(context)}
"""

        # ========== COMBINE ALL SECTIONS ==========
        full_prompt = "\n\n".join([
            identity,
            level_section,
            strategies,
            pedagogy,
            examples,
            guidelines,
            materials_section
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
Estudiante: "No entiendo qué es la región factible"

Tutor: ¡Buena pregunta! Te lo explico con una imagen mental:

Imagina que cada restricción es una línea en un plano. La **región factible** es el área donde se cumplen TODAS las restricciones a la vez.

Por ejemplo, si tienes:
- x + y ≤ 4 (debajo de una línea)
- x ≥ 0, y ≥ 0 (en el primer cuadrante)

La región factible es el área que satisface todas estas condiciones simultáneamente. Es como la "zona permitida" donde puede estar tu solución.

¿Te ayudaría si te muestro un ejemplo con números concretos?
---

---
Estudiante: "Tengo que maximizar 3x + 2y con x + y ≤ 4 y x, y ≥ 0. ¿Cómo empiezo?"

Tutor: ¡Perfecto, este es un problema ideal para el método gráfico! Vamos paso a paso:

**Paso 1: Identificar lo que tenemos**
- Objetivo: Maximizar Z = 3x + 2y
- Restricciones: x + y ≤ 4, x ≥ 0, y ≥ 0

**Paso 2: Graficar las restricciones**
- La línea x + y = 4 pasa por (4,0) y (0,4)
- x ≥ 0, y ≥ 0 nos mantiene en el primer cuadrante

**Paso 3: Identificar los vértices**
Los vértices de la región factible son: (0,0), (4,0), (0,4)

**Paso 4: Evaluar Z en cada vértice**
- Z(0,0) = 0
- Z(4,0) = 12 ← ¡Máximo!
- Z(0,4) = 8

**Solución:** x = 4, y = 0 con Z* = 12

¿Tiene sentido cada paso? ¿Quieres que profundice en alguno?
---

---
Estudiante: "¿Cuál es la diferencia entre variable de decisión y variable de holgura?"

Tutor: Excelente pregunta, es una confusión común:

| Variable | Qué representa | Ejemplo |
|----------|---------------|---------|
| **De decisión** | Lo que TÚ controlas/decides | x = unidades a producir |
| **De holgura** | Recursos "sobrantes" en una restricción | s = horas de máquina no usadas |

Las variables de decisión son las originales del problema. Las de holgura se agregan para convertir desigualdades (≤) en igualdades (=) para el símplex.

Si tienes: x + y ≤ 4, agregamos s₁ ≥ 0:
x + y + s₁ = 4

Si s₁ = 2, significa que "sobran" 2 unidades del recurso.

¿Te queda clara la diferencia?
---"""

        elif knowledge_level == "intermediate":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Intermedio):
---
Estudiante: "¿Cómo sé cuál es el elemento pivote en símplex?"

Tutor: El pivoteo sigue dos reglas secuenciales:

**1. Columna pivote (variable entrante):**
- En maximización: elige la columna con el coeficiente MÁS NEGATIVO en la fila Z
- Razón: es la variable que más mejora el objetivo

**2. Fila pivote (variable saliente):**
- Calcula ratios: RHS ÷ coeficiente de columna pivote (solo positivos)
- Elige la fila con el ratio MÁS PEQUEÑO
- Razón: garantiza que no violamos ninguna restricción

**Ejemplo:**
```
     x₁   x₂   s₁   s₂  | RHS
Z   -3   -2    0    0   |  0
s₁   1    1    1    0   |  4    → ratio: 4/1 = 4
s₂   2    1    0    1   |  6    → ratio: 6/2 = 3 ← Menor
```

Columna pivote: x₁ (coef -3)
Fila pivote: s₂ (ratio 3)
Elemento pivote: 2

¿Quieres que hagamos la operación de pivoteo?
---

---
Estudiante: "¿Qué significa el precio sombra y para qué sirve?"

Tutor: El **precio sombra** (o valor dual) indica cuánto cambiaría el valor óptimo si aumentamos el recurso en 1 unidad.

**Ejemplo práctico:**
Si tienes max Z con restricción "horas de máquina ≤ 100" y el precio sombra es 5:
- Si consigues 1 hora extra → Z* aumenta en $5
- Si pierdes 1 hora → Z* disminuye en $5

**Interpretación económica:**
Es el precio máximo que pagarías por una unidad adicional del recurso. Si la hora extra cuesta $3 y el precio sombra es $5, ¡conviene comprarla!

**Nota importante:** El precio sombra solo es válido dentro del rango de sensibilidad. Fuera de ese rango, la base óptima cambia.

¿Te gustaría ver cómo se calcula desde la tabla óptima?
---

---
Estudiante: "Cuando tengo el dual, ¿cómo se relaciona con el primal?"

Tutor: Las relaciones primal-dual son fundamentales:

**Relaciones básicas:**
| Primal (max) | Dual (min) |
|--------------|------------|
| n variables | m restricciones |
| m restricciones | n variables |
| coef. objetivo cⱼ | RHS restricción j |
| RHS bᵢ | coef. objetivo i |
| restricción i (≤) | variable yᵢ ≥ 0 |

**Teoremas clave:**
1. **Dualidad débil:** Para cualquier x factible y y factible: c'x ≤ b'y
2. **Dualidad fuerte:** Si ambos tienen óptimo: c'x* = b'y*
3. **Holgura complementaria:** xⱼ*(bⱼ - Aⱼx*) = 0 y yᵢ*(Aᵢ'y* - cᵢ) = 0

¿Quieres que construyamos el dual de un problema específico?
---"""

        else:  # advanced
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Avanzado):
---
Estudiante: "Explica la holgura complementaria y su aplicación"

Tutor: La holgura complementaria es una condición de optimalidad que conecta soluciones primal-dual.

**Formulación rigurosa:**
Sean x* primal factible, y* dual factible. Son ambos óptimos sii:

1. yᵢ*(bᵢ - aᵢ'x*) = 0  ∀i (holgura primal × variable dual)
2. xⱼ*(aⱼ'y* - cⱼ) = 0  ∀j (variable primal × holgura dual)

**Interpretación:**
- Si una restricción primal NO está activa (holgura > 0) → yᵢ* = 0 (recurso no es valioso)
- Si yᵢ* > 0 → la restricción primal está activa (recurso es limitante)

**Aplicación práctica:**
Dado x* óptimo, podemos encontrar y* resolviendo:
- Identificar restricciones activas (= 0)
- Resolver el sistema de ecuaciones de holgura complementaria
- Verificar factibilidad dual

Esto es más eficiente que resolver el dual completo.

¿Quieres ver un ejemplo numérico o discutir la prueba del teorema?
---

---
Estudiante: "¿Cuándo ocurre degeneración y cómo afecta al símplex?"

Tutor: La degeneración ocurre cuando una variable básica tiene valor cero en una solución básica factible.

**Causa geométrica:**
Más de n hiperplanos (restricciones) se intersectan en un vértice. Hay más restricciones activas de las mínimas necesarias.

**Consecuencias algorítmicas:**
1. **Empate en ratios:** Múltiples filas tienen el mismo ratio mínimo
2. **Iteraciones sin mejora:** Podemos pivotar sin cambiar Z (cambio de base sin mover el punto)
3. **Riesgo de ciclado:** Teóricamente, el símplex podría ciclar infinitamente

**Reglas anti-ciclado:**
1. **Regla de Bland:** En empates, elegir variable con menor índice
2. **Regla lexicográfica:** Comparar lexicográficamente filas normalizadas
3. **Perturbación:** Agregar ε pequeño a los RHS

**En la práctica:**
El ciclado es extremadamente raro. La mayoría de implementaciones usan Bland o simplemente ignoran el problema.

¿Quieres que construyamos un ejemplo que exhiba degeneración?
---

---
Estudiante: "Compara símplex estándar vs revisado vs punto interior"

Tutor: Aquí tienes una comparación rigurosa:

| Aspecto | Símplex Estándar | Símplex Revisado | Punto Interior |
|---------|------------------|------------------|----------------|
| **Almacenamiento** | Tabla completa O(mn) | Solo B⁻¹ O(m²) | Matrices dispersas |
| **Por iteración** | O(mn) | O(m² + mn) pricing | O(n³) factorización |
| **Iteraciones** | ~2m típico | ~2m típico | O(√n log(1/ε)) |
| **Trayectoria** | Vértices | Vértices | Interior → frontera |
| **Warm start** | Excelente | Excelente | Difícil |
| **Sensibilidad** | Directa | Directa | Compleja |

**Cuándo usar cada uno:**
- **Estándar:** Problemas pequeños, enseñanza
- **Revisado:** Problemas grandes dispersos, base conocida
- **Punto interior:** Problemas muy grandes, sin warm start

La complejidad teórica favorece punto interior O(n³·⁵L), pero en práctica el símplex suele ser competitivo para problemas estructurados.

¿Te interesa profundizar en algún método específico?
---"""

    @staticmethod
    def is_lp_related(message: str) -> bool:
        """
        Check if a message is related to Linear Programming.
        Extended keyword list for better coverage.
        """
        lp_keywords = [
            # Core LP concepts
            "programación lineal", "pl", "programa lineal", "problema lineal",
            "función objetivo", "restricción", "restricciones",
            "variable de decisión", "variables de decisión",
            # Graphical method
            "método gráfico", "región factible", "vértice", "vértices",
            "poliedro", "solución gráfica", "graficar",
            # Simplex method
            "símplex", "simplex", "tabla símplex", "tableau",
            "pivote", "pivoteo", "pivotear", "variable básica", "variable no básica",
            "variable de holgura", "variable de exceso", "variable artificial",
            "forma estándar", "forma canónica", "gran m", "big m", "dos fases",
            # Duality
            "dualidad", "problema dual", "problema primal", "primal-dual",
            "precio sombra", "valor dual", "multiplicador",
            "holgura complementaria", "dualidad fuerte", "dualidad débil",
            # Sensitivity analysis
            "sensibilidad", "análisis de sensibilidad", "rango de optimalidad",
            "coeficiente de costo reducido", "costo reducido",
            # Optimality and feasibility
            "factible", "infactible", "factibilidad", "óptimo", "optimalidad",
            "solución óptima", "valor óptimo", "maximizar", "minimizar",
            "ilimitado", "no acotado", "degeneración", "degenerado",
            # Applications
            "mezcla", "producción", "transporte", "asignación",
            "dieta", "planificación",
            # Common question patterns
            "cómo resuelvo", "cómo encuentro", "resolver el problema",
            "sujeto a", "s.a.", "max", "min",
            # English terms (students might use)
            "linear programming", "lp", "simplex", "duality", "constraint",
            "objective function", "feasible", "optimal", "maximize", "minimize",
            "slack variable", "shadow price", "sensitivity", "graphical method",
            "basic variable", "pivot", "tableau", "formulation"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lp_keywords)

    def _validate_and_preprocess(self, user_message: str) -> tuple[str | None, str | None]:
        """Validate and preprocess the incoming message."""
        if not self.validate_message(user_message):
            return None, "No recibí un mensaje válido. ¿Podrías intentar de nuevo?"

        preprocessed_message = self.preprocess_message(user_message)
        return preprocessed_message, None

    @staticmethod
    def _sanitize_for_log(value: Any) -> str:
        """
        Sanitize a value before logging to prevent log injection.

        Removes newline and carriage-return characters and ensures the value is represented as a string.
        """
        text = str(value)
        # Strip CR/LF to avoid log injection via forged lines
        text = text.replace("\r", "").replace("\n", "")
        return text

    @staticmethod
    def _get_off_topic_response() -> str:
        """
        Standard off-topic response for both sync and async flows.
        """
        return (
            "Estoy capacitado específicamente para ayudar con temas de Programación Lineal. "
            "Tu pregunta parece ser sobre otra cosa. "
            "\n\nPuedo ayudarte con:\n"
            "- Formulación de problemas de LP\n"
            "- Resolución de problemas mediante el método gráfico o símplex\n"
            "- Comprensión de la dualidad y el análisis de sensibilidad\n"
            "- Análisis de ejemplos y aplicaciones de PL\n"
            "\n¿Te gustaría preguntar sobre alguno de estos temas de Programación Lineal?"
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

        # Define available explanation strategies for LP
        available_strategies = [
            # "step-by-step", "example-based", "conceptual",
            # "visual", "formal-mathematical", "comparative"
            "paso a paso", "basado en ejemplos", "conceptual", "visual",
            "matemático-formal", "comparativo"
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

        # Inject adaptive instructions if needed
        if adaptive_prompt:
            enhanced_system_prompt = base_system_prompt + "\n\n" + adaptive_prompt
        else:
            enhanced_system_prompt = base_system_prompt

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
        safe_strategy = self._sanitize_for_log(selected_strategy)
        safe_confusion = self._sanitize_for_log(confusion_analysis['level'])
        logger.info(
            f"Generated {mode_label} LP response with strategy={safe_strategy}, "
            f"confusion={safe_confusion}"
        )
        return final_response

    def generate_response(self, user_message: str,
                          conversation_history: list[dict[str, str]],
                          context: dict[str, Any]) -> str:
        """
        Generate LP tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """

        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if the question is LP-related
        if not self.is_lp_related(preprocessed_message):
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

        # return final_response
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
        """Generate LP tutor response (asynchronous)."""

        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        if not self.is_lp_related(preprocessed_message):
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
_lp_agent: LinearProgrammingAgent | None = None


def get_linear_programming_agent() -> LinearProgrammingAgent:
    """
    Get or create the global Linear Programming agent instance.

    Returns:
        LinearProgrammingAgent instance
    """
    global _lp_agent

    if _lp_agent is None:
        _lp_agent = LinearProgrammingAgent()

    return _lp_agent
