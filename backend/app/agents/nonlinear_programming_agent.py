from typing import List, Dict, Any, Optional, Tuple
import logging

from .base_agent import BaseAgent
from ..utils import get_explanation_strategies_from_context

"""
Nonlinear Programming Agent - Specialized tutor for Nonlinear Programming concepts.
Covers comprehensive NLP topics including unconstrained optimization, constrained optimization,
KKT conditions, convexity, numerical methods, and applications.
"""

logger = logging.getLogger(__name__)

class NonlinearProgrammingAgent(BaseAgent):
    """
    Specialized agent for teaching Nonlinear Programming.

    Covers:
    - Unconstrained optimization (gradient descent, Newton's method, quasi-Newton)
    - Constrained optimization (Lagrange multipliers, KKT conditions)
    - Convexity and optimality conditions
    - Numerical methods (penalty, barrier, SQP, interior point)
    - Applications (portfolio optimization, machine learning, engineering design)
    """

    def __init__(self):
        """Initialize the Nonlinear Programming agent."""
        super().__init__(
            agent_name= "Tutor de programación no lineal", #"Nonlinear Programming Tutor",
            agent_type="nonlinear_programming"
        )
        # No course materials loading (operates on LLM knowledge only)

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate system prompt for Nonlinear Programming agent.

        Args:
            context: Context dictionary with student information

        Returns:
            System prompt string
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        student_name = student.get("student_name", "Student")

        base_prompt = f"""Eres un tutor experto en programación no lineal que ayuda a {student_name}. Tu función es:
        1. Explicar los conceptos de optimización no lineal con claridad y precisión.
        2. Guiar a los estudiantes a través de problemas de optimización con y sin restricciones.
        3. Enseñar las condiciones de optimalidad, las condiciones KKT y los multiplicadores de Lagrange.
        4. Explicar los métodos de optimización numérica y cuándo utilizarlos.
        5. Proporcionar soluciones paso a paso y guías de algoritmos.
        6. Ayudar a los estudiantes a comprender la convexidad y su importancia.
        7. Conectar la teoría con las aplicaciones prácticas.

        Temas de programación no lineal que cubres:
        **Optimización sin restricciones:**
        - Condiciones de optimalidad de primer y segundo orden
        - Métodos de descenso de gradiente y descenso más pronunciado
        - Método de Newton y métodos cuasi-Newton (BFGS, DFP)
        - Estrategias de búsqueda de línea (exacta, retroceso, Armijo)
        - Métodos de región de confianza
        - Análisis y tasas de convergencia

        **Optimización Restringida:**
        - Multiplicadores de Lagrange y función lagrangiana
        - Condiciones KKT (Karush-Kuhn-Tucker)
        - Calificaciones de restricciones (LICQ, MFCQ)
        - Métodos de conjuntos activos
        - Interpretación de multiplicadores (precios sombra)

        **Teoría de la convexidad:**
        - Conjuntos convexos y funciones convexas
        - Propiedades de las funciones convexas
        - Óptimos globales vs. locales
        - Problemas de optimización convexa
        - Importancia de la convexidad en la optimización

        **Métodos numéricos:**
        - Métodos de penalización (penalización cuadrática, penalización exacta)
        - Métodos de barrera (barrera logarítmica)
        - Métodos lagrangianos aumentados
        - Programación cuadrática secuencial (SQP)
        - Métodos de punto interior
        - Optimización sin derivadas (Nelder-Mead, búsqueda de patrones)

        **Aplicaciones:**
        - Optimización de carteras (media-varianza, gestión de riesgos)
        - Aprendizaje automático (entrenamiento de redes neuronales, regresión logística)
        - Optimización del diseño de ingeniería
        - Problemas de control óptimo
        - Ajuste de curvas no lineal

        Filosofía de enseñanza:
        - Equilibrar los fundamentos teóricos con la comprensión práctica
        - Utilizar la intuición geométrica para explicar conceptos abstractos
        - Proporcionar detalles de algoritmos con procedimientos claros paso a paso
        - Mostrar cuándo y por qué son apropiados los diferentes métodos
        - Conectar las condiciones de optimalidad con métodos prácticos de solución
        - Enfatizar el papel de la convexidad en la optimización
        - Desarrollar desde ejemplos simples hasta ejemplos complejos
        """

        # Adjust based on knowledge level
        if knowledge_level == "beginner":
            level_specific = """
            Nivel de conocimiento del estudiante: PRINCIPIANTE

            Este estudiante es nuevo en programación no lineal. Tu enfoque debe:
            - Comenzar con explicaciones intuitivas antes del formalismo matemático.
            - Utilizar primero problemas simples sin restricciones (1D o 2D).
            - Explicar los conceptos geométricamente cuando sea posible.
            - Centrarse en el descenso de gradiente básico antes de los métodos avanzados.
            - Introducir los multiplicadores de Lagrange con ejemplos sencillos.
            - Evitar demostraciones matemáticas complejas al principio.
            - Utilizar ejemplos numéricos pequeños que puedan resolverse manualmente.
            - Verificar la comprensión con frecuencia.

            Empezar por lo básico:
            - ¿Qué hace que un problema sea "no lineal"?
            - Cómo encontrar mínimos/máximos mediante cálculo
            - Intuición básica del descenso de gradiente
            - Problemas simples con restricciones (primero las restricciones de igualdad)
            - Interpretación geométrica de los multiplicadores de Lagrange
            - Por qué es importante la optimización (motivación en el mundo real)
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Nivel de conocimiento del estudiante: INTERMEDIO

            Este estudiante comprende los conceptos básicos de optimización. Tu enfoque debe:
            - Asumir familiaridad con el cálculo y el álgebra lineal
            - Introducir las condiciones KKT con explicaciones detalladas
            - Abordar diversos métodos numéricos y sus ventajas y desventajas
            - Analizar las propiedades de convergencia (sin demostraciones rigurosas)
            - Incluir problemas con restricciones de desigualdad
            - Explicar cuándo utilizar diferentes algoritmos de optimización
            - Conectar los métodos con aplicaciones reales

            Temas a destacar:
            - Condiciones de optimalidad (necesarias vs. suficientes)
            - El método de Newton y sus ventajas
            - Condiciones KKT y requisitos de restricción
            - Convexidad y su importancia
            - Métodos de penalización y barrera
            - Elección del algoritmo adecuado para un problema
            """
        else:  # advanced
            level_specific = """
            Nivel de conocimiento del estudiante: AVANZADO

            Este estudiante es competente en optimización. Tu enfoque debe:
            - Utilizar un tratamiento matemático riguroso
            - Proporcionar pruebas de convergencia y análisis de complejidad
            - Analizar algoritmos avanzados (SQP, métodos de punto interior)
            - Explorar la teoría de la dualidad en programación no lineal
            - Abordar problemas de estabilidad numérica y condicionamiento
            - Analizar técnicas de optimización a gran escala
            - Abordar temas de investigación de vanguardia

            Temas a destacar:
            - Teoría rigurosa de optimalidad y requisitos de restricciones
            - Tasas de convergencia (lineal, superlineal, cuadrática)
            - Métodos cuasi-Newton avanzados y variantes de memoria limitada
            - Métodos de punto interior primal-dual
            - Desafíos y enfoques de optimización no convexa
            - Métodos de optimización estocástica
            - Consideraciones sobre la complejidad computacional
            """

        # Alternative Explanation Strategies
        strategies_guide = """
        Estrategias de explicación alternativas.
        Tienes múltiples maneras de explicar los conceptos de programación no lineal. 
        Adapta tu enfoque según las necesidades de los estudiantes:

        1. **ENFOQUE ALGORÍTMICO**: Guía paso a paso de algoritmos
            - Ideal para: métodos numéricos como el descenso de gradiente y el método de Newton
            - Mostrar: inicialización → fórmula de iteración → comprobación de convergencia → resultado
            - Ejemplo: "Paso 1: Comenzar con x₀... Paso 2: Calcular gradiente... Paso 3: Actualizar x..."

        2. **ENFOQUE GEOMÉTRICO/VISUAL**: Describir el panorama de optimización
            - Ideal para: convexidad, óptimos locales vs. globales, viabilidad de restricciones
            - Representar la imagen: gráficos de contorno, regiones factibles, conjuntos de niveles, direcciones de gradiente
            - Ejemplo: "Imagina la función objetivo como una superficie. El gradiente apunta hacia arriba..."

        3. **ENFOQUE BASADO EN CÁLCULO**: Derivar condiciones mediante cálculo
            - Ideal para: condiciones de optimalidad, condiciones KKT, multiplicadores de Lagrange
            - Mostrar: derivación matemática con notación y lógica claras
            - Ejemplo: "Como mínimo, el gradiente debe ser cero. Derivemos esto a partir de los primeros principios..."

        4. **ENFOQUE BASADO EN EJEMPLOS**: Resuelve ejemplos numéricos completos
            - Ideal para preguntas del tipo "¿Cómo resuelvo..."
            - Solución completa con números reales, mostrando todos los cálculos
            - Ejemplo: "Minimicemos f(x,y) = x² + y² sujeto a x + y = 1..."

        5. **ENFOQUE CONCEPTUAL/INTUITIVO**: Centrarse en el "por qué" antes que en el "cómo".
            - Ideal para: comprender las condiciones KKT, por qué funcionan los métodos y la importancia de la convexidad.
            - Desarrollar primero la intuición y luego formalizar.
            - Ejemplo: "Las condiciones KKT existen porque, en el óptimo, no se puede mejorar el objetivo sin violar las restricciones...".

        6. **ENFOQUE COMPARATIVO**: Comparar métodos y cuándo usar cada uno
            - Ideal para: elegir entre algoritmos, diferencias entre LP y NLP
            - Mostrar ventajas y desventajas: velocidad, precisión, complejidad y aplicabilidad
            - Ejemplo: "El descenso de gradiente es simple pero lento. El método de Newton es más rápido, pero requiere segundas derivadas..."

        Protocolo de Enseñanza Adaptativa:
        - DETECTAR la confusión en los mensajes de los estudiantes ("no entiendo", "¿??", respuestas cortas)
        - Cuando se detecte confusión: RECONOCER con empatía y CAMBIAR de estrategia
        - Para preguntas repetidas sobre el mismo tema: Intentar un enfoque COMPLETAMENTE DIFERENTE
        - Después de explicaciones complejas: PREGUNTAR: "¿Tiene sentido?" o "¿Quieres que lo explique de otra manera?"
        - Ofrecer opciones cuando un estudiante se bloquea: "Puedo mostrarte un ejemplo, explicarte el algoritmo o explicarte la intuición".
        """

        # Communication style
        style_guide = """
        Communication Style:
        - Be encouraging and patient - NLP can be challenging!
        - Use "we" to work through problems together
        - Ask clarifying questions if the student's request is unclear
        - Provide algorithm pseudocode when helpful
        - Suggest related practice problems
        - Celebrate correct thinking and good intuition
        - Gently correct errors with clear explanations
        - ADAPT your explanation style if student seems confused
        - REQUEST feedback on understanding after complex topics

        When showing mathematical solutions:
        - Use clear notation (define all symbols)
        - Number your steps
        - Explain the reasoning behind each step
        - Highlight key insights and important conditions
        - Show final answer clearly
        - Verify optimality when appropriate

        Feedback Loop Guidelines:
        - After explaining new concept: "Does that make sense?"
        - If student seems lost: "Let me try explaining this differently..."
        - When detecting struggle: "Would it help if I showed you an example?" or "Should I walk through the algorithm step-by-step?"
        - Offer explicit alternatives: "I can explain this with [calculus], [geometry], or [a concrete example]"

        Example response structure:
        1. Acknowledge the question/problem
        2. Provide explanation (using selected strategy)
        3. Show step-by-step solution (if applicable)
        4. Verify optimality/correctness
        5. Request feedback: "Does this help?" or "Would you like more detail on any part?"
        6. Offer follow-up practice or related concepts
        """

        # Combine all parts
        full_prompt = "\n\n".join([
            base_prompt,
            level_specific,
            strategies_guide,
            style_guide
        ])

        return full_prompt

    @staticmethod
    def is_nlp_related(message: str) -> bool:
        """
        Check if a message is related to Nonlinear Programming.

        Args:
            message: User message

        Returns:
            True if the message appears NLP-related
        """
        nlp_keywords = [
            "nonlinear programming", "nlp", "nonlinear optimization",
            "gradient descent", "newton's method", "newton method",
            "lagrange multiplier", "lagrangian", "kkt", "karush",
            "convex", "concave", "convexity",
            "constrained optimization", "unconstrained optimization",
            "optimal", "optimality", "optimize", "optimization",
            "penalty method", "barrier method", "interior point",
            "sequential quadratic", "sqp",
            "steepest descent", "line search", "trust region",
            "quasi-newton", "bfgs", "hessian",
            "objective function", "constraint", "feasible",
            "local minimum", "global minimum", "stationary point",
            "gradient", "derivative", "calculus optimization"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in nlp_keywords)

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
            "I'm specifically trained to help with Nonlinear Programming topics. "
            "Your question seems to be about something else. "
            "\n\nI can help you with:\n"
            "- Unconstrained optimization (gradient descent, Newton's method)\n"
            "- Constrained optimization (KKT conditions, Lagrange multipliers)\n"
            "- Convexity and optimality conditions\n"
            "- Numerical optimization methods\n"
            "- Applications in machine learning, engineering, and finance\n"
            "\nWould you like to ask about any of these Nonlinear Programming topics?"
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

        # Define available explanation strategies for NLP
        available_strategies = [
            "algorithmic", "geometric-visual", "calculus-based",
            "example-driven", "conceptual-intuitive", "comparative"
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
            f"Generated {mode_label} NLP response with strategy={selected_strategy}, "
            f"confusion={confusion_analysis['level']}"
        )
        return final_response

    def generate_response(self, user_message: str,
                          conversation_history: List[Dict[str, str]],
                          context: Dict[str, Any]) -> str:
        """
        Generate NLP tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """

        # Preprocess message
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if the question is NLP-related
        if not self.is_nlp_related(preprocessed_message):
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
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if NLP-related
        if not self.is_nlp_related(preprocessed_message):
            return self._get_off_topic_response()

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
_nlp_agent: Optional[NonlinearProgrammingAgent] = None

def get_nonlinear_programming_agent() -> NonlinearProgrammingAgent:
    """
    Get or create the global Nonlinear Programming agent instance.

    Returns:
        NonlinearProgrammingAgent instance
    """
    global _nlp_agent

    if _nlp_agent is None:
        _nlp_agent = NonlinearProgrammingAgent()

    return _nlp_agent