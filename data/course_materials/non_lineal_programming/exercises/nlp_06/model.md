# P6 — Modelo

## Solución

1. Calcular el valor del punto $(1, 0)$ en la función:
    - $f(1, 0) = 4$ 
2. Calcular el gradiente:
    - $\nabla f(x, y) = (6 - 4x + 2y, 2x - 4y)$
    - En el punto $(1, 0)$ $ \rightarrow $ $\nabla f(1, 0) = (2, 2)$ $\implies$ $\nabla f(1, 0) \neq 0$
3. Calcular matriz Hessiana:
$$
H =
\begin{pmatrix}
-4 & 2 \\
2& -4
\end{pmatrix}
$$
    - $h_1 = -4 < 0$; $h_2 = 12 > 0$
    - La matriz $H$ es definida negativa $ \forall (x, y) $; $\therefore$ es cóncava con un máximo global.
4. Calcular paso ya que $\nabla f(1, 0) \neq 0$.
    - $h(\alpha_k) = f(x_k + \alpha_k \nabla f(x^k))$
    - $h(\alpha_k) = f((1, 0) + \alpha (2, 2))$
    - $h(\alpha_k) = f(1 + 2\alpha, 2\alpha)$
5. Reemplazar el punto $f(1 + 2\alpha, 2\alpha)$ en la función $f(x, y)$.
    - $f(1 + 2\alpha, 2\alpha) = 6(1 + 2\alpha) - 2(1 + 2\alpha)^2 + 2(1 + 2\alpha)(2\alpha) - 2(2\alpha)^2$.
    - $f(1 + 2\alpha, 2\alpha) = (6 + 12\alpha) - 2(1 + 4\alpha + 4\alpha^2) + (4\alpha + 8\alpha^2) - 8\alpha^2$.
    - Agrupando términos $ \rightarrow $ $f(1 + 2\alpha, 2\alpha) = -8\alpha^2 + 8\alpha + 4$.
    - $ \therefore $ $h(\alpha_k) = -8\alpha^2 + 8\alpha + 4$.
    - Derivando $ \rightarrow $ $h'(\alpha_k) = -16\alpha + 8 = 0$ $ \implies $ $\alpha = \frac{1}{2}$.
6. Actualizar punto:
    - $x_{k+1} = x_k + \alpha_k \nabla f(x_k)$
    - $x_{k+1} = (1, 0) + \frac{1}{2} (2, 2) = (1, 0) + (1, 1)$
    - $x_{k+1} = (2, 1)$ $ \leftarrow $ punto nuevo.
7. Evaluar el punto obtenido en $\nabla f(x, y)$
    - $\nabla f(2, 1) = (0, 0)$
    - Como $H$ es definida negativa $ \forall (x, y) $, el punto $(2, 1)$ es un máximo global.
8. Calcular el valor del punto $(2, 1)$ en la función:
    - $f(2, 1) = 12 - 8 + 4 - 2 = 6$
9. Usando el método de Newton:
$$
H =
\begin{pmatrix}
-4 & 2 \\
2& -4
\end{pmatrix}
$$
10. Calcular $H^{-1}$:
$$
H^{-1} = \frac{1}{16 -4}
\begin{pmatrix}
-4 & -2 \\
-2& -4
\end{pmatrix}
= \frac{1}{12}
\begin{pmatrix}
-4 & -2 \\
-2& -4
\end{pmatrix}
$$
11. $x_{k+1} = x_k - H^{-1} (x_k)\nabla f(x_k) $
$$
= (1, 0) - \frac{1}{12}
\begin{pmatrix}
-4 & -2 \\
-2& -4
\end{pmatrix}
\begin{pmatrix}
2 \\
2
\end{pmatrix}
= (1, 0) - (-1, -1) = (2, 1) \leftarrow \text{punto óptimo}.
$$

**Conclusión:**
- Como se verifica tanto por el método del gradiente y de Newton, el punto $(2, 1)$ es máximo global, 
- ya que $\nabla f(2, 1) = (0, 0)$ 
- y la matriz Hessiana es definida negativa $ \forall (x, y) $. 
- El valor máximo de la función en $f(2, 1) = 6 $.

