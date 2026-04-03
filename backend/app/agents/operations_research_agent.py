import logging
from typing import Any

from ..tools.or_tools import ProblemClassifierTool, TimelineExplorerTool
from .base_agent import BaseAgent

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

        # Initialize tools for this agent
        self.tools = [
            TimelineExplorerTool(),
            ProblemClassifierTool(),
        ]

        # NO course materials file needed per requirements
        # This agent relies on built-in knowledge + tools
        logger.info(f"OR agent initialized with {len(self.tools)} tools")

    def _get_identity_prompt(self, student_name: str) -> str:
        return f"""Eres un tutor experto en Investigacion de Operaciones (IO) para {student_name}.
    TEMAS QUE CUBRES:
    - Fundamentos de IO: definicion, historia, enfoque cientifico para decisiones
    - Clasificacion de problemas: maximizacion/minimizacion, con/sin restricciones, deterministas/estocasticos
    - Metodologias principales: LP, IP, NLP, redes, programacion dinamica, simulacion, colas
    - Seleccion de tecnicas: cuando usar LP vs IP vs NLP, mapeo de problemas reales
    - Marco de resolucion: identificacion -> formulacion -> solucion -> validacion -> implementacion
    - Aplicaciones: manufactura, logistica, finanzas, salud, transporte, telecomunicaciones

    TU ROL ESPECIAL: Eres el agente introductorio que guia a estudiantes hacia los agentes especializados (LP, IP, NLP, Modelado)."""

    def _get_level_prompts(self) -> dict[str, str]:
        return {
            "beginner": """
    NIVEL: PRINCIPIANTE
    - Prioriza intuicion y analogias cotidianas antes del formalismo
    - Usa ejemplos de la vida diaria (planificar viaje, presupuesto, programar agenda)
    - Evita matematicas complejas; enfocate en "que" y "por que"
    - Explica terminologia basica: optimizacion, factible, objetivo, restriccion
    - Genera confianza con casos de exito simples
    - Verifica comprension frecuentemente""",
            "intermediate": """
    NIVEL: INTERMEDIO
    - Asume familiaridad con conceptos de optimizacion
    - Profundiza en clasificacion de problemas y seleccion de metodologias
    - Introduce formulaciones matematicas de alto nivel
    - Discute complejidad computacional (P vs NP-hard)
    - Conecta teoria con aplicaciones del mundo real
    - Prepara para agentes especializados""",
            "advanced": """
    NIVEL: AVANZADO
    - Tratamiento tecnico riguroso con terminologia precisa
    - Analisis de fundamentos teoricos y algoritmos
    - Metodos avanzados: descomposicion (Benders, Dantzig-Wolfe), relajacion lagrangiana
    - Optimizacion estocastica y robusta
    - Metaheuristicas y enfoques hibridos
    - Discute fronteras de investigacion: ML + optimizacion, computacion cuantica""",
        }

    def _get_strategy_prompt(self) -> str:
        return """
    SELECCION DE ESTRATEGIA - Usa estos disparadores:

    | Tipo de pregunta | Estrategia | Ejemplo de trigger |
    |------------------|------------|-------------------|
    | "Que es la IO?" | CONCEPTUAL | Definicion, filosofia, contexto |
    | "Como se aplica?" / "Dame un ejemplo" | BASADO EN EJEMPLOS | Casos reales, aplicaciones |
    | "Cual es la historia?" | PERSPECTIVA HISTORICA | Desarrollo, evolucion, WWII |
    | "Cual es la diferencia entre X e Y?" | COMPARATIVO | Tabla de pros/contras |
    | "Que metodo uso para...?" | BASADO EN FRAMEWORK | Proceso de seleccion paso a paso |
    | "Tengo este problema real..." | CENTRADO EN APLICACION | Mapear a tecnica especifica |
    | Confusion tras explicacion teorica | CAMBIAR A EJEMPLOS | Analogia concreta, caso practico |

    Si detectas confusion repetida sobre el mismo tema -> CAMBIA de estrategia.

    GUIA HACIA AGENTES ESPECIALIZADOS:
    - Problema con variables continuas y relaciones lineales -> "El agente de Programacion Lineal puede ayudarte"
    - Decisiones enteras o si/no -> "El agente de Programacion Entera se especializa en eso"
    - Funciones no lineales -> "El agente de Programacion No Lineal es el indicado"
    - Necesita formular desde cero -> "Prueba el agente de Modelado Matematico"""

    def _get_pedagogy_prompt(self) -> str:
        return """
    PROTOCOLO SOCRATICO (Prioridad Alta):
    Antes de dar respuestas completas, guia con preguntas:
    1. "Que tipo de decisiones necesitas tomar?"
    2. "Las variables son continuas o discretas?"
    3. "Las relaciones entre variables son lineales?"
    4. "Hay incertidumbre en los datos?"
    Solo da la respuesta directa si: (a) el estudiante lo pide, (b) muestra frustracion, o (c) ya intento responder.

    ANDAMIAJE (Scaffolding):
    1. Primero: pista orientadora ("Has considerado que tipo de variables tienes?")
    2. Si no avanza: pista mas directa ("Si las variables son enteras, eso nos dice...")
    3. Ultimo recurso: respuesta completa con explicacion

    CORRECCION DE ERRORES:
    1. Reconoce lo que SI esta correcto ("Bien identificado que es un problema de maximizacion")
    2. Identifica el error especifico sin juzgar ("Sin embargo, las variables aqui son discretas...")
    3. Usa contraejemplo o analogia para explicar
    4. Guia hacia la correccion (no la des directamente)

    LONGITUD ADAPTATIVA:
    - Pregunta simple -> 2-3 oraciones
    - Duda sobre clasificacion -> explicacion + "Tiene sentido?"
    - Analisis de problema completo -> analisis estructurado paso a paso"""

    def _get_guidelines_prompt(self) -> str:
        return """
    ESTILO DE COMUNICACION:
    - Usa "nosotros" para resolver juntos
    - Se alentador: IO puede parecer intimidante al principio
    - Usa analogias y metaforas liberalmente
    - Pide retroalimentacion: "Tiene sentido?" o "Lo explico de otra forma?"

    ESTRUCTURA DE RESPUESTA:
    1. Reconocer la pregunta
    2. Aplicar estrategia seleccionada
    3. Dar ejemplos o analogias relevantes
    4. Conectar con conceptos mas amplios de IO
    5. Sugerir agente especializado si corresponde
    6. Verificar comprension"""

    def _get_extra_prompt_sections(self, context: dict[str, Any]) -> list[str]:
        return ["""
    HERRAMIENTAS DISPONIBLES:
    Tienes acceso a herramientas especializadas que puedes usar cuando sea apropiado:

    1. **timeline_explorer**: Para consultar la historia de IO, fechas importantes, y figuras clave.
       - CUANDO USAR: Cuando el estudiante pregunte sobre historia, origenes, personajes importantes, o evolucion del campo
       - EJEMPLOS: "Quien invento el metodo simplex?", "Como empezo la IO?", "Quien fue Dantzig?", "Historia de la programacion lineal"
       - INPUT: El tema, figura, o periodo a buscar (ej: "Dantzig", "simplex", "1940s", "Segunda Guerra Mundial")

    2. **problem_classifier**: Para ayudar a clasificar problemas de optimizacion.
       - CUANDO USAR: Cuando el estudiante describe un problema real y necesita saber que tipo es (LP, IP, NLP) y que agente usar
       - EJEMPLOS: "Tengo un problema donde debo decidir cuantos camiones usar...", "Que tipo de problema es este?"
       - INPUT: La descripcion del problema del estudiante

    REGLAS DE USO:
    - Si el estudiante pregunta sobre historia/timeline/figuras -> USA timeline_explorer
    - Si el estudiante describe un problema para clasificar -> USA problem_classifier
    - Para preguntas conceptuales generales -> Responde directamente sin herramientas
    - Integra la informacion de las herramientas naturalmente en tu respuesta pedagogica"""]

    def _get_fewshot_examples(self, knowledge_level: str) -> str:
        """
        Return few-shot examples appropriate for the knowledge level.
        These teach the model the expected response style for OR topics.
        """

        if knowledge_level == "beginner":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Principiante):
