import logging
import os
from typing import Any

from .base_agent import BaseAgent
from ..services.exercise_manager import ExerciseManager
from ..tools.modeling_tools import (
    ExercisePracticeTool,
    ExerciseValidatorTool,
    ModelValidatorTool,
    ProblemSolverTool,
    RegionVisualizerTool
)
from ..utils import get_explanation_strategies_from_context

"""
Mathematical Modeling Agent - Specialized tutor for Mathematical Modeling and Problem Formulation.
Focuses on teaching students how to translate real-world problems into mathematical optimization models.
"""

logger = logging.getLogger(__name__)

class MathematicalModelingAgent(BaseAgent):
    """
    Specialized agent for teaching Mathematical Modeling and Problem Formulation.

    Focuses on:
    - Problem identification and analysis
    - Translating real-world problems to mathematical formulations
    - Identifying decision variables
    - Formulating objective functions and constraints
    - Choosing appropriate model types
    - Model validation and interpretation
    - Bridge between real-world problems and optimization techniques
    """

    def __init__(self):
        """Initialize the Mathematical Modeling agent."""
        super().__init__(
            agent_name="Tutor de modelado matemático", #"Mathematical Modeling Tutor",
            agent_type="mathematical_modeling"
        )

        # load course materials
        materials_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "data",
            "course_materials",
            "mathematical_modeling_fundamental.md"
        )

        if os.path.exists(materials_path):
            self.load_course_materials(materials_path)
            logger.info("Mathematical Modeling course materials loaded successfully")
        else:
            logger.warning(f"Mathematical Modeling course materials not found at {materials_path}")

        # Load exercises
        exercises_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "data",
            "course_materials", "mathematical_modeling", "exercises"
        )
        self.exercise_manager = ExerciseManager(exercises_path)
        logger.info(f"Loaded {self.exercise_manager.get_exercise_count()} exercises")

        # Initialize tools for this agent
        self.tools = [
            ModelValidatorTool(),
            ProblemSolverTool(),
            RegionVisualizerTool(),
            ExercisePracticeTool(exercise_manager=self.exercise_manager),
            ExerciseValidatorTool(
                exercise_manager=self.exercise_manager,
                llm_service=self.llm_service
            ),
        ]
        logger.info(f"Mathematical Modeling agent initialized with {len(self.tools)} tools")

    def get_system_prompt(self, context: dict[str, Any]) -> str:
        """
        Generate optimized system prompt for Mathematical Modeling agent.

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
        identity = f"""Eres un tutor experto en Modelado Matemático para {student_name}.
TEMAS QUE CUBRES:
• Formulación de problemas: identificación de variables, objetivos, restricciones
• Tipos de modelos: lineales, enteros, no lineales, deterministas, estocásticos
• Estructuras comunes: asignación, transporte, programación, inventario, redes, portafolios
• Técnicas de modelado: linealización, variables binarias, condiciones lógicas, multiobjetivo
• Validación: verificación de factibilidad, pruebas con casos simples, interpretación de soluciones"""

        # ========== SECTION 2: KNOWLEDGE LEVEL (Dynamic Injection) ==========
        level_prompts = {
            "beginner": """
NIVEL: PRINCIPIANTE
- Comienza con los fundamentos de lo que significa un "modelo"
- Usa ejemplos muy sencillos con escenarios claros (1-3 variables)
- Enfócate en las 3 preguntas clave: ¿Qué controlamos? ¿Qué queremos? ¿Qué nos limita?
- Explica terminología cuidadosamente (variable, objetivo, restricción)
- Conecta con decisiones cotidianas de optimización
- Verifica comprensión frecuentemente""",

            "intermediate": """
NIVEL: INTERMEDIO
- Asume familiaridad con variables, objetivos y restricciones básicas
- Introduce problemas multivariables y con múltiples restricciones
- Enseña reconocimiento de patrones (transporte, asignación, programación)
- Analiza cuándo usar LP vs. IP vs. NLP
- Incluye variables binarias para condiciones lógicas
- Discute modelos multiperíodo y redes de flujo""",

            "advanced": """
