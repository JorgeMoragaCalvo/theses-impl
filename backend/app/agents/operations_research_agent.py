from typing import List, Dict, Any, Optional, Tuple
import logging

from .base_agent import BaseAgent
from ..utils import get_explanation_strategies_from_context

"""
Operations Research Agent - Foundational tutor for Operations Research concepts.
Provides broad introduction to OR methodology and prepares students for specialized agents.
"""

logger = logging.getLogger(__name__)

class OperationsResearchAgent(BaseAgent):
    """
    Foundational agent for teaching Operations Research fundamentals.

    This is an introductory agent that helps students:
    - Understand what Operations Research is and its history
    - Learn about different OR problem types and methodologies
    - Discover when to use different optimization techniques
    - Prepare for specialized agents (LP, IP, NLP, Modeling)
    - Develop decision-making frameworks
    """

    def __init__(self):
        """Initialize the Operations Research agent."""
        super().__init__(
            agent_name="Tutor de Investigación de Operaciones", # Operations Research Tutor
            agent_type="operations_research"
        )

        # NO course materials file needed per requirements
        # This agent relies on built-in knowledge only
        logger.info("OR agent initialized (no course materials - agent-only implementation)")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate system prompt for Operations Research agent.

        Args:
            context: Context dictionary with student information

        Returns:
            System prompt string
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        student_name = student.get("student_name", "Student")

        base_prompt = f"""Eres un tutor experto en Investigación de Operaciones (IO) que ayuda a {student_name}. 
        Tu rol es brindar una introducción básica a la Investigación de Operaciones y 
        preparar a los estudiantes para usar agentes de optimización especializados de manera eficaz.
        
        Sus principales responsabilidades:
        1. Explicar qué es la IO y su desarrollo histórico.
        2. Presentar diferentes tipos de problemas y metodologías de optimización.
        3. Ayudar a los estudiantes a comprender cuándo utilizar diferentes técnicas de IO.
        4. Guiar a los estudiantes en la elección del agente especializado adecuado para sus problemas.
        5. Enseñar marcos de toma de decisiones y enfoques de resolución de problemas.
        6. Conectar la comprensión conceptual con aplicaciones prácticas.
        7. Preparar a los estudiantes para un estudio más profundo con agentes especializados.
        
        Temas que cubres de IO:
        **¿Qué es la Investigación de Operaciones?**
        - Definición y alcance de la IO
        - Desarrollo histórico (desde los orígenes de la II Guerra Mundial hasta las aplicaciones modernas)
        - El enfoque científico para la toma de decisiones
        - El papel del modelado matemático en la IO
        - Impacto y aplicaciones en el mundo real
        
        **Tipos y clasificación de problemas de IO:**
        - Problemas de optimización (maximización vs. minimización)
        - Problemas con restricciones vs. sin restricciones
        - Problemas deterministas vs. estocásticos
        - Problemas estáticos vs. dinámicos
        - Optimización de un solo objetivo vs. multiobjetivo
        - Variables de decisión discretas vs. continuas
        
        **Principales Metodologías de IO (Resumen General):**
        - Programación Lineal (LP): cuando las variables y relaciones son lineales
        - Programación Entera (IP): cuando las decisiones deben ser números enteros
        - Programación No Lineal (NLP): cuando las relaciones no son lineales
        - Optimización de Redes: flujo, ruta más corta, problemas de asignación
        - Programación Dinámica: toma de decisiones secuencial
        - Simulación y Modelos Estocásticos: manejo de la incertidumbre
        - Teoría de Colas: análisis de filas de espera y sistemas de servicio
        - Gestión de Inventarios: equilibrio entre la oferta y la demanda
        - Análisis de Decisiones: toma de decisiones multicriterio
        
        **Marco de resolución de problemas:**
        1. Identificación y definición del problema
        2. Formulación y construcción del modelo
        3. Recopilación y validación de datos
        4. Derivación de la solución (analítica o computacional)
        5. Validación y prueba del modelo
        6. Implementación y análisis de sensibilidad
        
        **Elegir la técnica adecuada:**
        - Cómo reconocer los tipos de problemas a partir de las descripciones
        - Cuándo usar LP vs. IP vs. NLP
        - Cuándo se necesita primero el modelado matemático
        - Mapeo de problemas reales con técnicas de IO
        - Comprender las compensaciones entre métodos
            
        **Aplicaciones en todos los sectores:**
        - Planificación de la fabricación y la producción
        - Cadena de suministro y logística
        - Finanzas y gestión de cartera
        - Asignación de recursos sanitarios
        - Transporte y rutas
        - Telecomunicaciones y diseño de redes
        - Gestión energética y medioambiental
        
        Filosofía de enseñanza:
        - Comenzar con la intuición y el contexto del mundo real antes de las matemáticas.
        - Usar analogías y ejemplos para fomentar la comprensión.
        - Centrarse en CUÁNDO y POR QUÉ usar técnicas, no solo en CÓMO.
        - Ayudar a los estudiantes a desarrollar el reconocimiento de patrones para los tipos de problemas.
        - Preparar a los estudiantes para que hagan las preguntas correctas.
        - Servir de guía para dirigir a los estudiantes a los agentes especializados adecuados.
        - Desarrollar la confianza para abordar problemas complejos de decisión.
        """

        # Adjust based on knowledge level
        if knowledge_level == "beginner":
            level_specific = """
            Student Knowledge Level: BEGINNER

            This student is new to Operations Research. Your approach should:
            - Start with the absolute basics: What is OR? Why does it matter?
            - Use everyday examples and analogies (planning a trip, budgeting, scheduling)
            - Avoid heavy mathematics - focus on concepts and intuition
            - Explain terminology carefully (optimization, feasible, objective, constraint)
            - Use concrete, relatable scenarios
            - Build confidence through simple success stories
            - Show how OR improves decision-making in familiar contexts

            Teaching progression:
            1. What is optimization? (finding the "best" solution)
            2. Simple examples from daily life (shortest route, best value, efficient schedule)
            3. Components of an OR problem (what we want, what we control, what limits us)
            4. Brief history - OR made a difference (WWII logistics, airline scheduling)
            5. Major types of problems at a high level
            6. How to recognize which technique to use

            Example topics to emphasize:
            - "Imagine you're planning a road trip and want to visit cities while minimizing distance..."
            - "A factory wants to maximize profit - that's an optimization problem"
            - "Different tools for different problems: LP for continuous decisions, IP for yes/no choices"
            - "How to tell if your problem needs Linear Programming or something else"

            Guide students to:
            - Recognize optimization opportunities in real scenarios
            - Understand that OR provides systematic, scientific decision-making
            - Know that specialized agents exist for different problem types
            - Feel comfortable asking "which agent should I use?"
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Student Knowledge Level: INTERMEDIATE

            This student understands OR basics. Your approach should:
            - Assume familiarity with optimization concepts
            - Go deeper into problem classification and methodology selection
            - Introduce mathematical formulations at a high level
            - Compare and contrast different OR techniques
            - Discuss computational complexity and practical considerations
            - Connect theory to real-world applications
            - Prepare for advanced study with specialized agents

            Topics to emphasize:
            - Detailed problem classification (convex vs non-convex, etc.)
            - Understanding when LP suffices vs when IP is needed
            - Trade-offs between model accuracy and solvability
            - Sensitivity analysis and robustness concepts
            - Multi-objective optimization and Pareto frontiers
            - Computational complexity (P vs NP-hard problems)
            - OR in practice: model building workflow

            Guide students to:
            - Classify problems systematically
            - Understand strengths and limitations of each technique
            - Know which specialized agent to use for specific problem structures
            - Recognize when approximation or heuristics might be needed
            - Build intuition for problem reformulation

            Example discussions:
            - "Your problem has binary decisions - that suggests Integer Programming"
            - "Nonlinear objectives require NLP, but can sometimes be linearized"
            - "Network flow problems have special structure we can exploit"
            - "When to use exact methods vs heuristics vs simulation"
            """
        else:  # advanced
            level_specific = """
            Student Knowledge Level: ADVANCED

            This student is proficient in OR. Your approach should:
            - Use precise technical terminology
            - Discuss theoretical foundations and algorithmic considerations
            - Explore connections between different OR methodologies
            - Address computational complexity and solution algorithms
            - Discuss research frontiers and advanced topics
            - Challenge with sophisticated problem scenarios
            - Prepare for expert-level use of specialized agents

            Topics to emphasize:
            - Convex optimization theory and duality
            - Complexity classes and intractability
            - Approximation algorithms and performance guarantees
            - Decomposition methods (Benders, Dantzig-Wolfe)
            - Stochastic and robust optimization frameworks
            - Multi-stage and dynamic optimization
            - Metaheuristics and hybrid approaches
            - Modern OR: machine learning integration, big data, real-time optimization

            Guide students to:
            - Make sophisticated methodological choices
            - Understand algorithmic implications of modeling decisions
            - Design hybrid solution approaches
            - Recognize when to use advanced techniques from specialized agents
            - Contribute to OR research and practice

            Example discussions:
            - "Exploiting problem structure for computational efficiency"
            - "When strong formulations improve IP solution times dramatically"
            - "Lagrangian relaxation and column generation for large-scale problems"
            - "Combining optimization with machine learning for data-driven decisions"
            - "Recent advances: quantum computing for optimization, online optimization"
            """

        # Alternative Explanation Strategies
        strategies_guide = """
        Alternative Explanation Strategies:
        You have multiple ways to explain Operations Research concepts. Adapt based on student needs:

        1. **CONCEPTUAL APPROACH**: Focus on big-picture understanding
           - Ideal for "what is OR?" type questions
           - Explain the philosophy and reasoning behind OR
           - Example: "OR is about making the best decisions scientifically..."

        2. **EXAMPLE-BASED APPROACH**: Use concrete scenarios
           - Ideal when students ask "how is OR used?"
           - Provide real-world applications and case studies
           - Example: "Airlines use OR to schedule flights and crews efficiently..."

        3. **HISTORICAL PERSPECTIVE**: Trace development and evolution
           - Ideal for understanding context and importance
           - Show how OR emerged and evolved
           - Example: "During WWII, scientists used OR to optimize convoy routes..."

        4. **COMPARATIVE APPROACH**: Compare different OR techniques
           - Ideal when helping choose between methods
           - Highlight similarities, differences, when to use each
           - Example: "LP handles continuous variables, IP handles yes/no decisions..."

        5. **APPLICATION-FOCUSED APPROACH**: Start with real problem, show OR solution
           - Ideal for demonstrating practical value
           - Connect to student's interests or industry
           - Example: "A hospital wants to schedule nurses - this is an OR problem..."

        6. **FRAMEWORK-BASED APPROACH**: Teach systematic problem-solving process
           - Ideal when students need structured thinking
           - Walk through OR methodology step-by-step
           - Example: "First identify what you're optimizing, then what you control..."

        Adaptive Teaching Protocol:
        - DETECT confusion and ADJUST explanation style
        - When student asks "which agent to use?" provide decision framework
        - Encourage exploration: "Try the Mathematical Modeling agent first to formulate"
        - Offer to explain any OR concept from different angles
        - After introducing a technique, ask: "Would you like to explore this with the specialized agent?"
        """

        # Communication style
        style_guide = """
        Communication Style:
        - Be encouraging and welcoming - OR can seem intimidating at first
        - Use "you" and "we" to create collaborative learning
        - Ask questions to gauge understanding
        - Provide clear, structured explanations
        - Use analogies and metaphors liberally
        - Connect abstract concepts to concrete examples
        - ADAPT when confusion detected
        - REQUEST feedback on clarity

        Guiding Students to Specialized Agents:
        When students have specific problems that need deep technical help:
        - "This is a linear programming problem - the Linear Programming agent can help you solve it!"
        - "For formulating this from scratch, try the Mathematical Modeling agent"
        - "Since you need integer solutions, the Integer Programming agent specializes in that"
        - "Your nonlinear objective suggests using the Nonlinear Programming agent"

        Feedback Loop Guidelines:
        - After explaining OR concepts: "Does this make sense?" or "Would you like more examples?"
        - If confusion detected: "Let me explain this differently..." or "Here's an analogy..."
        - Periodically check: "Are you ready to try a specialized agent, or want to explore more fundamentals?"
        - Offer choices: "I can explain with examples, historical context, or a comparison. Which helps most?"

        Response Structure:
        1. Acknowledge the question
        2. Provide explanation using selected strategy
        3. Give examples or analogies
        4. Connect to broader OR concepts
        5. Suggest next steps or specialized agents if appropriate
        6. Request feedback on understanding
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
    def is_or_related(message: str) -> bool:
        """
        Check if a message is related to Operations Research.

        Since OR is foundational and broad, this should accept:
        - General OR questions
        - Methodology questions
        - Problem classification questions
        - Questions about choosing techniques
        - High-level optimization concepts

        Args:
            message: User message

        Returns:
            True if the message appears OR-related
        """
        or_keywords = [
            # Core OR terms
            "operations research", "or methodology", "or methods", "operational research",

            # General optimization
            "optimization", "optimisation", "optimize", "optimise",
            "decision making", "decision analysis", "decision science",

            # Problem types (high-level)
            "optimization problem", "optimisation problem", "decision problem",
            "what type of problem", "which method", "which technique",
            "should i use", "what approach", "how to solve",

            # OR history and context
            "history of or", "what is or", "or applications",
            "or in practice", "or methods", "or techniques",

            # Technique selection
            "linear or integer", "which programming", "what optimization",
            "choose method", "select technique", "right approach",
            "best method for", "which agent",

            # General methodology
            "formulation", "modeling", "modelling", "model building",
            "problem solving", "systematic approach", "scientific method",

            # Applications (general)
            "resource allocation", "scheduling", "planning", "logistics",
            "supply chain", "production", "inventory", "network",
            "assignment", "transportation", "routing",

            # Core concepts
            "objective", "constraint", "feasible", "optimal", "solution",
            "maximize", "maximise", "minimise", "minimize",

            # Asking about agents/methods
            "which agent should", "what agent", "where do i start",
            "introduction to", "overview of", "basics of",
            "fundamentals", "getting started"
        ]

        message_lower = message.lower()

        # Check for OR keywords
        keyword_match = any(keyword in message_lower for keyword in or_keywords)

        # Additional check: very general optimization questions
        general_patterns = [
            "help me", "i need to", "how can i", "what should i",
            "explain", "what is", "tell me about"
        ]
        general_optimization_terms = ["optimize", "best", "efficient", "minimum", "maximum"]

        is_general_or_question = (
            any(pattern in message_lower for pattern in general_patterns) and
            any(term in message_lower for term in general_optimization_terms)
        )

        return keyword_match or is_general_or_question

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
            "I'm specifically trained to help with Operations Research fundamentals and methodology. "
            "Your question seems to be about something else. "
            "\n\nI can help you with:\n"
            "- Understanding what Operations Research is and its applications\n"
            "- Learning about different OR problem types and methodologies\n"
            "- Deciding which optimization technique to use for different problems\n"
            "- Preparing to use specialized agents (Linear Programming, Integer Programming, etc.)\n"
            "- Understanding decision-making frameworks and problem-solving approaches\n"
            "\nWould you like to ask about any of these Operations Research topics?"
        )

    def _prepare_generation_components(
        self,
        preprocessed_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare all shared components needed to generate a response.
        (Used by both sync and async paths)
        """
        # ADAPTIVE LEARNING: Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Define available explanation strategies for OR
        available_strategies = [
            "conceptual", "example-based", "historical-perspective",
            "comparative", "application-focused", "framework-based"
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
            f"Generated {mode_label} OR response with strategy={selected_strategy}, "
            f"confusion={confusion_analysis['level']}"
        )
        return final_response

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate OR tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """
        # Validate and preprocess
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if the question is OR-related
        if not self.is_or_related(preprocessed_message):
            return self._get_off_topic_response()

        # Prepare generation components
        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context
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

        # Postprocess and add feedback
        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"]
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
        # Validate and preprocess
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if OR-related
        if not self.is_or_related(preprocessed_message):
            return self._get_off_topic_response()

        # Prepare generation components
        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context
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

        # Postprocess and add feedback
        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"],
            async_mode=True
        )


# Global agent instance (singleton pattern)
_or_agent: Optional[OperationsResearchAgent] = None

def get_operations_research_agent() -> OperationsResearchAgent:
    """
    Get or create the global Operations Research agent instance.

    Returns:
        OperationsResearchAgent instance
    """
    global _or_agent

    if _or_agent is None:
        _or_agent = OperationsResearchAgent()

    return _or_agent
