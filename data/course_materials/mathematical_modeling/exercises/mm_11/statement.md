# P11 — Suministro minas de carbón
Cuatro minas de carbón suministran combustible a tres hornos de una acería. En la tabla se presentan las distancias entre las minas y los hornos, las toneladas que puede suministrar mensualmente cada mina, y las toneladas que requiere cada horno al mes.

Considerando que el costo de transporte es proporcional a la distancia entre dos puntos geométricos, determinar la forma de realizar los suministros de carbón a **costo minimo**.

| Mina \ Horno | A    | B    | C    | Oferta |
|--------------|------|------|------|--------|
| T            | 8    | 4    | 22   | 150    |
| X            | 12   | 8    | 20   | 100    |
| Y            | 13   | 20   | 10   | 50     |
| Z            | 18   | 14   | 4    | 200    |
| Demanda      | 1000 | 1000 | 1000 | -      |

## Lo que se pide

- Defina variables de decisión.
- Formule función objetivo.
- Formule restricciones.
- Indique tipo de modelo.

## Pistas

- Identifique los orígenes (minas) y destinos (hornos) del problema.
- La oferta total (500 t) es menor que la demanda total (3000 t): el problema es **no balanceado**. Use igualdades para la oferta y desigualdades (≤) para la demanda.
- Las distancias de la tabla son directamente los coeficientes de costo en la función objetivo.
- El modelo tiene 12 variables de decisión ($x_{ij}$, una por cada par mina–horno).