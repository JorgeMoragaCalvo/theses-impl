# P4 — Modelo

## Patrones de corte posibles

| Patrón | 30 cm | 45 cm | 50 cm | Desperdicio (cm) |
|--------|-------|-------|-------|------------------|
| 1      | 3     | 0     | 0     | 10               |
| 2      | 1     | 1     | 0     | 25               |
| 3      | 1     | 0     | 1     | 20               |
| 4      | 0     | 2     | 0     | 10               |
| 5      | 0     | 1     | 1     | 5                |
| 6      | 0     | 0     | 2     | 0                |

## Variables de decisión

$x_j$ = número de rollos de 100 cm cortados con el patrón j (j = 1, ..., 6)

- $x_1$ = número de rollos cortador según el esquema 1
- $x_2$ = número de rollos cortador según el esquema 2
- $x_3$ = número de rollos cortador según el esquema 3
- $x_4$ = número de rollos cortador según el esquema 4
- $x_5$ = número de rollos cortador según el esquema 5
- $x_6$ = número de rollos cortador según el esquema 6

## Función objetivo

min $Z = 10x_1 + 25x_2 + 20x_3 + 10x_4 + 5x_5$

## Restricciones

**Demanda de rollos de 30 cm (800):**
- $3x_1 + x_2 + x_3 \geq 800$

**Demanda de rollos de 45 cm (500):**
- $x_2 + 2x_4 + x_5 \geq 500$

**Demanda de rollos de 50 cm (1000):**
- $x_3 + x_5 + 2x_6 \geq 1000$

**No negatividad:**
- $x_j \geq 0$ ∀j = 1, ..., 6

## Tipo de modelo

Programación Lineal Entera (PLI)