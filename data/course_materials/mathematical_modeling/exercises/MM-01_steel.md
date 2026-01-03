# MM-01: Producción de Acero para Construcción Naval

## Contexto
Una empresa siderúrgica ha recibido un pedido de **500 toneladas** de acero destinado a la construcción naval. El acero debe cumplir con requisitos específicos de composición química.

## Datos del Problema

### Requisitos de Composición del Acero

| Elemento Químico | Mínimo (%) | Máximo (%) |
|------------------|------------|------------|
| Carbono (C)      | 2.0        | 3.0        |
| Cobre (Cu)       | 0.4        | 0.6        |
| Manganeso (Mn)   | 1.2        | 1.65       |

### Materias Primas Disponibles

| Materia Prima | C (%) | Cu (%) | Mn (%) | Disponibilidad (t) | Costo ($/t) |
|---------------|-------|--------|--------|---------------------|-------------|
| Hierro 1      | 2.5   | 0      | 1.3    | 400                 | 200         |
| Hierro 2      | 3.0   | 0      | 0.8    | 300                 | 250         |
| Hierro 3      | 0     | 0.3    | 0      | 600                 | 150         |
| Cobre 1       | 0     | 90     | 0      | 500                 | 220         |
| Cobre 2       | 0     | 96     | 4.0    | 200                 | 240         |
| Aluminio 1    | 0     | 0.4    | 1.2    | 300                 | 200         |
| Aluminio 2    | 0     | 0.6    | 0      | 250                 | 165         |

## Objetivo
Determinar la mezcla de materias primas que **minimice el costo total** de producción, cumpliendo con los requisitos de composición y las restricciones de disponibilidad.

## Preguntas Guía

1. ¿Qué decisiones debe tomar la empresa?
2. ¿Qué quiere lograr la empresa?
3. ¿Cuánto acero necesitan producir en total?
4. ¿Cómo se calcula el porcentaje de un elemento en la mezcla final?
5. ¿Pueden usar más materia prima de la que tienen disponible?

## Hints

### Hint 1: Variables
Las variables representan las cantidades de cada materia prima a utilizar. ¿Cuántas materias primas diferentes hay?

### Hint 2: Función Objetivo
El objetivo es minimizar costos. Si cada materia prima tiene un precio por tonelada, ¿cómo calculas el costo total de usar cierta cantidad de cada una?

### Hint 3: Restricciones de Composición
Si mezclas 100t de Hierro 1 (2.5% C) con 100t de Hierro 3 (0% C), la mezcla de 200t tiene:
- Carbono total: 100×0.025 + 100×0 = 2.5t
- Porcentaje: 2.5/200 = 1.25%

### Hint 4: Formulación de Porcentajes
El porcentaje de un elemento = (cantidad del elemento en la mezcla) / (cantidad total de mezcla).

Para que el porcentaje sea ≥ P%, la cantidad del elemento debe ser ≥ P% × cantidad total.