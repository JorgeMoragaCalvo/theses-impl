# P5 — Optimización irrestricta

## Enunciado
Utilizando el método del gradiente y el método de Newton, resolver:
$$ minimizar f(x, y) = (x - 2)^2 + 2x +y^2 - y + 3 $$ 
desde el punto $(1, 1)$.

---

## Pistas
- Hint 1: Expande $(x-2)^2$ y simplifica la función. Luego calcula el gradiente $\nabla f$ y la matriz Hessiana $H$ para determinar la naturaleza de los puntos críticos.
- Hint 2: Para el método del gradiente, usa $x_{k+1} = x_k - \alpha_k \nabla f(x_k)$ donde $\alpha_k$ minimiza $h(\alpha) = f(x_k - \alpha \nabla f(x_k))$. Para Newton, usa $x_{k+1} = x_k - H^{-1}\nabla f(x_k)$.

## Tipo de Modelo
- PNL irrestricto

