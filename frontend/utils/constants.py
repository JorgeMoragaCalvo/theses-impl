"""
Shared constants for the frontend application.
Ensures consistency with backend Topic enum values.
"""

# Topic mappings: backend enum value -> display name
TOPIC_DISPLAY_NAMES = {
    "operations_research": "Operations Research",
    "mathematical_modeling": "Mathematical Modeling",
    "linear_programming": "Linear Programming",
    "integer_programming": "Integer Programming",
    "nonlinear_programming": "Nonlinear Programming"
}

# Topic options for dropdowns/selectors: display name -> backend enum value
TOPIC_OPTIONS = {
    "Operations Research": "operations_research",
    "Mathematical Modeling": "mathematical_modeling",
    "Linear Programming": "linear_programming",
    "Integer Programming": "integer_programming",
    "Nonlinear Programming": "nonlinear_programming"
}

# Ordered the list of topics for display (human-readable)
TOPICS_LIST = [
    "Operations Research",
    "Mathematical Modeling",
    "Linear Programming",
    "Integer Programming",
    "Nonlinear Programming"
]

# Topic descriptions for the welcome screen
TOPIC_DESCRIPTIONS = {
    "Operations Research": [
        "Introduction to optimization",
        "Problem formulation basics",
        "Decision-making frameworks"
    ],
    "Mathematical Modeling": [
        "Translating real problems to math",
        "Variable and constraint identification",
        "Objective function design"
    ],
    "Linear Programming": [
        "LP formulation and solution",
        "Simplex method",
        "Duality theory"
    ],
    "Integer Programming": [
        "Binary and integer variables",
        "Branch and bound methods",
        "Combinatorial optimization"
    ],
    "Nonlinear Programming": [
        "Unconstrained optimization",
        "Constrained optimization",
        "KKT conditions",
        "Gradient methods"
    ]
}

# Default topic for new sessions
DEFAULT_TOPIC = "Linear Programming"