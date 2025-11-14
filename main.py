import pandas as pd
from settings import *
import matplotlib.pyplot as plt

import numpy as np

def simulate_prod(params, df):
    """
    params = [RUE, p_fruit, T_base, T_opt, D]
    df     = DataFrame avec colonnes 'Tot_PAR', 'Tair'
    """
    RUE, p_fruit, T_base, T_opt, D = params
    
    T = df["Tair"].values
    PAR = df["Tot_PAR"].values

    # facteur température
    fT = (T - T_base) / (T_opt - T_base)
    fT = np.clip(fT, 0, 1)

    # biomasse produite
    S = RUE * PAR * fT

    # fraction vers fruits
    F = p_fruit * S

    # retard (en jours, entier)
    D_int = int(round(D))
    P_model = np.zeros_like(F)

    if D_int < len(F):
        P_model[D_int:] = F[:-D_int]  # P_t = F_{t-D}

    return P_model

from scipy.optimize import least_squares

def residuals(params, df):
    # production observée (remplace NaN par 0)
    Prod_obs = df["ProdA"].fillna(0).values
    
    Prod_model = simulate_prod(params, df)
    
    # residu = modèle - data
    return Prod_model - Prod_obs
# valeurs initiales
x0 = [
    0.4,   # RUE
    0.6,   # p_fruit
    5.0,   # T_base
    22.0,  # T_opt
    45.0   # D (jours)
]

# bornes (optionnel mais conseillé)
bounds = (
    [0.0, 0.0, 0.0, 10.0, 10.0],   # min
    [5.0, 1.0, 15.0, 35.0, 90.0]   # max
)
PROD_COL = "ProdA"
df_fit = df_merged.copy()
df_fit[PROD_COL] = df_fit[PROD_COL].fillna(0)

# 2) Tair : on interpole (sinon NaN -> NaN dans le modèle)
df_fit["Tair"] = df_fit["Tair"].interpolate(limit_direction="both")

# 3) Tot_PAR : on remplace NaN par 0 (pas de lumière mesurée)
df_fit["Tot_PAR"] = df_fit["Tot_PAR"].fillna(0)

# 4) On garde uniquement les lignes où Tair & Tot_PAR sont finies
mask = np.isfinite(df_fit["Tair"]) & np.isfinite(df_fit["Tot_PAR"]) & np.isfinite(df_fit[PROD_COL])
df_fit = df_fit.loc[mask].copy()
result = least_squares(residuals, x0, bounds=bounds, args=(df_fit,))

print("Succès ?", result.success)
print("Message :", result.message)

RUE_fit, p_fruit_fit, T_base_fit, T_opt_fit, D_fit = result.x
print("Paramètres ajustés :")
print(" RUE       =", RUE_fit)
print(" p_fruit   =", p_fruit_fit)
print(" T_base    =", T_base_fit)
print(" T_opt     =", T_opt_fit)
print(" D (jours) =", D_fit)


import matplotlib.pyplot as plt

Prod_obs = df_fit[PROD_COL].values
Prod_model = simulate_prod(result.x, df_fit)

plt.figure(figsize=(12, 6))
plt.plot(df_fit.index, Prod_obs, label="ProdA observée")
plt.plot(df_fit.index, Prod_model, label="ProdA modèle", linestyle="--")
plt.xlabel("Temps (index ou %time)")
plt.ylabel("Production (kg/m²/j)")
plt.title("Production de tomates : modèle dynamique à retard vs données")
plt.legend()
plt.tight_layout()
plt.show()