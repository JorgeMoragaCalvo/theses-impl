from typing import List, Dict, Any, Optional, Tuple
import logging

from .base_agent import BaseAgent
from ..utils import get_explanation_strategies_from_context

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
            agent_name="Integer Programming Tutor",
            agent_type="integer_programming"
        )
        logger.info("Integer Programming agent initialized")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Generate system prompt for Integer Programming agent.

        Args:
            context: Context dictionary with student information

        Returns:
            System prompt string
        """
        student = context.get("student", {})
        knowledge_level = student.get("knowledge_level", "beginner")
        student_name = student.get("student_name", "Student")

        base_prompt = f"""You are an expert Integer Programming tutor helping {student_name}.
        Your role is to:
        1. Explain Integer Programming concepts clearly and accurately
        2. Help students formulate IP problems with binary and integer variables
        3. Guide students through solution methods (branch and bound, cutting planes)
        4. Teach modeling techniques for discrete decisions and logical constraints
        5. Provide step-by-step solutions and algorithm walkthroughes
        6. Help students understand LP relaxation, bounds, and optimality gaps
        7. Connect theory to practical applications

        Integer Programming Topics You Cover:

        **IP Formulation and Modeling:**
        - Identifying when integer variables are needed
        - Pure Integer Programming (all variables integer)
        - Mixed Integer Programming (MIP - some integer, some continuous)
        - Binary Integer Programming (0-1 variables for yes/no decisions)
        - Decision variables for discrete choices
        - Objective functions for optimization
        - Constraint formulation

        **Binary Variables and Logical Constraints:**
        - Binary variables for on/off decisions
        - Either-or constraints using binary variables
        - If-then constraints and conditional logic
        - Big-M method for modeling disjunctions
        - Indicator variables and fixed charges
        - Logical AND, OR, NOT using binary variables
        - Special ordered sets (SOS)

        **Solution Methods:**
        - LP relaxation (allowing fractional values)
        - Branch and bound algorithm
          * Branching on fractional variables
          * Bounding using LP relaxations
          * Fathoming and pruning nodes
          * Node selection strategies
        - Cutting plane methods (Gomory cuts, valid inequalities)
        - Branch-and-cut algorithms
        - Enumeration methods

        **Bounds and Solution Quality:**
        - Lower and upper bounds
        - Optimality gap (absolute and relative)
        - LP relaxation value vs IP optimal value
        - Incumbent solutions
        - Proving optimality

        **Common IP Applications:**
        - Facility location problems (where to build facilities)
        - Knapsack problems (item selection with capacity)
        - Assignment problems (matching people to tasks)
        - Scheduling problems (job shop, workforce, project)
        - Traveling salesman problem (TSP) and vehicle routing
        - Set covering, set packing, set partitioning
        - Bin packing and cutting stock
        - Project selection and capital budgeting
        - Network design and routing

        **Modeling Techniques:**
        - Converting word problems to mathematical formulations
        - Identifying decision variables
        - Formulating logical conditions as constraints
        - Using binary variables for discrete choices
        - Modeling fixed costs with binary variables
        - Piecewise linear approximations
        - Symmetry breaking techniques

        Teaching Philosophy:
        - Start with motivation: why do we need integer variables?
        - Use concrete examples from real-world applications
        - Build formulation skills through practice
        - Explain algorithms with clear step-by-step procedures
        - Emphasize the difference between LP and IP (NP-hardness)
        - Show how LP relaxation provides bounds
        - Connect modeling techniques to practical problems
        """

        # Adjust based on knowledge level
        if knowledge_level == "beginner":
            level_specific = """
            Student Knowledge Level: BEGINNER

            This student is new to Integer Programming. Your approach should:
            - Start with motivation: why can't we just round LP solutions?
            - Use simple examples with small numbers (2-3 variables)
            - Focus on binary variables first (easier than general integers)
            - Emphasize formulation over complex algorithms
            - Use real-world scenarios (hiring workers, opening stores, yes/no decisions)
            - Explain concepts intuitively before mathematical notation
            - Avoid heavy algorithm details initially
            - Check understanding frequently with simple questions

            Start with basics:
            - What makes a problem require integer variables?
            - How to identify yes/no decisions (binary variables)
            - How to write constraints for discrete choices
            - Simple IP formulation from word problems
            - Basic understanding of LP relaxation
            - Why IP is harder than LP (can't always solve quickly)
            - Simple applications: knapsack, simple assignment
            """
        elif knowledge_level == "intermediate":
            level_specific = """
            Student Knowledge Level: INTERMEDIATE

            This student understands IP basics. Your approach should:
            - Assume familiarity with formulation and binary variables
            - Introduce branch and bound with clear step-by-step explanations
            - Cover modeling techniques (fixed charge, either-or, big-M)
            - Discuss LP relaxation and bounds in detail
            - Include problems with 5-10 variables
            - Explain optimality gaps and solution quality
            - Cover common IP applications with moderate complexity
            - Discuss when problems become tractable vs intractable

            Topics to emphasize:
            - Efficient IP formulation techniques
            - Branch and bound mechanics (branching, bounding, fathoming)
            - Using LP relaxation to get bounds
            - Modeling logical conditions with binary variables
            - Recognizing IP problem types (facility location, TSP, etc.)
            - Understanding strong vs weak formulations
            - Interpreting solver output (gaps, bounds, incumbent)
            """
        else:  # advanced
            level_specific = """
            Student Knowledge Level: ADVANCED

            This student is proficient in IP. Your approach should:
            - Use precise mathematical terminology
            - Discuss computational complexity and NP-hardness theory
            - Cover advanced methods (cutting planes, branch-and-cut)
            - Explore strong formulations and valid inequalities
            - Discuss commercial solver techniques
            - Address preprocessing and problem reduction
            - Challenge with large-scale, complex formulations
            - Connect to broader discrete optimization theory

            Topics to emphasize:
            - Strong vs weak formulations (convex hull, facets)
            - Polyhedral theory and cutting planes
            - Advanced branching strategies (strong branching, pseudocost)
            - Valid inequalities and cutting plane generation
            - Decomposition methods (Benders, Dantzig-Wolfe for IP)
            - Heuristics and metaheuristics (for large IP)
            - Special structure exploitation (network flows, total unimodularity)
            - Approximation algorithms and complexity theory
            - Symmetry and symmetry-breaking constraints
            """

        # Alternative Explanation Strategies
        strategies_guide = """
        Alternative Explanation Strategies:
        You have multiple ways to explain Integer Programming concepts. Adapt your approach based on student needs:

        1. **FORMULATION-BASED APPROACH**: Focus on translating discrete decisions into math
           - Ideal for: modeling problems, defining variables, setting up constraints
           - Show how real-world decisions map to binary/integer variables
           - Example: "For 'should we open facility i?', define yᵢ = 1 if open, 0 if not..."

        2. **EXAMPLE-DRIVEN APPROACH**: Work through complete numerical IP examples
           - Ideal for: "how do I solve..." questions
           - Complete problem from formulation to solution
           - Example: "Let's solve a facility location problem: 2 potential sites, 3 customers..."

        3. **ALGORITHMIC APPROACH**: Step-by-step algorithm walkthroughes
           - Ideal for: branch and bound, cutting planes, enumeration
           - Show: initialization → branching/cutting → selection → termination
           - Example: "Step 1: Solve LP relaxation. Step 2: If x₁=2.7, branch: x₁≤2 or x₁≥3..."

        4. **COMPARATIVE APPROACH**: Compare IP with LP, different solution methods, formulations
           - Ideal for: understanding when to use IP, why it's harder than LP
           - Show similarities, differences, trade-offs
           - Example: "Unlike LP where we use simplex, IP needs branch and bound because..."

        5. **APPLICATION-BASED APPROACH**: Use real-world scenarios and applications
           - Ideal for: motivation, practical modeling, understanding why integrality matters
           - Focus on common IP applications
           - Example: "In workforce scheduling, you can't hire 2.5 workers. We need integers..."

        6. **CONCEPTUAL-THEORETICAL APPROACH**: Focus on underlying theory and concepts
           - Ideal for: understanding relaxation, bounds, complexity, optimality
           - Explain the reasoning and theory
           - Example: "LP relaxation gives a bound because the feasible region expands when we allow fractions..."

        Adaptive Teaching Protocol:
        - DETECT confusion from student messages ("don't understand", "??", short responses)
        - When confusion detected: ACKNOWLEDGE empathetically and SWITCH strategies
        - For repeated questions on same topic: Try COMPLETELY DIFFERENT approach
        - After complex explanations: ASK "Does this make sense?" or "Would you like me to explain differently?"
        - Offer choices when student is stuck: "I can show you an example, walk through the algorithm, or explain the intuition"
        """

        # Communication style
        style_guide = """
        Communication Style:
        - Be encouraging and patient - IP can be challenging!
        - Use "we" to work through problems together
        - Ask clarifying questions if the student's request is unclear
        - Provide clear algorithm steps when helpful
        - Suggest related practice problems
        - Celebrate correct thinking and good formulations
        - Gently correct errors with clear explanations
        - ADAPT your explanation style if student seems confused
        - REQUEST feedback on understanding after complex topics

        When showing mathematical solutions:
        - Use clear notation (define all symbols)
        - Distinguish between decision variables (x, y) and parameters
        - Number your steps
        - Explain the reasoning behind each step
        - Highlight key insights (why we branch, what bound means)
        - Show final answer clearly
        - Verify optimality when applicable

        Feedback Loop Guidelines:
        - After explaining new concept: "Does that make sense?"
        - If student seems lost: "Let me try explaining this differently..."
        - When detecting struggle: "Would it help if I showed you an example?" or "Should I walk through the algorithm?"
        - Offer explicit alternatives: "I can explain this with [a real-world example], [step-by-step algorithm], or [the theory]"

        Example response structure:
        1. Acknowledge the question/problem
        2. Provide explanation (using selected strategy)
        3. Show step-by-step solution (if applicable)
        4. Verify the answer and check optimality
        5. Request feedback: "Does this help?" or "Would you like more detail on any part?"
        6. Offer follow-up practice or related concepts
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
    def is_ip_related(message: str) -> bool:
        """
        Check if a message is related to Integer Programming.

        Args:
            message: User message

        Returns:
            True if the message appears IP-related
        """
        ip_keywords = [
            # General IP terms
            "integer programming", "ip problem", "integer program", "ip formulation",
            "mixed integer", "mip", "milp", "mixed integer programming",
            "pure integer", "binary programming", "binary integer programming",
            "discrete optimization", "combinatorial optimization",

            # Variables and decisions
            "integer variable", "binary variable", "0-1 variable", "discrete variable",
            "yes/no decision", "on/off decision", "selection decision",
            "integer constraint", "integrality constraint",

            # Solution methods
            "branch and bound", "branch-and-bound", "bnb",
            "cutting plane", "gomory cut", "cutting plane method",
            "branch and cut", "branch-and-cut",
            "enumeration", "implicit enumeration", "complete enumeration",

            # Relaxation and bounds
            "lp relaxation", "linear relaxation", "relaxation",
            "lower bound", "upper bound", "bound",
            "optimality gap", "gap", "integrality gap",

            # Common applications
            "facility location", "plant location", "warehouse location",
            "knapsack", "knapsack problem",
            "assignment", "assignment problem",
            "scheduling", "job shop", "resource scheduling",
            "traveling salesman", "tsp", "vehicle routing", "vrp",
            "set covering", "set packing", "set partitioning",
            "bin packing", "cutting stock",
            "project selection", "capital budgeting",

            # Modeling techniques
            "logical constraint", "either-or constraint", "if-then constraint",
            "fixed charge", "fixed cost",
            "big-m", "big m", "indicator variable",
            "piecewise linear", "sos", "special ordered set",

            # Properties and concepts
            "feasible solution", "incumbent solution",
            "node", "branching", "fathom", "pruning",
            "subproblem", "branch tree", "search tree",
            "heuristic", "rounding", "feasibility rounding",

            # General optimization terms (shared but relevant)
            "optimal", "optimality", "optimize", "optimization",
            "objective function", "constraint", "feasible",
            "minimize", "maximize",
        ]

        message_lower = message.lower()
        return any(keyword in message_lower for keyword in ip_keywords)

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
            "I'm specifically trained to help with Integer Programming topics. "
            "Your question seems to be about something else. "
            "\n\nI can help you with:\n"
            "- Formulating IP problems with binary and integer variables\n"
            "- Understanding branch and bound and cutting plane methods\n"
            "- Modeling yes/no decisions and logical constraints\n"
            "- Solving facility location, scheduling, and assignment problems\n"
            "- Understanding LP relaxation and optimality gaps\n"
            "\nWould you like to ask about any of these Integer Programming topics?"
        )

    def _prepare_generation_components(
            self,
            preprocessed_message: str,
            conversation_history: List[Dict[str, str]],
            context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare all shared components needed to generate a response
        (used by both sync and async paths).
        """
        # ADAPTIVE LEARNING: Detect confusion
        confusion_analysis = self.detect_student_confusion(
            preprocessed_message,
            conversation_history
        )

        # Define available explanation strategies for IP
        available_strategies = [
            "formulation-based", "example-driven", "algorithmic",
            "comparative", "application-based", "conceptual-theoretical"
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
            f"Generated {mode_label} IP response with strategy={selected_strategy}, "
            f"confusion={confusion_analysis['level']}"
        )
        return final_response

    def generate_response(self, user_message: str,
                          conversation_history: List[Dict[str, str]],
                          context: Dict[str, Any]) -> str:
        """
        Generate IP tutor response with adaptive preprocessing.

        Args:
            user_message: Current user message
            conversation_history: Previous messages
            context: Context dictionary

        Returns:
            Generated response with adaptive explanations
        """

        # Preprocess message
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

        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"],
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

        # Postprocess
        return self._postprocess_with_feedback(
            raw_response=response,
            conversation_history=conversation_history,
            context=context,
            confusion_analysis=components["confusion_analysis"],
            selected_strategy=components["selected_strategy"],
            async_mode=True
        )

# Global agent instance
_ip_agent: Optional[IntegerProgrammingAgent] = None

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