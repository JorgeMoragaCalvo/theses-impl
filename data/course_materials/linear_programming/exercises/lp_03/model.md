# Solución P3

## Modelo de programación lineal

### Variables de decisión
- $X$: cantidad (en miles de \$) invertidos en fondos garantizados.
- $Y$: cantidad (en miles de \$) invertidos en fondos mixtos.

### Función objetivo
- Maximizar $z = 0.07X + 0.08Y + 0.12(12 - X - Y) = 1.44 - 0.05X - 0.04Y$

### Restricciones
- $12 - X - Y \geq 0$
- $12 - X - Y \leq 2$
- $X - 3Y \geq 0$
- $X, Y \geq 0$

## Solución gráfica

![image03](data/course_materials/linear_programming/images/image-03.png)

*Solución gráfica (referencia visual ilustrativa; no se entrega ni se evalúa). Puedes pedírsela al tutor.*

Al probar los vértices de la región factible en $(9, 3), (12, 0), (10, 0) \text{ y } (7.5, 2.5)$, se obtiene una rentabilidad óptima de la inversión de \$965 al invertir \$7500 en fondos mixtos, \$2500 en fondos garantizados y \$2000 en la Bolsa de Valores.