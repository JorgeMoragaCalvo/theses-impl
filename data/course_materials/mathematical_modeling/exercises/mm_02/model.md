# P2 — Modelo

## Variables de decisión

x_ij = 1 si el trabajador i es asignado a la tarea j, 0 en caso contrario

## Función objetivo

min Z = Σᵢ Σⱼ c_ij · x_ij

## Restricciones

**Cada trabajador realiza exactamente una tarea:**
Σⱼ x_ij = 1 ∀i = 1, ..., n

**Cada tarea es realizada por exactamente un trabajador:**
Σᵢ x_ij = 1 ∀j = 1, ..., n

**Binariedad:**
x_ij ∈ {0, 1} ∀i, j

## Tipo de modelo

Programación Lineal Entera (PLI)