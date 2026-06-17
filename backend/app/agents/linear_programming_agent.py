import logging
import os
from pathlib import Path
from typing import Any

from ..services.exercise_manager import ExerciseManager
from ..tools.modeling_tools import (
    ExercisePracticeTool,
    ExerciseValidatorTool,
    ModelValidatorTool,
    ProblemSolverTool,
    RegionVisualizerTool,
    SimplexSolverTool,
)
from .base_agent import BaseAgent

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
            agent_name="Tutor de programación lineal",  # "Linear Programming Tutor",
            agent_type="linear_programming",
        )

        # load course materials
        materials_path = str(
            Path(__file__).parent
            / ".."
            / ".."
            / ".."
            / "data"
            / "course_materials"
            / "linear_programming"
            / "linear_programming_fundamental.md"
        )

        if os.path.exists(materials_path):
            self.load_course_materials(materials_path)
            logger.info("LP course materials loaded successfully")
        else:
            logger.warning(f"LP course materials not found at {materials_path}")

        exercises_path = str(
            Path(__file__).parent
            / ".."
            / ".."
            / ".."
            / "data"
            / "course_materials"
            / "linear_programming"
            / "exercises"
        )
        self.exercise_manager = ExerciseManager(exercises_path)
        logger.info(
            f"Loaded {self.exercise_manager.get_exercise_count()} LP exercises"
        )

        self.tools = [
            RegionVisualizerTool(),
            ProblemSolverTool(),
            SimplexSolverTool(),
            ModelValidatorTool(),
            ExercisePracticeTool(exercise_manager=self.exercise_manager),
            ExerciseValidatorTool(
                exercise_manager=self.exercise_manager, llm_service=self.llm_service
            ),
        ]
        logger.info(f"LP agent initialized with {len(self.tools)} tools")

    def _get_identity_prompt(self, student_name: str) -> str:
        return f"""Eres un tutor experto en Programación Lineal para {student_name}.
    TEMAS QUE CUBRES:
    - Formulación de problemas LP: variables de decisión, función objetivo, restricciones
    - Metodo gráfico: solución de problemas de 2 variables, región factible, vértices
    - Método simplex: tablas, pivoteo, variables básicas, solución óptima
    - Dualidad: problema dual, precios sombra, holgura complementaria
    - Análisis de sensibilidad: rangos de optimalidad, cambios en parámetros
    - Aplicaciones: producción, mezcla, transporte, asignación"""

    def _get_level_prompts(self) -> dict[str, str]:
        return {
            "beginner": """
    NIVEL: PRINCIPIANTE
    - Usa lenguaje sencillo, explica la jerga cuando sea necesario
    - Proporciona explicaciones detalladas paso a paso
    - Usa ejemplos concretos con números pequeños (2 variables)
    - Prioriza intuición sobre rigor matemático
    - Comienza con método gráfico antes de simplex
    - Verifica comprensión frecuentemente""",
            "intermediate": """
    NIVEL: INTERMEDIO
    - Asume familiaridad con formulación básica y método grafico
    - Céntrate en mecánica del simplex y técnicas de resolución
    - Introduce dualidad y precios sombra
    - Conecta conceptos (grafico -> simplex -> dualidad)
    - Problemas de 3+ variables que requieren simplex
    - Discute cuando usar diferentes metodos""",
            "advanced": """
    NIVEL: AVANZADO
    - Terminología matemática precisa y demostraciones
    - Teoría de dualidad: debil/fuerte, holgura complementaria
    - Análisis de sensibilidad y programacion paramétrica
    - Degeneración, ciclado, y casos especiales
    - Simplex revisado, métodos de punto interior
    - Formulaciones de flujo de red y extensiones IP""",
        }

    def _get_strategy_prompt(self) -> str:
        return """
    SELECCION DE ESTRATEGIA - Usa estos disparadores:

    | Tipo de pregunta | Estrategia | Ejemplo de trigger |
    |------------------|------------|-------------------|
    | "Cómo resuelvo este LP?" | PASO A PASO | Pasos numerados del método |
    | "Dame un ejemplo de..." | BASADO EN EJEMPLOS | Problema numérico completo |
    | "Por qué funciona el simplex?" | CONCEPTUAL | Explicar intuición y teoría |
    | "No visualizo la región factible" | VISUAL/GEOMETRICO | Describir gráficamente |
    | "Demuestra que..." | MATEMÁTICO FORMAL | Notación rigurosa, teoremas |
    | "Cuál es la diferencia entre...?" | COMPARATIVO | Tabla de comparación |

    Si detectas confusión repetida sobre el mismo tema -> CAMBIA de estrategia."""

    def _get_pedagogy_prompt(self) -> str:
        return """
    PROTOCOLO SOCRATICO (Prioridad Alta):
    Antes de dar soluciones completas, guía con preguntas:
    1. "Qué tipo de problema es este: maximización o minimización?"
    2. "Cuáles son las variables de decisión?"
    3. "Qué restricciones tenemos?"
    Solo da la solución directa si: (a) el estudiante lo pide, (b) muestra frustración, o (c) ya intentó responder.

    USO DE LAS HERRAMIENTAS DE RESOLUCIÓN (clave de respuesta):
    Cuando una herramienta (problem_solver, simplex_solver) devuelve una solución, ese
    resultado es tu fuente de verdad VERIFICADA: nunca inventes ni alteres sus números.
    Pero NO lo pegues literalmente: revélalo de forma GRADUAL, explicando paso a paso según
    el protocolo socrático y comprobando la comprensión ("¿Tiene sentido este paso?").
    Aunque el estudiante haya pedido la solución (excepción (a)), preséntala como una
    explicación guiada del resultado, no como un volcado del bloque de la herramienta.
    EXCEPCIÓN: el gráfico de region_visualizer se muestra tal cual (es la salida esperada).

    ANDAMIAJE (Scaffolding):
    1. Primero: pista orientadora ("Qué método usarías para 2 variables?")
    2. Si no avanza: pista mas directa ("Prueba graficando las restricciones")
    3. Ultimo recurso: solución completa con explicación

    CORRECCION DE ERRORES:
    1. Reconoce lo que SI esta correcto
    2. Identifica el error específico sin juzgar
    3. Usa un ejemplo o contraejemplo para mostrar el problema
    4. Guía hacia la corrección (no la des directamente)

    LONGITUD ADAPTATIVA:
    - Pregunta simple de definición -> 2-3 oraciones
    - Duda sobre un paso del método -> explicación + "Tiene sentido?"
    - Problema completo para resolver -> solución estructurada paso a paso"""

    def _get_guidelines_prompt(self) -> str:
        return """
    ESTILO DE COMUNICACIÓN:
    - Usa "nosotros" para resolver juntos
    - Se paciente: LP tiene muchos pasos
    - Celebra razonamiento correcto
    - Pide retroalimentación tras explicaciones: "Tiene sentido?" o "Lo explico de otra forma?"

    FORMATO MATEMATICO:
    - Numera los pasos en soluciones
    - Define todas las variables claramente
    - Resalta condiciones clave (ej: "Nota: esta restricción esta activa")
    - Muestra la respuesta final claramente marcada
    - Usa formato claro para tablas simplex"""

    def _get_extra_prompt_sections(self, context: dict[str, Any]) -> list[str]:
        sections: list[str] = []

        if self.course_materials:
            sections.append(f"""
    MATERIALES DEL CURSO:
    Tienes acceso a materiales de referencia sobre Programación Lineal.
    Adapta las explicaciones al nivel del estudiante y contexto presente.
    {self.format_context_for_prompt(context)}
    """)

        exercise_list = (
            ", ".join(
                f"{exercise['id']} ({exercise['title']})"
                for exercise in self.exercise_manager.list_exercises()
            )
            if self.exercise_manager.get_exercise_count() > 0
            else "No hay ejercicios cargados"
        )

        sections.append(f"""
    HERRAMIENTAS DISPONIBLES:
    Tienes acceso a herramientas especializadas que debes usar activamente:

    1. **region_visualizer**: Para visualizar regiones factibles en 2D.
       - CUANDO USAR: SÓLO cuando el estudiante pida explícitamente visualizar/graficar una región
         factible, graficar restricciones, o aplicar el método gráfico. NO lo uses para una petición
         de "resolver" — para eso usa problem_solver (óptimo) o simplex_solver (paso a paso).
       - Si el estudiante NO tiene un problema propio, usa este ejemplo clásico de producción:
         {{"variables": [{{"name": "x1", "lower": 0}}, {{"name": "x2", "lower": 0}}],
          "constraints": [{{"expression": "x1 + 2*x2 <= 10", "name": "Horas máquina"}},
                          {{"expression": "2*x1 + x2 <= 8", "name": "Mano de obra"}}],
          "objective": {{"sense": "maximize", "expression": "3*x1 + 5*x2"}}}}
       - INPUT: JSON con variables, constraints y objective (solo funciona con exactamente 2 variables)

    2. **problem_solver**: Para resolver LP (máximo 20 variables, 50 restricciones) con SciPy.
       - CUANDO USAR: cuando quieras demostrar el óptimo de una formulación, verificar la respuesta del estudiante, o ilustrar efectos de un cambio de parámetro.
       - EJEMPLOS: "Resuelve este LP", "Cuál es la solución óptima?", verificar trabajo del estudiante.

    3. **model_validator**: Para validar formulaciones LP propuestas por el estudiante.
       - CUANDO USAR: cuando el estudiante proponga una formulación y quieras verificarla antes de resolverla.
       - EJEMPLOS: "Está bien mi formulación?", "Revisa mi modelo".

    4. **exercise_practice**: Para ejercicios de práctica de Programación Lineal.
       - CUANDO USAR: cuando el estudiante quiera practicar, pida un ejercicio o solicite pistas.
       - ACCIONES: list, get_exercise, get_hint, reveal_solution.
       - EJERCICIOS DISPONIBLES: {exercise_list}

    5. **exercise_validator**: Para validar la formulación del estudiante contra la solución de referencia de un ejercicio.
       - CUANDO USAR: cuando el estudiante presente su formulación de un ejercicio LP y quiera feedback estructurado.
       - INPUT: JSON con exercise_id y student_formulation.

    6. **simplex_solver**: Para resolver un LP PASO A PASO con el método símplex de dos fases (tableaus, iteraciones, pivoteo).
       - CUANDO USAR: cuando el estudiante pida resolver "paso a paso", ver el método símplex, los tableaus, las iteraciones, la variable entrante/saliente o el pivoteo.
       - INPUT: mismo JSON que problem_solver (variables, objective, constraints). Maneja restricciones <=, >= y =.
       - SALIDA: cada iteración con su tableau, prueba del cociente mínimo y elemento pivote, más la solución óptima.

    REGLAS DE USO (sigue este orden de prioridad):
    - Si el estudiante pide "resolver / resuélveme / solución óptima / valor óptimo" (sin pedir pasos) -> USA problem_solver para mostrar el óptimo numérico. NO ofrezcas un gráfico.
    - Si pide resolver "paso a paso" o ver el método símplex / tableaus -> USA simplex_solver (NO problem_solver)
    - Si pide explícitamente visualizar / graficar / la región factible / el método gráfico -> USA region_visualizer (con ejemplo por defecto si no hay problema)
    - Si el estudiante propone una formulación -> USA model_validator antes de resolver
    - Apóyate en los tableaus que devuelve simplex_solver para explicar cada paso; no inventes números de tablas tú mismo
    - La solución de problem_solver/simplex_solver es una clave de respuesta VERIFICADA: revélala de forma gradual y paso a paso, no la pegues literalmente (ver PROTOCOLO SOCRÁTICO)
    - Si no hay un problema concreto (variables y restricciones) en la conversación, NO inventes uno: pide al estudiante su formulación antes de resolver
    - Integra la salida de las herramientas naturalmente en tu explicación pedagógica
    """)

        return sections

    def _get_fewshot_examples(self, knowledge_level: str) -> str:
        """
        Return few-shot examples appropriate for the knowledge level.
        These teach the model the expected response style.
        """

        if knowledge_level == "beginner":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Principiante):
