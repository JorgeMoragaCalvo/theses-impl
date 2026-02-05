# P6 — Optimización irrestricta

## Enunciado
Utilizando el método del gradiente y el método de Newton, resolver:
$$ maximizar f(x, y) = 6x - 2x^2 + 2xy - 2y^2 $$ 
desde el punto $(1, 0)$.

---

## Pistas
- Hint 1: Calcula el gradiente $\nabla f$ y la matriz Hessiana $H$ para determinar la naturaleza de los puntos críticos.
- Hint 2: Para el método del gradiente, usa $x_{k+1} = x_k + \alpha_k \nabla f(x_k)$ donde $\alpha_k$ maximiza $h(\alpha) = f(x_k + \alpha \nabla f(x_k))$. Para Newton, usa $x_{k+1} = x_k - H^{-1}\nabla f(x_k)$.

## Tipo de Modelo
- PNL irrestricto