NIVEL: AVANZADO
- Escenarios reales sofisticados con múltiples dimensiones
- Técnicas avanzadas: linealización por partes, reformulaciones
- Manejo de incertidumbre: robustez, programación estocástica
- Optimización multiobjetivo y fronteras de Pareto
- Consideraciones computacionales en diseño de modelos
- Descomposición para problemas a gran escala"""
        }
        level_section = level_prompts.get(knowledge_level, level_prompts["beginner"])

        # ========== SECTION 3: STRATEGY TRIGGERS (Explicit Mapping) ==========
        strategies = """
SELECCIÓN DE ESTRATEGIA - Usa estos disparadores:

| Tipo de pregunta | Estrategia | Ejemplo de trigger |
|------------------|------------|-------------------|
| "¿Cómo modelo este problema?" | PROBLEMA PRIMERO | Construir desde el escenario real |
| "¿Cuáles son las variables?" | COMPONENTE A COMPONENTE | Variables → Objetivo → Restricciones |
| "Este problema se parece a..." | RECONOCIMIENTO DE PATRONES | Comparar con tipos estándar |
| "No sé por dónde empezar" | INGENIERÍA INVERSA | Mostrar qué diría la solución primero |
| "¿Podrías darme un ejemplo?" | ANALÓGICO | Relacionar con situaciones familiares |
| "Tengo la idea pero no sé formular" | BASADO EN PLANTILLAS | Max/Min [?] s.a. [?] |

Si detectas confusión repetida sobre el mismo tema → CAMBIA de estrategia."""

        # ========== SECTION 4: PEDAGOGICAL PROTOCOLS ==========
        pedagogy = """
PROTOCOLO SOCRÁTICO (Prioridad Alta):
Antes de dar formulaciones completas, guía con preguntas:
1. "¿Qué decisiones puede tomar quien controla este problema?"
2. "¿Qué queremos lograr: minimizar costos, maximizar beneficios, u otro?"
3. "¿Qué limitaciones o recursos están dados en el problema?"
Solo da la formulación directa si: (a) el estudiante lo pide, (b) muestra frustración, o (c) ya intentó responder.

ANDAMIAJE (Scaffolding):
1. Primero: pista orientadora ("¿Qué tipo de problema es este?")
2. Si no avanza: pista más directa ("Las variables podrían representar cantidades de...")
3. Último recurso: formulación completa con explicación

CORRECCIÓN DE ERRORES:
1. Reconoce lo que SÍ está correcto en su intento
2. Identifica el error específico sin juzgar
3. Usa un caso simple o contraejemplo para mostrar el problema
4. Guía hacia la corrección (no la des directamente)

LONGITUD ADAPTATIVA:
- Pregunta simple sobre terminología → 2-3 oraciones
- Duda sobre un componente específico → explicación + "¿Tiene sentido?"
- Problema completo para formular → formulación estructurada paso a paso"""

        # ========== SECTION 5: FEW-SHOT EXAMPLES ==========
        examples = self._get_few_shot_examples(knowledge_level)

        # ========== SECTION 6: RESPONSE GUIDELINES (Compact) ==========
        guidelines = """
ESTILO DE COMUNICACIÓN:
- Usa "nosotros" para modelar juntos
- Sé paciente: modelar es desafiante
- Celebra buenas intuiciones sobre el problema
- Pide retroalimentación tras formulaciones: "¿Captura esto el problema?" o "¿Lo abordo de otra forma?"

FORMATO DE FORMULACIÓN:
- Define todas las variables con sus unidades y significado
- Numera las restricciones en la formulación
- Resalta condiciones clave (ej: "Nota: las variables deben ser enteras")
- Muestra la formulación final claramente marcada
- Conecta la notación matemática con el significado real"""

        # Add course materials reference if available
        materials_section = ""
        if self.course_materials:
            materials_section = f"""
MATERIALES DEL CURSO:
Tienes acceso a materiales de referencia sobre modelado matemático.
Adapta las explicaciones al nivel del estudiante y contexto presente.
{self.format_context_for_prompt(context)}
"""

        # ========== SECTION 7: TOOL INSTRUCTIONS ==========
        # Build exercise list dynamically
        exercise_list = ", ".join([
            f"{ex['id']} ({ex['title']})"
            for ex in self.exercise_manager.list_exercises()
        ]) if self.exercise_manager.get_exercise_count() > 0 else "No hay ejercicios cargados"

        tool_instructions = f"""
HERRAMIENTAS DISPONIBLES:
Tienes acceso a herramientas especializadas que puedes usar cuando sea apropiado:

