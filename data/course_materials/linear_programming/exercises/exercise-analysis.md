# Detailed Analysis of Each Exercise

### lp_01 — Fábrica de circuitos impresos (Printed Circuit Boards)

- Type: Linear Programming (LP) — Resource allocation / product mix
- Variables: 2 continuous (units of circuit A and circuit B)
- Constraints: 3 resource availability (resistors, transistors, capacitors), non-negativity
- Key challenge: Almost none. Direct data-to-model mapping with three "≤" resource limits and a simple profit-maximization objective. Solvable graphically.

### lp_02 — Planificación producción industria automotriz (Auto Assembly Planning)

- Type: Linear Programming (LP) — Production planning with shared-capacity constraints
- Variables: 2 continuous (hundreds of sedans, hundreds of minivans)
- Constraints: 1 paint-shop fractional-capacity (1/2000 · x₁ + 1/1500 · x₂ ≤ 1), 1 assembly fractional-capacity, non-negativity
- Key challenge: Capacity is expressed as daily throughput per single product, so constraints must be built as fractions of the working day. Also requires scaling variables to hundreds of cars, and part 2 asks for surplus/slack interpretation at the optimum — a step beyond pure solving.

### lp_03 — Fondos de inversión (Investment Funds)

- Type: Linear Programming (LP) — Portfolio allocation
- Variables: 3 funds reduced to 2 decision variables (X = guaranteed, Y = mixed; stock = 12 − X − Y)
- Constraints: total-budget bounds (12 − X − Y ≥ 0 and ≤ 2), tax ratio (X ≥ 3Y), non-negativity
- Key challenge: The third investment is eliminated by substitution, which also rewrites the objective (z = 1.44 − 0.05X − 0.04Y). Recognizing the substitution and the resulting sign change in the objective is the main hurdle.

### lp_04 — Planificación de producción fábrica de tubos (Steel Tube Production)

- Type: Linear Programming (LP) — Product mix, three products / three machines
- Variables: 3 continuous (units of small, medium, large tubes)
- Constraints: 3 machine time limits (A ≤ 90, B ≤ 54, C ≤ 93 hours), non-negativity
- Key challenge: The only exercise that **cannot** be solved graphically — three decision variables require the simplex method (or a solver). This raises both the conceptual and computational bar above every other LP exercise here.

### lp_05 — Planificación de la producción fábrica de cables (Cable Production)

- Type: Linear Programming (LP) — Product mix
- Variables: 2 continuous (kg of aluminium wire, kg of copper wire)
- Constraints: electricity limit (≤ 500 kWh), labour limit (≤ 40 h), copper raw-material cap (≤ 60 kg), non-negativity
- Key challenge: Minimal. Three "≤" constraints with decimal coefficients (0.25, 0.5). Direct graphical solution; the only mild friction is the fractional coefficients.

### lp_06 — Fábrica de cobertizos (Garden Sheds)

- Type: Linear Programming (LP) — Product mix
- Variables: 2 continuous (sheds of type A and type B)
- Constraints: machine time (≤ 30 h), man-hours (≤ 60 h), non-negativity
- Key challenge: The simplest exercise in the set. Two variables, two clean integer constraints, straightforward profit maximization. Textbook introductory graphical LP.

### lp_07 — Cultivos de cebada y Bruselas (Barley & Brussels Crops)

- Type: Linear Programming (LP) — Land/resource allocation
- Variables: 2 continuous (hectares of barley, hectares of brussels)
- Constraints: total land (≤ 20 ha), budget (≤ 480 U.M.), labour in man-days, non-negativity
- Key challenge: Three interacting constraints (land, money, labour) instead of two. Still a clean graphical problem, but the student must coordinate three limits simultaneously.

### lp_08 — Confección blusas y faldas (Blouses & Skirts)

- Type: Linear Programming (LP) — Product mix
- Variables: 2 continuous (blouses, skirts)
- Constraints: Ann's time (≤ 7 h), Margaret's time (≤ 5 h, with a ½-hour-per-skirt coefficient), non-negativity
- Key challenge: Very small. Two constraints; the only subtlety is the fractional ½-hour coefficient and discarding the naive "equal quantity" idea in favour of the profit-optimal solution.

### lp_09 — Transporte de paquetes (Package Transport)

- Type: Linear Programming (LP) — Minimization with coverage + ratio constraints
- Variables: 2 continuous (large vans, small vans)
- Constraints: demand coverage (200x + 80y ≥ 1200), budget (≤ 300), fleet ratio (x ≤ y), non-negativity
- Key challenge: A **minimization** objective with a mix of "≥" and "≤" constraints plus a ratio constraint. The combination of a demand floor and a cost ceiling makes the feasible region less obvious than the pure-maximization product-mix problems.

### lp_10 — Fábrica de tornillos (Screw Factory)

- Type: Linear Programming (LP) — Product mix, two machines
- Variables: 2 continuous (boxes of wood screws, boxes of metal screws)
- Constraints: threading machine, slotting machine (each ≤ 60 h/week), non-negativity
- Key challenge: Mostly direct, but the machine availability is given in hours (60 h) while per-unit times are in minutes, so a unit conversion (60 h → 3600 min) is required before formulating.

