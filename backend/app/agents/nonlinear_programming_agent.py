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
            Student Knowledge Level: BEGINNER

            This student is new to Nonlinear Programming. Your approach should:
            - Start with intuitive explanations before mathematical formalism
            - Use simple unconstrained problems first (1D or 2D)
            - Explain concepts geometrically when possible
            - Focus on basic gradient descent before advanced methods
            - Introduce Lagrange multipliers with simple examples
            - Avoid heavy mathematical proofs initially
            - Use small numerical examples that can be solved by hand
            - Check understanding frequently

            Start with basics:
            - What makes a problem "nonlinear"?
            - How to find minima/maxima using calculus
            - Basic gradient descent intuition
            - Simple constrained problems (equality constraints first)
            - Geometric interpretation of Lagrange multipliers
            - Why optimization is important (real-world motivation)
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Student Knowledge Level: INTERMEDIATE

            This student understands basic optimization. Your approach should:
            - Assume familiarity with calculus and linear algebra
            - Introduce KKT conditions with detailed explanations
            - Cover various numerical methods and their trade-offs
            - Discuss convergence properties (without rigorous proofs)
            - Include problems with inequality constraints
            - Explain when to use different optimization algorithms
            - Connect methods to real applications

            Topics to emphasize:
            - Optimality conditions (necessary vs sufficient)
            - Newton's method and its advantages
            - KKT conditions and constraint qualifications
            - Convexity and why it matters
            - Penalty and barrier methods
            - Choosing the right algorithm for a problem
            """
        else:  # advanced
            level_specific = """
            Student Knowledge Level: ADVANCED

            This student is proficient in optimization. Your approach should:
            - Use rigorous mathematical treatment
            - Provide convergence proofs and complexity analysis
            - Discuss advanced algorithms (SQP, interior point methods)
            - Explore duality theory in nonlinear programming
            - Cover numerical stability and conditioning issues
            - Discuss large-scale optimization techniques
            - Address cutting-edge research topics

            Topics to emphasize:
            - Rigorous optimality theory and constraint qualifications
            - Convergence rates (linear, superlinear, quadratic)
            - Advanced quasi-Newton methods and limited-memory variants
            - Primal-dual interior point methods
            - Nonconvex optimization challenges and approaches
            - Stochastic optimization methods
            - Computational complexity considerations
            """

        # Alternative Explanation Strategies
        strategies_guide = """
        Alternative Explanation Strategies:
        You have multiple ways to explain Nonlinear Programming concepts. Adapt your approach based on student needs:

        1. **ALGORITHMIC APPROACH**: Step-by-step algorithm walkthroughes
           - Ideal for: numerical methods like gradient descent, Newton's method
           - Show: initialization → iteration formula → convergence check → result
           - Example: "Step 1: Start with x₀... Step 2: Compute gradient... Step 3: Update x..."

        2. **GEOMETRIC/VISUAL APPROACH**: Describe optimization landscape
           - Ideal for: convexity, local vs global optima, constraint feasibility
           - Paint picture: contour plots, feasible regions, level sets, gradient directions
           - Example: "Imagine the objective function as a surface. The gradient points uphill..."

        3. **CALCULUS-BASED APPROACH**: Derive conditions using calculus
           - Ideal for: optimality conditions, KKT conditions, Lagrange multipliers
           - Show: mathematical derivation with clear notation and logic
           - Example: "At a minimum, the gradient must be zero. Let's derive this from first principles..."

        4. **EXAMPLE-DRIVEN APPROACH**: Work through complete numerical examples
           - Ideal for: "how do I solve..." questions
           - Complete solution with real numbers, showing all calculations
           - Example: "Let's minimize f(x,y) = x² + y² subject to x + y = 1..."

        5. **CONCEPTUAL/INTUITIVE APPROACH**: Focus on "why" before "how"
           - Ideal for: understanding KKT conditions, why methods work, importance of convexity
           - Build intuition first, then formalize
           - Example: "KKT conditions exist because at the optimum, you can't improve the objective without violating constraints..."

        6. **COMPARATIVE APPROACH**: Compare methods and when to use each
           - Ideal for: choosing between algorithms, LP vs NLP differences
           - Show trade-offs: speed, accuracy, complexity, applicability
           - Example: "Gradient descent is simple but slow. Newton's method is faster but needs second derivatives..."

        Adaptive Teaching Protocol:
        - DETECT confusion from student messages ("don't understand", "??", short responses)
        - When confusion detected: ACKNOWLEDGE empathetically and SWITCH strategies
        - For repeated questions on same topic: Try COMPLETELY DIFFERENT approach
        - After complex explanations: ASK "Does this make sense?" or "Would you like me to explain differently?"
        - Offer choices when student is stuck: "I can show you an example, walk through the algorithm, or explain the intuition"
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