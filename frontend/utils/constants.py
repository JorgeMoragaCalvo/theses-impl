"""
Constantes compartidas para la aplicación frontend.
Asegura consistencia con los valores enum de Topic del backend.
"""

# Mapeo de temas: valor enum del backend -> nombre para mostrar
TOPIC_DISPLAY_NAMES = {
    "operations_research": "Investigación de Operaciones",
    "mathematical_modeling": "Modelado Matemático",
    "linear_programming": "Programación Lineal",
    "integer_programming": "Programación Entera",
    "nonlinear_programming": "Programación No Lineal"
}

# Opciones de temas para selectores: nombre para mostrar -> valor enum del backend
TOPIC_OPTIONS = {
    "Investigación de Operaciones": "operations_research",
    "Modelado Matemático": "mathematical_modeling",
    "Programación Lineal": "linear_programming",
    "Programación Entera": "integer_programming",
    "Programación No Lineal": "nonlinear_programming"
}

# Lista ordenada de temas para mostrar (legible)
TOPICS_LIST = [
    "Investigación de Operaciones",
    "Modelado Matemático",
    "Programación Lineal",
    "Programación Entera",
    "Programación No Lineal"
]

# Descripciones de temas para la pantalla de bienvenida
TOPIC_DESCRIPTIONS = {
    "Investigación de Operaciones": [
        "Introducción a la optimización",
        "Fundamentos de formulación de problemas",
        "Marcos de toma de decisiones"
    ],
    "Modelado Matemático": [
        "Traducción de problemas reales a matemáticas",
        "Identificación de variables y restricciones",
        "Diseño de función objetivo"
    ],
    "Programación Lineal": [
        "Formulación y solución de PL",
        "Método Simplex",
        "Teoría de dualidad"
    ],
    "Programación Entera": [
        "Variables binarias y enteras",
        "Métodos de ramificación y acotamiento",
        "Optimización combinatoria"
    ],
    "Programación No Lineal": [
        "Optimización sin restricciones",
        "Optimización con restricciones",
        "Condiciones KKT",
        "Métodos de gradiente"
    ]
}

# Tema predeterminado para nuevas sesiones
DEFAULT_TOPIC = "Programación Lineal"