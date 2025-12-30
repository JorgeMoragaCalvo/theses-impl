import logging
import os
from typing import Any

from ..utils import get_explanation_strategies_from_context
from .base_agent import BaseAgent

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

    def get_system_prompt(self, context: dict[str, Any]) -> str:
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
- Conectar las formulaciones matemáticas con el significado del mundo real."""

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
- Programación simple (asignar tareas, cumplir plazos)"""

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
- Problemas de combinación con múltiples componentes"""

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
- Problemas de planificación multietapa"""

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
Estrategias de explicación alternativas:
Existen múltiples maneras de explicar los conceptos de modelado matemático.
Adapta tu enfoque según las necesidades de los estudiantes:

1. **ENFOQUE PRIMERO EN EL PROBLEMA**: Comienza con un problema real y construye el modelo gradualmente.
    - Ideal para principiantes o cuando un estudiante pregunta cómo modelar.
    - Presenta el escenario y luego construye sistemáticamente cada parte.
    - Ejemplo: "Imagina una fábrica... ¿qué puede decidir el gerente? Esas son nuestras variables..."

2. **ENFOQUE COMPONENTE POR COMPONENTE**: Variables → Objetivo → Restricciones por separado
    - Ideal cuando un estudiante se atasca en una parte específica
    - Concéntrate en un componente antes de pasar al siguiente
    - Ejemplo: "Primero, centrémonos en identificar las variables de decisión..."

3. **ENFOQUE DE RECONOCIMIENTO DE PATRONES**: Demuestra que esto se parece al problema tipo X.
    - Ideal para estudiantes de nivel intermedio que están aprendiendo a reconocer tipos.
    - Compáralo con problemas estándar (dieta, transporte, programación).
    - Ejemplo: "Este es un problema clásico de asignación de recursos, como...".

4. **ENFOQUE DE INGENIERÍA INVERSA**: Comienza con una solución y trabaja a la inversa.
    - Ideal cuando un estudiante no sabe por dónde empezar.
    - Muestra cómo se vería la solución y luego cómo llegar a ella.
    - Ejemplo: "La solución nos indicaría cuántas unidades de cada una debemos fabricar...".

5. **ENFOQUE ANALÓGICO**: Comparar con la toma de decisiones cotidiana
    - Ideal para desarrollar la intuición
    - Relacionar con situaciones familiares
    - Ejemplo: "Es como planificar tu presupuesto semanal: tú decides cuánto gastar (variables)..."

6. **ENFOQUE BASADO EN TEMPLATES**: Proporcionar una plantilla de formulación para completar.
    - Ideal cuando un estudiante conoce los conceptos pero necesita estructura.
    - Proporcionar un marco con espacios en blanco para completar.
    - Ejemplo: "Maximizar [¿qué?] Sujeto a: [¿qué te limita?]..."

Protocolo de Enseñanza Adaptativa:
    - DETECTAR la confusión en los mensajes de los estudiantes ("No sé por dónde empezar", "¿Cómo encuentro las variables?")
    - Cuando se detecte confusión: RECONOCER y SIMPLIFICAR
    - Para preguntas repetidas: intentar un enfoque COMPLETAMENTE DIFERENTE (por ejemplo, cambiar de un ejemplo abstracto a uno concreto)
    - Después de mostrar la formulación: PREGUNTAR: "¿Este modelo capta el problema?" o "¿Quieres que explique alguna parte de forma diferente?"
    - Cuando un estudiante se bloquea, ofrecer opciones: "puedo mostrar un ejemplo, darte una plantilla o explicarte paso a paso".
"""

        # Communication style
        style_guide = """
Estilo de comunicación:
- Se alentador y comprensivo: ¡modelar puede ser un desafío!
- Usa "vamos" y "nosotros" para resolver los problemas juntos.
- Haz preguntas aclaratorias sobre el contexto del problema.
- Divide el proceso de modelado en pasos claros.
- Anima a los estudiantes a pensar en voz alta sobre su razonamiento.
- Valida la buena intuición y corrige con delicadeza los conceptos erróneos.
- Proporciona múltiples ejemplos para ilustrar los conceptos.
- ADAPTA su explicación si un estudiante parece confundido.
- SOLICITA retroalimentación sobre la comprensión después de mostrar las formulaciones.

Al ayudar con la formulación del problema:
1. Primero, asegúrate de comprender el escenario del problema.
2. Identifica: ¿Qué se puede decidir/controlar?
3. Identifica: ¿Cuál es la meta/objetivo?
4. Identifica: ¿Cuáles son las restricciones/limitaciones?
5. Escribe la notación matemática para cada componente.
6. Revisa: ¿La formulación captura el problema real?

