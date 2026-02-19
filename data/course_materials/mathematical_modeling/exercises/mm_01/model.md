# P1 — Modelo

## Variables de decisión

$x_i$ = toneladas de materia prima $i$ a utilizar $(i = 1, 2, ..., 7)$

## Función objetivo

min Z = $200x_1 + 250x_2 + 150x_)3 + 220x_4 + 240x_5 + 200x_6 + 165x_7$

## Restricciones

**Demanda total:**
- $x_1 + x_2 + x_3 + x_4 + x_5 + x_6 + x_7 = 500$

**Carbon (2% - 3%):**
- $0.025x_1 + 0.03x_2 \geq 0.02 \cdot 500$
- $0.025x_1 + 0.03x_2 \leq 0.03 \cdot 500$

**Cobre (0.4% - 0.6%):**
- $0.003x_3 + 0.9x_4 + 0.96x_5 + 0.004x_6 + 0.006x_7 \geq 0.004 \cdot 500$
- $0.003x_3 + 0.9x_4 + 0.96x_5 + 0.004x_6 + 0.006x_7 \leq 0.006 \cdot 500$

**Manganeso (1.2% - 1.65%):**
- $0.013x_1 + 0.008x_2 + 0.04x_5 + 0.012x_6 \geq 0.012 \cdot 500$
- $0.013x_1 + 0.008x_2 + 0.04x_5 + 0.012x_6 \leq 0.0165 \cdot 500$

**Disponibilidad:**
- $x_1 \leq 400$, $x_2 \leq 300$, $x_3 \leq 600$, $x_4 \leq 500$, $x_5 \leq 200$, $x_6 \leq 300$, $x_7 \leq 250$

**No negatividad:**
- $x_i \geq 0; \space \forall i$

## Tipo de modelo

Programación Lineal (PL)