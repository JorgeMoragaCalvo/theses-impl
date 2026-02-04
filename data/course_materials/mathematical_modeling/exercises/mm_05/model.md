# P5 — Modelo

## Variables de decisión

$x_i$ = 1 si la carga i se embarca, 0 en caso contrario (i = 1, ..., 8)

## Función objetivo

max Z = 500x₁ + 600x₂ + 380x₃ + 750x₄ + 590x₅ + 820x₆ + 300x₇ + 910x₈

## Restricciones

**Capacidad del barco (3000 m²):**
400x₁ + 350x₂ + 600x₃ + 800x₄ + 870x₅ + 950x₆ + 780x₇ + 640x₈ ≤ 3000

**Binariedad:**
$x_i$ ∈ {0, 1} ∀i

## Tipo de modelo

Programación Lineal Entera Binaria (PLI - Problema de la Mochila)