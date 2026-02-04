# P7 — Modelo

## Variables de decisión

$x_i$ = cantidad de ventanas producidas en el mes i (i = 1, ..., 6)

$I_i$ = inventario de ventanas al final del mes i (i = 1, ..., 6)

## Función objetivo

min Z = 35000x₁ + 31500x₂ + 38500x₃ + 33600x₄ + 36400x₅ + 35000x₆ + 4600(I₁ + I₂ + I₃ + I₄ + I₅ + I₆)

## Restricciones

**Balance de inventario (demanda mensual: 100, 250, 190, 140, 220, 110):**

x₁ - I₁ = 100

I₁ + x₂ - I₂ = 250

I₂ + x₃ - I₃ = 190

I₃ + x₄ - I₄ = 140

I₄ + x₅ - I₅ = 220

I₅ + x₆ - I₆ = 110

**No negatividad:**

$x_i$ ≥ 0, $I_i$ ≥ 0 ∀i

## Tipo de modelo

Programación Lineal (PL - Planificación de Producción e Inventario)
