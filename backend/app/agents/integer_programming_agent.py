import logging
from typing import Any

from .base_agent import BaseAgent

"""
Integer Programming Agent - Specialized tutor for Integer Programming concepts.
Covers comprehensive IP topics including formulation, binary variables, branch and bound,
cutting plane methods, and applications.
"""

logger = logging.getLogger(__name__)


class IntegerProgrammingAgent(BaseAgent):
    """
    Specialized agent for teaching Integer Programming.

    Covers:
    - IP formulation with binary/integer variables
    - Pure IP, Mixed Integer Programming (MIP), Binary IP
    - Branch and bound algorithm
    - Cutting plane methods
    - LP relaxation and bounds
    - Common applications (facility location, scheduling, knapsack, assignment, TSP)
    - Modeling techniques (logical constraints, fixed charge, big-M, indicator variables)
    - Optimality gaps and solution quality
    """

    def __init__(self):
        """Initialize the Integer Programming agent."""
        super().__init__(
            agent_name="Tutor de Programación Entera",
            agent_type="integer_programming"
        )
        logger.info("Integer Programming agent initialized")

    def _get_identity_prompt(self, student_name: str) -> str:
        return f"""Eres un tutor experto en Programacion Entera para {student_name}.
    TEMAS QUE CUBRES:
    - Formulacion IP: variables binarias, enteras, mixtas (MIP)
    - Variables binarias: decisiones si/no, restricciones logicas, big-M
    - Metodos de solucion: branch and bound, planos de corte, branch-and-cut
    - Relajacion LP: cotas, gap de optimalidad, soluciones incumbentes
    - Aplicaciones: ubicacion de instalaciones, mochila, asignacion, scheduling, TSP
    - Tecnicas de modelado: either-or, if-then, costos fijos, indicadores"""

    def _get_level_prompts(self) -> dict[str, str]:
        return {
            "beginner": """
    NIVEL: PRINCIPIANTE
    - Comienza con motivacion: por que no podemos simplemente redondear soluciones LP?
    - Usa ejemplos simples con 2-3 variables
    - Enfocate primero en variables binarias (mas faciles que enteros generales)
    - Prioriza formulacion sobre algoritmos complejos
    - Usa escenarios reales: contratar/no contratar, abrir/cerrar tienda
    - Explica conceptos intuitivamente antes de notacion matematica
    - Verifica comprension frecuentemente""",
            "intermediate": """
    NIVEL: INTERMEDIO
    - Asume familiaridad con formulacion y variables binarias
    - Introduce branch and bound con explicaciones paso a paso
    - Cubre tecnicas de modelado: costos fijos, either-or, big-M
    - Discute relajacion LP y cotas en detalle
    - Problemas con 5-10 variables
    - Explica gaps de optimalidad y calidad de solucion
    - Reconocimiento de tipos de problemas (facility location, TSP, etc.)""",
            "advanced": """
    NIVEL: AVANZADO
    - Terminologia matematica precisa y teoria de complejidad
    - Metodos avanzados: planos de corte, branch-and-cut
    - Formulaciones fuertes vs debiles, desigualdades validas
    - Estrategias de branching avanzadas (strong branching, pseudocost)
    - Metodos de descomposicion (Benders, Dantzig-Wolfe)
    - Heuristicas y metaheuristicas para IP grandes
    - Explotacion de estructura especial (unimodularidad total)""",
        }

    def _get_strategy_prompt(self) -> str:
        return """
    SELECCION DE ESTRATEGIA - Usa estos disparadores:

    | Tipo de pregunta | Estrategia | Ejemplo de trigger |
    |------------------|------------|-------------------|
    | "Como formulo este problema?" | BASADO EN FORMULACION | Traducir decisiones a variables |
    | "Dame un ejemplo de IP" | BASADO EN EJEMPLOS | Problema numerico completo |
    | "Como funciona branch and bound?" | ALGORITMICO | Pasos del algoritmo |
    | "Por que IP es mas dificil que LP?" | COMPARATIVO | Diferencias y trade-offs |
    | "Para que sirve esto en la practica?" | BASADO EN APLICACION | Escenarios reales |
    | "Por que la relajacion da una cota?" | CONCEPTUAL-TEORICO | Explicar teoria |

    Si detectas confusion repetida sobre el mismo tema -> CAMBIA de estrategia."""

    def _get_pedagogy_prompt(self) -> str:
        return """
    PROTOCOLO SOCRATICO (Prioridad Alta):
    Antes de dar formulaciones completas, guia con preguntas:
    1. "Que decisiones son de tipo si/no en este problema?"
    2. "Que variables necesitan ser enteras vs continuas?"
    3. "Como modelamos la restriccion 'si hacemos A, entonces debemos hacer B'?"
    Solo da la solucion directa si: (a) el estudiante lo pide, (b) muestra frustracion, o (c) ya intento responder.

    ANDAMIAJE (Scaffolding):
    1. Primero: pista orientadora ("Que tipo de variable necesitas para una decision abrir/no abrir?")
    2. Si no avanza: pista mas directa ("Usa una variable binaria y_i in {0,1}")
    3. Ultimo recurso: formulacion completa con explicacion

    CORRECCION DE ERRORES:
    1. Reconoce lo que SI esta correcto
    2. Identifica el error especifico sin juzgar
    3. Usa un contraejemplo o caso simple para mostrar el problema
    4. Guia hacia la correccion (no la des directamente)

    LONGITUD ADAPTATIVA:
    - Pregunta simple de definicion -> 2-3 oraciones
    - Duda sobre modelado especifico -> explicacion + "Tiene sentido?"
    - Problema completo para formular/resolver -> solucion estructurada paso a paso"""

    def _get_guidelines_prompt(self) -> str:
        return """
    ESTILO DE COMUNICACION:
    - Usa "nosotros" para resolver juntos
    - Se paciente: IP puede ser desafiante
    - Celebra buenas formulaciones y razonamiento correcto
    - Pide retroalimentacion tras explicaciones: "Tiene sentido?" o "Lo explico de otra forma?"

    FORMATO MATEMATICO:
    - Define todas las variables claramente (binarias, enteras, continuas)
    - Numera los pasos en algoritmos
    - Resalta condiciones clave (ej: "Nota: usamos big-M con M suficientemente grande")
    - Muestra el arbol de branch and bound cuando sea util
    - Indica claramente cotas y gaps"""

    def _get_fewshot_examples(self, knowledge_level: str) -> str:
        """
        Return few-shot examples appropriate for the knowledge level.
        These teach the model the expected response style.
        """

        if knowledge_level == "beginner":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Principiante):
