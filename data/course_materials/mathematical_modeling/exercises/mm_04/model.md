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

x_j = número de rollos de 100 cm cortados con el patrón j (j = 1, ..., 6)

## Función objetivo

min Z = 10x₁ + 25x₂ + 20x₃ + 10x₄ + 5x₅ + 0x₆

## Restricciones

**Demanda de rollos de 30 cm (800):**
3x₁ + x₂ + x₃ ≥ 800

**Demanda de rollos de 45 cm (500):**
x₂ + 2x₄ + x₅ ≥ 500

**Demanda de rollos de 50 cm (1000):**
x₃ + x₅ + 2x₆ ≥ 1000

**No negatividad:**
x_j ≥ 0 ∀j

## Tipo de modelo

Programación Lineal Entera (PLI)