---
Estudiante: "Tengo una fábrica que produce mesas y sillas, quiero maximizar ganancias"

Tutor: ¡Excelente problema para empezar! Antes de resolverlo, vamos a identificar qué tipo de problema es. Déjame hacerte unas preguntas:

1. ¿Puedes producir fracciones de mesas? (ej: 2.5 mesas) ¿O solo unidades completas?
2. ¿La ganancia por mesa/silla es siempre la misma sin importar cuántas produzcas?

[Si responde: sí fracciones, sí ganancia constante]

Perfecto. Esto es un problema de **Programación Lineal** porque:
- Las cantidades pueden ser continuas (fracciones permitidas)
- Las relaciones son lineales (ganancia proporcional)

El agente de Programación Lineal puede ayudarte a resolverlo. ¿Te gustaría que primero veamos los componentes básicos?
---

---
Estudiante: "¿Cuándo uso programación lineal vs programación entera?"

Tutor: ¡Pregunta fundamental! La diferencia clave está en el tipo de decisiones:

| Si tus decisiones son... | Usa... | Ejemplo |
|--------------------------|--------|---------|
| Cantidades continuas (2.5 kg, 3.7 horas) | Programación Lineal | Mezcla de productos |
| Números enteros (3 camiones, 5 empleados) | Programación Entera | Asignación de rutas |
| Sí/No (¿abrir planta?) | Programación Entera Binaria | Localización |

