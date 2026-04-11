# P12 — Demanda centrales eléctricas
*Powerco* cuenta con tres centrales eléctricas para cubrir la demanda de cuatro ciudades.

La tabla indica el suministro disponible en cada planta en MWh. Las demandas de potencia *peak* de las ciudades abastecidas y los costos por enviar un MWh desde cada planta a cada ciudad.

Debido a problemas logísticos, no existen líneas de trasmisión desde la central 1 a la ciudad 3, y desde la central 2 a la ciudad 4.

Determinar la forma de **minimizar el costo** de satisfacer la demanda de potencia *peak* de todas las ciudades.

| Central \ Ciudad | 1  | 2  | 3  | 4  | Suministros |
|------------------|----|----|----|----|-------------|
| 1                | 5  | 9  | -  | 4  | 28          |
| 2                | 6  | 10 | 3  | -  | 32          |
| 3                | 4  | 2  | 5  | 7  | 60          |
| Demanda          | 48 | 29 | 40 | 33 | -           |

## Lo que se pide

- Defina variables de decisión.
- Formule función objetivo.
- Formule restricciones.
- Indique tipo de modelo.

## Pistas

- Identifique orígenes (centrales) y destinos (ciudades); las rutas prohibidas simplemente no generan variables.
- El suministro total (120 MWh) es menor que la demanda total (150 MWh): el problema es **no balanceado**. Para balancearlo, añada una central ficticia con 30 MWh de capacidad y costos cero.
- Use restricciones de suministro con $\leq$ (capacidad máxima) y de demanda con $=$ (satisfacer toda la demanda).
- Las rutas prohibidas equivalen a excluir esas variables del modelo (o fijarlas en cero).