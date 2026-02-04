# P3 — Modelo

## Variables de decisión

$x_i$ = número de porciones del alimento i (i = 1: Avena, 2: Pollo, 3: Huevo, 4: Leche, 5: Carne, 6: Manzana)

## Función objetivo

min Z = 23x₁ + 240x₂ + 83x₃ + 210x₄ + 620x₅ + 89x₆

## Restricciones

**Energía mínima (2000 Kcal):**
110x₁ + 205x₂ + 160x₃ + 160x₄ + 420x₅ + 110x₆ ≥ 2000

**Proteína mínima (95 g):**
4x₁ + 32x₂ + 13x₃ + 18x₄ + 64x₅ + 14x₆ ≥ 95

**Calcio mínimo (800 mg):**
2x₁ + 12x₂ + 54x₃ + 185x₄ + 22x₅ + 80x₆ ≥ 800

**No negatividad:**
$x_i$ ≥ 0 ∀i

## Tipo de modelo

Programación Lineal (PL)