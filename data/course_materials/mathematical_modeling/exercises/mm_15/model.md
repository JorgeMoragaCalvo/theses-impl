# P15 — Modelo
## Variables de decision

- $x_a$: cantidad de acres a sembrar con semillas A.
- $x_b$: cantidad de acres a sembrar con semillas B.
- $x_c$: cantidad de acres a sembrar con semillas C.

## Función Objetivo

Maximizar: $100x_a + 300x_b + 200x_c$

## Restricciones

1. Cantidad de acres disponibles.
   - $x_a + x_b + x_3c \leq 120$
2. Presupuesto disponible para las semillas.
   - $40x_a + 20x_b + 30x_c \leq 3400$
3. Número de días laborales disponibles.
   - $x_a + 2x_b + x_c \leq 170$
4. Restricción de no negatividad.
   - $x_a, x_b, x_c \geq 0$

## Tipo de modelo
- Modelo de Programación Lineal (PL).
