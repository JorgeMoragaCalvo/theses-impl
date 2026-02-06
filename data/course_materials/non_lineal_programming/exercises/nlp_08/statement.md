# P8 — Optimización irrestricta

## Enunciado
Minimice la siguiente función:
$$ min f(x, y) = x^2 + y^2 + xy - 3x $$ 
Se piensa que el punto $(2, -1)$ es una solución óptima.

---

## Pistas
- Hint 1: Calcula el gradiente $\nabla f$ y la matriz Hessiana $H$. Verifica si $H$ es definida positiva usando los menores principales.
- Hint 2: Evalúa el gradiente en el punto $(2, -1)$. Si $\nabla f(2, -1) = (0, 0)$ y $H$ es definida positiva, entonces el punto es un mínimo global.

## Tipo de Modelo
- PNL irrestricto