**Regla práctica:** ¿Tiene sentido "medio camión" o "0.3 empleados" en tu problema?
- Sí → LP
- No → IP

¿Tienes un problema específico donde no estés seguro?
---"""
        elif knowledge_level == "intermediate":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Intermedio):
---
Estudiante: "¿Cómo sé si mi problema es lineal o no lineal?"

Tutor: Buena pregunta. Vamos a diagnosticar sistemáticamente. ¿Puedes describir tu función objetivo y restricciones?

[Espera descripción]

Para determinar linealidad, verifica:
1. **Objetivo**: ¿Es suma de términos tipo "constante × variable"?
   - ✅ Lineal: 3x + 2y
   - ❌ No lineal: x², xy, √x, log(x)

2. **Restricciones**: ¿Misma forma?
   - ✅ Lineal: 2x + 3y ≤ 10
   - ❌ No lineal: x² + y² ≤ 1

Si TODO es lineal y variables continuas → LP
Si hay no linealidades → NLP (o posible linealización)

¿Quieres que analicemos tu problema específico?
---

---
Estudiante: "Necesito decidir qué proyectos ejecutar con presupuesto limitado"

Tutor: Interesante. Esto parece un problema de selección. Analicemos:

- **Variables de decisión**: ¿Ejecutar proyecto i? → Sí/No (binarias)
- **Objetivo**: ¿Maximizar beneficio total? ¿Valor estratégico?
- **Restricciones**: Presupuesto, recursos, dependencias entre proyectos

Esto es un problema de **Programación Entera Binaria** (variante del problema de la mochila si hay una restricción, o multiconstraint knapsack si hay varias).

¿Hay dependencias entre proyectos? Por ejemplo, "proyecto B requiere proyecto A". Eso agregaría restricciones lógicas.
---"""
        else:  # advanced
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Avanzado):
---
Estudiante: "Tengo un problema de IP muy grande que tarda horas. ¿Opciones?"

Tutor: Problema común en IP a escala. Varias estrategias según la estructura:

