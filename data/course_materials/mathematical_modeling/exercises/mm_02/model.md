# P2 — Modelo

## Variables de decisión

$x_{ij}$ = 1 si el trabajador i es asignado a la tarea j, 0 en caso contrario

## Función objetivo

min Z = Σᵢ Σⱼ $c_{ij}$ · $x_{ij}$

## Restricciones

**Cada trabajador realiza exactamente una tarea:**
- $\sum_{j} \ x_{ij}$ = 1 ∀i = 1, ..., n

**Cada tarea es realizada por exactamente un trabajador:**
- $\sum_{i} \ {x_ij}$ = 1 ∀j = 1, ..., n

**Binariedad:**
${x_ij} \in \ \{0, 1\} \ \forall \ i, j $

## Tipo de modelo

Programación Lineal Entera (PLI)