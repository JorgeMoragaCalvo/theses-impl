# P5 — Modelo

## Solución

1. Calcular el valor del punto $(1, 1)$ en la función:
    - $f(1, 1) = 6$ 
2. Expandir y reducir términos de la función:
    - $f(x, y) = x^2 - 4x + 4 + 2x + y^2 - y + 3$
    - $f(x, y) = x^2 - 2x + y^2 - y + 7$
3. Calcular el gradiente:
    - $\nabla f(x, y) = (2x - 2, 2y - 1)$
    - En el punto $(1, 1)$ $ \rightarrow $ $\nabla f(1, 1) = (0, 1)$
4. Calcular matriz Hessiana:
$$
H =
\begin{pmatrix}
2 & 0 \\
0& 2
\end{pmatrix}
$$
    - $h_1 = 2 > 0 $; $h_2 = 4 > 0 $ $ \implies $ $H$ es positiva definida $ \forall (x, y) $.
5. Calcular paso ya que $\nabla f(1, 1) \neq 0$.
    - $h(\alpha_k) = f(x_k + \alpha_k \nabla f(x^k))$
    - $h(\alpha_k) = f((1, 1) - \alpha (0, 1))$
    - $h(\alpha_k) = f(1, 1 - \alpha)$
6. Reemplazar el punto $f(1, 1 - \alpha)$ en la función $f(x, y)$.
    - $f(1, 1 - \alpha) = 1 - 2 + (1 - \alpha)^2 - (1 - \alpha) + 7 $.
    - Agrupando términos $ \rightarrow $ $f(1, 1 - \alpha) = \alpha^2 - \alpha + 6 $.
    - $ \therefore $ $h(\alpha_k) = \alpha^2 - \alpha + 6$.
    - $h'(\alpha_k) = 2\alpha - 1 = 0$ $ \implies $ $\alpha = \frac{1}{2}$.
7. Actualizar punto:
    - $x_{k+1} = x_k - \alpha_k \nabla f(x_k)$
    - $x_{k+1} = (1, 1) - \frac{1}{2} (0, 1)$
    - $x_{k+1} = (1, \frac{1}{2})$ $ \leftarrow $ punto nuevo.
8. Evaluar el punto obtenido en $\nabla f(x, y)$
    - $\nabla f(1, \frac{1}{2}) = (0, 0)$
    - Como $H$ es definida positiva $ \forall (x, y) $, el punto $(1, \frac{1}{2})$ es un mínimo global.
9. Calcular el valor del punto $(1, \frac{1}{2})$ en la función:
    - $f(1, \frac{1}{2}) = 1 + 2 + \frac{1}{4} - \frac{1}{2} + 3 = \frac{23}{4} = 5.75$
10. Usando el método de Newton:
$$
H =
\begin{pmatrix}
2 & 0 \\
0& 2
\end{pmatrix}
$$
11. Calcular $H^{-1}$:
$$
H^{-1} = \frac{1}{4}
\begin{pmatrix}
2 & 0 \\
0& 2
\end{pmatrix}
=
\begin{pmatrix}
\frac{1}{2} & 0 \\
0& \frac{1}{2}
\end{pmatrix}
$$
12. $x_{k+1} = x_k - H^{-1} (x_k)\nabla f(x_k) $
$$
= (1, 1)
\begin{pmatrix}
\frac{1}{2} & 0 \\
0& \frac{1}{2}
\end{pmatrix}
=
\begin{pmatrix}
0 \\
1
\end{pmatrix}
= (1, 1) - (0, \frac{1}{2}) = (1, \frac{1}{2})
$$

**Conclusión:**
- Como se verifica tanto por el método del gradiente y de Newton, el punto $(1, \frac{1}{2})$ es mínimo global, 
- ya que $\nabla f(1, \frac{1}{2}) = (0, 0)$ 
- y la matriz Hessiana es definida positiva $ \forall (x, y) $. 
- El valor mínimo de la función en $f(1, \frac{1}{2}) = \frac{23}{4} = 5.75 $.
