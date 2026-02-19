# P10 — Modelo

## Variables de decisión
- $x_{ij}$: cantidad de unidades desde el centro $i$ al detallista $j$; con $i = 1, 2, 3 $ y $j = 1, ..., 5 $

## Función Objetivo
- minimizar: $\sum_{i=1}^{3} \sum_{j=1}^{5} c_{ij}x_{ij}$

## Restricciones
- $o_i$: oferta del punto de distribución $i$

- $d_j$: demanda del punto detallista $j$

- $\sum_{j=1}^{5} x_{ij} \leq o_i$; con $i = 1, 2, 3$

- $\sum_{i=1}^{3} x_{ij} \geq d_j$; con $j = 1, ..., 5$

- **De no negatividad**: $x_{ij} \geq 0$;