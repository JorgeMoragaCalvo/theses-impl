# P6 — Modelo

## Variables de decisión

x_ij = cantidad en kg de materia prima i utilizada para el producto j

Donde:
- i ∈ {a (avena), m (maíz), l (melaza)}
- j ∈ {g (gránulos), p (polvo)}

Variables específicas:
- x_ag, x_ap = kg de avena para gránulos y polvo
- x_mg, x_mp = kg de maíz para gránulos y polvo
- x_lg, x_lp = kg de melaza para gránulos y polvo

## Función objetivo

min Z = Costo materias primas + Costo molienda + Costo mezcla + Costo granulación + Costo tamizado

min Z = 0.13(x_ag + x_ap) + 0.17(x_mg + x_mp) + 0.12(x_lg + x_lp)
      + 0.25(x_ag + x_ap + x_mg + x_mp)
      + 0.05(x_ag + x_ap + x_mg + x_mp + x_lg + x_lp)
      + 0.42(x_ag + x_mg + x_lg)
      + 0.17(x_ap + x_mp + x_lp)

## Restricciones

**Satisfacción de demanda:**
- Gránulos: x_ag + x_mg + x_lg = 9000
- Polvo: x_ap + x_mp + x_lp = 12000

**Requisitos nutricionales para gránulos:**
- Proteínas: 0.136x_ag + 0.041x_mg + 0.05x_lg ≥ 0.095(x_ag + x_mg + x_lg)
- Lípidos: 0.071x_ag + 0.024x_mg + 0.003x_lg ≥ 0.02(x_ag + x_mg + x_lg)
- Fibra: 0.07x_ag + 0.037x_mg + 0.25x_lg ≤ 0.06(x_ag + x_mg + x_lg)

**Requisitos nutricionales para polvo:**
- Proteínas: 0.136x_ap + 0.041x_mp + 0.05x_lp ≥ 0.095(x_ap + x_mp + x_lp)
- Lípidos: 0.071x_ap + 0.024x_mp + 0.003x_lp ≥ 0.02(x_ap + x_mp + x_lp)
- Fibra: 0.07x_ap + 0.037x_mp + 0.25x_lp ≤ 0.06(x_ap + x_mp + x_lp)

**Disponibilidad de materias primas:**
- Avena: x_ag + x_ap ≤ 11900
- Maíz: x_mg + x_mp ≤ 23500
- Melaza: x_lg + x_lp ≤ 750

**No negatividad:**
x_ag, x_ap, x_mg, x_mp, x_lg, x_lp ≥ 0

## Tipo de modelo

Programación Lineal (PL) - Problema de Mezcla/Blending
