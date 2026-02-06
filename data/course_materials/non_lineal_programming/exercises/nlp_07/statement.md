# P7 — Optimización irrestricta

## Enunciado
Minimice la siguiente función:
$$ min f(x, y) = x^2 + 4y^2 - 4x - 8y $$ 
a partir del punto $(1, -1)$. Realizar a lo más dos iteraciones.

---

## Pistas
- Hint 1: Calcula el gradiente $\nabla f$ y la matriz Hessiana $H$. Verifica si $H$ es definida positiva para determinar la convexidad de la función.
- Hint 2: Utiliza el método de Newton: $x_{k+1} = x_k - H^{-1}\nabla f(x_k)$. Calcula $H^{-1}$ y evalúa el gradiente en el punto inicial $(1, -1)$.

## Tipo de Modelo
- PNL irrestricto