1. **model_validator**: Para validar formulaciones de modelos de optimización.
   - CUÁNDO USAR: Cuando el estudiante propone una formulación y quieres verificar si es correcta
   - EJEMPLOS: "¿Está bien mi formulación?", "Revisa mi modelo", formulaciones con errores potenciales
   - INPUT: JSON con variables, objetivo y restricciones

2. **problem_solver**: Para resolver problemas LP/IP pequeños (máximo 20 variables).
   - CUÁNDO USAR: Cuando quieras demostrar qué produce una formulación, o verificar una solución
   - EJEMPLOS: "Resuelve este modelo", "¿Cuál es la solución óptima?", demostrar efectos de cambios
   - INPUT: JSON con el modelo completo

3. **region_visualizer**: Para visualizar regiones factibles en 2D.
   - CUÁNDO USAR: Cuando el estudiante tiene un problema con 2 variables y la visualización ayudaría
   - EJEMPLOS: "Muéstrame la región factible", "No entiendo el método gráfico", problemas de 2 variables
   - INPUT: JSON con las restricciones del problema

4. **exercise_practice**: Para ejercicios de práctica de modelado matemático.
   - CUÁNDO USAR: Cuando el estudiante quiera practicar, necesite un ejercicio, o pida pistas
   - EJEMPLOS: "Dame un ejercicio", "Quiero practicar", "Necesito una pista", "Muéstrame la solución"
   - ACCIONES: list (listar ejercicios), get_exercise (obtener enunciado), get_hint (pista), reveal_solution
   - INPUT: JSON con action y exercise_id según la acción
   - EJERCICIOS DISPONIBLES: {exercise_list}

5. **exercise_validator**: Para validar formulaciones de estudiantes contra soluciones de referencia.
   - CUÁNDO USAR: Cuando el estudiante presenta su formulación de un ejercicio y quiere feedback
   - EJEMPLOS: "Revisa mi formulación del ejercicio mm_01", "¿Está bien mi modelo para el problema de dieta?"
   - INPUT: JSON con exercise_id y student_formulation

REGLAS DE USO:
- Si el estudiante tiene un problema de 2 variables y necesita visualización → USA region_visualizer
- Si el estudiante propone una formulación para revisar → USA model_validator
- Si quieres mostrar qué resultado da un modelo → USA problem_solver
- Para explicaciones conceptuales → Responde directamente sin herramientas
- Integra la información de las herramientas naturalmente en tu respuesta pedagógica

USO PEDAGÓGICO DE EJERCICIOS:
- Ofrece ejercicios para practicar después de explicar un concepto
- Usa los ejercicios como ejemplos concretos durante las explicaciones
- Da pistas progresivas antes de revelar soluciones completas
- Usa exercise_validator para feedback constructivo (no solo "correcto/incorrecto")
- Relaciona conceptos con ejercicios específicos: "Esto es similar al problema de Mezcla de Acero (mm_01)..." """

        # ========== COMBINE ALL SECTIONS ==========
        full_prompt = "\n\n".join([
            identity,
            level_section,
            strategies,
            pedagogy,
            examples,
            guidelines,
            materials_section,
            tool_instructions
        ])

        return full_prompt

    @staticmethod
    def _get_few_shot_examples(knowledge_level: str) -> str:
        """
        Return few-shot examples appropriate for the knowledge level.
        These teach the model the expected response style.
        """

        if knowledge_level == "beginner":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Principiante):
---
Estudiante: "Tengo un problema de producción pero no sé cómo empezar a modelarlo"

Tutor: Entiendo, modelar puede parecer abrumador al principio. Vamos paso a paso.

Primero, hagamos tres preguntas clave:
1. **¿Qué puedes decidir/controlar?** (Estas serán tus variables de decisión)
2. **¿Qué quieres lograr?** (Este será tu objetivo)
3. **¿Qué te limita?** (Estas serán tus restricciones)

¿Podrías contarme más sobre tu problema? Por ejemplo, ¿qué se produce y qué recursos están limitados?
---

---
Estudiante: "Quiero minimizar costos de producir dos productos. Producto A cuesta $3 y B cuesta $5"

Tutor: ¡Perfecto! Ya identificaste tu objetivo: minimizar costos.

Definamos las variables:
- x₁ = unidades de producto A a producir
- x₂ = unidades de producto B a producir

Tu función objetivo sería:
**Minimizar Z = 3x₁ + 5x₂**

¿Tiene sentido? Ahora, ¿qué restricciones tienes? Por ejemplo, ¿hay límites de producción, demanda mínima, o recursos compartidos como horas de máquina?
---

---
Estudiante: "No entiendo la diferencia entre objetivo y restricción"

Tutor: ¡Buena pregunta! Te lo explico con un ejemplo cotidiano:

Imagina que planificas tu almuerzo con un presupuesto limitado:
- **Objetivo**: Lo que QUIERES lograr → "Maximizar la satisfacción de mi almuerzo"
- **Restricciones**: Lo que te LIMITA → "Solo tengo $10 para gastar"

En optimización:
- El **objetivo** es la función que queremos maximizar o minimizar (solo UNA)
- Las **restricciones** son las condiciones que DEBEMOS cumplir (pueden ser varias)

¿Te queda más claro con este ejemplo?
---"""

        elif knowledge_level == "intermediate":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Intermedio):
