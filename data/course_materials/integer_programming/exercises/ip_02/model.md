# Solución P2

## 1. Formular modelo matemático

### Variables de decisión
- $X_1 =$ cantidad de carteros a tiempo completo que deben comenzar su turno a 5 días los lunes.
- $X_2 =$ cantidad de carteros a tiempo completo que deben comenzar su turno a 5 días los martes.
- $X_3 =$ cantidad de carteros a tiempo completo que deben comenzar su turno a 5 días los miércoles.
- $X_4 =$ cantidad de carteros a tiempo completo que deben comenzar su turno a 5 días los jueves.
- $X_5 =$ cantidad de carteros a tiempo completo que deben comenzar su turno a 5 días los viernes.
- $X_6 =$ cantidad de carteros a tiempo completo que deben comenzar su turno a 5 días los sábados.
- $X_7 =$ cantidad de carteros a tiempo completo que deben comenzar su turno a 5 días los domingos.

### Función objetivo
Minimizar $z = X_1 + X_2 + X_3 + X_4 + X_5 + X_6 + X_7$

### Restricciones
El número de carteros que trabajan el mismo día debe ser al menos igual al número de carteros necesarios para ese día. Por ejemplo, el número de carteros que trabajan los viernes será el de aquellos que comienzan sus turnos los lunes, martes, miércoles, jueves y viernes, y debe ser un mínimo de 14, y así sucesivamente con todos los días de la semana. 

- $X_1 + X_2 + X_3 + X_4 + X_5 \geq 14$
- $X_2 + X_3 + X_4 + X_5 + X_6 \geq 16$
- $X_3 + X_4 + X_5 + X_6 + X_7 \geq 11$
- $X_4 + X_5 + X_6 + X_7 + X_1 \geq 17$
- $X_5 + X_6 + X_7 + X_1 + X_2 \geq 13$
- $X_6 + X_7 + X_1 + X_2 + X_3 \geq 15$
- $X_7 + X_1 + X_2 + X_3 + X_4 \geq 19$