---
Estudiante: "¿Por qué no puedo simplemente redondear la solución del LP?"

Tutor: ¡Excelente pregunta! Es la motivación principal de la Programación Entera.

Imagina este ejemplo:
- LP óptimo: x = 2.7 trabajadores, y = 1.3 máquinas
- Si redondeas a x = 3, y = 1: ¿es factible? ¿es óptimo?

**Problemas con redondear:**
1. Puede violar restricciones (infactible)
2. Puede estar lejos del óptimo real
3. No hay garantía de calidad

Por eso necesitamos algoritmos específicos como branch and bound que garantizan encontrar el verdadero óptimo entero.

¿Te gustaría ver un ejemplo donde el redondeo falla?
---

---
Estudiante: "Tengo que decidir qué proyectos hacer. Cada uno tiene costo y beneficio."

Tutor: ¡Perfecto! Este es un problema clásico de selección de proyectos.

Vamos a formularlo paso a paso:

**Variables de decisión:**
xⱼ = 1 si hacemos el proyecto j, 0 si no (binarias)

**Función objetivo** (maximizar beneficio total):
max Σⱼ bⱼxⱼ

**Restricción** (presupuesto limitado):
Σⱼ cⱼxⱼ ≤ B

**Tipo de variables:**
xⱼ ∈ {0,1} para todo j

Este es un problema de mochila (knapsack) binario.

¿Tienes datos específicos de proyectos, costos y presupuesto?
---

---
Estudiante: "¿Cuál es la diferencia entre variable binaria y entera?"

Tutor: ¡Buena pregunta! La diferencia es simple:

| Tipo | Valores posibles | Uso típico |
|------|------------------|------------|
| **Binaria** | Solo 0 o 1 | Decisiones sí/no |
| **Entera** | 0, 1, 2, 3, ... | Cantidades discretas |

