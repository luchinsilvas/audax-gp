import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from PIL import Image
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from io import BytesIO
import os
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

st.set_page_config(
    page_title="KPIs Top 7",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

df = st.session_state['tms']
df_matches = st.session_state['matches']

# Selecciona solo las columnas deseadas de df_matches
df_matches_filtered = df_matches[['match_id', 'match_date', 'competition', 'season', 'match_week',  'competition_stage', 'home_team', 'away_team']]

# Haz el merge (unión) por match_id, manteniendo todas las columnas de df
df = pd.merge(df, df_matches_filtered, on='match_id', how='left')
df.columns = df.columns.str.replace("^team_match_", "", regex=True)

# --- Calcular Goal Envolvement Index (GEI) ---
df["Goal Envolvement Index"] = (
    (df["xa"] + df["key_passes"] + df["assists"]) * (10 * 0.3) / 3 +
    (df["through_balls"] + df["passes_into_box"] + df["passes_inside_box"] + df["crosses_into_box"]) * (10 * 0.2) / 4 +
    df["box_cross_ratio"] * (10 * 0.05) +
    (df["sp_xa"] + df["deep_progressions"] + df["touches_inside_box"]) * (10 * 0.15) / 3 +
    (df["xgchain"] + df["xgbuildup"]) * (10 * 0.1) / 2 +
    (df["xgchain_per_possession"] + df["xgbuildup_per_possession"]) * (10 * 0.1) / 2 +
    (df["obv_pass"] + df["obv_dribble_carry"]) * (10 * 0.05) / 2 +
    df["forward_passes"] * (10 * 0.05)
) / df["minutes"]

# --- Calcular Goal Conversion Index (GCI) ---
df["Goal Conversion Index"] = (
    df["goals"] * (10 * 0.3) +
    df["np_xg"] * (10 * 0.2) +
    df["np_xg_per_shot"] * (10 * 0.2) +
    df["np_shots_on_target"] * (10 * 0.1) +
    df["shot_touch_ratio"] * (10 * 0.1) +
    df["penalties_won"] * (10 * 0.05) +
    df["obv_shot"] * (10 * 0.05)
) / df["np_shots"]

# --- Calcular Possession GoalChance Index (PGC) ---
df["Possession GoalChance Index"] = (
    (df["key_passes"] + df["assists"] + df["xa"] + df["xgchain"]) * (10 * 0.85) / 4 +
    df["touches_inside_box"] * (10 * 0.15)
) / df["possession"]

# --- Normalizar KPIs entre 0 y 9.5 ---
kpi_columns = ["Goal Envolvement Index", "Goal Conversion Index", "Possession GoalChance Index"]

# Sustituir NaN por 0.01
df[kpi_columns] = df[kpi_columns].fillna(0.01) 

# Escalar valores
scaler = MinMaxScaler(feature_range=(0.5, 9.5))
df[[col + " (norm)" for col in kpi_columns]] = scaler.fit_transform(df[kpi_columns])

# --- KPI Compuesto ponderado ---
df["GoalOpenPlay Performance Index"] = ((
    df["Goal Envolvement Index (norm)"] * 3 +
    df["Goal Conversion Index (norm)"] * 4.5 +
    df["Possession GoalChance Index (norm)"] * 2
) / (9.5)+ 3)  

# Tope de 9.7
df["GoalOpenPlay Performance Index"] = df["GoalOpenPlay Performance Index"].clip(upper=9.75)

# --- Calcular promedio por equipo (incluyendo team_id) ---
avg_kpis = df.groupby(["team_name", "team_id"])[[
    "np_xg", "np_shots", "obv_shot", "xgchain", "goals",
    "Goal Envolvement Index (norm)",
    "Goal Conversion Index (norm)",
    "Possession GoalChance Index (norm)",
    "GoalOpenPlay Performance Index"
]].mean().reset_index()

# --- Añadir columnas identificadoras de promedio ---
avg_kpis["match_id"] = "AVG"
avg_kpis["match_date"] = 2005
avg_kpis["account_id"] = 7336
avg_kpis["competition"] = "Chile - Primera División"
avg_kpis["season"] = 2005
avg_kpis["match_week"] = df['match_week'].dropna().max()  # jornada máxima jugada
avg_kpis["competition_stage"] = "Regular Season"
avg_kpis["home_team"] = "AVG"
avg_kpis["away_team"] = "AVG"


# --- Reordenar columnas para que coincidan con df original ---
avg_kpis = avg_kpis[[
    "match_id", "team_name", "team_id", "account_id", "match_date", "competition", "season", "match_week",
    "competition_stage", "home_team", "away_team", "np_xg", "np_shots", "obv_shot", "xgchain", "goals",
    "Goal Envolvement Index (norm)", "Goal Conversion Index (norm)",
    "Possession GoalChance Index (norm)", "GoalOpenPlay Performance Index"
]]

# --- Calcular promedio general (ALL_TEAMS_AVG) ---
all_teams_avg = avg_kpis[[
    "np_xg", "np_shots", "goals",
    "Goal Envolvement Index (norm)", "Goal Conversion Index (norm)",
    "Possession GoalChance Index (norm)", "GoalOpenPlay Performance Index"
]].mean()

# --- Crear fila para ALL_TEAMS_AVG ---
all_teams_avg_row = {
    "match_id": "AVG",
    "team_name": "ALL_TEAMS_AVG",
    "team_id": 1,
    "account_id": 7336,
    "match_date": 2005,
    "competition": "Chile - Primera División",
    "season": 2005 ,
    "match_week": df['match_week'].dropna().max(),
    "competition_stage": "Regular Season",
    "home_team": "AVG",
    "away_team": "AVG",
    **all_teams_avg.to_dict()
}

# --- Añadir fila de promedio general a avg_kpis ---
avg_kpis = pd.concat([avg_kpis, pd.DataFrame([all_teams_avg_row])], ignore_index=True)

# --- Concatenar el dataframe original con los promedios ---
df_final = pd.concat([df[[
    "match_id", "team_name", "team_id", "account_id", "match_date", "competition", "season", "match_week",
    "competition_stage", "home_team", "away_team", "np_xg", "np_shots", "obv_shot", "xgchain", "goals",
    "Goal Envolvement Index (norm)", "Goal Conversion Index (norm)",
    "Possession GoalChance Index (norm)", "GoalOpenPlay Performance Index"
]], avg_kpis], ignore_index=True)

# --- Crear columna 'match_score' tipo "home(goals) - away(goals)" ---
# Obtener goles por equipo por partido
goals_pivot = df.pivot_table(index="match_id", columns="team_name", values="goals", aggfunc="first")

# Obtener combinaciones únicas de partidos
df_scores = df[["match_id", "home_team", "away_team"]].drop_duplicates()

# Crear columna con formato deseado
def get_score(row):
    try:
        home_goals = goals_pivot.loc[row["match_id"], row["home_team"]]
        away_goals = goals_pivot.loc[row["match_id"], row["away_team"]]
        return f'{row["home_team"]}({int(home_goals)}) - {row["away_team"]}({int(away_goals)})'
    except:
        return None  # En caso de partidos incompletos o filas "AVG"

df_scores["match_score"] = df_scores.apply(get_score, axis=1)


# Unir con df_final
df_final = df_final.merge(df_scores[["match_id", "match_score"]], on="match_id", how="left")
# 8. Rellenar NaN
df_final = df_final.fillna({
    "match_score": "AVG"
})

#-> df_final para match report

st.session_state['df_final'] = df_final

# Goal Conversión Index:

# --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
avg_only = df_final[
    (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
].copy()

# --- Crear columna de ranking según Goal Conversion Index (norm) (descendente) ---
avg_only["Rank (avg)"] = avg_only["Goal Conversion Index (norm)"].rank(
    ascending=False, method="min"
).astype(int)

# --- Ordenar por ranking ---
ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

# --- Obtener valor máximo de jornadas jugadas ---
max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

# --- Crear columna 'match_week' con ese valor constante ---
ranking_avg["match_week"] = max_jornada

# --- Renombrar columnas (quitar '(norm)') ---
ranking_avg = ranking_avg.rename(columns={
    "GoalOpenPlay Performance Index": "GoalOpenPlay Performance Index",
    "Goal Envolvement Index (norm)": "Goal Envolvement Index",
    "Goal Conversion Index (norm)": "Goal Conversion Index",
    "Possession GoalChance Index (norm)": "Possession GoalChance Index"
})

# --- Seleccionar columnas finales ---
ranking_avg_display_GCI = ranking_avg[[
    "Rank (avg)", "team_name", "team_id", "match_week",
    "GoalOpenPlay Performance Index", 
    "Goal Envolvement Index", 
    "Goal Conversion Index", 
    "Possession GoalChance Index"
]]

# Goal Envolvment Index (gei)

# --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
avg_only = df_final[
    (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
].copy()

# --- Crear columna de ranking según Goal Performance Index (descendente) ---
avg_only["Rank (avg)"] = avg_only["Goal Envolvement Index (norm)"].rank(ascending=False, method="min").astype(int)

# --- Ordenar por ranking ---
ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

# --- Obtener valor máximo de jornadas jugadas ---
max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

# --- Crear columna 'match_week' con ese valor constante ---
ranking_avg["match_week"] = max_jornada

# --- Renombrar columnas (quitar '(norm)') ---
ranking_avg = ranking_avg.rename(columns={
    "GoalOpenPlay Performance Index": "GoalOpenPlay Performance Index",
    "Goal Envolvement Index (norm)": "Goal Envolvement Index",
    "Goal Conversion Index (norm)": "Goal Conversion Index",
    "Possession GoalChance Index (norm)": "Possession GoalChance Index"
})

# --- Seleccionar columnas finales ---
ranking_avg_display_GEI = ranking_avg[[
    "Rank (avg)", "team_name", "team_id", "match_week",
    "GoalOpenPlay Performance Index", 
    "Goal Envolvement Index", 
    "Goal Conversion Index",  
    "Possession GoalChance Index"
]]

# Possesion GoalChance Index (PGC)

# --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
avg_only = df_final[
    (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
].copy()

# --- Crear columna de ranking según Goal Performance Index (descendente) ---
avg_only["Rank (avg)"] = avg_only[ "Possession GoalChance Index (norm)"].rank(ascending=False, method="min").astype(int)

# --- Ordenar por ranking ---
ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

# --- Obtener valor máximo de jornadas jugadas ---
max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

# --- Crear columna 'match_week' con ese valor constante ---
ranking_avg["match_week"] = max_jornada

# --- Renombrar columnas (quitar '(norm)') ---
ranking_avg = ranking_avg.rename(columns={
    "GoalOpenPlay Performance Index": "GoalOpenPlay Performance Index",
    "Goal Envolvement Index (norm)": "Goal Envolvement Index",
    "Goal Conversion Index (norm)": "Goal Conversion Index",
    "Possession GoalChance Index (norm)": "Possession GoalChance Index"
})

# --- Seleccionar columnas finales ---
ranking_avg_display_PGI = ranking_avg[[
    "Rank (avg)", "team_name", "team_id", "match_week",
    "GoalOpenPlay Performance Index", 
    "Goal Envolvement Index", 
    "Goal Conversion Index",  
    "Possession GoalChance Index"
]]

# Goal Openplay Performance Index (GPI)

# --- Filtrar solo filas de promedio por equipo (excluyendo ALL_TEAMS_AVG) ---
avg_only = df_final[
    (df_final["match_id"] == "AVG") & (df_final["team_name"] != "ALL_TEAMS_AVG")
].copy()

# --- Crear columna de ranking según Goal Performance Index (descendente) ---
avg_only["Rank (avg)"] = avg_only["GoalOpenPlay Performance Index"].rank(ascending=False, method="min").astype(int)

# --- Ordenar por ranking ---
ranking_avg = avg_only.sort_values(by="Rank (avg)").reset_index(drop=True)

# --- Obtener valor máximo de jornadas jugadas ---
max_jornada = df_final[df_final["match_id"] != "AVG"]["match_week"].max()

# --- Crear columna 'match_week' con ese valor constante ---
ranking_avg["match_week"] = max_jornada

# --- Renombrar columnas (quitar '(norm)') ---
ranking_avg = ranking_avg.rename(columns={
    "GoalOpenPlay Performance Index": "GoalOpenPlay Performance Index",
    "Goal Envolvement Index (norm)": "Goal Envolvement Index",
    "Goal Conversion Index (norm)": "Goal Conversion Index",
    "Possession GoalChance Index (norm)": "Possession GoalChance Index"
})

# --- Seleccionar columnas finales ---
ranking_avg_display_GPI = ranking_avg[[
    "Rank (avg)", "team_name", "team_id", "match_week",
    "GoalOpenPlay Performance Index", 
    "Goal Envolvement Index", 
    "Goal Conversion Index",  
    "Possession GoalChance Index"
]]

# SetPiece Efficacy Index (SEI) Estudio Balón Parado:

df = st.session_state['tss']

def normalize_series_min_max(s, new_min=0.5, new_max=9.5):
    old_min = s.min()
    old_max = s.max()
    if old_max == old_min:
        return pd.Series(np.full_like(s, (new_min + new_max) / 2), index=s.index)
    normalized = (s - old_min) / (old_max - old_min)
    scaled = normalized * (new_max - new_min) + new_min
    return scaled

# Cálculo de eficiencias a balón parado
df['corner_shot_efficiency'] = df['team_season_shots_from_corners_pg'] / df['team_season_corners_pg']
df['corner_goal_efficiency'] = df['team_season_goals_from_corners_pg'] / df['team_season_corners_pg']
df['corner_xg_efficiency'] = df['team_season_corner_xg_pg'] / df['team_season_corners_pg']

df['free_kick_shot_efficiency'] = df['team_season_shots_from_free_kicks_pg'] / df['team_season_free_kicks_pg']
df['free_kick_goal_efficiency'] = df['team_season_goals_from_free_kicks_pg'] / df['team_season_free_kicks_pg']
df['free_kick_xg_efficiency'] = df['team_season_free_kick_xg_pg'] / df['team_season_free_kicks_pg']

df['dfk_goal_efficiency'] = df['team_season_direct_free_kick_goals_pg'] / df['team_season_direct_free_kicks_pg']
df['dfk_xg_efficiency'] = df['team_season_direct_free_kick_xg_pg'] / df['team_season_direct_free_kicks_pg']
df['direct_free_kick_shot_efficiency'] = df['team_season_shots_from_direct_free_kicks_pg'] / df['team_season_direct_free_kicks_pg']

df['throw_in_shot_efficiency'] = df['team_season_shots_from_throw_ins_pg'] / df['team_season_throw_ins_pg']
df['throw_in_goal_efficiency'] = df['team_season_goals_from_throw_ins_pg'] / df['team_season_throw_ins_pg']
df['throw_in_xg_efficiency'] = df['team_season_throw_in_xg_pg'] / df['team_season_throw_ins_pg']

# Subíndices ponderados
df['corner_subindex'] = (
    df['corner_goal_efficiency'] * 0.15 +
    df['corner_xg_efficiency'] * 0.10 +
    df['corner_shot_efficiency'] * 0.10
)

df['free_kick_subindex'] = (
    df['free_kick_goal_efficiency'] * 0.15 +
    df['free_kick_xg_efficiency'] * 0.10 +
    df['free_kick_shot_efficiency'] * 0.10
)

df['directfk_subindex'] = (
    df['dfk_goal_efficiency'] * 0.10 +
    df['dfk_xg_efficiency'] * 0.05 +
    df['direct_free_kick_shot_efficiency'] * 0.05
)

df['throw_in_subindex'] = (
    df['throw_in_goal_efficiency'] * 0.10 +
    df['throw_in_xg_efficiency'] * 0.05 +
    df['throw_in_shot_efficiency'] * 0.05
)

# Normalizar subíndices
df['corner_subindex_norm'] = normalize_series_min_max(df['corner_subindex'], 3.12, 9.75)
df['free_kick_subindex_norm'] = normalize_series_min_max(df['free_kick_subindex'], 3.12, 9.75)
df['directfk_subindex_norm'] = normalize_series_min_max(df['directfk_subindex'], 3.12, 9.75)
df['throw_in_subindex_norm'] = normalize_series_min_max(df['throw_in_subindex'], 3.15, 9.75)

# DataFrame final con columnas normalizadas
df_setpiece = df[['team_name', 'team_id',
                  'corner_subindex_norm',
                  'free_kick_subindex_norm',
                  'directfk_subindex_norm',
                  'throw_in_subindex_norm']].copy()

# Eliminar filas con NaNs
df_setpiece.dropna(inplace=True)


# KPI global de balón parado con pesos
df_setpiece['SetPiece Eficcacy Index'] = (
    df_setpiece['corner_subindex_norm'] * 0.50 +
    df_setpiece['free_kick_subindex_norm'] * 0.25 +
    df_setpiece['directfk_subindex_norm'] * 0.15 +
    df_setpiece['throw_in_subindex_norm'] * 0.10
)

# Eliminar (norm() de emcabezado)
df_setpiece.rename(columns=lambda x: x.replace('_norm', ''), inplace=True)

# GoalSetPiece Performance Index (GSPI)

# Verificar columnas
required_columns = [
    "team_season_sp_goal_ratio",
    "team_season_xg_per_sp",
    "team_season_sp_shot_ratio",
    "team_season_sp_goals_pg",
    "team_season_sp_pg",
    
]

missing = [col for col in required_columns if col not in df.columns]
if missing:
    raise ValueError(f"Faltan columnas necesarias: {missing}")

# Calcular volumen eficacia
volume_efficacy = df["team_season_sp_goals_pg"] / df["team_season_sp_pg"]

# Normalizar función
def normalize(s):
    return (s - s.min()) / (s.max() - s.min())

# Normalizar variables
goal_conversion_norm = normalize(df["team_season_sp_goal_ratio"])
xg_efficiency_norm = normalize(df["team_season_xg_per_sp"])
shot_conversion_norm = normalize(df["team_season_sp_shot_ratio"])
volume_efficacy_norm = normalize(volume_efficacy)

# Calcular KPI combinado
df["GoalSetPiece Performance Index"] = (
    0.35 * goal_conversion_norm +
    0.25 * xg_efficiency_norm +
    0.20 * shot_conversion_norm +
    0.20 * volume_efficacy_norm
)* 9.5 + 0.5

# DataFrame reducido para análisis
df_setpiece_efficiency = df[["team_name", "team_id", "GoalSetPiece Performance Index"]].copy()

df_setpiece_efficiency  = df_setpiece.merge(
    df_setpiece_efficiency.drop(columns=["team_name"]),
    on='team_id',
    how='inner'
)

df_setpiece_efficiency.sort_values("GoalSetPiece Performance Index", ascending=False)

# DATAFRAME FINAL

df_GoalKPIs = ranking_avg_display_GPI.merge(
    df_setpiece_efficiency.drop(columns=["team_name"]),
    on='team_id',
    how='inner'
)

# --- Normalizar subíndices entre 0.5 y 9.5 ---
def normalize_to_range(series, new_min=0.5, new_max=9.5):
    old_min = series.min()
    old_max = series.max()
    if old_max == old_min:
        return pd.Series([new_min] * len(series), index=series.index)
    return ((series - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min

cols_to_norm = [
    "Goal Envolvement Index",
    "Goal Conversion Index",
    "Possession GoalChance Index",
    
]
df_GoalKPIs.rename(columns={
    "corner_subindex": "corner Efficiency",
    "free_kick_subindex": "freekick Efficiency",
    "directfk_subindex": "directfk Efficiency",
    "throw_in_subindex": "throw in Efficiency"
}, inplace=True)

for col in cols_to_norm:
    df_GoalKPIs[col] = normalize_to_range(df_GoalKPIs[col], 0.500, 9.500)

# Obtener valores TOP para cada Indice (Top 7):

# Suponiendo que df_GoalKPIs es tu DataFrame original
df = df_GoalKPIs.copy()

kpis = [
    "GoalOpenPlay Performance Index", "Goal Envolvement Index",
    "Goal Conversion Index", "Possession GoalChance Index",
    "corner Efficiency", "freekick Efficiency",
    "directfk Efficiency", "throw in Efficiency",
    "SetPiece Eficcacy Index", "GoalSetPiece Performance Index"
]

# Crear DataFrame con índice y ahora columna 'team_name'
df_KPIs_TopValues = pd.DataFrame(
    {
        "team_name": ["TopValues (min)", "TopValues (max)"],
    },
    index=["TopValues (min)", "TopValues (max)"]
)

# Rellenar los valores min y max por KPI
for idx_label in ["TopValues (min)", "TopValues (max)"]:
    row = {}
    for kpi in kpis:
        top7 = df.nlargest(7, columns=kpi)[kpi]
        val = top7.min() if idx_label.endswith("(min)") else top7.max()
        row[kpi] = round(val, 3)
    df_KPIs_TopValues.loc[idx_label, kpis] = pd.Series(row)

# Asegúrate de que 'team_name' es la primera columna
df_KPIs_TopValues = df_KPIs_TopValues.reset_index(drop=True)

# Supongamos que tus DataFrames ya están creados
# df_GoalKPIs: DataFrame con los datos de los equipos
# df_KPIs_TopValues: DataFrame con filas "TopValues (min)" y "TopValues (max)"

# 1. Eliminar la columna team_id de ambos (si está presente)
if "team_id" in df_GoalKPIs.columns:
    df_GoalKPIs = df_GoalKPIs.drop(columns=["team_id"])
if "team_id" in df_KPIs_TopValues.columns:
    df_KPIs_TopValues = df_KPIs_TopValues.drop(columns=["team_id"])

# 2. Asegurar que 'Rank (avg)' y 'match_week' están en df_KPIs_TopValues
match_week_val = df_GoalKPIs["match_week"].iloc[0]
df_KPIs_TopValues["match_week"] = match_week_val
df_KPIs_TopValues["Rank (avg)"] = 0  # o cualquier valor placeholder

# 3. Reordenar columnas para que coincidan con df_GoalKPIs
cols = df_GoalKPIs.columns.tolist()
# Es importante que coincidan exactamente, de lo contrario concat() rellenará con NaN :contentReference[oaicite:1]{index=1}
df_KPIs_TopValues = df_KPIs_TopValues[cols]

# 4. Concatenar verticalmente
df_GoalKPIs_TopValues= pd.concat([df_KPIs_TopValues, df_GoalKPIs], ignore_index=True).round(2)

# CÁLCULO DE ÍNDICE GOAL PERFORMANCE TEAM INDEX:
# GP Open Play 70% y GSP PI 30%

df_GoalKPIs_TopValues["Goal Performance Team Index"] = (
    0.70* df_GoalKPIs_TopValues["GoalOpenPlay Performance Index"].astype(float) +
    0.30 * df_GoalKPIs_TopValues["GoalSetPiece Performance Index"].astype(float)
).round(3)

df["Goal Performance Team Index"] = (
    0.70 * df_GoalKPIs_TopValues["GoalOpenPlay Performance Index"] +
    0.30 * df_GoalKPIs_TopValues["GoalSetPiece Performance Index"]
).round(2)

st.session_state['gtv'] = df_GoalKPIs_TopValues

# CELDA 31 DE ARCHIVO SEVI: KPIs Metricas de Goal Performance

# Suponiendo que tienes este DataFrame ya preparado
ranking_df = st.session_state['gtv']

def add_image(img, fig, left, bottom, width, height, alpha=1.0):
    """
    Agrega una imagen (PIL) a una figura de matplotlib en coordenadas relativas a la figura.
    Parámetros:
        - img: imagen PIL (Image.open(...))
        - fig: figura matplotlib
        - left, bottom: coordenadas relativas (entre 0 y 1)
        - width, height: tamaño relativo (entre 0 y 1)
        - alpha: opacidad (entre 0 y 1)
    """
    ax_img = fig.add_axes([left, bottom, width, height], anchor='C')
    ax_img.imshow(img)
    ax_img.axis('off')
    ax_img.set_alpha(alpha)

# --- Supongo que df_GoalKPIs_TopValues ya está cargado ---

clasif = st.session_state['cce']
rank_df = clasif.loc[:,'Rank':'Equipo']
rank_df.columns = ["Rank", "team_name"]
# Crear diccionario para acceso rápido
team_rank_reference = dict(zip(rank_df["team_name"], rank_df["Rank"]))

top7_teams = [team for team, rank in team_rank_reference.items() if rank <= 7]
top7_order = {team: rank - 1 for team, rank in team_rank_reference.items() if rank <= 7}  # índice 0-6

# === RENOMBRAR COLUMNAS DE KPI ===
column_rename_map = {
    "Goal Envolvement Index (norm)": "Goal Envolvement Index",
    "Goal Conversion Index (norm)": "Goal Conversion Index",
    "Goal Performance Team Index (norm)": "Goal Performance Team Index",
    "GoalOpenPlay Performance Index (norm)": "GoalOpenPlay Performance Index",
    "Possession GoalChance Index (norm)": "Possession GoalChance Index",
    "SetPiece Eficcacy Index (norm)": "SetPiece Eficcacy Index",
    "GoalSetPiece Performance Index (norm)": "GoalSetPiece Performance Index",
}
df_GoalKPIs_TopValues.rename(columns=column_rename_map, inplace=True)

st.markdown("<h1 style='text-align: center;'>Ranking Top 7</h1>", unsafe_allow_html=True)
ai_rank = team_rank_reference["Audax Italiano"]

# === DATOS ===
ranking_df = df_GoalKPIs_TopValues.copy()
ranking_df = ranking_df[~ranking_df["team_name"].str.contains("TopValues")].copy()

# Añadir Rank real al dataframe
ranking_df["Rank"] = ranking_df["team_name"].map(team_rank_reference)

# === OPCIONES Y PALETAS ===
kpi_options = [
    "Goal Performance Team Index",
    "GoalOpenPlay Performance Index",
    "Goal Envolvement Index",
    "Goal Conversion Index",
    "Possession GoalChance Index",
    "SetPiece Eficcacy Index",
    "GoalSetPiece Performance Index"
]

kpi_descriptions = {
    "Goal Performance Team Index": "> Goal Team Performance: Rendimiento final entorno al gol",
    "GoalOpenPlay Performance Index": "> Goal OpenPlay: Rendimiento en Juego dinámico",
    "Goal Envolvement Index": "> Goal Envolvement: Participación en jugadas de gol",
    "Goal Conversion Index": "> Goal Conversion: Eficiencia de finalización",
    "Possession GoalChance Index": "> Possession GoalChance: Ocasiones con posesión",
    "SetPiece Eficcacy Index": "> SetPiece Eficcacy: Eficacia a balón parado",
    "GoalSetPiece Performance Index": "> Goal SetPiece: Rendimiento a balón parado",
}

green_colors = ["darkgreen", "limegreen", "lightgreen"]
green_cmap = LinearSegmentedColormap.from_list("custom_green", green_colors)
green_palette = green_cmap(np.linspace(0, 1, 7))

def make_red_palette(n):
    return plt.cm.Reds(np.linspace(0.3, 0.9, n))

def clean_kpi_name(name):
    return name.replace("Index", "").strip()

def add_image(img, fig, left=0, bottom=0, width=1, height=1):
    ax = fig.add_axes([left, bottom, width, height], anchor='C')
    ax.imshow(img)
    ax.axis('off')

# === GENERAR TABLA PERSONALIZADA ===
def generate_custom_table_image(df, kpi_list, team_name, badge_dir):
    df = df.copy()
    table_data = {}
    for kpi in kpi_list:
        sd = df[["team_name", kpi]].sort_values(kpi, ascending=False).reset_index(drop=True)
        table_data[kpi] = list(zip(sd[kpi], sd["team_name"]))

    rows, cols = len(df), len(kpi_list)
    fig, ax = plt.subplots(figsize=(3.5 * cols, 0.8 * rows))
    ax.set_facecolor("#0E3F5C")
    fig.patch.set_facecolor("#0E3F5C")

    for ci, kpi in enumerate(kpi_list):
        for ri, (val, team) in enumerate(table_data[kpi]):
            x, y = ci, rows - ri - 1

            # COLOREAR SOLO EL EQUIPO SELECCIONADO
            if team == team_name:
                if team in top7_order:
                    idx = top7_order[team]
                    cell_color = green_palette[idx]
                else:
                    cell_color = "darkred"
            else:
                cell_color = "#195A80"

            # DIBUJAR CELDA
            ax.add_patch(patches.Rectangle(
                (x, y), 1, 1,
                facecolor=cell_color,
                edgecolor="#0E3F5C",  # se sobreescribirá abajo si es necesario
                lw=3
            ))

            # INSERTAR ESCUDO SI CORRESPONDE
            if team == team_name:
                badge_path = os.path.join(badge_dir, f"{team}.png")
                if os.path.exists(badge_path):
                    try:
                        img = Image.open(badge_path)
                        box = OffsetImage(img, zoom=0.05)
                        ab = AnnotationBbox(box, (x + 0.135, y + 0.5), frameon=False)
                        ax.add_artist(ab)
                    except Exception as e:
                        print(f"Error loading badge for {team}: {e}")

            # VALOR DEL KPI
            ax.text(
                x + 0.5, y + 0.4, f"{val:.2f}",
                ha='center', va='bottom', fontsize=18, color='white', weight='bold',
                path_effects=[path_effects.withStroke(linewidth=3, foreground="#0E3F5C")]
            )

            # NOMBRE DEL EQUIPO + RANK
            real_rank = team_rank_reference.get(team, "-")
            team_text = f"{team} ({real_rank}º)"
            ax.text(
                x + 0.5, y + 0.35, team_text,
                ha='center', va='top', fontsize=13, color='white', weight='bold',
                path_effects=[path_effects.withStroke(linewidth=3, foreground="#0E3F5C")]
            )

    # ENCABEZADOS DE KPI
    for ci, kpi in enumerate(kpi_list):
        font_size = 17 if kpi == "Goal Performance Team Index" else 14
        color = 'aqua' if kpi == "Goal Performance Team Index" else 'white'
        ax.text(
            ci + 0.5, rows + 0.25, clean_kpi_name(kpi),
            ha='center', va='center', fontsize=font_size, color=color, weight='bold'
        )

    # BORDE NARANJA ALREDEDOR DE LA COLUMNA GOAL PERFORMANCE
    try:
        gp_index = kpi_list.index("Goal Performance Team Index")
        ax.add_patch(patches.Rectangle(
            (gp_index, 0), 1, rows, fill=False,
            edgecolor="aqua", linewidth=4
        ))
    except ValueError:
        pass  # si no está la columna, no hace nada

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows + 1)
    ax.axis('off')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf
# === GENERAR KPI BOXES ===
# === plot_team_kpi_boxes sin cambios de escudos ===
def plot_team_kpi_boxes(df, team_name):
    for kpi in kpi_options:
        df[f"Rank_{kpi}"] = df[kpi].rank(ascending=False, method='min').astype(int)

    row = df[df["team_name"] == team_name].iloc[0]
    outline_effect = [path_effects.withStroke(linewidth=2, foreground='black')]
    spacing = 6
    box_width, box_height = 5, 1

    fig, ax = plt.subplots(figsize=(20, 6), facecolor="#0E3F5C")
    ax.set_facecolor("#0E3F5C")

    red_palette = plt.cm.Reds(np.linspace(0.3, 0.9, len(df) - 7))

    # Título principal
    ax.set_title(f"{team_name} - Advanced Performance KPIs",
                 color='lightgray', fontsize=30, fontweight='bold', pad=30)

    # === Descripciones en dos columnas bajo el título ===

    left_col = list(kpi_descriptions.values())[:4]
    right_col = list(kpi_descriptions.values())[4:]

    for i, desc in enumerate(left_col):
        ax.text(-0.05, 2.6 - i * 0.2, desc, ha='left', va='center', fontsize=16, color='lightgray')
    for i, desc in enumerate(right_col):
        ax.text(spacing * len(kpi_options) / 2 + 1, 2.6 - i * 0.2, desc, ha='left', va='center', fontsize=16, color='lightgray')
                

    # Dibujar cajas KPI
     
    for i, kpi in enumerate(kpi_options):
        val = row[kpi]
        rank = row[f"Rank_{kpi}"]

        # === NUEVA LÓGICA DE COLORES SEGÚN VALOR ===
        if val >= 8.0:
            color = "darkgreen"
        elif val >= 6.0:
            color = "limegreen"
        elif val >= 4.5:
            color = "lightgreen"
        elif val >= 2.5:
            color = "salmon"
        elif val >= 1.5:
            color = "red"
        else:
            color = "darkred"
            

        x0 = i * spacing
        # Caja base
        box = patches.FancyBboxPatch((x0, 0.5), width=box_width, height=box_height,
                                    boxstyle="round,pad=0.2", edgecolor='black',
                                    linewidth=1, facecolor=color)
        ax.add_patch(box)

        # Si es KPI objetivo, borde aqua grueso
        if kpi == "Goal Performance Team Index":
            border_box = patches.FancyBboxPatch((x0, 0.5), width=box_width, height=box_height,
                                            boxstyle="round,pad=0.2", edgecolor='aqua',
                                            linewidth=4, facecolor='none')
            ax.add_patch(border_box)
            title_rank_color = 'aqua'    # texto del título y ranking
            value_color = 'white'        # valor numérico en blanco
        else:
            title_rank_color = 'white'
            value_color = 'white'

        def split_label(kpi):
            if "Goal Performance Team Index" in kpi:
                return "Goal\nPerformance"
            elif "GoalOpenPlay" in kpi:
                return "Goal\nOpenPlay"
            elif "GoalSetPiece" in kpi:
                return "Goal\nSetPiece"
            label = kpi.replace("Index", "").replace("Performance", "").strip()
            parts = label.split(" ", 1)
            return "\n".join(parts) if len(parts) == 2 else label

        ax.text(x0 + box_width / 2, 1.3, split_label(kpi), ha='center', va='center',
                fontsize=19, fontweight='bold', color=title_rank_color, path_effects=outline_effect)
        ax.text(x0 + box_width / 2, 0.8, f"{val:.2f}", ha='center', va='center',
                fontsize=44, fontweight='bold', color=value_color, path_effects=outline_effect)
        ax.text(x0 + box_width / 2, 0.45, f"{rank}ª pos.", ha='center', va='center',
                fontsize=20, fontweight='bold', color=title_rank_color, path_effects=outline_effect)

    ax.set_xlim(-0.4, spacing * len(kpi_options))
    ax.set_ylim(0, 3)
    ax.axis('off')
    
    # 8. Escudo central y Liga
    badge_path = f"img\Chile Primeradivision\{team_name}.png"
    liga_path = f"img\Chile Primeradivision\Liga de Primera.png"

    badge = Image.open(badge_path)
    add_image(badge, fig, left= 0.05, bottom=0.84, width=0.2, height=0.2)  # Tamaño y posición ajustada
    liga = Image.open(liga_path)
    add_image(liga, fig, left=0.77, bottom=0.82, width=0.2, height=0.2)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf

# === DASHBOARD FINAL ===
def update_dashboard(selected_kpi, selected_team):
    df_filtered = ranking_df.copy()
    badge_dir = "img\Chile Primeradivision"
    buf_table = generate_custom_table_image(df_filtered, kpi_options, selected_team, badge_dir)
    buf_kpi = plot_team_kpi_boxes(df_filtered, selected_team)

    im_table = Image.open(buf_table)
    im_kpi = Image.open(buf_kpi)

    fig, axs = plt.subplots(2, 1, figsize=(30, 18), gridspec_kw={'height_ratios': [7, 3]})
    axs[0].imshow(im_table)
    axs[0].axis('off')
    #axs[0].set_title("Tabla de Ranking Top 7", fontsize=24, color='white', pad=20)
    axs[1].imshow(im_kpi)
    axs[1].axis('off')

    fig.patch.set_facecolor("#0E3F5C")
    plt.tight_layout()
    plt.show()

    safe_team = selected_team.replace(" ", "_")
    safe_kpi = selected_kpi.replace(" ", "_").replace(":", "").replace("/", "-")
    
    return fig

col_1 = update_dashboard('Goal Performance Team Index','Audax Italiano')

st.pyplot(col_1)