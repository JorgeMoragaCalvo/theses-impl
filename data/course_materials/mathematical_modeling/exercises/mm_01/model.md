# P1 — Modelo

## Variables de decisión

$x_i$ = toneladas de materia prima i a utilizar (i = 1, 2, ..., 7)

## Función objetivo

min Z = 200x₁ + 250x₂ + 150x₃ + 220x₄ + 240x₅ + 200x₆ + 165x₇

## Restricciones

**Demanda total:**
x₁ + x₂ + x₃ + x₄ + x₅ + x₆ + x₇ = 500

**Carbono (2% - 3%):**
2.5x₁ + 3x₂ ≥ 10
2.5x₁ + 3x₂ ≤ 15

**Cobre (0.4% - 0.6%):**
0.3x₃ + 90x₄ + 96x₅ + 0.4x₆ + 0.6x₇ ≥ 2
0.3x₃ + 90x₄ + 96x₅ + 0.4x₆ + 0.6x₇ ≤ 3

**Manganeso (1.2% - 1.65%):**
1.3x₁ + 0.8x₂ + 4x₅ + 1.2x₆ ≥ 6
1.3x₁ + 0.8x₂ + 4x₅ + 1.2x₆ ≤ 8.25

**Disponibilidad:**
x₁ ≤ 400
x₂ ≤ 300
x₃ ≤ 600
x₄ ≤ 500
x₅ ≤ 200
x₆ ≤ 300
x₇ ≤ 250

**No negatividad:**
x_i ≥ 0 ∀i

## Tipo de modelo

Programación Lineal (PL)