# P6 — Modelo

## Variables de decisión

$x_{ij}$ = cantidad en kg de materia prima $i$ utilizada para el producto $j$

Donde:
- i ∈ {a (avena), m (maíz), l (melaza)}
- j ∈ {g (gránulos), p (polvo)}

Variables específicas:
- $x_{ag}$, $x_{ap}$ = kg de avena para gránulos y polvo
- $x_{mg}$, $x_{mp}$ = kg de maíz para gránulos y polvo
- $x_{lg}$, $x_{lp}$ = kg de melaza para gránulos y polvo

## Función objetivo

$min \space Z$ = Costo materias primas + Costo molienda + Costo mezcla + Costo granulación + Costo tamizado

$min Z = 0.13(x_{ag} + x_{ap}) + 0.17(x_{mg} + x_{mp}) + 0.12(x_{lg} + x_{lp})
      + 0.25(x_{ag} + x_{ap} + x_{mg} + x_{mp})
      + 0.05(x_{ag} + x_{ap} + x_{mg} + x_{mp} + x_{lg} + x_{lp})
      + 0.42(x_{ag} + x_{mg} + x_{lg})
      + 0.17(x_{ap} + x_{mp} + x_{lp})$

## Restricciones

**Satisfacción de demanda:**
- Gránulos (alimento granulado): $x_{ag} + x_{mg} + x_{lg} \geq 9000$
- Polvo (alimento tamizado): $x_{ap} + x_{mp} + x_{lp} \geq 12000$

**Requisitos nutricionales para gránulos:**
- Proteínas: 0.136$x_{ag}$ + 0.041$x_{mg}$ + 0.05$x_{lg}$ ≥ 0.095($x_{ag}$ + $x_{mg}$ + $x_{lg}$)
- Lípidos: 0.071$x_{ag}$ + 0.024$x_{mg}$ + 0.003$x_{lg}$ ≥ 0.02($x_{ag}$ + $x_{mg}$ + $x_{lg}$)
- Fibra: 0.07$x_{ag}$ + 0.037$x_{mg}$ + 0.25$x_{lg}$ ≤ 0.06($x_{ag}$ + $x_{mg}$ + $x_{lg}$)

**Requisitos nutricionales para polvo (tamizado):**
- Proteínas: 0.136$x_{ap}$ + 0.041$x_{mp}$ + 0.05$x_{lp}$ ≥ 0.095($x_{ap}$ + $x_{mp}$ + $x_{lp}$)
- Lípidos: 0.071$x_{ap}$ + 0.024$x_{mp}$ + 0.003$x_{lp}$ ≥ 0.02($x_{ap}$ + $x_{mp}$ + $x_{lp}$)
- Fibra: 0.07$x_{ap}$ + 0.037$x_{mp}$ + 0.25$x_{lp}$ ≤ 0.06($x_{ap}$ + $x_{mp}$ + $x_{lp}$)

**Disponibilidad de materias primas:**
- Avena: $x_{ag}$ + $x_{ap}$ ≤ 11900
- Maíz: $x_{mg}$ + $x_{mp}$ ≤ 23500
- Melaza: $x_{lg}$ + $x_{lp}$ ≤ 750

**No negatividad:**
$x_{ag}$, $x_{ap}$, $x_{mg}$, $x_{mp}$, $x_{lg}$, $x_{lp}$ ≥ 0

## Tipo de modelo

Programación Lineal (PL) - Problema de Mezcla/Blending
