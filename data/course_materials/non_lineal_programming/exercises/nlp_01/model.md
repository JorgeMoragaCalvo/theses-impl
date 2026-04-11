# P1 — Modelo
## Desarrollo
1. Desarrollando $\rightarrow$ $f(x, y) = x^2 - 8x + 16 + x^2 - 4xy + 4y^2 = 2x^2 - 8x - 4xy + 4y^2 + 16$
2. Calcular el gradiente de $f(x, y)$:
   - $\nabla f(x, y) = (4x - 8 - 4y, -4x + 8y)$
3. Calcular el gradiente de $g(x, y) = x^2 - y$
   - $\nabla g(x, y) = (2x, -1)$
4. Tanto $(-1, 1) \text{ como } (1, 1)$ cumplen que $g(x, y) = 0$
5. Evaluar el punto $(-1, 1)$ en $\nabla f(x, y) = \lambda \nabla g(x, y)$ y verificar si $\exists$ un $\lambda$. Reemplazando:
   - $\nabla f(x, y) = \lambda \nabla g(x, y)$ $\rightarrow (-16, 12) = \lambda (-2, -1)$ $\implies \nexists \lambda$
6. Evaluar el punto $(1, 1)$ en $\nabla f(x, y) = \lambda \nabla g(x, y)$ y verificar si $\exists$ un $\lambda$. Reemplazando:
   - $\nabla f(x, y) = \lambda \nabla g(x, y)$ $\rightarrow (-8, 4) = \lambda (2, -1)$ $\implies \exists \lambda = -4$

> $\therefore (1, 1)$ es solución óptima.

# P2 — Modelo
## Desarrollo
1. Desarrollando $\rightarrow$ $f(x, y) = x^2 - 4x + 4 + y^2 - 2y + 1$
2. Calcular el gradiente de $f(x, y)$:
   - $\nabla f(x, y) = (2x - 4, 2y - 2)$
3. Calcular el gradiente de $g_1(x, y) = -y + x^2$
   - $\nabla g_1(x, y) = (2x, -1)$
4. Calcular el gradiente de $g_2(x, y) = x + y - 2$
   - $\nabla g_2(x, y) = (1, 1)$
5. El punto $(1, 1)$ cumple con que $g_1(x, y) = 0$ y $g_2(x, y) = 0$
6. Evaluar los gradientes en $(1, 1)$:
   - $\nabla f(1, 1) = (2 \cdot 1 - 4,\; 2 \cdot 1 - 2) = (-2, 0)$
   - $\nabla g_1(1, 1) = (2 \cdot 1, -1) = (2, -1)$
   - $\nabla g_2(1, 1) = (1, 1)$
7. Verificar la condición de estacionariedad KKT $\nabla f = \lambda_1 \nabla g_1 + \lambda_2 \nabla g_2$. Reemplazando:
   - $(-2, 0) = \lambda_1 (2, -1) + \lambda_2 (1, 1)$, lo que genera el sistema:
     - $2\lambda_1 + \lambda_2 = -2$
     - $-\lambda_1 + \lambda_2 = 0 \implies \lambda_1 = \lambda_2$
   - Sustituyendo: $3\lambda_1 = -2 \implies \lambda_1 = \lambda_2 = -\frac{2}{3}$
8. Verificar factibilidad dual (para minimización con restricciones $\leq 0 $ se requiere $\lambda_i \leq 0 $):
   - $\lambda_1 = -\frac{2}{3} \leq 0$ ✓
   - $\lambda_2 = -\frac{2}{3} \leq 0$ ✓

> $\therefore (1, 1)$ es solución óptima.
