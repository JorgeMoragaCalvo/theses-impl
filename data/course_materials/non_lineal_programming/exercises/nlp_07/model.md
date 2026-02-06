# P7 — Modelo

## Solución
1. Calcular el gradiente de $f(x, y)$:
    - $\nabla f(x, y) = (2x - 4, 8y - 8)$
    - En el punto $(1, -1)$ $ \rightarrow $ $\nabla f(1, -1) = (-2, -16)$ $\implies$ $\nabla f(1, -1) \neq 0$
2. Calcular la matriz Hessiana:
$$
H =
\begin{pmatrix}
2& 0 \\
0& 8
\end{pmatrix}
$$
    - $h_1 = 2 > 0 $; $h_2 = 16 > 0 $ $\implies$ $H$ es definida positiva $\forall (x, y)$; $\therefore$ es convexa en todo $x, y$ $\implies$ minimo global.
3. Utilizando Newton $\rightarrow$ $ x_{k+1} = x_k - H^{-1}f(x_k) $
4. Calcular $H^{-1}$:
$$
H^{-1} = \frac{1}{16}
\begin{pmatrix}
2& 0 \\
0& 8
\end{pmatrix}
=
\begin{pmatrix}
\frac{8}{16}& 0 \\
0& \frac{2}{16}
\end{pmatrix}
$$
5. Reemplazar en el algoritmo de Newton:
$$
x_{k+1} = (1, -1) - 
\begin{pmatrix}
\frac{8}{16}& 0 \\
0& \frac{2}{16}
\end{pmatrix}
\begin{pmatrix}
-2 \\
-16
\end{pmatrix}
=
(1, -1) - (-1, -2) = (2, 1)
$$
    - $\therefore$ $x_{k+1} = (2, 1)$
6. Evaluar el punto obtenido en $\nabla f(x, y)$
    - $\nabla f(2, 1) = (0, 0)$

**Conclusiones:**
- El punto $(2, 1)$ es punto óptimo.
- Como $H > 0 $, el punto $(2, 1)$ es minimo global.
- Calcular el valor del punto $(2, 1)$ en la función:
    - $f(2, 1) = 4 + 4 - 8 - 8 = -8$
- El valor mínimo de la función es $f(2, 1) = -8
- El valor de la función en el punto $(1, -1)$ es $f(1, -1) = 1 + 4 + 4 + 8 = 17$
- Se observa una disminución significativa en el valor de la función desde $17$ hasta $-8 $ en una sola iteración del método de Newton.