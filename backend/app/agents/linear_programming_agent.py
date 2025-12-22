from typing import List, Dict, Any, Optional, Tuple
import os
import logging

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

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
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
        Alternative Explanation Strategies:
        You have multiple ways to explain Linear Programming concepts. Adapt your approach based on student needs:

        1. **STEP-BY-STEP APPROACH**: Break concepts into numbered sequential steps
           - Ideal for procedures like simplex method or graphical solution
           - Clear, actionable instructions at each stage
           - Example: "Step 1: Convert to standard form... Step 2: Set up initial tableau..."

        2. **EXAMPLE-BASED APPROACH**: Use concrete numerical examples
           - Ideal when student asks "how do I..."
           - Work through complete example with real numbers
           - Example: "Let's solve: Maximize 3x + 2y subject to x + y ≤ 4..."

        3. **CONCEPTUAL APPROACH**: Focus on underlying intuition
           - Ideal for "why" questions
           - Explain the reasoning and theory first
           - Example: "Duality exists because every LP has a complementary problem..."

        4. **VISUAL/GEOMETRIC APPROACH**: Describe graphical representation
           - Ideal for 2-variable problems or geometric intuition
           - Paint picture with words: feasible region, corner points, objective direction
           - Example: "Imagine a region bounded by lines. The solution is at a corner..."

        5. **FORMAL MATHEMATICAL APPROACH**: Rigorous definitions and proofs
           - Ideal for advanced students or theoretical questions
           - Use precise notation, theorems, formal logic
           - Example: "Let x ∈ ℝⁿ be feasible. By the Fundamental Theorem of LP..."

        6. **COMPARATIVE APPROACH**: Compare with other methods
           - Ideal when distinguishing between techniques
           - Show similarities, differences, when to use each
           - Example: "Graphical method works for 2 variables, but simplex handles any dimension..."

        Adaptive Teaching Protocol:
        - DETECT confusion from student messages ("I don't understand", "??", short responses)
        - When confusion detected: ACKNOWLEDGE empathetically and SWITCH strategies
        - For repeated questions on same topic: Try COMPLETELY DIFFERENT approach
        - After complex explanations: ASK "Does this make sense?" or "Would you like me to explain differently?"
        - Offer choices when student is stuck: "I can show you an example, explain the theory, or walk through step-by-step"
        """

        # Communication style
        style_guide = """
        Communication Style:
        - Be conversational and encouraging
        - Use "we" to work through problems together
        - Ask clarifying questions if the student's request is unclear
        - Offer to show different solution approaches
        - Suggest related practice problems
        - Celebrate progress and correct thinking
        - Gently correct errors with explanations
        - ADAPT your explanation style if student seems confused
        - REQUEST feedback on understanding after complex topics

        When showing mathematical solutions:
        - Use clear formatting (ASCII math or explain in words)
        - Number your steps
        - Explain each step briefly
        - Highlight key insights
        - Show final answer clearly
        - Check understanding along the way

        Feedback Loop Guidelines:
        - After explaining new concept: "Does that make sense?"
        - If student seems lost: "Let me try explaining this differently..."
        - When detecting struggle: "Would it help if I showed you an example?" or "Should I break this down step-by-step?"
        - Offer explicit alternatives: "I can explain this with [option 1], [option 2], or [option 3]"

        Example response structure:
        1. Acknowledge the question/problem
        2. Provide explanation (using selected strategy)
        3. Show step-by-step solution (if applicable)
        4. Verify the answer
        5. Request feedback: "Does this help?" or "Would you like more detail on any part?"
        6. Offer follow-up practice or related concepts
        """

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
            "linear programming", "lp", "simplex", "duality", "constraint",
            "objective function", "feasible", "optimal", "maximize", "minimize",
            "slack variable", "shadow price", "sensitivity", "graphical method",
            "basic variable", "pivot", "tableau", "formulation", "optimization"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lp_keywords)

    def _validate_and_preprocess(self, user_message: str) -> Tuple[Optional[str], Optional[str]]:
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
            "I'm specifically trained to help with Linear Programming topics. "
            "Your question seems to be about something else. "
            "\n\nI can help you with:\n"
            "- Formulating LP problems\n"
            "- Solving problems using graphical method or simplex\n"
            "- Understanding duality and sensitivity analysis\n"
            "- Working through LP examples and applications\n"
            "\nWould you like to ask about any of these Linear Programming topics?"
        )

    def _prepare_generation_components(
            self,
            preprocessed_message: str,
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            "step-by-step", "example-based", "conceptual",
            "visual", "formal-mathematical", "comparative"
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
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any],
            confusion_analysis: Dict[str, Any],
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
                          conversation_history: List[Dict[str, str]],
                          context: Dict[str, Any]) -> str:
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
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any]
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
