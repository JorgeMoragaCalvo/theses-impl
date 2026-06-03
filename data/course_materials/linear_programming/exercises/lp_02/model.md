# Solución P2

## 1. Indicar el plan de producción diario que maximizaría las ganancias diarias de planta de ensamblaje de autos.

### Variables de decisión
$x_1 = $ Cientos de autos de cuatro puertas que se fabrica diariamente.

$x_2 = $ Cientos de minivans que se fabrica diariamente.

### Función objetivo
Maximizar $z = 2100x_1 + 3000x_2 \rightarrow z = 21x_1 + 30x_2$

### Restricciones
- R1: la fracción del día durante la cual la planta de pintura está ocupada es igual o menor a 1.
- R1: la fracción del día durante la cual la planta de pintura trabaja en sedanes de cuatro puertas: $\frac{1}{2000}$.
- R1: la fracción del día durante la cual la planta de pintura trabaja en minivans: $\frac{1}{1500}$.
- R1: $\frac{1}{20} x_1 + \frac{1}{15} x_2 \leq 1$
- R2: la fracción del día durante la cual la planta de ensamblaje está ocupada es igual o menor a 1. la fracción del día durante la cual la planta de ensamblaje trabaja en sedanes de cuatro puertas o minivans: $\frac{1}{2200}$.
- R2: $\frac{1}{22} x_1 + \frac{1}{22} x_2 \leq 1 $
- R3: restricciones de no negatividad: $x_i \geq 0 \forall i \in \{1,2\}$

#### Solución gráfica
![solution](data/course_materials/linear_programming/images/image-01.png)

*Solución gráfica (referencia visual ilustrativa; no se entrega ni se evalúa). Puedes pedírsela al tutor.*

$x_1 = 0, x_2 = 15$

Por lo tanto, la planta de ensamblaje de autos no debería ensamblar sedanes de cuatro puertas, sino $1500$ minivans al día, lo que supone un beneficio de $\$4500000$.

## 2. ¿Qué excedentes se producirían en la planta de pintura? ¿Y en la planta de ensamblaje?
La planta de pintura está saturada, es decir, no tiene excedentes, mientras que la planta de ensamblaje tiene un excedente de $0.3$.