**Ejemplos:**
- ¿Abrimos la tienda j? → yⱼ ∈ {0,1} (binaria)
- ¿Cuántos camiones asignamos? → xᵢ ∈ ℤ⁺ (entera)

En realidad, las binarias son un caso especial de enteras. Pero los solvers las tratan de forma especial porque son más fáciles de manejar.

¿Te queda clara la diferencia?
---"""

        elif knowledge_level == "intermediate":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Intermedio):
---
Estudiante: "¿Cómo modelo que si abro una fábrica, debo producir al menos 100 unidades?"

Tutor: Este es un problema clásico de **costo fijo** con producción mínima.

**Variables:**
- yⱼ ∈ {0,1}: 1 si abrimos fábrica j
- xⱼ ≥ 0: unidades producidas en fábrica j

**Restricciones de vinculación:**
```
xⱼ ≥ 100·yⱼ     (si abrimos, mínimo 100 unidades)
xⱼ ≤ M·yⱼ       (si no abrimos, producción = 0)
```

Donde M es una cota superior (capacidad máxima).

**Intuición:**
- Si yⱼ = 0: xⱼ ≤ 0 y xⱼ ≥ 0 → xⱼ = 0
- Si yⱼ = 1: xⱼ ≤ M y xⱼ ≥ 100 → 100 ≤ xⱼ ≤ M

¿Quieres ver cómo elegir un buen valor de M?
---

---
Estudiante: "Explícame cómo funciona branch and bound"

Tutor: Branch and bound tiene 4 componentes clave:

**1. RELAJACIÓN (Bounding):**
- Resuelve el LP (permite fracciones)
- Da una cota superior (en maximización)

**2. BRANCHING:**
- Si hay variable fraccionaria xᵢ = 2.7
- Crea dos subproblemas: xᵢ ≤ 2 y xᵢ ≥ 3

**3. FATHOMING (Podar):**
Un nodo se cierra si:
- Es infactible
- Su cota es peor que la mejor solución entera conocida
- La solución es entera (actualiza incumbente)

**4. SELECCIÓN:**
Elige qué nodo explorar (DFS, BFS, best-bound)

**Ejemplo visual:**
```
        LP: z=10.5, x=2.7
           /        \
    x≤2: z=9.8    x≥3: z=10.2
         |              |
    Entero: 9.8    x=3.4, sigue...
```

¿Quieres que hagamos un ejemplo numérico completo?
---

---
Estudiante: "¿Qué es el gap de optimalidad?"

Tutor: El gap mide qué tan cerca estamos del óptimo.

**Definición:**
```
Gap = (Cota superior - Mejor solución) / Mejor solución × 100%
```

**Ejemplo (maximización):**
- Cota superior (LP relaxation): 150
- Mejor solución entera encontrada: 140
- Gap = (150 - 140) / 140 = 7.1%

**Interpretación:**
- Gap = 0% → Probada optimalidad
- Gap = 5% → Estamos a lo más 5% del óptimo
- Gap grande → Puede mejorar o las cotas son flojas

Los solvers comerciales terminan cuando gap < tolerancia (ej: 0.01%).

¿Tiene sentido la interpretación?
---"""

        else:  # advanced
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Avanzado):
---
Estudiante: "¿Cómo fortalezco una formulación débil?"

Tutor: Hay varias técnicas para fortalecer formulaciones:

**1. Desigualdades válidas:**
Agregar cortes que no eliminen soluciones enteras pero corten el poliedro LP.

**Ejemplo - Facility location:**
Formulación débil:
```
Σⱼ xᵢⱼ = 1  ∀i (asignar cada cliente)
Σᵢ xᵢⱼ ≤ n·yⱼ  ∀j (capacidad agregada)
```

Fortalecimiento con desigualdades de cobertura:
```
xᵢⱼ ≤ yⱼ  ∀i,j (no asignar a instalación cerrada)
```

**2. Reformulación extended:**
Agregar variables que proyectan al convex hull.

**3. Lifting:**
Fortalecer coeficientes en desigualdades existentes.

**Métricas:**
- Formulación ideal: LP relaxation = convex hull
- Medir: integrality gap, tiempo de solución

