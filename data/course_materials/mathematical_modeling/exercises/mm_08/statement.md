# P8 — Salario total minimo

En un taller textil se requiere cocer botones, hacer ojales y planchar el producto antes de ir a control de calidad.

La demanda diaria es de 200 botones, 200 ojales y 30 prendas por planchar. El taller contrata a personas externas: P, F, J, E, para realizar estos trabajos.

Se debe distribuir el trabajo entre cuatros personas de modo que el salario total a pagar sea minimo. El tiempo por unidad se presenta en la siguiente tabla:

| Producto \ Persona | Ojal | Botón | Prenda | Capacidad de trabajo (min) | Salario por min (UM/hr) |
|--------------------|------|-------|--------|----------------------------|-------------------------|
| P                  | 5    | 2     | 10     | 130                        | 10                      |
| F                  | 3    | 4     | 12     | 80                         | 12                      |
| J                  | 4    | 3     | 9      | 100                        | 8                       |
| E                  | 5    | 3     | 8      | 120                        | 9                       |
| Demanda            | 200  | 200   | 30     | -                          | -                       |

## Lo que se pide

- Defina variables de decisión.
- Formule función objetivo.
- Formule restricciones.
- Indique tipo de modelo.

## Pistas

- El salario está en UM/hr, pero los tiempos de la tabla están en minutos. Hay que convertir las unidades para que sean consistentes (dividir el salario por 60 para obtener UM/min).
- Las restricciones de capacidad no limitan la cantidad de unidades producidas, sino el **tiempo total** (en minutos) que cada persona puede trabajar. Para cada persona, la suma de (tiempo por unidad × cantidad de unidades) de cada tarea debe respetar su capacidad.
- La función objetivo representa el costo total: para cada persona, es su salario por minuto multiplicado por el tiempo total que trabaja.
- Se necesitan 12 variables de decisión: una por cada combinación de persona (P, F, J, E) y tarea (botón, ojal, prenda).