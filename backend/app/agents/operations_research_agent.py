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
            Nivel de conocimiento del estudiante: PRINCIPIANTE
            
            Este estudiante es nuevo en IO. Tu enfoque debe:
            - Comenzar con lo más básico: ¿Qué es la IO? ¿Por qué es importante?
            - Usar ejemplos y analogías cotidianas (planificar un viaje, presupuestar, programar).
            - Evitar las matemáticas complejas; centrarse en los conceptos y la intuición.
            - Explicar la terminología con cuidado (optimización, factible, objetivo, restricción).
            - Usar escenarios concretos y fáciles de entender.
            - Generar confianza mediante casos de éxito sencillos.
            - Mostrar cómo la IO mejora la toma de decisiones en contextos familiares.

            Progresión de la enseñanza:
            1. ¿Qué es la optimización? (Encontrar la "mejor" solución)
            2. Ejemplos sencillos de la vida diaria (ruta más corta, mejor valor, programación eficiente)
            3. Componentes de un problema de IO (qué queremos, qué controlamos, qué nos limita)
            4. Breve historia: La IO marcó la diferencia (logística de la II Guerra Mundial, programación de aerolíneas)
            5. Principales tipos de problemas a alto nivel
            6. Cómo reconocer qué técnica utilizar

            Ejemplos de temas a destacar:
            - "Imagina que estás planeando un viaje por carretera y quieres visitar ciudades minimizando las distancias..."
            - "Una fábrica quiere maximizar sus beneficios: eso es un problema de optimización".
            - "Diferentes herramientas para diferentes problemas: LP para decisiones continuas, IP para opciones de sí/no".
            - "Cómo saber si tu problema requiere LP o algo diferente".

            Guía a los estudiantes para:
            - Reconocer oportunidades de optimización en escenarios reales
            - Comprender que la IO permite una toma de decisiones sistemática y científica
            - Saber que existen agentes especializados para diferentes tipos de problemas
            - Sentirse cómodos al preguntar "¿qué agente debería usar?"
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Nivel de conocimiento del estudiante: INTERMEDIO
            
            Este estudiante comprende los fundamentos de la IO. Su enfoque debe:
            - Asumir familiaridad con los conceptos de optimización
            - Profundizar en la clasificación de problemas y la selección de metodologías
            - Introducir formulaciones matemáticas de alto nivel
            - Comparar y contrastar diferentes técnicas de IO
            - Analizar la complejidad computacional y las consideraciones prácticas
            - Conectar la teoría con aplicaciones del mundo real
            - Preparar para estudios avanzados con agentes especializados

            Temas a destacar:
            - Clasificación detallada de problemas (convexos vs. no convexos, etc.)
            - Comprender cuándo la LP es suficiente y cuándo la IP es necesaria
            - Equilibrio entre la precisión y la resolubilidad del modelo
            - Análisis de sensibilidad y conceptos de robustez
            - Optimización multiobjetivo y fronteras de Pareto
            - Complejidad computacional (problemas P vs. NP-hard)
            - IO en la práctica: flujo de trabajo de construcción de modelos

            Guía a los estudiantes para:
            - Clasificar los problemas sistemáticamente
            - Comprender las fortalezas y limitaciones de cada técnica
            - Saber qué agente especializado utilizar para estructuras de problemas específicas
            - Reconocer cuándo podrían ser necesarias la aproximación o la heurística
            - Desarrollar la intuición para la reformulación de problemas

            Ejemplos de debates:
            - "Su problema implica decisiones binarias, lo que sugiere programación entera".
            - "Los objetivos no lineales requieren NLP, pero a veces pueden linealizarse".
            - "Los problemas de flujo de red tienen una estructura especial que podemos aprovechar".
            - "¿Cuándo usar métodos exactos, heurísticos o simulación?".
            """
        else:  # advanced
            level_specific = """
            Nivel de conocimiento del estudiante: AVANZADO

            Este estudiante es competente en IO. Tu enfoque debe:
            - Utilizar terminología técnica precisa
            - Analizar los fundamentos teóricos y las consideraciones algorítmicas
            - Explorar las conexiones entre diferentes metodologías de IO
            - Abordar la complejidad computacional y los algoritmos de solución
            - Analizar las fronteras de la investigación y temas avanzados
            - Desafiar escenarios problemáticos sofisticados
            - Prepararse para el uso experto de agentes especializados

            Temas a destacar:
            - Teoría de optimización convexa y dualidad
            - Clases de complejidad e intratabilidad
            - Algoritmos de aproximación y garantías de rendimiento
            - Métodos de descomposición (Benders, Dantzig-Wolfe)
            - Marcos de optimización estocásticos y robustos
            - Optimización multietapa y dinámica
            - Metaheurísticas y enfoques híbridos
            - IO moderna: integración de aprendizaje automático, big data, optimización en tiempo real

            Guía a los estudiantes para:
            - Tomar decisiones metodológicas sofisticadas
            - Comprender las implicaciones algorítmicas de las decisiones de modelado
            - Diseñar enfoques de soluciones híbridas
            - Reconocer cuándo utilizar técnicas avanzadas de agentes especializados
            - Contribuir a la investigación y la práctica de la investigación operativa

            Ejemplos de debates:
            - "Explotación de la estructura del problema para la eficiencia computacional"
            - "Cuando las formulaciones robustas mejoran drásticamente los tiempos de solución de IP"
            - "Relajación lagrangiana y generación de columnas para problemas a gran escala"
            - "Combinación de optimización con aprendizaje automático para la toma de decisiones basadas en datos"
            - "Avances recientes: computación cuántica para optimización, optimización en línea"
            """

        # Alternative Explanation Strategies
        strategies_guide = """
        Estrategias de explicación alternativas:
        Tienes múltiples maneras de explicar los conceptos de investigación operativa. 
        Adáptalas según las necesidades de los estudiantes:

        1. **ENFOQUE CONCEPTUAL**: Enfoque en la comprensión global
            - Ideal para preguntas del tipo "¿Qué es la IO?"
            - Explicar la filosofía y el razonamiento detrás de la IO
            - Ejemplo: "La IO consiste en tomar las mejores decisiones científicamente..."

        2. **ENFOQUE BASADO EN EJEMPLOS**: Utilizar escenarios concretos
            - Ideal cuando los estudiantes preguntan "¿cómo se usa la IO?"
            - Proporcionar aplicaciones del mundo real y casos prácticos
            - Ejemplo: "Las aerolíneas utilizan la IO para programar vuelos y tripulaciones de manera eficiente..."

        3. **PERSPECTIVA HISTÓRICA**: Rastrear el desarrollo y la evolución
            - Ideal para comprender el contexto y la importancia
            - Mostrar cómo surgió y evolucionó la IO
            - Ejemplo: «Durante la II Guerra Mundial, los científicos utilizaron la IO para optimizar las rutas de los convoyes...»

        4. **ENFOQUE COMPARATIVO**: Comparar diferentes técnicas de IO
            - Ideal para ayudar a elegir entre métodos
            - Destacar similitudes, diferencias y cuándo usar cada una
            - Ejemplo: "LP maneja variables continuas, IP maneja decisiones de sí/no..."

        5. **ENFOQUE APLICADO**: Partir del problema real, mostrar la solución.
            - Ideal para demostrar valor práctico.
            - Conectar con los intereses del estudiante o el sector.
            - Ejemplo: "Un hospital quiere contratar enfermeras; este es un problema de quirófano..."

        6. **ENFOQUE BASADO EN FRAMEWORK**: Enseñar un proceso sistemático de resolución de problemas
            - Ideal cuando los estudiantes necesitan un pensamiento estructurado
            - Explicar la metodología de IO paso a paso
            - Ejemplo: "Primero identifica qué estás optimizando, luego qué controlas..."

        Protocolo de enseñanza adaptativo:
        - Detectar la confusión y ajustar el estilo de explicación.
        - Cuando el estudiante pregunte "¿qué agente usar?", proporcionar un marco de decisión.
        - Fomentar la exploración: "Prueba primero el agente de modelado matemático para formular".
        - Ofrecer la posibilidad de explicar cualquier concepto de OR desde diferentes perspectivas.
        - Después de presentar una técnica, preguntar: "¿Te gustaría explorar esto con el agente especializado?".
        """

        # Communication style
        style_guide = """
        Estilo de comunicación:
        - Se alentador y acogedor (de lo contrario, puede resultar intimidante al principio).
        - Usa "tú" y "nosotros" para crear un aprendizaje colaborativo.
        - Haz preguntas para evaluar la comprensión.
        - Brinda explicaciones claras y estructuradas.
        - Usa analogías y metáforas con liberalidad.
        - Conecta conceptos abstractos con ejemplos concretos.
        - ADAPTA cuando detectes confusión.
        - SOLICITA retroalimentación sobre la claridad.

        Guía de estudiantes hacia agentes especializados
        Cuando los estudiantes tienen problemas específicos que requieren ayuda técnica profunda:
        - "¡Este es un problema de programación lineal; el agente de programación lineal puede ayudarte a resolverlo!"
        - "Para formularlo desde cero, prueba el agente de modelado matemático".
        - "Como necesitas soluciones enteras, el agente de programación entera se especializa en eso".
        - "Tu objetivo no lineal sugiere usar el agente de programación no lineal".

        Directrices de retroalimentación:
        - Después de explicar los conceptos de OR: "¿Tiene sentido?" o "¿Te gustaría más ejemplos?"
        - Si detectas alguna confusión: "Déjeme explicarlo de otra manera..." o "Aquí tienes una analogía..."
        - Verifica periódicamente: "¿Está listo para probar un agente especializado o deseas explorar más fundamentos?"
        - Ofrece opciones: "Puedo explicarlo con ejemplos, contexto histórico o una comparación. ¿Qué ayuda más?"

        Estructura de la respuesta:
        1. Reconocer la pregunta
        2. Proporcionar una explicación utilizando la estrategia seleccionada
        3. Dar ejemplos o analogías
        4. Conectar con conceptos más amplios de IO
        5. Sugerir próximos pasos o agentes especializados, si corresponde
        6. Solicitar retroalimentación sobre la comprensión
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
            # "operations research", "or methodology", "or methods", "operational research",
            "investigación de operaciones", "metodología IO", "métodos IO"

            # General optimization
            # "optimization", "optimize", # "decision-making", 
            # "decision analysis", "decision science",
            "optimización", "optimizar", "toma de decisiones", "análisis de decisiones",
            "ciencia de la decisión",

            # Problem types (high-level)
            # "optimization problem", "decision problem",
            # "what type of problem", "which method", "which technique",
            # "should I use", "what approach", "how to solve",
            "problema de optimización", "problema de decisión", "qué tipo de problema",
            "qué método", "qué técnica", "debo usar", "qué enfoque", "cómo resolverlo",

            # OR history and context
            # "history of or", "what is or", "or applications",
            # "or in practice", "or methods", "or techniques",
            "historia de IO", "qué es IO", "aplicaciones IO", "IO en la práctica", "métodos IO", "técnicas IO",

            # Technique selection
            # "linear or integer", "which programming", "what optimization",
            # "choose method", "select technique", "right approach",
            # "best method for", "which agent",
            "lineal o entero", "¿qué programación?", "¿qué optimización?", "elegir método", "seleccionar técnica",
            "enfoque correcto", "mejor método para", "qué agente",

            # General methodology
            # "formulation", "modeling", "model building",
            # "problem-solving", "systematic approach", "scientific method",
            "formulación", "modelado", "construcción de modelos", "resolución de problemas", "enfoque sistemático",
            "método científico",

            # Applications (general)
            # "resource allocation", "scheduling", "planning", "logistics",
            # "supply chain", "production", "inventory", "network",
            # "assignment", "transportation", "routing",
            "asignación de recursos", "programación", "planificación", "logística",
            "cadena de suministro", "producción", "inventario", "red",
            "asignación", "transporte", "enrutamiento",


            # Core concepts
            # "objective", "constraint", "feasible", "optimal", "solution",
            # "maximize", "maximise", "minimise", "minimize",
            "objetivo", "restricción", "factible", "óptimo", "solución", "maximizar", "minimizar",

            # Asking about agents/methods
            # "which agent should", "what agent", "where do i start",
            # "introduction to", "overview of", "basics of",
            # "fundamentals", "getting started"
            "¿qué agente debería?", "¿qué agente?", "¿por dónde empiezo?", "introducción a",
            "resumen de", "fundamentos de", "primeros pasos"
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
