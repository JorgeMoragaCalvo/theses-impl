# P8 — Modelo

## Variables de decisión

- $x_{pb}, x_{po}, x_{pp}$: número de botones, ojales y prendas planchadas por P.
- $x_{fb}, x_{fo}, x_{fp}$: número de botones, ojales y prendas planchadas por F.
- $x_{jb}, x_{jo}, x_{jp}$: número de botones, ojales y prendas planchadas por J.
- $x_{eb}, x_{eo}, x_{ep}$: número de botones, ojales y prendas planchadas por E.

## Tiempo por persona

| Producto \ Persona | Ojal | Botón | Prenda | Capacidad de trabajo (min) | Salario por min (UM/hr) |
|--------------------|------|-------|--------|----------------------------|-------------------------|
| P                  | 5    | 2     | 10     | 130                        | 10                      |
| F                  | 3    | 4     | 12     | 80                         | 12                      |
| J                  | 4    | 3     | 9      | 100                        | 8                       |
| E                  | 5    | 3     | 8      | 120                        | 9                       |

## Función objetivo

min $ Z = \frac{10}{60} (2x_{pb} + 5x_{po} + 10x_{pp}) + \frac{12}{60} (4x_{fb} + 3x_{fo} + 12x_{fp}) + \frac{8}{60} (3x_{jb} + 4x_{jo} + 9x_{jp}) + \frac{9}{60} (3x_{eb} + 5x_{eo} + 8x_{ep}) $

## Restricciones

### Demanda

- $x_{pb} + x_{fb} + x_{jb} + x_{eb} = 200$
- $x_{po} + x_{fo} + x_{jo} + x_{eo} = 200$
- $x_{pp} + x_{fp} + x_{jp} + x_{ep} = 30$

### Tiempo Disponible

- $2x_{pb} + 5x_{po} + 10x_{pp} \leq 130$
- $4x_{fb} + 3x_{fo} + 12x_{fp} \leq 80$
- $3x_{jb} + 4x_{jo} + 9x_{jp} \leq 100$
- $3x_{eb} + 5x_{eo} + 8x_{ep} \leq 120$

### No negatividad

$x_{ij} \geq 0$ $\forall$ $i$ en {p, f, j, e} y $j$ en {b, o, p}

## Tipo de modelo

Programación Lineal (PL). La función objetivo y todas las restricciones son lineales, y las variables de decisión son continuas y no negativas.