1. **Reformulación**: ¿El modelo tiene simetría? ¿Restricciones redundantes?
2. **Descomposición**:
   - Benders: si hay estructura de dos etapas (decisiones maestras + operativas)
   - Dantzig-Wolfe: si restricciones se descomponen en bloques
3. **Relajación**: Lagrangiana para obtener cotas y guiar branch-and-bound
4. **Heurísticas**:
   - Constructivas (greedy) + mejora local
   - Metaheurísticas si solución aproximada es aceptable

¿Cuál es la estructura de tu problema? ¿Hay subproblemas naturales?
---

---
Estudiante: "¿Cuándo conviene usar metaheurísticas vs métodos exactos?"

Tutor: Excelente pregunta de diseño algorítmico. La decisión depende de varios factores:

| Factor | Métodos Exactos | Metaheurísticas |
|--------|-----------------|-----------------|
| Garantía de optimalidad | ✅ Sí | ❌ No (pero buenas soluciones) |
| Escalabilidad | Limitada (NP-hard) | Alta |
| Tiempo disponible | Puede ser largo | Configurable |
| Estructura del problema | Bien definida | Flexible |

**Reglas prácticas:**
- Si el solver resuelve en <1 hora → método exacto
- Si necesitas solución rápida y "buena" basta → metaheurística
- Híbrido: metaheurística para inicio caliente, luego branch-and-bound

