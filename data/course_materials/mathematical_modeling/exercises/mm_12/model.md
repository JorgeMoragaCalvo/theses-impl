# P12 — Modelo

## Variables de decisión

$x_{ij}$ = MWh enviados desde la central $i$ a la ciudad $j$, donde $i \in \{1, 2, 3\}$, $j \in \{1, 2, 3, 4\}$

Las rutas inexistentes se excluyen del modelo: $x_{13}$ y $x_{24}$ no se definen (equivalentemente, $x_{13} = x_{24} = 0$).

## Función objetivo

$$\min Z = 5x_{11} + 9x_{12} + 4x_{14} + 6x_{21} + 10x_{22} + 3x_{23} + 4x_{31} + 2x_{32} + 5x_{33} + 7x_{34}$$

## Restricciones

**Suministro** (cada central no puede enviar más de lo disponible):
- $x_{11} + x_{12} + x_{14} \leq 28$
- $x_{21} + x_{22} + x_{23} \leq 32$
- $x_{31} + x_{32} + x_{33} + x_{34} \leq 60$

**Demanda** (cada ciudad debe recibir exactamente lo que requiere):
- $x_{11} + x_{21} + x_{31} = 48$
- $x_{12} + x_{22} + x_{32} = 29$
- $x_{23} + x_{33} = 40$
- $x_{14} + x_{34} = 33$

> **Nota:** El suministro total (120 MWh) es menor que la demanda total (150 MWh). El problema es **no balanceado** (oferta < demanda). Para resolverlo computacionalmente se añade una *central ficticia* con suministro de 30 MWh y costos cero; la asignación a esa central representa demanda no satisfecha.

**No negatividad:**
- $x_{ij} \geq 0 \quad \forall i, j$

## Tipo de modelo

Programación Lineal — Problema de Transporte con rutas prohibidas (PL)
