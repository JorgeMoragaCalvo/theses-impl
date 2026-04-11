# P15 — Modelo
## Variables de decision

$x_1$: cantidad de banjos producidos.
$x_2$: cantidad de guitarras producidas.
$x_3$: cantidad de mandolinas producidas.

## Función Objetivo

Maximizar: $250x_1 + 175x_2 + 125x_3$

## Restricciones

1. Restricción asociada a la disponibilidad de madera.
   - $x_1 + 2x_2 + x_3 \leq 50$
2. Restricción asociada a la disponibilidad de mano de obra.
   - $x_1 + 2x_2 + 2x_3 \leq 60$
3. Restricción asociada a la disponibilidad de metal.
   - $x_1 + x_2 + x_3 \leq 55$
4. Restricción de no negatividad.
   - $x_1, x_2, x_3 \geq 0$

## Tipo de modelo
- Programación Lineal (PL).
