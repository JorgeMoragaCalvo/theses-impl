# P5 — Modelo

## Variables de decisión
- $x_i$ = 1 si la carga i se embarca, 0 en caso contrario (i = 1, ..., 8)

## Función objetivo
- $max \ Z = 500x_1 + 600x_2 + 380x_3 + 750x_4 + 590x_5 + 820x_6 + 300x_7 + 910x_)8$

## Restricciones

**Capacidad del barco (3000 m²):**
- $400x_1 + 350x_2 + 600x_3 + 800x_4 + 870x_5 + 950x_6 + 780x_7 + 640x_8 \leq 3000$

**Binariedad:**
- $x_i \in \{0, 1\} \space \forall i$

## Tipo de modelo
- Programación Lineal Entera Binaria (PLI - Problema de la Mochila)