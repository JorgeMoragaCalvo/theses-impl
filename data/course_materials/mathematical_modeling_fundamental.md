# Mathematical Modeling Fundamentals

## Course Overview

Mathematical modeling is the process of translating real-world problems into mathematical formulations that can be analyzed and solved using optimization techniques. This course covers the fundamental concepts, techniques, and best practices for building effective mathematical models in operations research and optimization.

---

## Table of Contents

1. [Introduction to Mathematical Modeling](#1-introduction-to-mathematical-modeling)
2. [The Modeling Process](#2-the-modeling-process)
3. [Components of Mathematical Models](#3-components-of-mathematical-models)
4. [Model Types and Classification](#4-model-types-and-classification)
5. [Common Problem Structures](#5-common-problem-structures)
6. [Formulation Techniques](#6-formulation-techniques)
7. [Model Validation and Analysis](#7-model-validation-and-analysis)
8. [Real-World Applications](#8-real-world-applications)

---

## 1. Introduction to Mathematical Modeling

### 1.1 What is Mathematical Modeling?

Mathematical modeling is the art and science of representing real-world situations using mathematical language, structures, and relationships. A mathematical model captures the essential features of a problem in a form that can be analyzed, solved, and interpreted.

**Key Benefits:**
- Provides a structured approach to problem-solving
- Enables systematic analysis of complex situations
- Supports better decision-making through quantitative insights
- Allows testing of different scenarios without real-world implementation
- Facilitates communication about problems and solutions

### 1.2 Why Mathematical Models?

Real-world decision problems often involve:
- Multiple competing objectives
- Limited resources
- Complex relationships between variables
- Uncertainty about future outcomes
- Trade-offs between different goals

Mathematical models help us:
1. **Clarify** the problem structure
2. **Quantify** relationships and constraints
3. **Optimize** decisions systematically
4. **Predict** outcomes of different choices
5. **Communicate** solutions effectively

### 1.3 Types of Problems We Model

- **Resource allocation**: How to distribute limited resources optimally
- **Planning and scheduling**: Determining when and how to perform activities
- **Design decisions**: Selecting the best configuration or structure
- **Routing and logistics**: Finding efficient paths or flows
- **Portfolio selection**: Choosing the best combination of options
- **Production planning**: Deciding what, when, and how much to produce

---

## 2. The Modeling Process

### 2.1 Six Steps of Mathematical Modeling

#### Step 1: Problem Understanding
- Identify stakeholders and their objectives
- Understand the context and constraints
- Clarify what constitutes a "solution"
- Determine available data and information

**Key Questions:**
- What is the business/real-world problem?
- Who will use the model and its results?
- What decisions need to be made?
- What are the success criteria?

#### Step 2: Model Formulation
- Identify decision variables
- Define the objective function
- Specify constraints
- Choose appropriate model type

#### Step 3: Data Collection
- Gather necessary parameters and coefficients
- Validate data quality
- Handle missing or uncertain data
- Estimate relationships when data is limited

#### Step 4: Model Solution
- Choose appropriate solution method
- Implement the model in software
- Solve for optimal or good solutions
- Check for computational issues

#### Step 5: Solution Analysis
- Interpret results in real-world terms
- Check if solution makes practical sense
- Perform sensitivity analysis
- Identify key drivers of the solution

#### Step 6: Implementation and Monitoring
- Communicate results to stakeholders
- Implement the recommended decisions
- Monitor performance
- Update model as needed

### 2.2 Iterative Nature of Modeling

Modeling is rarely a one-pass process. You often need to:
- Refine the formulation based on initial results
- Add or remove constraints
- Adjust the level of detail
- Reconsider assumptions
- Balance model complexity vs. solvability

---

## 3. Components of Mathematical Models

Every optimization model has three essential components:

### 3.1 Decision Variables

**Definition:** Variables that represent the decisions to be made. These are the quantities we can control or choose.

**Notation:** Typically denoted as x₁, x₂, ..., xₙ or with descriptive subscripts

**Types:**
- **Continuous**: Can take any real value (e.g., production quantities, investment amounts)
- **Integer**: Must be whole numbers (e.g., number of workers, number of facilities)
- **Binary**: Can only be 0 or 1 (e.g., yes/no decisions, on/off states)

**Best Practices:**
- Define variables clearly with units
- Use mnemonic notation when possible (e.g., xᵢⱼ for flow from i to j)
- Specify the domain (non-negative, binary, etc.)
- Include time indices if relevant

**Example:**
```
xᵢⱼ = number of units shipped from warehouse i to customer j
yᵢ = 1 if we open facility at location i, 0 otherwise
```

### 3.2 Objective Function

**Definition:** A mathematical expression that quantifies the goal we want to achieve. This is what we optimize (maximize or minimize).

**Common Objectives:**
- **Maximize**: Profit, revenue, utility, efficiency, output
- **Minimize**: Cost, time, distance, waste, risk

**Form:**
```
Maximize (or Minimize): f(x₁, x₂, ..., xₙ)
```

**Best Practices:**
- Should align with true business objective
- Include all relevant costs/benefits
- Use consistent units
- Consider multiple objectives if necessary

**Examples:**
```
Maximize: 50x₁ + 40x₂  (total profit)
Minimize: 3y₁ + 5y₂ + 4y₃  (total cost)
Minimize: Σᵢ Σⱼ cᵢⱼxᵢⱼ  (total shipping cost)
```

### 3.3 Constraints

**Definition:** Restrictions or requirements that limit the values decision variables can take. They represent the "rules of the game."

**Types:**

1. **Resource Constraints**
   - Limited availability of materials, time, budget, capacity
   - Example: `2x₁ + 3x₂ ≤ 100` (limited raw material)

2. **Requirement Constraints**
   - Minimum service levels, demand fulfillment, quality standards
   - Example: `x₁ + x₂ ≥ 50` (must meet minimum demand)

3. **Balance Constraints**
   - Flow conservation, inventory balance
   - Example: `inflow - outflow = 0`

4. **Logical Constraints**
   - If-then conditions, either-or choices, ordering requirements
   - Example: `x₁ ≤ 100y₁` (can only produce if facility is open)

5. **Non-negativity Constraints**
   - Variables that cannot be negative
   - Example: `xᵢ ≥ 0 for all i`

**Best Practices:**
- Every constraint should represent a real limitation
- Avoid redundant constraints
- Check that constraints don't make problem infeasible
- Use appropriate inequality direction (≤, ≥, =)

---

## 4. Model Types and Classification

### 4.1 Linear Programming (LP)

**Characteristics:**
- Linear objective function
- Linear constraints
- Continuous decision variables

**Form:**
```
Maximize: c₁x₁ + c₂x₂ + ... + cₙxₙ
Subject to:
  a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ ≤ b₁
  a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ ≤ b₂
  ...
  xᵢ ≥ 0 for all i
```

**When to Use:**
- Proportional relationships
- Continuous quantities
- Problems with many variables and constraints
- When optimal solution is needed

**Examples:** Production planning, diet optimization, portfolio allocation

### 4.2 Integer Programming (IP)

**Characteristics:**
- Linear objective and constraints
- Some or all variables must be integers

**Variants:**
- **Pure IP**: All variables are integers
- **Mixed IP (MIP)**: Some variables are integers, some continuous
- **Binary IP (BIP)**: Variables are 0 or 1

**When to Use:**
- Indivisible items (machines, people, facilities)
- Yes/no decisions
- Logical conditions
- Counting or sequencing problems

**Examples:** Facility location, project selection, scheduling

### 4.3 Nonlinear Programming (NLP)

**Characteristics:**
- Nonlinear objective function or constraints
- Variables can be continuous or integer

**When to Use:**
- Economies/diseconomies of scale
- Diminishing returns
- Multiplicative relationships
- Physical laws (power, exponential relationships)

**Examples:** Portfolio optimization with risk, chemical process design, pricing

### 4.4 Network Models

**Characteristics:**
- Special structure with nodes and arcs
- Flow variables on arcs
- Can be very large but efficiently solved

**Types:**
- Shortest path
- Maximum flow
- Minimum cost flow
- Transportation and assignment

**When to Use:**
- Physical networks (transportation, telecommunications)
- Logical networks (project scheduling, supply chains)

### 4.5 Stochastic Programming

**Characteristics:**
- Includes uncertain parameters
- Considers probability distributions
- May involve scenarios or stages

**When to Use:**
- Significant uncertainty in parameters
- Need to hedge against risk
- Sequential decisions with uncertainty

---

## 5. Common Problem Structures

### 5.1 Resource Allocation Problems

**Situation:** Distribute limited resources among competing activities to maximize benefit or minimize cost.

**Structure:**
```
Decision Variables: xⱼ = amount of resource allocated to activity j
Objective: Maximize Σⱼ pⱼxⱼ (total profit)
Constraints: Σⱼ aᵢⱼxⱼ ≤ bᵢ for each resource i
```

**Examples:**
- Allocating budget across marketing channels
- Assigning people to projects
- Distributing inventory among stores

### 5.2 Production Planning Problems

**Situation:** Determine what and how much to produce to meet demand while minimizing cost or maximizing profit.

**Structure:**
```
Decision Variables: xⱼ = quantity of product j to produce
Objective: Maximize Σⱼ (pⱼ - cⱼ)xⱼ (total profit)
Constraints:
  - Capacity: Σⱼ tⱼxⱼ ≤ T (available time)
  - Demand: xⱼ ≥ dⱼ (meet minimum demand)
  - Resources: Σⱼ rᵢⱼxⱼ ≤ Rᵢ (available resources)
```

### 5.3 Transportation Problems

**Situation:** Ship goods from sources (suppliers) to destinations (customers) at minimum cost.

**Structure:**
```
Decision Variables: xᵢⱼ = amount shipped from source i to destination j
Objective: Minimize ΣᵢΣⱼ cᵢⱼxᵢⱼ (total shipping cost)
Constraints:
  - Supply: Σⱼ xᵢⱼ ≤ sᵢ for each source i
  - Demand: Σᵢ xᵢⱼ ≥ dⱼ for each destination j
```

### 5.4 Assignment Problems

**Situation:** Assign agents (people, machines) to tasks on a one-to-one basis to optimize performance.

**Structure:**
```
Decision Variables: xᵢⱼ = 1 if agent i assigned to task j, 0 otherwise
Objective: Minimize ΣᵢΣⱼ cᵢⱼxᵢⱼ (total cost or time)
Constraints:
  - Each agent to one task: Σⱼ xᵢⱼ = 1 for all i
  - Each task to one agent: Σᵢ xᵢⱼ = 1 for all j
  - Binary: xᵢⱼ ∈ {0,1}
```

### 5.5 Blending Problems

**Situation:** Mix ingredients to create products that meet specifications at minimum cost.

**Structure:**
```
Decision Variables: xⱼ = amount of ingredient j to use
Objective: Minimize Σⱼ cⱼxⱼ (total ingredient cost)
Constraints:
  - Requirements: lᵢ ≤ Σⱼ aᵢⱼxⱼ ≤ uᵢ (property i within bounds)
  - Total amount: Σⱼ xⱼ = Q (produce Q units)
```

**Examples:** Feed mix, petroleum blending, alloy production

### 5.6 Facility Location Problems

**Situation:** Decide where to locate facilities and how to allocate customers to them.

**Structure:**
```
Decision Variables:
  yᵢ = 1 if we open facility at location i, 0 otherwise
  xᵢⱼ = amount of demand j served by facility i
Objective: Minimize Σᵢ fᵢyᵢ + ΣᵢΣⱼ cᵢⱼxᵢⱼ (fixed + variable costs)
Constraints:
  - Demand: Σᵢ xᵢⱼ = dⱼ for all customers j
  - Capacity: Σⱼ xᵢⱼ ≤ Mᵢyᵢ for all facilities i
  - Open/close: yᵢ ∈ {0,1}
```

---

## 6. Formulation Techniques

### 6.1 Using Binary Variables for Logical Conditions

Binary variables (0 or 1) can represent:
- Yes/no decisions
- On/off states
- Presence/absence
- Before/after relationships

**Technique: Fixed Charge**
If we incur a fixed cost when using an activity:
```
Include: K·y in objective (fixed cost)
Add constraint: x ≤ M·y
Where: y = 1 if x > 0, y = 0 if x = 0
```

**Technique: Either-Or Constraints**
Either constraint A or constraint B must hold:
```
A: f(x) ≤ b₁
B: g(x) ≤ b₂
Formulate as:
  f(x) ≤ b₁ + M·y
  g(x) ≤ b₂ + M·(1-y)
  y ∈ {0,1}
Where M is a large number
```

**Technique: If-Then Constraints**
If condition A holds, then constraint B must hold:
```
If f(x) ≤ b₁, then g(x) ≤ b₂
Formulate as:
  g(x) ≤ b₂ + M·y
  f(x) ≥ b₁ + ε - M·(1-y)
  y ∈ {0,1}
```

### 6.2 Linearization Techniques

**Absolute Values:**
Minimize |x| can be reformulated as:
```
Minimize: z
Subject to:
  z ≥ x
  z ≥ -x
```

**Piecewise Linear Functions:**
For a function with breakpoints, use binary variables to select segments.

**Products of Binary Variables:**
If y₁·y₂ appears in objective (both binary):
```
Introduce: z = y₁·y₂
Add: z ≤ y₁
     z ≤ y₂
     z ≥ y₁ + y₂ - 1
     z ∈ {0,1}
```

### 6.3 Handling Multiple Time Periods

**Technique: Index by Time**
```
xₜ = decision in period t
Add inventory balance constraints:
  Iₜ = Iₜ₋₁ + xₜ - dₜ
Where I is inventory, d is demand
```

### 6.4 Multi-Objective Problems

When there are multiple objectives:

1. **Weighted Sum Method:**
   - Combine objectives: Minimize w₁f₁(x) + w₂f₂(x)
   - Weights reflect relative importance

2. **Constraint Method:**
   - Optimize one objective
   - Put bounds on others: f₂(x) ≤ threshold

3. **Goal Programming:**
   - Set target for each goal
   - Minimize deviations from targets

---

## 7. Model Validation and Analysis

### 7.1 Verification (Did we build the model right?)

**Checks:**
- Dimensions and units are consistent
- All constraints are correctly entered
- Objective includes all costs/benefits
- No typos or sign errors
- Model matches the formulation on paper

**Techniques:**
- Solve small test cases with known answers
- Check extreme cases (all zeros, maximum values)
- Review each constraint's purpose
- Have someone else review the model

### 7.2 Validation (Did we build the right model?)

**Checks:**
- Model represents the real problem accurately
- Important factors are included
- Solution makes practical sense
- Stakeholders agree model captures reality

**Techniques:**
- Compare results to historical data
- Test with scenarios from experience
- Get domain expert feedback
- Check if solution is implementable

### 7.3 Sensitivity Analysis

**Purpose:** Understand how solution changes with parameters

**Questions:**
- How much can costs change before solution changes?
- What if demand is 10% higher?
- Which constraints are most restrictive?
- What is the value of additional resources?

**Methods:**
- Change parameters one at a time
- Resolve and compare solutions
- Use shadow prices (dual values)
- Perform range analysis

### 7.4 Common Modeling Mistakes

1. **Wrong objective direction**: Maximizing when should minimize
2. **Wrong inequality direction**: Using ≤ instead of ≥
3. **Missing non-negativity**: Allowing negative values when not sensible
4. **Infeasible constraints**: Contradictory or impossible requirements
5. **Unbounded model**: No upper limit on objective
6. **Missing linking constraints**: Variables not properly connected
7. **Wrong units**: Mixing tons and pounds, hours and minutes
8. **Over-simplification**: Omitting important real-world aspects
9. **Over-complication**: Including unnecessary details

---

## 8. Real-World Applications

### 8.1 Supply Chain Management

**Problem Types:**
- Facility location and network design
- Production planning and scheduling
- Inventory management
- Transportation and routing

**Example Model:**
A company needs to decide:
- How many distribution centers to open
- Where to locate them
- How to assign customers to centers
- How to route deliveries

Objective: Minimize total cost (fixed + transportation)

### 8.2 Financial Planning

**Problem Types:**
- Portfolio selection
- Asset allocation
- Risk management
- Capital budgeting

**Example Model:**
An investor has $1 million to invest:
- Decision: How much in each asset
- Objective: Maximize expected return
- Constraints: Risk limits, diversification requirements

### 8.3 Workforce Management

**Problem Types:**
- Shift scheduling
- Staff assignment
- Training planning
- Workforce sizing

**Example Model:**
A call center needs to schedule staff:
- Decision: How many workers on each shift
- Objective: Minimize labor cost
- Constraints: Cover forecasted call volume, labor rules

### 8.4 Manufacturing

**Problem Types:**
- Production planning
- Inventory management
- Equipment scheduling
- Quality control

**Example Model:**
A factory produces multiple products:
- Decision: Production quantities each period
- Objective: Maximize profit
- Constraints: Machine capacity, material availability, storage limits

### 8.5 Energy and Utilities

**Problem Types:**
- Generation scheduling
- Network flow optimization
- Capacity expansion planning
- Demand response

### 8.6 Healthcare

**Problem Types:**
- Patient scheduling
- Resource allocation (beds, OR time)
- Staff rostering
- Facility location

---

## Summary: Keys to Good Modeling

1. **Understand the problem thoroughly** before writing equations
2. **Start simple** and add complexity as needed
3. **Define variables clearly** with units and meaning
4. **Connect math to reality** - every constraint should have a reason
5. **Validate continuously** - check if results make sense
6. **Communicate effectively** - explain models in business terms
7. **Iterate and refine** - modeling is a process, not a one-shot task
8. **Balance detail and solvability** - more complexity isn't always better

---

## Practice Guidelines

To become proficient at mathematical modeling:

1. **Read problems carefully**: Identify what's being asked
2. **Ask the three key questions**:
   - What can I control? (variables)
   - What do I want? (objective)
   - What limits me? (constraints)
3. **Start with small examples**: Build intuition
4. **Learn common patterns**: Recognize problem types
5. **Verify your formulation**: Test with simple cases
6. **Interpret solutions**: Translate math back to real world
7. **Practice regularly**: Modeling is a skill developed through practice

---

## Additional Resources

- Focus on understanding WHY constraints are structured certain ways
- Practice translating word problems systematically
- Study formulations of classic problems
- Learn to recognize patterns across different applications
- Develop intuition for what makes a good model

---

*This course material provides foundational knowledge for mathematical modeling in operations research and optimization. For specific solution techniques (Simplex, Branch and Bound, etc.), refer to specialized course materials for Linear Programming, Integer Programming, and Nonlinear Programming.*