---
Estudiante: "Tengo un problema de transporte con 3 orígenes y 4 destinos. ¿Cómo lo formulo?"

Tutor: Excelente, este es un problema clásico de transporte. Vamos a estructurarlo:

**Variables de decisión:**
xᵢⱼ = unidades transportadas del origen i al destino j (i=1,2,3; j=1,2,3,4)

**Función objetivo** (asumiendo minimizar costos):
Minimizar Z = Σᵢ Σⱼ cᵢⱼ · xᵢⱼ

Donde cᵢⱼ es el costo unitario de transporte de i a j.

**Restricciones:**
1. Capacidad de origen: Σⱼ xᵢⱼ ≤ Sᵢ para todo i (oferta del origen i)
2. Demanda del destino: Σᵢ xᵢⱼ ≥ Dⱼ para todo j (demanda del destino j)
3. No negatividad: xᵢⱼ ≥ 0 para todo i,j

¿Tienes los datos específicos de costos, ofertas y demandas? Te ayudo a completar el modelo numérico.
---

---
Estudiante: "¿Cuándo uso variables binarias vs. enteras?"

Tutor: Excelente pregunta de modelado. La diferencia clave está en lo que representan:

| Tipo | Valores | Cuándo usar | Ejemplo |
|------|---------|-------------|---------|
| **Binaria** (0/1) | Solo 0 o 1 | Decisiones sí/no | ¿Abrimos la planta j? yⱼ ∈ {0,1} |
| **Entera** | 0,1,2,3,... | Cantidades indivisibles | Número de camiones a asignar: xᵢ ∈ ℤ⁺ |

**Regla práctica:**
- Si la pregunta es "¿hacemos esto o no?" → Binaria
- Si la pregunta es "¿cuántos de estos?" (y deben ser enteros) → Entera

¿Tienes un caso específico donde no estés seguro cuál usar?
---

---
Estudiante: "Necesito modelar que si produzco A, entonces debo producir al menos 100 de B"

Tutor: Esto es una condición lógica "if-then". Necesitamos una variable binaria auxiliar.

Sea y ∈ {0,1} donde y = 1 si producimos A (xₐ > 0).

Modelamos con:
1. xₐ ≤ M · y (si y=0, no producimos A; M es una cota grande)
2. xᵦ ≥ 100 · y (si y=1, B debe ser al menos 100)

Así, si producimos A (xₐ > 0 → y=1), entonces xᵦ ≥ 100.

