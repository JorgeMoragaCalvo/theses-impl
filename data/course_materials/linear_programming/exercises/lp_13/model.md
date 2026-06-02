# Solución P12

## Variables de decisión
- $x =$ cantidad de miembros adultos.
- $y =$ cantidad de miembros jóvenes.

## Función objetivo
- Maximizar $z = 20x + 8y$

## Restricciones

De recaudación
- $20x + 8y \geq 800 $ 

Cantidad de miembros
- $x + y \leq 50 $

Proporción de jóvenes
- $\frac{1}{4} x \leq y \leq \frac{1}{3} x$
  - $\frac{1}{4} x \leq y$ $\implies$ $x - 4y \leq 0 $
  - $y \leq \frac{1}{3} x$ $\implies$ $x - 3y \geq 0 $

No negatividad
- $x, y \geq 0 $

## Solución gráfica
![lp_13_model.png](data/course_materials/linear_programming/images/image-09.png)

La cantidad total de miembros adultos y jóvenes que reúnen la mayor cantidad de dinero en suscripción es:
- $x = 40$ (adultos).
- $y = 10$ (jóvenes).
- Reúnen \$880