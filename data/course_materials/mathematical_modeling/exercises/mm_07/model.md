# P7 — Modelo

## Variables de decisión
- $x_i$ = cantidad de ventanas producidas en el mes i (i = 1, ..., 6)
- $I_i$ = inventario de ventanas al final del mes i (i = 1, ..., 6)

## Función objetivo

- $min \ Z = 35000x_1 + 31500x_2 + 38500x_3 + 33600x_4 + 36400x_5 + 35000x_6 + 4600(I_1 + I_2 + I_3 + I_4 + I_5 + I_6)$

## Restricciones

**Balance de inventario (demanda mensual: 100, 250, 190, 140, 220, 110):**
- $x_1 - I_1 = 100$
- $I_1 + x_2 - I_2 = 250$
- $I_2 + x_3 - I_3 = 190$
- $I_3 + x_4 - I_4 = 140$
- $I_4 + x_5 - I_5 = 220$
- $I_5 + x_6 - I_6 = 110$

**No negatividad:**
- $x_i$ ≥ 0, $I_i$ ≥ 0 ∀i

## Tipo de modelo

Programación Lineal (PL - Planificación de Producción e Inventario)