### lp_11 — Fábrica (Workforce Constraints)

- Type: Linear Programming (LP) — Constraint formulation only
- Variables: 2 (unskilled workers x, skilled workers y)
- Constraints: weekly wage cap (135x + 270y ≤ 24300, simplifies to x + 2y ≤ 180), minimum operators (x + y ≥ 110), minimum skilled (y ≥ 40), union ratio (y ≥ ½x), non-negativity
- Key challenge: The task is to **write all constraints**, not to optimize. The difficulty lies in translating four separate verbal conditions — including a wage simplification and a union ratio — into correct inequalities.

### lp_12 — Camping

- Type: Linear Programming (LP) — Mixed allocation
- Variables: 2 continuous (motorhomes x, tents y)
- Constraints: total area (200x + 90y ≤ 1800), motorhome count (x ≤ 6), people limit (4x + 3y ≤ 48), non-negativity
- Key challenge: Three substantive constraints of different natures (area, count, occupancy) that must hold simultaneously. Building the feasible region from these heterogeneous limits requires care.

### lp_13 — Club de tenis (Tennis Club)

- Type: Linear Programming (LP) — Membership planning with two-sided ratio
- Variables: 2 continuous (adult members x, youth members y)
- Constraints: revenue floor (20x + 8y ≥ 800), total membership (x + y ≤ 50), two-sided ratio (¼x ≤ y ≤ ⅓x), non-negativity
- Key challenge: The youth-to-adult ratio is **double-sided** (between ¼ and ⅓ of adults), producing two ratio inequalities that bound the region from both sides — conceptually trickier than a single-sided ratio.

---

## Ranking: Easiest to Hardest

### Rank: 1 (Easiest)
- Exercise: lp_06
- Name: Fábrica de cobertizos (Garden Sheds)
- Difficulty: Very easy
- Tier: 1
- Justification: Two variables, two clean integer constraints, direct profit maximization. The simplest possible introductory graphical LP.
---

### Rank: 2
- Exercises: lp_08, lp_01
- Names: Confección blusas y faldas; Fábrica de circuitos impresos
- Difficulty: Easy
- Tier: 1
- Justification: Still two-variable graphical problems. lp_08 adds a fractional ½-hour coefficient; lp_01 adds a third resource constraint. Both remain direct data-to-model mappings.
---

### Rank: 3
- Exercises: lp_10, lp_05
- Names: Fábrica de tornillos; Fábrica de cables
- Difficulty: Easy
- Tier: 1
- Justification: Two-variable problems with a small added wrinkle — lp_10 needs an hours→minutes unit conversion, lp_05 carries decimal coefficients and a third (raw-material) cap.
---

### Rank: 4
- Exercise: lp_07
- Name: Cultivos de cebada y Bruselas (Barley & Brussels)
- Difficulty: Medium
- Tier: 2
- Justification: Three interacting constraints (land, budget, labour) must be coordinated at once, moving beyond the two-constraint product-mix pattern.
---

### Rank: 5
- Exercises: lp_12, lp_13
- Names: Camping; Club de tenis
- Difficulty: Medium
- Tier: 2
- Justification: lp_12 combines three heterogeneous constraints (area, count, occupancy); lp_13 introduces a two-sided ratio constraint. Both demand more careful feasible-region construction.
---

### Rank: 6
- Exercises: lp_09, lp_11
- Names: Transporte de paquetes; Fábrica
- Difficulty: Medium
- Tier: 2
- Justification: lp_09 is a minimization with mixed "≥"/"≤" and a fleet ratio; lp_11 is a pure formulation task requiring four verbal conditions (incl. a wage simplification and union ratio) to be turned into correct inequalities.
---

### Rank: 7
- Exercises: lp_02, lp_03
- Names: Planificación industria automotriz; Fondos de inversión
- Difficulty: Medium-hard
- Tier: 3
- Justification: lp_02 needs fractional shared-capacity constraints, variable scaling, and slack interpretation; lp_03 requires eliminating a third variable by substitution and rewriting the objective. Both demand a modeling transformation before solving.
---

### Rank: 8 (Hardest)
- Exercise: lp_04
- Name: Planificación de producción fábrica de tubos (Steel Tubes)
- Difficulty: Hard
- Tier: 3
- Justification: The only exercise with three decision variables across three machines — it cannot be solved graphically and requires the simplex method or a solver, raising both the conceptual and computational difficulty above every other exercise.
---

## Summary

The difficulty progression follows a logical pattern:
- Tier 1 (Easy): lp_06, lp_08, lp_01, lp_10, lp_05 — two-variable graphical product-mix problems with two to three direct constraints; at most a unit conversion or decimal coefficients.
- Tier 2 (Medium): lp_07, lp_12, lp_13, lp_09, lp_11 — three or more interacting constraints, two-sided ratios, minimization objectives, or pure constraint-formulation tasks.
- Tier 3 (Hard): lp_02, lp_03, lp_04 — require a modeling transformation (fractional capacities, variable substitution) or, in the case of lp_04, three variables that move the problem beyond the graphical method into the simplex algorithm.
