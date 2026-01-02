# Modelamiento Matemático
## Problema 1
Una empresa siderúrgica ha recibido un pedido de 500 toneladas de acero destinado a la construcción naval. El acero debe cumplir con los siguientes requisitos porcentuales en su composición:

**Tabla 1**. Requisitos porcentuales

| Elemento Químico | minimo Porcentual (%) | Maximo Porcentual (%) |
| ---------------- | --------------------- | --------------------- |
| Carbon (C) | 2 | 3 |
| Cobre (Cu) | 0.4 | 0.6 |
| Manganeso (Mn) | 1.2 | 1.65 |

La empresa cuenta con siete materias primas diferentes en stock que pueden ser utilizadas para la producción del acero. En tabla nro. 2 se enumeran los porcentajes, las cantidades disponibles y los precios de todas las materias primas.

| Materia Prima | C%  | Cu% | Mn% | Disponibilidad en t | Costo en $/t |
|---------------|-----|-----|-----|---------------------|--------------|
| Hierro 1      | 2.5 | 0   | 1.3 | 400                 | 200          |
| Hierro 2      | 3   | 0   | 0.8 | 300                 | 250          |
| Hierro 3      | 0   | 0.3 | 0   | 600                 | 150          |
| Cobre 1       | 0   | 90  | 0   | 500                 | 220          |
| Cobre 2       | 0   | 96  | 4   | 200                 | 240          |
| Alumnio 1     | 0   | 0.4 | 1.2 | 300                 | 200          |
| Alumnio 2   | 0   | 0.6 | 0   | 250                 | 165          |

El objetivo es determinar la composición de la aleación que optimice la producción.

## Problema 2
Se cuenta con un conjunto de *n* trabajadores y una cantidad igual de tareas. Cualquiera de los *n* trabajadores puede realizar cualquiera de las *n* tareas, incurriendo en un costo *c*, que puede variar dependiendo de la asignación trabajador-tarea. Se quiere realizar todas las tareas, asignando exactamente un trabajador a cada tarea y solo una tarea a cada trabajador, de tal manera que se minimice el costo total de realizar todas las tareas.

## Problema 3
En el marco del programa de *JUNJI* para entrega de almuerzos a niños de educación preescolar, un equipo de nutricionistas se encuentra diseñando una dieta que contenga toda la energía (2000 Kcal), proteína (95 g) y calcio (800 mg) necesario para una alimentación saludable. Con este fin, el equipo eligió 6 alimentos por ser fuentes baratas de nutrientes y tabulo sus datos de valores nutritivos por porción en la tabla de valores nutritivos.

| Alimento | Porción    | Energía (Kcal) | Proteína (g) | Calcio (mg) | Precios (pesos) |
|----------|------------|----------------|--------------|-------------|-----------------|
| Avena    | 28 g       | 110            | 4            | 2           | 23              |
| Pollo    | 100 g      | 205            | 32           | 12          | 240             |
| Huevo    | 2 unidades | 160            | 13           | 54          | 83              |
| Leche    | 237 cc     | 160            | 18           | 185         | 210             |
| Carne    | 270 g      | 420            | 64           | 22          | 620             |
| Manzana  | 160 g      | 110            | 14           | 80          | 89              |

Se necesita plantear un modelo de *programacion lineal* para encontrar el menu que satisfaga las necesidades nutricionales propuestas por el equipo de nutricionistas al costo mínimo.