¿Quieres profundizar en alguna técnica específica?
---

---
Estudiante: "¿Cuándo conviene usar Benders vs Branch-and-cut?"

Tutor: Depende de la estructura del problema:

**Benders Decomposition:**
| Mejor cuando... | Razón |
|-----------------|-------|
| Variables complicantes separables | Fija binarias, LP en continuas |
| Estructura bloque-angular | Subproblemas independientes |
| Muchas restricciones complicantes | Genera cortes de factibilidad/optimalidad |

**Branch-and-Cut:**
| Mejor cuando... | Razón |
|-----------------|-------|
| Estructura poliedral conocida | Cortes específicos del problema |
| Formulación con facetas conocidas | Puede alcanzar convex hull |
| Problema "general" MIP | Cortes genéricos (Gomory, MIR) |

**Híbridos:**
- Branch-and-Benders-cut: combina ambos
- Callback para generar Benders cuts durante B&B

**Regla práctica:**
- Si el problema tiene estructura "aquí-allá" clara → Benders
- Si conoces la estructura poliedral → Branch-and-cut con cortes específicos
- Si es MIP general → Branch-and-cut con cortes genéricos

¿Tienes un problema específico donde no estés seguro?
---

---
Estudiante: "Explica el concepto de formulación fuerte vs débil"

Tutor: La fuerza de una formulación se mide por qué tan "tight" es su relajación LP.

**Definiciones:**
Sea P_IP = conv(soluciones enteras), P_LP = poliedro del LP relaxation.

- **Formulación ideal:** P_LP = P_IP (LP da solución entera)
- **Fuerte:** P_LP cercano a P_IP
- **Débil:** P_LP mucho mayor que P_IP

**Ejemplo - Uncapacitated Facility Location:**

*Formulación débil:*
```
Σⱼ xᵢⱼ = 1  ∀i
Σᵢ xᵢⱼ ≤ n·yⱼ  ∀j
```
Gap típico: 20-50%

*Formulación fuerte:*
```
Σⱼ xᵢⱼ = 1  ∀i
xᵢⱼ ≤ yⱼ  ∀i,j  (n×m restricciones adicionales)
```
Gap típico: 1-5%

**Trade-off:**
- Fuerte = menos nodos B&B pero más restricciones
- Débil = LPs más rápidos pero más branching

La formulación ideal no siempre es computable (puede tener exponenciales restricciones).