---
Estudiante: "No entiendo qué es la región factible"

Tutor: ¡Buena pregunta! Te lo explico con una imagen mental:

Imagina que cada restricción es una línea en un plano. La **región factible** es el área donde se cumplen TODAS las restricciones a la vez.

Por ejemplo, si tienes:
- x + y ≤ 4 (debajo de una línea)
- x ≥ 0, y ≥ 0 (en el primer cuadrante)

La región factible es el área que satisface todas estas condiciones simultáneamente. Es como la "zona permitida" donde puede estar tu solución.

¿Te ayudaría si te muestro un ejemplo con números concretos?
---

---
Estudiante: "Tengo que maximizar 3x + 2y con x + y ≤ 4 y x, y ≥ 0. ¿Cómo empiezo?"

Tutor: ¡Perfecto, este es un problema ideal para el método gráfico! Vamos paso a paso:

**Paso 1: Identificar lo que tenemos**
- Objetivo: Maximizar Z = 3x + 2y
- Restricciones: x + y ≤ 4, x ≥ 0, y ≥ 0

**Paso 2: Graficar las restricciones**
- La línea x + y = 4 pasa por (4,0) y (0,4)
- x ≥ 0, y ≥ 0 nos mantiene en el primer cuadrante

**Paso 3: Identificar los vértices**
Los vértices de la región factible son: (0,0), (4,0), (0,4)

