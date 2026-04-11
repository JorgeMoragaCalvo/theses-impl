# P11 — Modelo

## Variables de decisión

$x_{ij}$ = toneladas de carbón transportadas desde la mina $i$ al horno $j$ donde $i \in \{T, X, Y, Z\}$, $j \in \{A, B, C\}$

## Función objetivo

$$\min Z = 8x_{TA} + 4x_{TB} + 22x_{TC} + 12x_{XA} + 8x_{XB} + 20x_{XC} + 13x_{YA} + 20x_{YB} + 10x_{YC} + 18x_{ZA} + 14x_{ZB} + 4x_{ZC}$$

## Restricciones

**Oferta** (cada mina envía toda su producción disponible):
- $x_{TA} + x_{TB} + x_{TC} = 150$
- $x_{XA} + x_{XB} + x_{XC} = 100$
- $x_{YA} + x_{YB} + x_{YC} = 50$
- $x_{ZA} + x_{ZB} + x_{ZC} = 200$

**Demanda** (cada horno no puede recibir más de lo que requiere):
- $x_{TA} + x_{XA} + x_{YA} + x_{ZA} \leq 1000$
- $x_{TB} + x_{XB} + x_{YB} + x_{ZB} \leq 1000$
- $x_{TC} + x_{XC} + x_{YC} + x_{ZC} \leq 1000$

**No negatividad:**
- $x_{ij} \geq 0 \quad \forall i, j$

## Tipo de modelo

Programación Lineal — Problema de Transporte (PL)
