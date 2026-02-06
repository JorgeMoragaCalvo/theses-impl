# P8 — Modelo

## Solución

1. Calcular gradiente de $f(x, y)$:
    - $\nabla f(x,y) = (2x + y - 3, 2y + x)$
2. Calcular matriz Hessiana:
$$
H =
\begin{pmatrix}
2& 1 \\
1& 2
\end{pmatrix}
$$
    - $h_1 = 2 > 0$
    - $h_2 = 4 - 1 > 0$
    - $\therefore$ La matriz $H$ es definida positiva $\forall (x, y)$ $\rightarrow$ es convexa en todo $x, y$.
3. Evaluar el punto $(2, -1)$ en el gradiente:
    - $\nabla f(2, -1) = (0, 0)$
    - Como $H$ es definida positiva $\forall (x, y)$, el punto $(2, -1)$ es un mínimo global.

**Conclusiones:**
- El punto $(2, -1)$ cumple con la condición óptima y suficiente.
- Es el mínimo global.  