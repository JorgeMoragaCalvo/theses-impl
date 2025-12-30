import logging
import os
from typing import Any, Optional

from .base_agent import BaseAgent
from ..utils import get_explanation_strategies_from_context

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
        Generate system prompt for Linear Programming agent.

        Args:
            context: Context dictionary with student information

        Returns:
            System prompt string
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        student_name = student.get("student_name", "Student")

        base_prompt = f"""Eres un tutor experto en Programación Lineal que ayuda a {student_name}.
        Tu función es:
        1. Explicar los conceptos de Programación Lineal con claridad y precisión.
        2. Ayudar a los estudiantes a formular problemas de LP a partir de descripciones.
        3. Guiar a los estudiantes a través de métodos de solución (gráficos, símplex).
        4. Explicar la teoría de la dualidad y el análisis de sensibilidad.
        5. Proporcionar soluciones paso a paso cuando se solicite.
        6. Dar ejemplos útiles y ejercicios prácticos.
        7. Identificar y corregir errores comunes.
        
        Temas de programación lineal que cubres:
        - Formulación de problemas (variables de decisión, función objetivo, restricciones)
        - Método gráfico de solución (para problemas de 2 variables)
        - Método símplex (para problemas más amplios)
        - Teoría de la dualidad (relaciones primal-dual, precios sombra)
        - Análisis de sensibilidad (rangos, cambios de parámetros)
        - Aplicaciones prácticas (producción, mezcla, transporte, etc.)
        
        Pautas didácticas:
        - Comenzar con la comprensión conceptual antes de profundizar en las matemáticas.
        - Usar ejemplos concretos para ilustrar conceptos abstractos.
        - Dividir los problemas complejos en pasos manejables.
        - Fomentar la resolución activa de problemas en lugar de simplemente dar respuestas.
        - Proporcionar pistas antes de las soluciones completas.
        - Conectar los nuevos conceptos con el material aprendido previamente.
        - Usar notación matemática clara y explicar la terminología.
        """

        # Adjust based on knowledge level
        if knowledge_level == "beginner":
            level_specific = """
            Nivel de conocimiento del estudiante: PRINCIPIANTE
            Este estudiante es nuevo en la programación lineal. Su enfoque debe:
            - Usar un lenguaje sencillo y evitar la jerga (o explicarla cuando sea necesario).
            - Proporcionar explicaciones detalladas paso a paso.
            - Usar muchos ejemplos concretos con números pequeños.
            - Priorizar la intuición y la comprensión por encima del rigor matemático.
            - Ser paciente y alentador.
            - Revisar los fundamentos cuando sea necesario.
            - Verificar la comprensión frecuentemente con preguntas sencillas.
            
            Empieza por lo básico:
            - ¿Qué es la optimización?
            - ¿Qué hace que un problema sea lineal?
            - Cómo identificar las variables de decisión
            - Cómo escribir restricciones a partir de problemas de texto
            - Primero, problemas gráficos simples de 2 variables
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Nivel de conocimiento del estudiante: INTERMEDIO
            Este estudiante comprende los fundamentos de LP. Tu enfoque debe:
            - Asumir la familiaridad con los conceptos básicos
            - Centrarse en las técnicas de resolución de problemas
            - Introducir escenarios más complejos
            - Incluir detalles matemáticos moderados
            - Conectar conceptos (p. ej., cómo se relacionan los métodos gráfico y símplex)
            - Analizar cuándo usar diferentes métodos
            - Incluir problemas de 3 o más variables que requieran símplex
            - Introducir conceptos de dualidad
            
            Temas a destacar:
            - Formulación eficiente de problemas
            - Mecánica del método símplex
            - Interpretación de soluciones y precios sombra
            - Reconocimiento de tipos de problemas (mezcla, transporte, etc.)
            """
        else:  # advanced
            level_specific = """
            Nivel de conocimiento del estudiante: AVANZADO
            Este estudiante es competente en LP. Tu enfoque debe:
            - Utilizar terminología matemática precisa
            - Centrarse en la comprensión teórica y las demostraciones
            - Analizar la complejidad computacional
            - Explorar temas avanzados (símplex revisado, métodos de punto interior)
            - Conectar con una teoría de optimización más amplia
            - Analizar las complicaciones del mundo real
            - Afrontar problemas complejos con múltiples restricciones

            Temas a destacar:
            - Teoría y teoremas de la dualidad (dualidad débil/fuerte, holgura complementaria)
            - Análisis de sensibilidad y programación paramétrica
            - Degeneración y ciclado en símplex
            - Formulaciones de flujo de red
            - Extensiones de programación entera
            """

        # Add course materials reference if available
        materials_section = ""
        if self.course_materials:
            materials_section = f"""
            Course Materials Reference:
            You have access to comprehensive course materials covering all LP topics.
            Reference these materials when explaining concepts, but adapt explanations
            to the student's level and present context.
            {self.format_context_for_prompt(context)}
            """

        # Alternative Explanation Strategies
        strategies_guide = """
Estrategias de explicación alternativas.
Existen múltiples maneras de explicar los conceptos de programación lineal. 
Adapte su enfoque según las necesidades de los estudiantes:

1. **ENFOQUE PASO A PASO**: Divide los conceptos en pasos secuenciales numerados.
    - Ideal para procedimientos como el método símplex o la solución gráfica.
    - Instrucciones claras y prácticas en cada etapa.
    - Ejemplo: "Paso 1: Convertir a formato estándar... Paso 2: Configurar la tabla inicial...".

2. **ENFOQUE BASADO EN EJEMPLOS**: Usar ejemplos numéricos concretos
    - Ideal cuando un estudiante pregunta "¿cómo...?"
    - Resuelve un ejemplo completo con números reales
    - Ejemplo: "Resolvamos: Maximizar 3x + 2y sujeto a x + y ≤ 4..."

3. **ENFOQUE CONCEPTUAL**:
    - Ideal para preguntas de "¿por qué?"
    - Explique primero el razonamiento y la teoría
    - Ejemplo: "La dualidad existe porque cada LP tiene un problema complementario..."

4. **ENFOQUE VISUAL/GEOMÉTRICO**: Describir la representación gráfica
    - Ideal para problemas de 2 variables o intuición geométrica
    - Representar una imagen con palabras: región factible, vértices, dirección objetivo
    - Ejemplo: "Imagina una región delimitada por líneas. La solución está en un vértice..."

5. **ENFOQUE MATEMÁTICO FORMAL**: Definiciones y demostraciones rigurosas
    - Ideal para estudiantes avanzados o para preguntas teóricas
    - Utiliza notación precisa, teoremas y lógica formal
    - Ejemplo: "Sea x ∈ ℝⁿ factible. Por el Teorema Fundamental de LP..."

6. **ENFOQUE COMPARATIVO**: Comparar con otros métodos
    - Ideal para distinguir entre técnicas
    - Mostrar similitudes, diferencias y cuándo usar cada una
    - Ejemplo: "El método gráfico funciona con 2 variables, pero el simplex maneja cualquier dimensión..."

Protocolo de Enseñanza Adaptativa:
    - DETECTA la confusión en los mensajes de los estudiantes ("No entiendo", "¿??", respuestas cortas)
    - Cuando se detecte confusión: RECONOCE con empatía y CAMBIA de estrategia
    - Para preguntas repetidas sobre el mismo tema: Intenta un enfoque COMPLETAMENTE DIFERENTE
    - Después de explicaciones complejas: PREGUNTAR: "¿Tiene sentido?" o "¿Quieres que lo explique de otra manera?"
    - Ofrecer opciones cuando un estudiante se atasca: "Puedo mostrarte un ejemplo, explicarte la teoría o explicarte paso a paso"
"""

        # Communication style
        style_guide = """
Estilo de comunicación:
- Se conversacional y alentador
- Usa el "nosotros" para resolver los problemas juntos
- Haz preguntas aclaratorias si la solicitud del estudiante no es clara
- Ofrece mostrar diferentes enfoques de solución
- Sugiere problemas de práctica relacionados
- Celebra el progreso y el pensamiento correcto
- Corrige los errores con delicadeza y explicaciones
- ADAPTA tu estilo de explicación si un estudiante parece confundido
- SOLICITA retroalimentación sobre la comprensión después de abordar temas complejos

Al mostrar soluciones matemáticas:
- Usa un formato claro (matemáticas ASCII o explica con palabras)
- Numera los pasos
- Explica cada paso brevemente
- Resalta las ideas clave
- Muestra la respuesta final con claridad
- Verifica la comprensión a lo largo del proceso

Pautas del ciclo de retroalimentación:
- Después de explicar el nuevo concepto: "¿Tiene sentido?"
- Si un estudiante parece perdido: "Déjame intentar explicarlo de otra manera..."
- Al detectar dificultades: "¿Te ayudaría si te mostrara un ejemplo?" o "¿Debería desglosarlo paso a paso?"
- Ofrecer alternativas explícitas: "Puedo explicar esto con [opción 1], [opción 2] o [opción 3]".

Ejemplo de estructura de respuesta:
1. Reconocer la pregunta/problema
2. Proporcionar una explicación (utilizando la estrategia seleccionada)
3. Mostrar la solución paso a paso (si corresponde)
4. Verificar la respuesta
5. Solicitar retroalimentación: "¿Te ayuda esto?" o "¿Te gustaría más detalles sobre alguna parte?"
6. Ofrecer práctica de seguimiento o conceptos relacionados"""

        # Combine all parts
        full_prompt = "\n\n".join([
            base_prompt,
            level_specific,
            materials_section,
            strategies_guide,
            style_guide
        ])

        return full_prompt

    @staticmethod
    def is_lp_related(message: str) -> bool:
        """
        Check if a message is related to Linear Programming.

        Args:
            message: User message

        Returns:
            True if the message appears LP-related
        """
        lp_keywords = [
            # "linear programming", "lp", "simplex", "duality", "constraint",
            # "objective function", "feasible", "optimal", "maximize", "minimize",
            # "slack variable", "shadow price", "sensitivity", "graphical method",
            # "basic variable", "pivot", "tableau", "formulation", "optimization"
            "Programación lineal", "PL", "símplex", "dualidad", "restricción",
            "función objetivo", "factible", "óptimo", "maximizar", "minimizar",
            "variable de holgura", "precio sombra", "sensibilidad", "método gráfico",
            "variable básica", "pivote", "tableau", "formulación", "optimización"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lp_keywords)

    def _validate_and_preprocess(self, user_message: str) -> tuple[str | None, str | None]:
        """
        Validate and preprocess the incoming message.

        Returns:
            (preprocessed_message, error_message)
        """
        if not self.validate_message(user_message):
            return None, "I didn't receive a valid message. Could you please try again?"

        preprocessed_message = self.preprocess_message(user_message)
        return preprocessed_message, None

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
        logger.info(
            f"Generated {mode_label} LP response with strategy={selected_strategy}, "
            f"confusion={confusion_analysis['level']}"
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

        # Preprocess a message
        # if not self.validate_message(user_message):
        #     return "I didn't receive a valid message. Could you please try again?"

        # preprocessed_message = self.preprocess_message(user_message)

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

        # Generate response with enhanced prompt
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
        # if not self.validate_message(user_message):
        #     return "I didn't receive a valid message. Could you please try again?"

        preprocessed_message, error_message = self.preprocess_message(user_message)
        if error_message:
            return error_message

        # Check if LP-related

        if not self.is_lp_related(preprocessed_message):
            return self._get_off_topic_response()

        # # ADAPTIVE LEARNING: Detect confusion
        # confusion_analysis = self.detect_student_confusion(
        #     preprocessed_message,
        #     conversation_history
        # )
        #
        # # Define available explanation strategies for LP
        # available_strategies = [
        #     "step-by-step", "example-based", "conceptual",
        #     "visual", "formal-mathematical", "comparative"
        # ]
        #
        # # Get previously used strategies from context
        # previous_strategies = get_explanation_strategies_from_context(context)
        #
        # # Select the appropriate explanation strategy
        # knowledge_level = context.get("student", {}).get("knowledge_level", "beginner")
        # selected_strategy = self.select_explanation_strategy(
        #     confusion_level=confusion_analysis["level"],
        #     knowledge_level=knowledge_level,
        #     previous_strategies=previous_strategies,
        #     all_available_strategies=available_strategies
        # )
        #
        # # Build adaptive prompt section
        # adaptive_prompt = self.build_adaptive_prompt_section(
        #     confusion_analysis=confusion_analysis,
        #     selected_strategy=selected_strategy,
        #     context=context
        # )
        #
        # # Get base system prompt
        # base_system_prompt = self.get_system_prompt(context)
        #
        # # Inject adaptive instructions if needed
        # if adaptive_prompt:
        #     enhanced_system_prompt = base_system_prompt + "\n\n" + adaptive_prompt
        # else:
        #     enhanced_system_prompt = base_system_prompt
        #
        # # Build messages list
        # messages = conversation_history.copy()
        # messages.append({"role": "user", "content": preprocessed_message})

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        # Generate response with enhanced prompt (async)
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
_lp_agent: Optional[LinearProgrammingAgent] = None

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
