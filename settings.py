import pandas as pd
units = {
    # -------------------------
    # Variables d'entrée (X)
    # -------------------------
    "Tot_PAR": "µmol/m²/s",          # Total PAR inside (5 min)
    "Tair": "°C",                    # Air temperature (5 min)
    "HumDef": "g/m³",                # Humidity deficit (option V2)
    "CO2air": "ppm",                 # CO2 concentration (option V2)

    # -------------------------
    # Variable cible (Y)
    # -------------------------
    "ProdA": "kg/m²",                # Tomato production (per harvest date)

    # -------------------------
    # Variables auxiliaires (V2)
    # -------------------------
    "Truss development time": "days",    # Time flowering → harvest
    "Cum_trusses": "trusses/stem",       # Cumulative trusses (weekly)

    # -------------------------
    # Time columns (pour contrôle)
    # -------------------------
    "Time": "timestamp"
}
df = pd.read_excel("Resume.xlsx")
dfGreenhouse = pd.read_excel("Resume.xlsx", sheet_name=0)   # 1ère feuille
dfProduction = pd.read_excel("Resume.xlsx", sheet_name=1)   # 2ème feuille
dfCropParametre = pd.read_excel("Resume.xlsx", sheet_name=2)
dfGreenhouse = dfGreenhouse.apply(pd.to_numeric, errors="coerce")
dfProduction = dfProduction.apply(pd.to_numeric, errors="coerce")
dfCropParametre = dfCropParametre.apply(pd.to_numeric, errors="coerce")

# Mettre %time en index pour permettre le merge
dfGreenhouse = dfGreenhouse.set_index("%time")
dfProduction = dfProduction.set_index("%time")
dfCropParametre = dfCropParametre.set_index("%time")

# Join des trois dataframe sur %time
df_merged = dfGreenhouse.join(dfProduction, how="outer", lsuffix="_green", rsuffix="_prod")
df_merged = df_merged.join(dfCropParametre, how="outer", rsuffix="_crop")
