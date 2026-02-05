# Solución

1. Calcular el gradiente de $ f(x, y) $:
$$ \nabla f(x, y) = (4x^3 - 4y, -4x + 4y^3) $$
2. Calcular matriz Hessiana de $ f(x, y) $
$$
H =
\begin{pmatrix}
12x^2 & -4 \\
-4 & 12y^2
\end{pmatrix}
$$
3. Verificar cada punto tanto en el gradiente como en la matriz Hessiana.
    - $ \nabla f(1, -1) $ = $ (8, -8) $ $ \implies $ el punto no cumple con la condición necesaria de primer orden, es decir, $ \nabla f(1, -1) \neq 0 $. No es necesario calcular resultado en matriz Hessiana.
    - $ \nabla f(0, 0) $ = $ (0, 0) $. Cumple con condición de primer orden. Verificar resultado en matriz Hessiana.
$$
H (0, 0)=
\begin{pmatrix}
0 & -4 \\
-4 & 0
\end{pmatrix}
$$
    - $ h_1 = 0 $, $ h_2 = \det(H) = 0 - 16 = -16 < 0 $, $\therefore$ no cumple con la condición suficiente. La matriz $ H $ en el punto $ (0, 0) $ es indefinida $\implies$ punto silla.
    - Punto $(1, 1)$: $\nabla f(1, 1) = (0, 0)$, cumple con condición necesaria. Verificar resultado en matriz Hessiana.
$$
H (1, 1)=
\begin{pmatrix}
12 & -4 \\
-4 & 12
\end{pmatrix}
$$
    - $ h_1 = 12 > 0 $; $ h_2 = \det(H) = 144 - 16 = 128 > 0 $, $\therefore$ cumple con la condición suficiente. La matriz $ H $ en el punto $ (1, 1) $ es definida positiva $\implies$ mínimo local.

**Conclusión:**
- El punto $ (1, -1) $ no es solución óptima.
- El punto $ (0, 0) $ es un punto silla.
- El punto $ (1, 1) $ es un mínimo local y por ende solución óptima del problema de optimización irrestricta planteado.