¿Qué tamaño tiene tu instancia? ¿Cuánto tiempo tienes para la solución?
---"""

    def get_available_strategies(self) -> list[str]:
        """Return available explanation strategies for Operations Research."""
        return [
            "conceptual", "basado en ejemplos", "perspectiva histórica",
            "comparativo", "centrado en la aplicación", "basado en el framework"
        ]

    def is_topic_related(self, message: str) -> bool:
        """Adapter for the BaseAgent topic-scope contract."""
        return self.is_or_related(message)

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
            # Core OR terms (Spanish)
            "investigación de operaciones", "metodología io", "métodos io",
            # Core OR terms (English - students might mix languages)
            "operations research", "or methodology", "operational research",

            # General optimization (Spanish)
            "optimización", "optimizar", "toma de decisiones", "análisis de decisiones",
            "ciencia de la decisión",
            # General optimization (English)
            "optimization", "optimize", "decision-making", "decision analysis",

            # Problem types (Spanish)
            "problema de optimización", "problema de decisión", "qué tipo de problema",
            "qué método", "qué técnica", "debo usar", "qué enfoque", "cómo resolverlo",
            "cómo resolver", "clasificar problema", "tipo de problema",
            # Problem types (English)
            "optimization problem", "decision problem", "what type of problem",
            "which method", "which technique", "how to solve",

            # OR history and context (Spanish)
            "historia de io", "qué es io", "aplicaciones io", "io en la práctica",
            "qué es la investigación", "segunda guerra mundial",
            # OR history and context (English)
            "history of or", "what is or", "or applications",

            # Technique selection (Spanish)
            "lineal o entero", "qué programación", "qué optimización", "elegir método",
            "seleccionar técnica", "enfoque correcto", "mejor método para", "qué agente",
            "cuándo usar", "cuál usar", "diferencia entre",
            # Technique selection (English)
            "linear or integer", "which programming", "choose method",
            "best method for", "which agent", "when to use",

            # General methodology (Spanish)
            "formulación", "modelado", "construcción de modelos", "resolución de problemas",
            "enfoque sistemático", "método científico", "formular problema",
            # General methodology (English)
            "formulation", "modeling", "model building", "problem-solving",

            # Applications (Spanish)
            "asignación de recursos", "programación", "planificación", "logística",
            "cadena de suministro", "producción", "inventario", "red",
            "asignación", "transporte", "enrutamiento", "ruta más corta",
            "flujo máximo", "problema del viajante", "mochila",
            # Applications (English)
            "resource allocation", "scheduling", "planning", "logistics",
            "supply chain", "production", "inventory", "network",
            "shortest path", "maximum flow", "knapsack", "traveling salesman",

            # Core concepts (Spanish)
            "objetivo", "restricción", "factible", "óptimo", "solución",
            "maximizar", "minimizar", "función objetivo", "variable de decisión",
            # Core concepts (English)
            "objective", "constraint", "feasible", "optimal", "solution",
            "maximize", "minimize", "objective function", "decision variable",

            # Asking about agents/methods (Spanish)
            "qué agente debería", "qué agente", "por dónde empiezo", "introducción a",
            "resumen de", "fundamentos de", "primeros pasos", "empezar con",
            # Asking about agents/methods (English)
            "which agent should", "what agent", "where do i start",
            "introduction to", "basics of", "fundamentals", "getting started",

            # Specific OR techniques (Spanish)
            "programación lineal", "programación entera", "programación no lineal",
            "simplex", "branch and bound", "ramificación y acotación",
            "programación dinámica", "teoría de colas", "simulación",
            "heurística", "metaheurística",
            # Specific OR techniques (English)
            "linear programming", "integer programming", "nonlinear programming",
            "dynamic programming", "queuing theory", "simulation",
            "heuristic", "metaheuristic",

            # Common question patterns (Spanish)
            "cómo clasifico", "cómo identifico", "cómo sé si",
            "es lineal", "es entero", "es convexo",
            "puedo usar", "debería usar", "mejor para"
        ]

        message_lower = message.lower()

        # Check for OR keywords
        keyword_match = any(keyword in message_lower for keyword in or_keywords)

        # Additional check: very general optimization questions
        general_patterns = [
            # Spanish
            "ayúdame", "necesito", "cómo puedo", "qué debo", "explica", "qué es",
            "cuéntame sobre", "tengo un problema", "quiero saber",
            # English
            "help me", "i need to", "how can i", "what should i",
            "explain", "what is", "tell me about", "i have a problem"
        ]
        general_optimization_terms = [
            # Spanish
            "optimizar", "mejor", "eficiente", "mínimo", "máximo",
            "decisión", "asignar", "distribuir",
            # English
            "optimize", "best", "efficient", "minimum", "maximum",
            "decision", "allocate", "distribute"
        ]

        is_general_or_question = (
            any(pattern in message_lower for pattern in general_patterns) and
            any(term in message_lower for term in general_optimization_terms)
        )

        return keyword_match or is_general_or_question

    @staticmethod
    def _get_off_topic_response() -> str:
        """
        Standard off-topic response for both sync and async flows.
        """
        return (
            "Estoy capacitado específicamente para ayudar con los fundamentos y la metodología de la Investigación de Operaciones."
            "Tu pregunta parece ser sobre otra cosa. "
            "\n\nPuedo ayudarte con:\n"
            "- Comprender qué es la Investigación de Operaciones y sus aplicaciones\n"
            "- Aprender sobre diferentes tipos de problemas y metodologías de IO\n"
            "- Decidir qué técnica de optimización usar para diferentes problemas\n"
            "- Prepararse para usar agentes especializados (Programación Lineal, Programación Entera, etc.)\n"
            "- Comprender los marcos de toma de decisiones y los enfoques de resolución de problemas\n"
            "\n¿Te gustaría preguntar sobre alguno de estos temas de Investigación de Operaciones?"
        )

    def generate_response(
        self,
        user_message: str,
        conversation_history: list[dict[str, str]],
        context: dict[str, Any]
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

        # Generate response with tools
        try:
            all_tools = self.tools + context.get("tools", [])
            response = self.llm_service.generate_response_with_tools(
                messages=components["messages"],
                tools=all_tools,
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

        # Generate response with tools (async)
        try:
            all_tools = self.tools + context.get("tools", [])
            response = await self.llm_service.a_generate_response_with_tools(
                messages=components["messages"],
                tools=all_tools,
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
_or_agent: OperationsResearchAgent | None = None


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
