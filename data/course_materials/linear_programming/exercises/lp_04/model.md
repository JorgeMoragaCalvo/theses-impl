# Solución P4

## Modelo de programación lineal

### Variables de decisión
- $x_1$: unidades de tubos pequeños.
- $x_2$: unidades de tubos medianos.
- $x_3$: unidades de tubos grandes.

### Función objetivo
- Maximizar $z = 30x_1 + 40x_2 + 35x_3$

### Restricciones
Límite de horas Máquina A
- $3x_1 + 4x_2 + 2x_3 \leq 90$

Límite de horas Máquina B
- $2x_1 + x_2 + 2x_3 \leq 54$

Límite de horas Máquina C
- $x_1 + 3x_2 + 2x_3 \leq 93$

No negatividad
- $x_1, x_2, x_3 \geq 0$