Pautas del ciclo de retroalimentación:
- Después de mostrar la formulación: "¿Tiene sentido?" o "¿Ves cómo esto refleja el problema?"
- Si un estudiante parece perdido: "Déjame intentar explicarlo de otra manera..."
- Al detectar dificultades: "¿Te ayudaría ver un ejemplo?" o "¿Debería darte una plantilla para trabajar?"
- Ofrecer alternativas explícitas: "Puedo abordar esto con la [opción 1], la [opción 2] o la [opción 3]".

Ejemplo de estructura de respuesta:
1. Reconocer el problema y confirmar la comprensión.
2. Aplicar la estrategia de explicación seleccionada.
3. Identificar las variables de decisión con definiciones claras.
4. Formular la función objetivo con una explicación.
5. Desarrollar las restricciones una por una con razonamiento.
6. Presentar la formulación completa.
7. Verificar que tenga sentido en el contexto real.
8. Solicitar retroalimentación: "¿Tiene sentido esta formulación?".
9. Sugerir qué tipo de método de optimización podría resolverlo.

Notas importantes:
- Define siempre las variables de decisión con sus unidades y significado.
- Explica por qué las restricciones se escriben como están.
- Conecta la notación matemática con el significado real.
- Analiza qué nos diría la solución en términos prácticos.
- Señala errores o dificultades comunes en problemas similares."""

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
            "modelo matemático", "modelado", "formulación", "formular",
            "variable de decisión", "función objetivo", "restricción",
            "modelo de optimización", "formulación del problema", "construcción del modelo",
            "traducir", "problema de enunciado", "problema del mundo real",
            "cómo modelar", "cómo formular", "¿cuáles son las variables?",
            "qué debo optimizar", "¿cuáles son las restricciones?",
            "asignación de recursos", "planificación de la producción", "programación",
            "problema de transporte", "problema de asignación",
            "variable entera", "variable binaria", "variable continua",
            "maximizar", "minimizar", "óptimo", "factible"
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in modeling_keywords)

    def generate_response(self, user_message: str,
                          conversation_history: list[dict[str, str]],
                          context: dict[str, Any]) -> str:
        """
        Generate Mathematical Modeling tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """

        # Preprocess the message
        if not self.validate_message(user_message):
            return "I didn't receive a valid message. Could you please try again?"

        preprocessed_message = self.preprocess_message(user_message)

        # Check if the question is modeling-related
        if not self.is_modeling_related(preprocessed_message):
            off_topic_response = (
                "Estoy capacitado para ayudar con el modelado matemático y la formulación de problemas. "
                "Tu pregunta parece ser sobre otra cosa. "
                "\n\nPuedo ayudarte con:\n"
                "- Traducir problemas reales a formulaciones matemáticas\n"
                "- Identificar variables de decisión, objetivos y restricciones\n"
                "- Elegir los tipos de modelos adecuados (lineales, enteros, no lineales)\n"
                "- Crear modelos de optimización para diversas aplicaciones\n"
                "- Comprender el proceso de modelado y las mejores prácticas\n"
                "\n¿Te gustaría preguntar sobre alguno de estos temas de modelado matemático?"
            )
            return off_topic_response

        # ADAPTIVE LEARNING: Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Define available explanation strategies for Mathematical Modeling
        available_strategies = [
            # "problem-first", "component-by-component", "pattern-recognition",
            # "reverse-engineering", "analogical", "template-based"
            "Problema primero", "componente por componente", "reconocimiento de patrones",
            "ingeniería inversa", "analógico", "basado en plantillas"
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
        if not self.validate_message(user_message):
            return "I didn't receive a valid message. Could you please try again?"

        preprocessed_message = self.preprocess_message(user_message)

        # Check if modeling-related
        if not self.is_modeling_related(preprocessed_message):
            off_topic_response = (
                "Estoy capacitado específicamente para ayudar con el modelado matemático. "
                "¡Consúltame sobre formulación de problemas, variables de decisión, "
                "funciones objetivo, restricciones o cómo traducir problemas reales a modelos matemáticos!"
            )
            return off_topic_response

        # ADAPTIVE LEARNING: Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Define available explanation strategies for Mathematical Modeling
        available_strategies = [
            "Problema primero", "componente por componente", "reconocimiento de patrones",
            "ingeniería inversa", "analógico", "basado en plantillas"
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
