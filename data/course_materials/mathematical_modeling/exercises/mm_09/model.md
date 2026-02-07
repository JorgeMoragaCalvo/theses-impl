# P9 — Modelo

## Variables de decisión
- $x_1$: Cantidad de estuches tipo S.
- $x_2$: Cantidad de estuches tipo M.
- $x_3$: Cantidad de mochilas tipo S.
- $x_4$: Cantidad de mochilas tipo M.

## Función Objetivo
Maximizar la utilidad.
$$ maximizar: \space 650x_1 + 900x_2 + 1500x_3 + 1950x_4 $$

## Restricciones
1. De corte:
$$ 8x_1 + 10x_2 + 16x_3 + 18x_4 \leq 12000 \space (5 \text{ trabajadores} \times 8 \text{ horas/día} \times 5 \text{ días/semana} \times 60 \text{ min/hora}) $$
2. De costura:
$$ 10x_1 + 11x_2 + 17x_3 + 20x_4 \leq 24000 \space (10 \text{ trabajadores} \times 8 \text{ horas/día} \times 5 \text{ días/semana} \times 60 \text{ min/hora}) $$
3. De hilo:
$$ x_1 + 1.2x_2 + 2.2x_3 + 2.8x_4 \leq 20000 $$
4. De género:
$$ 0.25x_1 + 0.5x_2 + x_3 + 1.25x_4 \leq 5000 $$
5. De no negatividad:
$$ x_i \geq 0 \space \text{con} \space i = 1, 2, 3, 4.$$