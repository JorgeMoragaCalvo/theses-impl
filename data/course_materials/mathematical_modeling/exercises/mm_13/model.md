# P13 — Modelo

## Variables de decisión

- $r_t$ = motores ensamblados en tiempo regular durante el trimestre $t$
- $h_t$ = motores ensamblados en tiempo extra durante el trimestre $t$
- $I_t$ = inventario de motores al **final** del trimestre $t$

donde $t \in \{1, 2, 3, 4\}$, con inventario inicial $I_0 = 10$

## Función objetivo

$$\min Z = \sum_{t=1}^{4} \left( 400r_t + 450h_t + 20I_t \right)$$

## Restricciones

**Balance de inventario** (inventario final = inventario inicial + producción − demanda):
- $I_1 = 10 + r_1 + h_1 - 40$
- $I_2 = I_1 + r_2 + h_2 - 60$
- $I_3 = I_2 + r_3 + h_3 - 75$
- $I_4 = I_3 + r_4 + h_4 - 25$

**Capacidad de producción:**
- $r_t \leq 40 \quad \forall t$ (capacidad tiempo regular)
- $h_t \leq 50 \quad \forall t$ (capacidad tiempo extra)

**Demanda a tiempo** (no se permiten faltantes):
- $I_t \geq 0 \quad \forall t$

**No negatividad:**
- $r_t, h_t \geq 0 \quad \forall t$

## Tipo de modelo

Programación Lineal — Planificación de producción con inventario (PL)
