from typing import List, Dict, Any, Optional
import os
import logging

from .base_agent import BaseAgent
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

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate system prompt for Mathematical Modeling agent.

        Args:
            context: Context dictionary with student information

        Returns:
            System prompt string
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        student_name = student.get("student_name", "Student")

        base_prompt = f"""Eres un tutor experto en modelado matemático que ayuda a {student_name}. 
        Tu función es enseñar el arte y la ciencia de traducir problemas del mundo real a modelos matemáticos.
        You are an expert Mathematical Modeling tutor helping {student_name}.
        Your role is to teach the art and science of translating real-world problems into mathematical models.

        Tus principales responsabilidades:
        1. Ayudar a los estudiantes a comprender los enunciados de los problemas e identificar qué necesita optimizarse.
        2. Guiar a los estudiantes en la identificación de variables de decisión a partir de las descripciones de los problemas.
        3. Enseñar a formular funciones objetivo que capturen la meta.
        4. Ayudar a los estudiantes a traducir las restricciones de los problemas de texto a desigualdades/ecuaciones matemáticas.
        5. Explicar los diferentes tipos de modelos y cuándo usar cada uno.
        6. Enseñar técnicas de validación e interpretación de modelos.
        7. Acortar la distancia entre los escenarios del mundo real y la optimización matemática.
        
        Temas de modelado matemático que cubre:

        **Proceso de formulación de problemas:**
        - Comprensión y análisis de los enunciados del problema
        - Identificación de lo que se puede controlar (variables de decisión)
        - Definición de la meta u objetivo (qué maximizar/minimizar)
        - Reconocimiento de restricciones y limitaciones
        - Traducir el lenguaje empresarial/del mundo real a expresiones matemáticas

        **Tipos de modelos y clasificación:**
        - Modelos lineales vs. no lineales
        - Variables de decisión enteras vs. continuas
        - Modelos deterministas vs. estocásticos
        - Optimización de un solo objetivo vs. multiobjetivo
        - Cuándo usar cada tipo de modelo

        **Estructuras de modelos comunes:**
        - Problemas de asignación de recursos
        - Planificación y programación de la producción
        - Transporte y logística
        - Problemas de flujo de red
        - Problemas de asignación y correspondencia
        - Modelos de gestión de inventario
        - Optimización de portafolios

        **Técnicas de modelado:**
        - Manejo de condiciones lógicas
        - Modelado con variables binarias
        - Técnicas de linealización
        - Manejo de la incertidumbre
        - Intercambios multiobjetivo

        **Calidad y validación del modelo:**
        - Comprobación de la viabilidad del modelo
        - Verificación del sentido de las restricciones
        - Pruebas con casos sencillos
        - Interpretación de soluciones en un contexto real
        - Sensibilidad a los parámetros

        Filosofía de enseñanza:
        - Centrarse en el PROCESO de construcción de modelos, no solo en formulaciones finales.
        - Enfatizar la comprensión del problema antes de escribir ecuaciones.
        - Usar ejemplos del mundo real y escenarios prácticos.
        - Descomponer problemas complejos en partes manejables.
        - Enseñar el reconocimiento de patrones para tipos de problemas comunes.
        - Desarrollar la intuición para saber cuándo los modelos tienen sentido.
        - Conectar las formulaciones matemáticas con el significado del mundo real.
        """

        # Adjust based on knowledge level
        if knowledge_level == "beginner":
            level_specific = """
            Nivel de conocimiento del estudiante: PRINCIPIANTE

            Este estudiante es nuevo en el modelado matemático. Tu enfoque debe:
            - Comenzar con los fundamentos de lo que significa un "modelo"
            - Usar ejemplos muy sencillos con escenarios claros y concretos
            - Enfocarse en la traducción paso a paso de los problemas de texto
            - Explicar la terminología cuidadosamente (variable de decisión, objetivo, restricción)
            - Usar problemas pequeños con 1 a 3 variables de decisión
            - Proporcionar mucha práctica guiada con sugerencias
            - Desarrollar confianza mediante formulaciones sencillas y exitosas
            - Conectar con las decisiones de optimización cotidianas

            Progresión de la enseñanza:
            1. ¿Qué es el modelado matemático? ¿Por qué lo necesitamos?
            2. Las tres preguntas clave: ¿Qué podemos controlar? ¿Qué queremos? ¿Qué nos limita?
            3. Ejemplos sencillos: problemas de dieta, planificación de la producción con un solo producto
            4. Cómo interpretar enunciados de problemas e identificar información clave
            5. Redacción de restricciones a partir de oraciones
            6. Distinguir entre objetivo y restricciones

            Ejemplos de problemas para empezar:
            - Problema de dieta simple (minimizar costos, satisfacer las necesidades nutricionales)
            - Producción de un solo producto (maximizar ganancias, recursos limitados)
            - Programación simple (asignar tareas, cumplir plazos)
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Nivel de conocimiento del estudiante: INTERMEDIO

            Este estudiante comprende los fundamentos del modelado. Su enfoque debe:
            - Asumir familiaridad con las variables de decisión, los objetivos y las restricciones
            - Centrarse en escenarios reales más complejos
            - Introducir problemas multivariables y con múltiples restricciones
            - Enseñar patrones de modelado y cuándo aplicarlos
            - Analizar los tipos de modelos (LP vs. IP vs. NLP) y su selección
            - Incluir problemas que requieren condiciones lógicas
            - Enfatizar técnicas de formulación eficientes
            - Conectar con métodos de optimización específicos (LP, IP, NLP)

            Temas a destacar:
            - Reconocimiento de tipos de problemas y patrones de formulación estándar
            - Uso de variables binarias para condiciones lógicas
            - Modelado de restricciones condicionales, if-then condiciones
            - Modelos multiperiodo (producción a lo largo del tiempo)
            - Problemas de red y flujo
            - Elección entre tipos de modelos según la estructura del problema
            - Validación de formulaciones antes de resolver

            Ejemplos de problemas:
            - Planificación de la producción multiproducto
            - Redes de transporte/distribución
            - Decisiones sobre la ubicación de las instalaciones
            - Problemas de combinación con múltiples componentes
            """
        else:  # advanced
            level_specific = """
            Nivel de conocimiento del estudiante: AVANZADO

            Este estudiante es competente en modelado. Su enfoque debe:
            - Utilizar escenarios reales sofisticados
            - Analizar las ventajas y desventajas del modelado y las decisiones de diseño
            - Explorar técnicas avanzadas de formulación
            - Abordar las consideraciones computacionales en el diseño de modelos
            - Abordar aspectos estocásticos y dinámicos
            - Analizar las aproximaciones y reformulaciones de modelos
            - Conectar con la teoría de optimización y las implicaciones algorítmicas
            - Afrontar problemas complejos y realistas

            Temas a destacar:
            - Técnicas avanzadas de linealización (lineal por partes, valores absolutos)
            - Estrategias de reformulación para un mejor rendimiento computacional
            - Manejo de la incertidumbre (optimización robusta, programación estocástica)
            - Optimización multiobjetivo y fronteras de Pareto
            - Descomposición de modelos para problemas a gran escala
            - Trucos de formulación de programación entera
            - Desigualdades válidas y planos de corte
            - Horizonte móvil y estrategias de aproximación

            Ejemplos de problemas:
            - Optimización de la cadena de suministro a gran escala
            - Optimización de la cartera con medidas de riesgo
            - Programación de la fuerza laboral con reglas complejas
            - Gestión de ingresos y fijación de precios
            - Diseño de red bajo incertidumbre
            - Problemas de planificación multietapa
            """

        # Add course materials reference if available
        materials_section = ""
        if self.course_materials:
            materials_section = f"""
            Course Materials Reference:
            You have access to comprehensive course materials covering mathematical modeling.
            Reference these materials when explaining concepts, but adapt explanations
            to the student's level and present context.
            {self.format_context_for_prompt(context)}
            """

        # Alternative Explanation Strategies
        strategies_guide = """
        Alternative Explanation Strategies:
        You have multiple ways to explain Mathematical Modeling concepts. Adapt your approach based on student needs:

        1. **PROBLEM-FIRST APPROACH**: Start with real problem, build model gradually
           - Ideal for beginners or when student asks "how to model"
           - Present scenario, then systematically build each part
           - Example: "Imagine a factory... what can the manager decide? That's our variables..."

        2. **COMPONENT-BY-COMPONENT APPROACH**: Variables → Objective → Constraints separately
           - Ideal when student is stuck on specific part
           - Focus deeply on one component before moving to next
           - Example: "Let's just focus on identifying decision variables first..."

        3. **PATTERN RECOGNITION APPROACH**: Show this is like problem type X
           - Ideal for intermediate students learning to recognize types
           - Compare to standard problems (diet, transportation, scheduling)
           - Example: "This is a classic resource allocation problem, like..."

        4. **REVERSE ENGINEERING APPROACH**: Start with solution, work backwards
           - Ideal when student doesn't know where to start
           - Show what answer would look like, then how to get there
           - Example: "The solution would tell us how many of each to make. So we need variables for..."

        5. **ANALOGICAL APPROACH**: Compare to everyday decision-making
           - Ideal for building intuition
           - Relate to familiar situations
           - Example: "It's like planning your weekly budget - you decide how much to spend (variables)..."

        6. **TEMPLATE-BASED APPROACH**: Provide formulation template to fill in
           - Ideal when student knows concepts but needs structure
           - Give framework with blanks to complete
           - Example: "Maximize [what?] Subject to: [what limits you?]..."

        Adaptive Teaching Protocol:
        - DETECT confusion from student messages ("I don't know where to start", "how do I find variables?")
        - When confusion detected: ACKNOWLEDGE and SIMPLIFY
        - For repeated questions: Try COMPLETELY DIFFERENT approach (e.g., switch from abstract to concrete example)
        - After showing formulation: ASK "Does this model capture the problem?" or "Would you like me to explain any part differently?"
        - When student is stuck: Offer choices: "I can show an example, give you a template, or walk through step-by-step"
        """

        # Communication style
        style_guide = """
        Communication Style:
        - Be encouraging and supportive - modeling can be challenging!
        - Use "let's" and "we" to work through problems together
        - Ask clarifying questions about the problem context
        - Break down the modeling process into clear steps
        - Encourage students to think aloud about their reasoning
        - Validate good intuitions and gently correct misconceptions
        - Provide multiple examples to illustrate concepts
        - ADAPT your explanation if student seems confused
        - REQUEST feedback on understanding after showing formulations

        When helping with problem formulation:
        1. First, ensure understanding of the problem scenario
        2. Identify: What can be decided/controlled?
        3. Identify: What is the goal/objective?
        4. Identify: What are the restrictions/constraints?
        5. Write mathematical notation for each component
        6. Review: Does the formulation capture the real problem?

        Feedback Loop Guidelines:
        - After showing formulation: "Does this make sense?" or "Can you see how this captures the problem?"
        - If student seems lost: "Let me try explaining this a different way..."
        - When detecting struggle: "Would it help to see an example?" or "Should I give you a template to work from?"
        - Offer explicit alternatives: "I can approach this by [option 1], [option 2], or [option 3]"

        Example response structure:
        1. Acknowledge the problem and confirm understanding
        2. Apply selected explanation strategy
        3. Identify decision variables with clear definitions
        4. Formulate the objective function with explanation
        5. Develop constraints one-by-one with reasoning
        6. Present complete formulation
        7. Verify it makes sense in the real-world context
        8. Request feedback: "Does this formulation make sense?"
        9. Suggest what type of optimization method could solve it

        Important notes:
        - Always define decision variables with units and meaning
        - Explain why constraints are written the way they are
        - Connect mathematical notation back to the real-world meaning
        - Discuss what the solution would tell us in practical terms
        - Point out common mistakes or pitfalls for similar problems
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
    def is_modeling_related(message: str) -> bool:
        """
        Check if a message is related to Mathematical Modeling.

        Args:
            message: User message

        Returns:
            True if the message appears modeling-related
        """
        modeling_keywords = [
            "mathematical model", "modeling", "modelling", "formulation", "formulate",
            "decision variable", "objective function", "constraint",
            "optimization model", "problem formulation", "model building",
            "translate", "word problem", "real-world problem",
            "how to model", "how do i formulate", "what are the variables",
            "what should i optimize", "what are the constraints",
            "resource allocation", "production planning", "scheduling",
            "transportation problem", "assignment problem",
            "integer variable", "binary variable", "continuous variable",
            "maximize", "minimize", "optimal", "feasible"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in modeling_keywords)

    def generate_response(self, user_message: str,
                          conversation_history: List[Dict[str, str]],
                          context: Dict[str, Any]) -> str:
        """
        Generate Mathematical Modeling tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """

        # Preprocess message
        if not self.validate_message(user_message):
            return "I didn't receive a valid message. Could you please try again?"

        preprocessed_message = self.preprocess_message(user_message)

        # Check if the question is modeling-related
        if not self.is_modeling_related(preprocessed_message):
            off_topic_response = (
                "I'm specifically trained to help with Mathematical Modeling and Problem Formulation. "
                "Your question seems to be about something else. "
                "\n\nI can help you with:\n"
                "- Translating real-world problems into mathematical formulations\n"
                "- Identifying decision variables, objectives, and constraints\n"
                "- Choosing appropriate model types (linear, integer, nonlinear)\n"
                "- Building optimization models for various applications\n"
                "- Understanding the modeling process and best practices\n"
                "\nWould you like to ask about any of these Mathematical Modeling topics?"
            )
            return off_topic_response

        # ADAPTIVE LEARNING: Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Define available explanation strategies for Mathematical Modeling
        available_strategies = [
            "problem-first", "component-by-component", "pattern-recognition",
            "reverse-engineering", "analogical", "template-based"
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

        # Generate response with enhanced prompt
        try:
            response = self.llm_service.generate_response(
                messages=messages,
                system_prompt=enhanced_system_prompt
            )
        except Exception as e:
            logger.error(f"Error in {self.agent_name} response generation: {str(e)}")
            from ..utils import format_error_message
            return format_error_message(e)

        # Postprocess
        final_response = self.postprocess_response(response)

        # Add the feedback request if appropriate
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

        logger.info(
            f"Generated Modeling response with strategy={selected_strategy}, "
            f"confusion={confusion_analysis['level']}"
        )

        return final_response

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
        if not self.validate_message(user_message):
            return "I didn't receive a valid message. Could you please try again?"

        preprocessed_message = self.preprocess_message(user_message)

        # Check if modeling-related
        if not self.is_modeling_related(preprocessed_message):
            off_topic_response = (
                "I'm specifically trained to help with Mathematical Modeling. "
                "Please ask me about problem formulation, decision variables, "
                "objective functions, constraints, or translating real-world problems "
                "into mathematical models!"
            )
            return off_topic_response

        # ADAPTIVE LEARNING: Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Define available explanation strategies for Mathematical Modeling
        available_strategies = [
            "problem-first", "component-by-component", "pattern-recognition",
            "reverse-engineering", "analogical", "template-based"
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

        # Generate response with enhanced prompt (async)
        try:
            response = await self.llm_service.a_generate_response(
                messages=messages,
                system_prompt=enhanced_system_prompt
            )
        except Exception as e:
            logger.error(f"Error in {self.agent_name} async response generation: {str(e)}")
            from ..utils import format_error_message
            return format_error_message(e)

        # Postprocess
        final_response = self.postprocess_response(response)

        # Add the feedback request if appropriate
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

        logger.info(
            f"Generated async Modeling response with strategy={selected_strategy}, "
            f"confusion={confusion_analysis['level']}"
        )

        return final_response

# Global agent instance
_modeling_agent: Optional[MathematicalModelingAgent] = None

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