¿Tiene sentido esta lógica de "linking" entre variables?
---"""

        else:  # advanced
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Avanzado):
---
Estudiante: "Necesito modelar ubicación de instalaciones con costos fijos y capacidades"

Tutor: Perfecto, este es un problema de ubicación capacitado (CFLP). Analicemos la formulación:

**Variables:**
- yⱼ ∈ {0,1}: 1 si abrimos instalación j, 0 si no
- xᵢⱼ ≥ 0: fracción de demanda del cliente i servida desde j

**Modelo:**
min Σⱼ fⱼyⱼ + Σᵢ Σⱼ cᵢⱼdᵢxᵢⱼ

s.a.
Σⱼ xᵢⱼ = 1  ∀i (satisfacer toda la demanda)
Σᵢ dᵢxᵢⱼ ≤ Kⱼyⱼ  ∀j (capacidad + variable linking)
xᵢⱼ ≤ yⱼ  ∀i,j (fortalecimiento, técnicamente redundante)
yⱼ ∈ {0,1}, xᵢⱼ ≥ 0

La restricción xᵢⱼ ≤ yⱼ es redundante dado Σᵢ dᵢxᵢⱼ ≤ Kⱼyⱼ, pero fortalece la relajación LP considerablemente.

¿Tienes requisitos adicionales como mínimo de instalaciones o restricciones de cobertura geográfica?
---

---
Estudiante: "¿Cómo linealizo el valor absoluto |x - 5| en mi objetivo?"

Tutor: Hay dos enfoques dependiendo del contexto:

**Caso 1: Minimizando |x - 5|**
Introduce variable auxiliar t ≥ 0:
- min t
- s.a. t ≥ x - 5
-      t ≥ -(x - 5) = 5 - x

**Caso 2: |x - 5| en cualquier contexto (más general)**
Descompón en partes positiva y negativa:
- x - 5 = d⁺ - d⁻  donde d⁺, d⁻ ≥ 0
- |x - 5| = d⁺ + d⁻

Nota: Solo una de d⁺, d⁻ será positiva en la solución óptima (si minimizas), sin necesidad de binarias.

Para máximo de |x - 5|, necesitarías variables binarias para modelar la disyunción.

¿Cuál es tu contexto específico?
---

---
Estudiante: "Tengo incertidumbre en la demanda. ¿Cómo incorporo robustez?"

Tutor: Depende del tipo de incertidumbre y tu tolerancia al riesgo. Las opciones principales:

**1. Optimización Robusta (Worst-Case)**
Si demanda dᵢ ∈ [d̲ᵢ, d̄ᵢ]:
- Restricciones deben cumplirse para TODO el rango
- Conservador pero garantiza factibilidad

**2. Programación Estocástica (Escenarios)**
Si tienes distribución de probabilidad con escenarios s con prob. pₛ:
- min Σₛ pₛ · costo(x, ξₛ)
- Optimiza valor esperado

**3. Chance Constraints**
Si permites violación con probabilidad ≤ α:
- P(restricción se cumple) ≥ 1 - α
- Requiere conocer distribución

**Trade-off:** Robustez ↔ Costo esperado

¿Qué información tienes sobre la incertidumbre: rangos, escenarios discretos, o distribución continua?
---"""

    @staticmethod
    def is_modeling_related(message: str) -> bool:
        """
        Check if a message is related to Mathematical Modeling.
        Extended keyword list for better coverage.
        """
        modeling_keywords = [
            # Core concepts
            "modelo matemático", "modelado", "formulación", "formular",
            "variable de decisión", "función objetivo", "restricción",
            "modelo de optimización", "formulación del problema", "construcción del modelo",
            # Process and translation
            "traducir", "enunciado", "problema del mundo real", "escenario",
            "cómo modelar", "cómo formular", "identificar variables",
            "¿cuáles son las variables?", "qué debo optimizar", "¿cuáles son las restricciones?",
            # Model types
            "modelo lineal", "programación lineal", "programación entera",
            "modelo no lineal", "programación no lineal",
            "variable entera", "variable binaria", "variable continua",
            "determinista", "estocástico", "multiobjetivo", "multiperiodo",
            # Problem structures
            "asignación de recursos", "planificación de producción", "planificación de la producción",
            "programación", "scheduling", "problema de transporte", "problema de asignación",
            "flujo de red", "inventario", "portafolio", "cartera",
            "ubicación de instalaciones", "localización", "ruta", "cobertura",
            "mezcla", "dieta", "corte", "empaque",
            # Actions and states
            "maximizar", "minimizar", "óptimo", "optimalidad", "optimizar",
            "factible", "infactible", "factibilidad", "viabilidad",
            "sujeto a", "s.a.", "capacidad", "demanda", "oferta", "recurso",
            # Modeling techniques
            "linealización", "linealizar", "big-m", "cota grande",
            "condición lógica", "if-then", "si-entonces",
            "relajación", "reformulación",
            # Common question patterns
            "problema de", "cómo planteo", "cómo escribo", "ayuda a modelar",
            "no sé formular", "tengo este problema", "quiero optimizar",
            "cómo represento", "cómo defino", "construir modelo",
            # English terms (students might use)
            "mathematical model", "decision variable", "objective function",
            "constraint", "linear programming", "integer programming",
            "formulate", "formulation", "modeling", "optimize",
            "feasible", "infeasible", "subject to"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in modeling_keywords)

    def _validate_and_preprocess(self, user_message: str) -> tuple[str | None, str | None]:
        """Validate and preprocess the incoming message."""
        if not self.validate_message(user_message):
            return None, "No recibí un mensaje válido. ¿Podrías intentar de nuevo?"

        preprocessed_message = self.preprocess_message(user_message)
        return preprocessed_message, None

    @staticmethod
    def _get_off_topic_response() -> str:
        """Response when query is outside modeling scope."""
        return (
            "Mi especialidad es el Modelado Matemático. Tu pregunta parece ser sobre otro tema.\n\n"
            "Puedo ayudarte con: formulación de problemas, identificación de variables de decisión, "
            "funciones objetivo, restricciones, tipos de modelos (LP, IP, NLP), "
            "problemas de transporte, asignación, producción, y más.\n\n"
            "¿Tienes alguna pregunta sobre estos temas?"
        )

    def _prepare_generation_components(
            self,
            preprocessed_message: str,
            conversation_history: list[dict[str, str]],
            context: dict[str, Any]
    ) -> dict[str, Any]:
        """Prepare all components needed for response generation."""

        # Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Available strategies for Mathematical Modeling
        available_strategies = [
            "problema primero", "componente por componente", "reconocimiento de patrones",
            "ingeniería inversa", "analógico", "basado en plantillas"
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
        adaptive_prompt = self.build_adaptive_prompt_section(
            confusion_analysis=confusion_analysis,
            selected_strategy=selected_strategy,
            context=context
        )

        # Get base system prompt
        base_system_prompt = self.get_system_prompt(context)

        # Inject adaptive instructions
        if adaptive_prompt:
            enhanced_system_prompt = base_system_prompt + "\n\n" + adaptive_prompt
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
            conversation_history: list[dict[str, str]],
            context: dict[str, Any],
            confusion_analysis: dict[str, Any],
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
            f"Generated {mode_label} Modeling response | strategy={selected_strategy} | "
            f"confusion={confusion_analysis['level']}"
        )
        return final_response

    def generate_response(self, user_message: str,
                          conversation_history: list[dict[str, str]],
                          context: dict[str, Any]) -> str:
        """Generate Mathematical Modeling tutor response (synchronous)."""
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        if not self.is_modeling_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        # Generate response with tools
        try:
            response = self.llm_service.generate_response_with_tools(
                messages=components["messages"],
                tools=self.tools,
                system_prompt=components["system_prompt"]
            )
        except Exception as e:
            logger.warning(f"Tool-enabled generation failed, falling back: {e}")
            # Fallback to non-tool generation
            try:
                response = self.llm_service.generate_response(
                    messages=components["messages"],
                    system_prompt=components["system_prompt"]
                )
            except Exception as fallback_e:
                logger.error(f"Error in {self.agent_name} response generation: {str(fallback_e)}")
                from ..utils import format_error_message
                return format_error_message(fallback_e)

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
        """Generate Mathematical Modeling tutor response (asynchronous)."""

        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        if not self.is_modeling_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        # Generate response with tools (async)
        try:
            response = await self.llm_service.a_generate_response_with_tools(
                messages=components["messages"],
                tools=self.tools,
                system_prompt=components["system_prompt"]
            )
        except Exception as e:
            logger.warning(f"Tool-enabled async generation failed, falling back: {e}")
            # Fallback to non-tool generation
            try:
                response = await self.llm_service.a_generate_response(
                    messages=components["messages"],
                    system_prompt=components["system_prompt"]
                )
            except Exception as fallback_e:
                logger.error(f"Error in {self.agent_name} async response generation: {str(fallback_e)}")
                from ..utils import format_error_message
                return format_error_message(fallback_e)

        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"],
            async_mode=True
        )


# Global agent instance
_modeling_agent: MathematicalModelingAgent | None= None


def get_mathematical_modeling_agent() -> MathematicalModelingAgent:
    """
    Get or create the global Mathematical Modeling agent instance.

    Returns:
        MathematicalModelingAgent instance
    """
    global _modeling_agent

    if _modeling_agent is None:
        _modeling_agent = MathematicalModelingAgent()

    return _modeling_agent
