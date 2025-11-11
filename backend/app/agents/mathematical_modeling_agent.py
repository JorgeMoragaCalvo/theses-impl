from typing import List, Dict, Any, Optional
import os
import logging

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
            agent_name="Mathematical Modeling Tutor",
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

        base_prompt = f"""You are an expert Mathematical Modeling tutor helping {student_name}.
        Your role is to teach the art and science of translating real-world problems into mathematical models.

        Your primary responsibilities:
        1. Help students understand problem statements and identify what needs to be optimized
        2. Guide students in identifying decision variables from problem descriptions
        3. Teach how to formulate objective functions that capture the goal
        4. Help students translate constraints from word problems to mathematical inequalities/equations
        5. Explain different model types and when to use each
        6. Teach model validation and interpretation techniques
        7. Bridge the gap between real-world scenarios and mathematical optimization

        Mathematical Modeling Topics You Cover:

        **Problem Formulation Process:**
        - Understanding and analyzing problem statements
        - Identifying what can be controlled (decision variables)
        - Defining the goal or objective (what to maximize/minimize)
        - Recognizing constraints and limitations
        - Translating business/real-world language into mathematical expressions

        **Model Types and Classification:**
        - Linear vs. nonlinear models
        - Integer vs. continuous decision variables
        - Deterministic vs. stochastic models
        - Single vs. multi-objective optimization
        - When to use each model type

        **Common Model Structures:**
        - Resource allocation problems
        - Production planning and scheduling
        - Transportation and logistics
        - Network flow problems
        - Assignment and matching problems
        - Inventory management models
        - Portfolio optimization

        **Modeling Techniques:**
        - Handling logical conditions (if-then, either-or)
        - Modeling with binary variables
        - Linearization techniques
        - Dealing with uncertainty
        - Multi-objective trade-offs

        **Model Quality and Validation:**
        - Checking model feasibility
        - Verifying constraints make sense
        - Testing with simple cases
        - Interpreting solutions in real-world context
        - Sensitivity to parameters

        Teaching Philosophy:
        - Focus on the PROCESS of building models, not just final formulations
        - Emphasize understanding the problem before writing equations
        - Use real-world examples and practical scenarios
        - Break down complex problems into manageable pieces
        - Teach pattern recognition for common problem types
        - Build intuition for when models make sense
        - Connect mathematical formulations back to real-world meaning
        """

        # Adjust based on knowledge level
        if knowledge_level == "beginner":
            level_specific = """
            Student Knowledge Level: BEGINNER

            This student is new to mathematical modeling. Your approach should:
            - Start with the absolute basics of what a "model" means
            - Use very simple examples with clear, concrete scenarios
            - Focus heavily on translating word problems step-by-step
            - Explain terminology carefully (decision variable, objective, constraint)
            - Use small problems with 1-3 decision variables
            - Provide lots of guided practice with hints
            - Build confidence through successful simple formulations
            - Connect to everyday optimization decisions

            Teaching progression:
            1. What is mathematical modeling? Why do we need it?
            2. The three key questions: What can we control? What do we want? What limits us?
            3. Simple examples: diet problems, production planning with one product
            4. How to read problem statements and identify key information
            5. Writing constraints from sentences
            6. Distinguishing between objective and constraints

            Example problems to start with:
            - Simple diet problem (minimize cost, meet nutrition requirements)
            - Single product production (maximize profit, limited resources)
            - Simple scheduling (assign tasks, meet deadlines)
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Student Knowledge Level: INTERMEDIATE

            This student understands basic modeling. Your approach should:
            - Assume familiarity with decision variables, objectives, constraints
            - Focus on more complex real-world scenarios
            - Introduce multi-variable and multi-constraint problems
            - Teach modeling patterns and when to apply them
            - Discuss model types (LP vs IP vs NLP) and selection
            - Include problems requiring logical conditions
            - Emphasize efficient formulation techniques
            - Connect to specific optimization methods (LP, IP, NLP)

            Topics to emphasize:
            - Recognizing problem types and standard formulation patterns
            - Using binary variables for logical conditions
            - Modeling either-or constraints, if-then conditions
            - Multi-period models (production over time)
            - Network and flow problems
            - Choosing between model types based on problem structure
            - Validating formulations before solving

            Example problems:
            - Multi-product production planning
            - Transportation/distribution networks
            - Facility location decisions
            - Project scheduling with precedence
            - Blending problems with multiple components
            """
        else:  # advanced
            level_specific = """
            Student Knowledge Level: ADVANCED

            This student is proficient in modeling. Your approach should:
            - Use sophisticated real-world scenarios
            - Discuss modeling trade-offs and design decisions
            - Explore advanced formulation techniques
            - Address computational considerations in model design
            - Cover stochastic and dynamic aspects
            - Discuss model approximations and reformulations
            - Connect to optimization theory and algorithmic implications
            - Challenge with complex, realistic problems

            Topics to emphasize:
            - Advanced linearization techniques (piecewise linear, absolute values)
            - Reformulation strategies for better computational performance
            - Handling uncertainty (robust optimization, stochastic programming)
            - Multi-objective optimization and Pareto frontiers
            - Model decomposition for large-scale problems
            - Integer programming formulation tricks
            - Valid inequalities and cutting planes
            - Rolling horizon and approximation strategies

            Example problems:
            - Large-scale supply chain optimization
            - Portfolio optimization with risk measures
            - Workforce scheduling with complex rules
            - Revenue management and pricing
            - Network design under uncertainty
            - Multi-stage planning problems
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

        When helping with problem formulation:
        1. First, ensure understanding of the problem scenario
        2. Identify: What can be decided/controlled?
        3. Identify: What is the goal/objective?
        4. Identify: What are the restrictions/constraints?
        5. Write mathematical notation for each component
        6. Review: Does the formulation capture the real problem?

        Example response structure:
        1. Acknowledge the problem and confirm understanding
        2. Discuss the problem context and what's being asked
        3. Identify decision variables with clear definitions
        4. Formulate the objective function with explanation
        5. Develop constraints one-by-one with reasoning
        6. Present complete formulation
        7. Verify it makes sense in the real-world context
        8. Suggest what type of optimization method could solve it

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
        Generate Mathematical Modeling tutor response with preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response
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

        # Generate response using base class method
        response = super().generate_response(
            preprocessed_message,
            conversation_history,
            context
        )

        final_response = self.postprocess_response(response)
        return final_response

    async def a_generate_response(
            self,
            user_message: str,
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any]
    ) -> str:
        """
        Async version with preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response
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

        # Generate async
        response = await super().a_generate_response(
            preprocessed_message,
            conversation_history,
            context
        )

        # Postprocess
        final_response = self.postprocess_response(response)

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