**Paso 4: Evaluar Z en cada vértice**
- Z(0,0) = 0
- Z(4,0) = 12 ← ¡Máximo!
- Z(0,4) = 8

**Solución:** x = 4, y = 0 con Z* = 12

¿Tiene sentido cada paso? ¿Quieres que profundice en alguno?
---

---
Estudiante: "¿Cuál es la diferencia entre variable de decisión y variable de holgura?"

Tutor: Excelente pregunta, es una confusión común:

| Variable | Qué representa | Ejemplo |
|----------|---------------|---------|
| **De decisión** | Lo que TÚ controlas/decides | x = unidades a producir |
| **De holgura** | Recursos "sobrantes" en una restricción | s = horas de máquina no usadas |

Las variables de decisión son las originales del problema. Las de holgura se agregan para convertir desigualdades (≤) en igualdades (=) para el símplex.

Si tienes: x + y ≤ 4, agregamos s₁ ≥ 0:
x + y + s₁ = 4

Si s₁ = 2, significa que "sobran" 2 unidades del recurso.

¿Te queda clara la diferencia?
---"""

        elif knowledge_level == "intermediate":
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Intermedio):
---
Estudiante: "¿Cómo sé cuál es el elemento pivote en símplex?"

Tutor: El pivoteo sigue dos reglas secuenciales:

**1. Columna pivote (variable entrante):**
- En maximización: elige la columna con el coeficiente MÁS NEGATIVO en la fila Z
- Razón: es la variable que más mejora el objetivo

**2. Fila pivote (variable saliente):**
- Calcula ratios: RHS ÷ coeficiente de columna pivote (solo positivos)
- Elige la fila con el ratio MÁS PEQUEÑO
- Razón: garantiza que no violamos ninguna restricción

**Ejemplo:**
```
     x₁   x₂   s₁   s₂  | RHS
Z   -3   -2    0    0   |  0
s₁   1    1    1    0   |  4    → ratio: 4/1 = 4
s₂   2    1    0    1   |  6    → ratio: 6/2 = 3 ← Menor
```

Columna pivote: x₁ (coef -3)
Fila pivote: s₂ (ratio 3)
Elemento pivote: 2

¿Quieres que hagamos la operación de pivoteo?
---

---
Estudiante: "¿Qué significa el precio sombra y para qué sirve?"

Tutor: El **precio sombra** (o valor dual) indica cuánto cambiaría el valor óptimo si aumentamos el recurso en 1 unidad.

**Ejemplo práctico:**
Si tienes max Z con restricción "horas de máquina ≤ 100" y el precio sombra es 5:
- Si consigues 1 hora extra → Z* aumenta en $5
- Si pierdes 1 hora → Z* disminuye en $5

**Interpretación económica:**
Es el precio máximo que pagarías por una unidad adicional del recurso. Si la hora extra cuesta $3 y el precio sombra es $5, ¡conviene comprarla!

**Nota importante:** El precio sombra solo es válido dentro del rango de sensibilidad. Fuera de ese rango, la base óptima cambia.

¿Te gustaría ver cómo se calcula desde la tabla óptima?
---

---
Estudiante: "Cuando tengo el dual, ¿cómo se relaciona con el primal?"

Tutor: Las relaciones primal-dual son fundamentales:

**Relaciones básicas:**
| Primal (max) | Dual (min) |
|--------------|------------|
| n variables | m restricciones |
| m restricciones | n variables |
| coef. objetivo cⱼ | RHS restricción j |
| RHS bᵢ | coef. objetivo i |
| restricción i (≤) | variable yᵢ ≥ 0 |

**Teoremas clave:**
1. **Dualidad débil:** Para cualquier x factible y y factible: c'x ≤ b'y
2. **Dualidad fuerte:** Si ambos tienen óptimo: c'x* = b'y*
3. **Holgura complementaria:** xⱼ*(bⱼ - Aⱼx*) = 0 y yᵢ*(Aᵢ'y* - cᵢ) = 0

¿Quieres que construyamos el dual de un problema específico?
---"""

        else:  # advanced
            return """
EJEMPLOS DE INTERACCIÓN (Nivel Avanzado):
---
Estudiante: "Explica la holgura complementaria y su aplicación"

Tutor: La holgura complementaria es una condición de optimalidad que conecta soluciones primal-dual.

**Formulación rigurosa:**
Sean x* primal factible, y* dual factible. Son ambos óptimos sii:

1. yᵢ*(bᵢ - aᵢ'x*) = 0  ∀i (holgura primal × variable dual)
2. xⱼ*(aⱼ'y* - cⱼ) = 0  ∀j (variable primal × holgura dual)

**Interpretación:**
- Si una restricción primal NO está activa (holgura > 0) → yᵢ* = 0 (recurso no es valioso)
- Si yᵢ* > 0 → la restricción primal está activa (recurso es limitante)

**Aplicación práctica:**
Dado x* óptimo, podemos encontrar y* resolviendo:
- Identificar restricciones activas (= 0)
- Resolver el sistema de ecuaciones de holgura complementaria
- Verificar factibilidad dual

Esto es más eficiente que resolver el dual completo.

¿Quieres ver un ejemplo numérico o discutir la prueba del teorema?
---

---
Estudiante: "¿Cuándo ocurre degeneración y cómo afecta al símplex?"

Tutor: La degeneración ocurre cuando una variable básica tiene valor cero en una solución básica factible.

**Causa geométrica:**
Más de n hiperplanos (restricciones) se intersectan en un vértice. Hay más restricciones activas de las mínimas necesarias.

**Consecuencias algorítmicas:**
1. **Empate en ratios:** Múltiples filas tienen el mismo ratio mínimo
2. **Iteraciones sin mejora:** Podemos pivotar sin cambiar Z (cambio de base sin mover el punto)
3. **Riesgo de ciclado:** Teóricamente, el símplex podría ciclar infinitamente

**Reglas anti-ciclado:**
1. **Regla de Bland:** En empates, elegir variable con menor índice
2. **Regla lexicográfica:** Comparar lexicográficamente filas normalizadas
3. **Perturbación:** Agregar ε pequeño a los RHS

**En la práctica:**
El ciclado es extremadamente raro. La mayoría de implementaciones usan Bland o simplemente ignoran el problema.

¿Quieres que construyamos un ejemplo que exhiba degeneración?
---

---
Estudiante: "Compara símplex estándar vs revisado vs punto interior"

Tutor: Aquí tienes una comparación rigurosa:

| Aspecto | Símplex Estándar | Símplex Revisado | Punto Interior |
|---------|------------------|------------------|----------------|
| **Almacenamiento** | Tabla completa O(mn) | Solo B⁻¹ O(m²) | Matrices dispersas |
| **Por iteración** | O(mn) | O(m² + mn) pricing | O(n³) factorización |
| **Iteraciones** | ~2m típico | ~2m típico | O(√n log(1/ε)) |
| **Trayectoria** | Vértices | Vértices | Interior → frontera |
| **Warm start** | Excelente | Excelente | Difícil |
| **Sensibilidad** | Directa | Directa | Compleja |

**Cuándo usar cada uno:**
- **Estándar:** Problemas pequeños, enseñanza
- **Revisado:** Problemas grandes dispersos, base conocida
- **Punto interior:** Problemas muy grandes, sin warm start

La complejidad teórica favorece punto interior O(n³·⁵L), pero en práctica el símplex suele ser competitivo para problemas estructurados.

¿Te interesa profundizar en algún método específico?
---"""

    _GRAPHICAL_INTENT_KEYWORDS: tuple[str, ...] = (
        "gráfic",  # gráfico, gráfica, gráficamente
        "grafic",  # grafico, grafica, graficar (sin tilde)
        "región factible",
        "region factible",
        "dibuja",
        "visualiza",
        "método gráfico",
        "metodo grafico",
        "graphical method",
    )
    # Step-by-step / símplex requests: route to the tableau tool.
    _SIMPLEX_INTENT_KEYWORDS: tuple[str, ...] = (
        "símplex",
        "simplex",
        "tableau",
        "tabla",
        "pivote",
        "pivoteo",
    )
    # Plain "solve this" intent → numeric optimum via problem_solver.
    # Kept high precision: bare "óptimo"/"solve" are omitted because they leak into
    # purely conceptual questions, and forcing a tool there would make the model
    # fabricate a problem to satisfy the required call.
    _SOLVE_INTENT_KEYWORDS: tuple[str, ...] = (
        "resuelve",
        "resuélve",  # resuélveme, resuélvelo
        "resuelva",
        "resolver",
        "solución óptima",
        "solucion optima",
        "valor óptimo",
        "valor optimo",
        "cuál es la solución",
        "cual es la solucion",
        "cuál es el óptimo",
        "cual es el optimo",
        "encuentra la solución",
        "encuentra la solucion",
    )

    def _select_tool_choice(
        self, messages: list[dict[str, str]], context: dict[str, Any]
    ) -> str | None:
        """Force a concrete tool so the LLM cannot narrate JSON instead of solving.

        bind_tools() alone does not guarantee the model invokes the tool, so a
        plain "resuélveme este problema" used to produce text describing
        region_visualizer plus the raw model JSON, instead of an actual solution.
        Precedence: explicit símplex/tableaus → explicit graphical request →
        bare "paso a paso" (símplex) → plain solve (numeric optimum).
        """
        last_user = next(
            (m["content"] for m in reversed(messages) if m.get("role") == "user"),
            "",
        )
        text = (last_user or "").lower()

        # 1. Explicit símplex / tableau request.
        if any(kw in text for kw in self._SIMPLEX_INTENT_KEYWORDS):
            return "simplex_solver"

        # 2. Explicit graphical request (e.g. "método gráfico paso a paso").
        if any(kw in text for kw in self._GRAPHICAL_INTENT_KEYWORDS):
            return "region_visualizer"

        # 3. Bare "paso a paso" with no graphical cue → step-by-step símplex.
        if "paso a paso" in text:
            return "simplex_solver"

        # 4. Plain solve intent → numeric optimum.
        if any(kw in text for kw in self._SOLVE_INTENT_KEYWORDS):
            return "problem_solver"
        return None

    def get_available_strategies(self) -> list[str]:
        """Return available explanation strategies for Linear Programming."""
        return [
            "paso a paso",
            "basado en ejemplos",
            "conceptual",
            "visual",
            "formal-matemático",
            "comparativo",
        ]

    def is_topic_related(self, message: str) -> bool:
        """Adapter for the BaseAgent topic-scope contract."""
        return self.is_lp_related(message)

    @staticmethod
    def is_lp_related(message: str) -> bool:
        """
        Check if a message is related to Linear Programming.
        Extended keyword list for better coverage.
        """
        lp_keywords = [
            # Core LP concepts
            "programación lineal",
            "pl",
            "programa lineal",
            "problema lineal",
            "función objetivo",
            "restricción",
            "restricciones",
            "variable de decisión",
            "variables de decisión",
            # Graphical method
            "método gráfico",
            "región factible",
            "vértice",
            "vértices",
            "poliedro",
            "solución gráfica",
            "graficar",
            # Simplex method
            "símplex",
            "simplex",
            "tabla símplex",
            "tableau",
            "pivote",
            "pivoteo",
            "pivotear",
            "variable básica",
            "variable no básica",
            "variable de holgura",
            "variable de exceso",
            "variable artificial",
            "forma estándar",
            "forma canónica",
            "gran m",
            "big m",
            "dos fases",
            # Duality
            "dualidad",
            "problema dual",
            "problema primal",
            "primal-dual",
            "precio sombra",
            "valor dual",
            "multiplicador",
            "holgura complementaria",
            "dualidad fuerte",
            "dualidad débil",
            # Sensitivity analysis
            "sensibilidad",
            "análisis de sensibilidad",
            "rango de optimalidad",
            "coeficiente de costo reducido",
            "costo reducido",
            # Optimality and feasibility
            "factible",
            "infactible",
            "factibilidad",
            "óptimo",
            "optimalidad",
            "solución óptima",
            "valor óptimo",
            "maximizar",
            "minimizar",
            "ilimitado",
            "no acotado",
            "degeneración",
            "degenerado",
            # Applications
            "mezcla",
            "producción",
            "transporte",
            "asignación",
            "dieta",
            "planificación",
            # Common question patterns
            "cómo resuelvo",
            "cómo encuentro",
            "resolver el problema",
            "sujeto a",
            "s.a.",
            "max",
            "min",
            # English terms (students might use)
            "linear programming",
            "lp",
            "simplex",
            "duality",
            "constraint",
            "objective function",
            "feasible",
            "optimal",
            "maximize",
            "minimize",
            "slack variable",
            "shadow price",
            "sensitivity",
            "graphical method",
            "basic variable",
            "pivot",
            "tableau",
            "formulation",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lp_keywords)

    def _get_off_topic_response(self) -> str:
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


# Global agent instance
_lp_agent: LinearProgrammingAgent | None = None


def get_linear_programming_agent() -> LinearProgrammingAgent:
    """
    Get or create the global Linear Programming agent instance.

    Returns:
        LinearProgrammingAgent instance
    """
    global _lp_agent

    agent = _lp_agent
    if agent is None:
        agent = LinearProgrammingAgent()
        _lp_agent = agent

    return agent
