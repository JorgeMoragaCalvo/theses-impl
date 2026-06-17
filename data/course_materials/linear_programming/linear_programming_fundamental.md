# Linear Programming Fundamentals

## Course Overview

Linear Programming (LP) is the branch of mathematical optimization concerned with maximizing or minimizing a linear objective function subject to linear equality and inequality constraints, over continuous decision variables. It is the workhorse of operations research: production planning, blending, transportation, assignment, and resource allocation problems all reduce to LPs. This material covers the core theory and the four techniques an LP student must master — **formulation**, the **graphical method**, the **simplex method**, **duality**, and **sensitivity analysis** — and closes with classic applications.

**What makes a problem an LP:**
- A single linear objective function (maximize or minimize).
- Linear constraints (each is a weighted sum of variables compared with ≤, ≥, or =).
- Continuous decision variables (any real value in the feasible region).
- Non-negativity of variables unless stated otherwise.

If any of these break — a product of variables, an integer requirement, a fixed cost triggered by a yes/no decision — the problem is no longer a pure LP and belongs to nonlinear or integer programming.

---

## Table of Contents

1. [The Standard LP Form](#1-the-standard-lp-form)
2. [Formulating an LP](#2-formulating-an-lp)
3. [The Graphical Method](#3-the-graphical-method)
4. [The Simplex Method](#4-the-simplex-method)
5. [Duality](#5-duality)
6. [Sensitivity Analysis](#6-sensitivity-analysis)
7. [Special Cases and Diagnostics](#7-special-cases-and-diagnostics)
8. [Classic Applications](#8-classic-applications)

---

## 1. The Standard LP Form

A linear program in **standard maximization form** is written:

```
Maximize:    z = c₁x₁ + c₂x₂ + ... + cₙxₙ
Subject to:  a₁₁x₁ + a₁₂x₂ + ... + a₁ₙxₙ ≤ b₁
             a₂₁x₁ + a₂₂x₂ + ... + a₂ₙxₙ ≤ b₂
             ...
             aₘ₁x₁ + aₘ₂x₂ + ... + aₘₙxₙ ≤ bₘ
             xⱼ ≥ 0   for all j = 1..n
```

**Terminology:**
- **cⱼ** — objective coefficients (profit/cost per unit of variable j).
- **aᵢⱼ** — technological coefficients (consumption of resource i per unit of j).
- **bᵢ** — right-hand side (availability of resource i).
- **Feasible region** — the set of points satisfying every constraint.
- **Optimal solution** — a feasible point that gives the best objective value.

**Converting to standard form:**
- A minimization can be turned into a maximization: `min z = -max(-z)`.
- A `≥` constraint becomes `≤` by multiplying both sides by −1.
- An equality `=` can be split into a `≤` and a `≥`.
- A **slack variable** sᵢ ≥ 0 turns `aᵢ·x ≤ bᵢ` into the equation `aᵢ·x + sᵢ = bᵢ`.
- A **surplus variable** turns `≥` into an equation by subtracting a non-negative amount.
- A variable unrestricted in sign is replaced by the difference of two non-negative variables: `xⱼ = xⱼ⁺ − xⱼ⁻`.

---

## 2. Formulating an LP

Translating a word problem into an LP is the most important skill. Ask three questions:

1. **What can I decide?** → decision variables (with explicit units).
2. **What do I want?** → objective function.
3. **What limits me?** → constraints.

**Worked example — product mix:**
A workshop makes tables (x₁) and chairs (x₂). Each table yields $50 profit and needs 4 h of carpentry and 2 h of finishing; each chair yields $40 and needs 3 h of carpentry and 1 h of finishing. There are 240 h of carpentry and 100 h of finishing available.

```
Decision variables:
  x₁ = number of tables produced
  x₂ = number of chairs produced

Maximize:    z = 50x₁ + 40x₂          (total profit)
Subject to:  4x₁ + 3x₂ ≤ 240          (carpentry hours)
             2x₁ + 1x₂ ≤ 100          (finishing hours)
             x₁, x₂ ≥ 0
```

**Formulation tips:**
- Define variables with units and a time index if relevant.
- Each constraint should encode one real limitation; name it in a comment.
- Keep units consistent across a constraint (don't mix hours and minutes).
- Watch the inequality direction: resources are usually `≤`, requirements `≥`.

---

## 3. The Graphical Method

For problems with **exactly two decision variables**, the LP can be solved by drawing it. The method is the clearest way to build intuition for why optimal solutions occur at corners.

**Steps:**
1. Plot each constraint as a line (treat `≤`/`≥` as `=`, then draw the line).
2. Shade the side of each line that satisfies the inequality.
3. The intersection of all shaded half-planes is the **feasible region** (a convex polygon).
4. Identify the **vertices** (corner points) where constraint lines intersect.
5. Evaluate the objective z at each vertex; the best value is optimal.

**The Fundamental Theorem of Linear Programming:** if an LP has an optimal solution, at least one optimal solution occurs at a **vertex (extreme point)** of the feasible region. This is why we only need to check corners, not every interior point.

**Iso-profit/iso-cost line:** alternatively, draw the objective for a fixed z and slide it parallel in the improving direction until it last touches the feasible region — that contact point is optimal.

---

## 4. The Simplex Method

The graphical method fails beyond two variables. The **simplex method** (Dantzig, 1947) solves LPs of any size by walking from vertex to adjacent vertex along the edges of the feasible region, improving the objective at each step until no improving move remains.

**Key ideas:**
- After adding slack/surplus variables, the constraints form a system of equations with more variables than equations. A **basic feasible solution** sets the extra (non-basic) variables to zero and solves for the rest — geometrically, a vertex.
- Each iteration swaps one variable into the basis and one out (**pivoting**), moving to a better adjacent vertex.

**The tableau iteration:**
1. **Build the initial tableau** with slack variables forming the starting basis.
2. **Optimality test:** for maximization, if every coefficient in the objective (z) row is ≥ 0, the current solution is optimal — stop.
3. **Choose the entering variable:** the non-basic variable with the most negative reduced cost (the "most improving" direction).
4. **Ratio test (leaving variable):** divide each RHS bᵢ by the positive entering-column entry aᵢ; the smallest non-negative ratio identifies the leaving (basic) variable — this keeps the next solution feasible.
5. **Pivot:** use row operations to make pivot element 1 and clear the rest of its column.
6. Repeat from step 2.

**Reading the final tableau:**
- The values of the basic variables give the optimal solution.
- The objective row gives the optimal z.
- The objective-row coefficients of the slack variables are the **shadow prices** (dual values) — see Duality.

**Variants worth knowing:**
- **Big-M / Two-Phase method** — handle `≥` and `=` constraints that have no obvious initial basic feasible solution, by introducing artificial variables.
- **Degeneracy** — a basic variable equal to zero; can cause cycling, prevented by anti-cycling rules (e.g., Bland's rule).

---

## 5. Duality

Every LP (the **primal**) has a companion LP (the **dual**) built from the same data. Duality gives both economic meaning and a way to check optimality.

**Constructing the dual** (for primal maximization with `≤` constraints):
- The dual is a **minimization**.
- Each primal constraint becomes a dual-variable yᵢ.
- Each primal variable becomes a dual constraint.
- The primal RHS (b) becomes the dual objective coefficients; the primal objective coefficients (c) become the dual RHS.

```
Primal:                         Dual:
  Max  cᵀx                        Min  bᵀy
  s.t. Ax ≤ b                     s.t. Aᵀy ≥ c
       x ≥ 0                           y ≥ 0
```

**Key theorems:**
- **Weak duality:** for any feasible primal x and feasible dual y, `cᵀx ≤ bᵀy`. Every dual feasible solution bounds the primal optimum.
- **Strong duality:** if the primal has an optimal solution, so does the dual, and their optimal objective values are **equal**.
- **Complementary slackness:** at optimality, if a primal constraint has slack (is not binding), its dual variable is 0; and if a dual variable is positive, its primal constraint is binding. Symmetrically for variables and their reduced costs. This links the two solutions and is a practical optimality check.

**Economic interpretation — shadow prices:** the optimal dual-variable yᵢ is the **shadow price** of resource i: the rate at which the optimal objective z would improve per additional unit of bᵢ, valid within a range. A binding constraint has a positive shadow price; a non-binding (slack) constraint has a shadow price of 0 — extra units of an already-abundant resource are worthless.

---

## 6. Sensitivity Analysis

Real data is uncertain. Sensitivity (post-optimality) analysis asks how the optimal solution and objective respond to changes in the data **without re-solving from scratch**.

**Objective coefficient ranging (range of optimality):**
- For each cⱼ, the range over which it can vary while the **current optimal vertex stays optimal** (the basis is unchanged, though z changes).
- Outside the range, a different vertex becomes optimal.

**Right-hand-side ranging (range of feasibility):**
- For each bᵢ, the range over which the **shadow price stays valid**.
- Within the range, each extra unit of resource i changes z by exactly the shadow price yᵢ.

**Reduced cost:** for a variable that is zero in the optimal solution, the reduced cost is how much its objective coefficient must improve before it becomes attractive to produce.

**Typical questions answered:**
- How much can a product's profit drop before we'd change the production plan?
- What is one more hour of the bottleneck resource worth? (its shadow price)
- Which constraints are binding (the true bottlenecks)?
- If demand rises 10%, does the optimal basis change?

---

## 7. Special Cases and Diagnostics

A well-posed LP has a unique optimum, but four other outcomes occur and must be recognized:

1. **Multiple (alternative) optima** — the objective line is parallel to a binding constraint edge; every point on that edge is optimal. Signaled by a zero reduced cost on a non-basic variable at optimality.
2. **Unbounded** — the objective can improve without limit because the feasible region is open in the improving direction. Usually means a constraint is missing.
3. **Infeasible** — no point satisfies all constraints; the feasible region is empty. Usually contradictory requirements (e.g., a minimum demand exceeding total capacity).
4. **Degenerate** — a vertex where a basic variable is zero; can slow or cycle the simplex method but does not, by itself, mean the model is wrong.

**Common formulation mistakes:** wrong objective direction, wrong inequality direction, missing non-negativity, inconsistent units, and unbounded/infeasible models caused by an omitted or contradictory constraint.

---

## 8. Classic Applications

LP underlies a large family of standard problems. The four below are the applications the LP tutor emphasizes:

### 8.1 Production / Product Mix
Decide how much of each product to make to maximize profit subject to capacity and material limits (the worked example in §2). The canonical LP.

### 8.2 Blending / Diet
Mix ingredients to meet quality or nutritional specifications at minimum cost.
```
Min  Σⱼ cⱼxⱼ                    (ingredient cost)
s.t. lᵢ ≤ Σⱼ aᵢⱼxⱼ ≤ uᵢ         (each property within spec)
     Σⱼ xⱼ = Q                  (total batch size)
     xⱼ ≥ 0
```

### 8.3 Transportation
Ship from supply sources to demand destinations at minimum cost.
```
Min  Σᵢ Σⱼ cᵢⱼxᵢⱼ              (total shipping cost)
s.t. Σⱼ xᵢⱼ ≤ sᵢ   ∀ source i   (supply)
     Σᵢ xᵢⱼ ≥ dⱼ   ∀ destination j (demand)
     xᵢⱼ ≥ 0
```
A balanced transportation problem (total supply = total demand) always has an optimal solution, and has integer optima when supplies and demands are integer.

### 8.4 Assignment
A special transportation problem: match agents to tasks one-to-one to minimize total cost or time. Though naturally a 0/1 problem, its LP relaxation always yields integer solutions, so it is solved as an LP.

---

## Summary: Keys to Solving LPs

1. **Formulate carefully** — variables with units, objective, constraints, non-negativity.
2. **Two variables → graph it**; build intuition for corner-point optimality.
3. **More variables → simplex**; pivot from vertex to better vertex until optimal.
4. **Use duality** to interpret resources (shadow prices) and to verify optimality (complementary slackness).
5. **Run sensitivity analysis** before trusting a plan built on uncertain data.
6. **Diagnose** infeasibility, unboundedness, and alternative optima — they usually point to a modeling error.

---

*This material covers the LP-specific theory and solution techniques (graphical method, simplex, duality, sensitivity analysis) that the general Mathematical Modeling Fundamentals defers here. For integer-restricted decisions see Integer Programming (Branch and Bound); for nonlinear objectives or constraints see Nonlinear Programming.*