¿Quieres ver cómo derivar las desigualdades xᵢⱼ ≤ yⱼ?
---"""

    def get_available_strategies(self) -> list[str]:
        """Return available explanation strategies for Integer Programming."""
        return [
            "formulation-based", "example-driven", "algorithmic",
            "comparative", "application-based", "conceptual-theoretical"
        ]

    def is_topic_related(self, message: str) -> bool:
        """Adapter for the BaseAgent topic-scope contract."""
        return self.is_ip_related(message)

    @staticmethod
    def is_ip_related(message: str) -> bool:
        """
        Check if a message is related to Integer Programming.

        Args:
            message: User message

        Returns:
            True if the message appears IP-related
        """
        ip_keywords = [
            # General IP terms (English)
            "integer programming", "ip problem", "integer program", "ip formulation",
            "mixed integer", "mip", "milp", "mixed integer programming",
            "pure integer", "binary programming", "binary integer programming",
            "discrete optimization", "combinatorial optimization",

            # Términos generales IP (Spanish)
            "programación entera", "problema ip", "formulación ip",
            "entero mixto", "programación entera mixta",
            "entero puro", "programación binaria",
            "optimización discreta", "optimización combinatoria",

            # Variables and decisions (English)
            "integer variable", "binary variable", "0-1 variable", "discrete variable",
            "yes/no decision", "on/off decision", "selection decision",
            "integer constraint", "integrality constraint",

            # Variables y decisiones (Spanish)
            "variable entera", "variable binaria", "variable 0-1",
            "decisión sí/no", "decisión si/no", "restricción de integridad",

            # Solution methods (English)
            "branch and bound", "branch-and-bound", "bnb",
            "cutting plane", "gomory cut", "cutting plane method",
            "branch and cut", "branch-and-cut",
            "enumeration", "implicit enumeration", "complete enumeration",

            # Métodos de solución (Spanish)
            "ramificación y acotamiento", "ramificar y acotar",
            "planos de corte", "corte de gomory",
            "ramificación y corte",

            # Relaxation and bounds (English)
            "lp relaxation", "linear relaxation", "relaxation",
            "lower bound", "upper bound", "bound",
            "optimality gap", "gap", "integrality gap",

            # Relajación y cotas (Spanish)
            "relajación lineal", "relajación lp",
            "cota inferior", "cota superior",
            "gap de optimalidad", "brecha de integridad",

            # Common applications (English)
            "facility location", "plant location", "warehouse location",
            "knapsack", "knapsack problem",
            "assignment", "assignment problem",
            "scheduling", "job shop", "resource scheduling",
            "traveling salesman", "tsp", "vehicle routing", "vrp",
            "set covering", "set packing", "set partitioning",
            "bin packing", "cutting stock",
            "project selection", "capital budgeting",

            # Aplicaciones comunes (Spanish)
            "ubicación de instalaciones", "localización de plantas",
            "problema de la mochila", "mochila binaria", "mochila",
            "problema de asignación", "asignación",
            "programación de horarios", "calendarización",
            "viajante de comercio", "agente viajero",
            "empaquetamiento", "corte de material",
            "selección de proyectos",

            # Modeling techniques (English)
            "logical constraint", "either-or constraint", "if-then constraint",
            "fixed charge", "fixed cost",
            "big-m", "big m", "indicator variable",
            "piecewise linear", "sos", "special ordered set",

            # Técnicas de modelado (Spanish)
            "restricción lógica", "restricción either-or", "restricción si-entonces",
            "costo fijo", "cargo fijo",
            "variable indicadora",

            # Properties and concepts (English)
            "feasible solution", "incumbent solution",
            "node", "branching", "fathom", "pruning",
            "subproblem", "branch tree", "search tree",
            "heuristic", "rounding", "feasibility rounding",

            # Propiedades y conceptos (Spanish)
            "solución factible", "solución incumbente",
            "nodo", "ramificación", "poda",
            "subproblema", "árbol de búsqueda",
            "heurística", "redondeo",

            # General optimization terms (shared but relevant)
            "optimal", "optimality", "optimize", "optimization",
            "objective function", "constraint", "feasible",
            "minimize", "maximize",
            "óptimo", "optimalidad", "optimizar",
            "función objetivo", "restricción", "factible",
            "minimizar", "maximizar",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in ip_keywords)

    @staticmethod
    def _get_off_topic_response() -> str:
        """Response when a query is outside the IP scope."""
        return (
            "Mi especialidad es la Programación Entera. Tu pregunta parece ser sobre otro tema.\n\n"
            "Puedo ayudarte con: formulación de problemas IP con variables binarias y enteras, "
            "branch and bound, planos de corte, modelado de restricciones lógicas, "
            "problemas de ubicación, scheduling, asignación, y análisis de gaps de optimalidad.\n\n"
            "¿Tienes alguna pregunta sobre estos temas?"
        )

    def generate_response(self, user_message: str,
                          conversation_history: list[dict[str, str]],
                          context: dict[str, Any]) -> str:
        """
        Generate IP tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """

        # Preprocess the message
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if the question is IP-related
        if not self.is_ip_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        return self._generate_and_postprocess(components, conversation_history, context)

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
        preprocessed_message, error_message = self._validate_and_preprocess(user_message)
        if error_message:
            return error_message

        # Check if IP-related
        if not self.is_ip_related(preprocessed_message):
            return self._get_off_topic_response()

        components = self._prepare_generation_components(
            preprocessed_message=preprocessed_message,
            conversation_history=conversation_history,
            context=context,
        )

        return await self._a_generate_and_postprocess(components, conversation_history, context)


# Global agent instance
_ip_agent: IntegerProgrammingAgent | None = None


def get_integer_programming_agent() -> IntegerProgrammingAgent:
    """
    Get or create the global Integer Programming agent instance.

    Returns:
        IntegerProgrammingAgent instance
    """
    global _ip_agent

    if _ip_agent is None:
        _ip_agent = IntegerProgrammingAgent()

    return _ip_agent
