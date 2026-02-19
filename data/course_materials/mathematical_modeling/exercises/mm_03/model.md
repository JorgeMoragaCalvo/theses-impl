# P3 — Modelo

## Variables de decisión

$x_i$ = número de porciones del alimento $i$ ($i$ = 1: Avena, 2: Pollo, 3: Huevo, 4: Leche, 5: Carne, 6: Manzana)

## Función objetivo

min $Z = 23x_1 + 240x_2 + 83x_3 + 210x_4 + 620x_5 + 89x_6$

## Restricciones

**Energía mínima (2000 Kcal):**
- $110x_1 + 205x_2 + 160x_3 + 160x_4 + 420x_5 + 110x_6 \geq 2000$

**Proteína mínima (95 g):**
- $4x_1 + 32x_2 + 13x_3 + 18x_4 + 64x_5 + 14x_6 \geq 95$

**Calcio mínimo (800 mg):**
- $2x_1 + 12x_2 + 54x_3 + 185x_4 + 22x_5 + 80x_6 \geq 800$

**No negatividad:**
- $x_i$ ≥ 0 ∀i

## Tipo de modelo

Programación Lineal (PL)