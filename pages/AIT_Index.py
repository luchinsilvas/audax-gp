
import pandas as pd
import numpy as np
from statsbombpy import sb
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import date

def wide_space_default():
    st.set_page_config(layout="wide")

wide_space_default()

# Funciones comunes
#from functions import *

# ------------------------
# TITULOS
# ------------------------
st.title("🔎 Análisis de Afinidad - Liga de Primera 2025")
st.write('Selecciona un jugador para analizar, en qué posición será analizado y un jugador para compararlo')
st.divider()

# ------------------------
# LECTURA DE DATOS
# ------------------------

# CREDENCIALES DE API

SB_USERNAME ="plataforma@audaxitaliano.cl"
SB_PASSWORD ="1kC6oQjp"

creds={"user":SB_USERNAME, "passwd": SB_PASSWORD}

# DF de estadisticas de la temporda por Jugador, para la competición elegida

player_season_stats = sb.player_season_stats(competition_id=103, season_id=315, creds=creds)
player_season_stats = player_season_stats[player_season_stats["primary_position"] != 'Goalkeeper']
player_season_stats["birth_date"] = pd.to_datetime(player_season_stats["birth_date"], errors='coerce')
player_season_stats["player_weight"] = player_season_stats["player_weight"].fillna(0)
player_season_stats["player_height"] = player_season_stats["player_height"].fillna(0)
player_season_stats["secondary_position"] = player_season_stats["secondary_position"].fillna(' ')


players_ai = player_season_stats[player_season_stats.team_name == "Audax Italiano"]
# ------------------------
# GENERACION DE FILTROS
## 1. Selección de Jugador (variable player_name)
# ------------------------

flt_1 , flt_2 , flt_3 = st.columns(3)

st.markdown(
    """
    <style>
    /* Change background color of the selected option */
    div[data-baseweb="select"] > div {
        background-color: #0E3F5C;
        border-color: 0050a0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with flt_1:
    ply_selected = st.selectbox(
        "Selecciona el jugador a analizar",
        player_season_stats["player_name"].unique().tolist(),
        index=0,
        placeholder="Selecciona un jugador",
        accept_new_options=True,
    )

    st.write("You selected:", ply_selected)

ply_full = player_season_stats[player_season_stats.player_name == ply_selected]



plyppos = ply_full["primary_position"].unique()[0]
plyspos = ply_full["secondary_position"].unique()[0]

pos_options = [plyppos,plyspos]

with flt_2:
    pos_selected = st.selectbox(
        "Selecciona la posición para analizar",
        pos_options,
        index=0,
        placeholder="Selecciona una posición",
        accept_new_options=True,
    )

    st.write("You selected:", pos_selected)

pos_full = pos_selected

players_ai_pos = players_ai[(players_ai['primary_position'] == pos_full) | (players_ai['secondary_position'] == pos_full)]
prof = players_ai_pos["player_name"].unique().tolist()

with flt_3:

    prof_selected = st.selectbox(
        "Selecciona el jugador para comparar",
        prof,
        index=0,
        placeholder="Selecciona un jugador",
        accept_new_options=True,
    )

    st.write("You selected:", prof_selected)

prof_full = players_ai_pos[players_ai_pos.player_name == prof_selected]


# 3.5 Mostrar dataframe con los datos generales del jugador seleecionado:

cont_name = ply_full["player_name"].tolist()[0]
cont_team = ply_full["team_name"].tolist()[0]
cont_pripos = ply_full["primary_position"].tolist()[0]
cont_secpos = ply_full["secondary_position"].tolist()[0]
cont_liga = "Primera División Chile 2025"

cont_peso = round(ply_full["player_weight"].tolist()[0])
delta_peso = round(cont_peso - player_season_stats["player_weight"].mean())

cont_altura = round(ply_full["player_height"].tolist()[0])
delta_altura = round(cont_altura - player_season_stats["player_height"].mean())

cont_minutos = round(ply_full["player_season_minutes"].tolist()[0])
delta_minutos = round(cont_minutos - player_season_stats["player_season_minutes"].max())

cont_partidos = ply_full["player_season_appearances"].tolist()[0]
delta_partidos = round(cont_partidos - player_season_stats["player_season_appearances"].max())

cont_otro = ply_full["player_season_starting_appearances"].tolist()[0]
delta_otro = round(cont_otro - player_season_stats["player_season_appearances"].max())

cont_birth = ply_full["birth_date"].tolist()[0]

def calculo_edad(nacimiento):
    hoy = date.today()
    try:
        #nacimiento = date.fromisoformat(nacimiento)
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        return edad
    except ValueError:
        return "Formato de fecha no válido"
    
player_season_stats["player_age"] = player_season_stats["birth_date"].apply(calculo_edad)
avg_edad = player_season_stats['player_age'].mean()

cont_edad = calculo_edad(cont_birth)
delta_edad = round((cont_edad - avg_edad) , ndigits=2) 

css_c1 = """
.st-key-container1 {
    background-color: #0E3F5C;
    color: #black;
    border-width: 1px;
}
"""

st.html(f"<style>{css_c1}</style>")


cont_1 = st.container(border=True , height=260 , key="container1")

with cont_1:
    ra , rc = st.columns(2 , gap=None , vertical_alignment='top')


    with ra:
        
        tile = st.container(height='content' , border=False , horizontal=False, gap="small") 
        with tile:
            st.markdown("""
                        <style>
                        .custom-title {
                            font-size: 25px !important; /* Adjust the size as needed */
                            font-weight: bold; /* Optional: for bold text */
                            color: #FFFFF; /* Optional: for custom color */
                        }
                        </style>
                        """, unsafe_allow_html=True)
            #html_title = f"<h1>{cont_name}</h1>"
            html_title = '<p class="custom-title">'+cont_name+'</p>'
            st.markdown(html_title, unsafe_allow_html=True)
            st.markdown(cont_team)
            st.markdown('Posiciones: '+ cont_pripos+' - '+cont_secpos)
            st.markdown(cont_liga)

    with rc:
        cont_rc = st.container(horizontal=True)
        with cont_rc:
            st.metric(label="Edad",value=cont_edad,delta=delta_edad , delta_color="inverse")
            if cont_peso != 0:
                st.metric(label="Peso (kg)",value=cont_peso , delta=delta_peso , delta_color="inverse")
            else:
                st.markdown('Peso no encontrado')
            if cont_altura != 0:
                st.metric(label="Altura (cm)",value=cont_altura , delta=delta_altura)
            else:
                st.markdown('Altura no encontrada')
        cont_rc2 = st.container(horizontal=True)
        with cont_rc2:
            st.metric(label="Partidos",value=cont_partidos , delta=delta_partidos , delta_color="off")
            st.metric(label="Titular", value= cont_otro , delta=delta_otro , delta_color="off")
            st.metric(label="Min. Jugados", value= cont_minutos , delta=delta_minutos , delta_color="off")



       

# 4. Selección de métricas

# Con la posición seleccionada, creamos un array con las métricas a considerar:

secc_by_pos = {
    'Right Centre Back': ['CB_Fisico','CB_Defensa','CB_Pase'], 
    'Left Centre Back': ['CB_Fisico','CB_Defensa','CB_Pase'], 
    'Centre Back': ['CB_Fisico','CB_Defensa','CB_Pase'], 
    'Left Back': ['FB_Defensa','FB_Pase','FB_Ofensiva'], 
    'Right Back': ['FB_Defensa','FB_Pase','FB_Ofensiva'], 
    'Left Wing Back': ['WB_Defensa','WB_Pase','WB_Ofensiva'],
    'Right Wing Back': ['WB_Defensa','WB_Pase','WB_Ofensiva'], 
    'Left Defensive Midfielder': ['DM_Defensa','DM_Pase','DM_Ofensiva'], 
    'Centre Defensive Midfielder': ['DM_Defensa','DM_Pase','DM_Ofensiva'], 
    'Right Defensive Midfielder': ['DM_Defensa','DM_Pase','DM_Ofensiva'], 
    'Left Midfielder': ['OM_Tiros','OM_Generación','OM_Exterior'],
    'Right Midfielder': ['OM_Tiros','OM_Generación','OM_Exterior'],
    'Left Centre Midfielder': ['CM_Defensa','CM_Pase','CM_Ofensiva'], 
    'Right Centre Midfielder': ['CM_Defensa','CM_Pase','CM_Ofensiva'], 
    'Centre Attacking Midfielder': ['AM_Tiros','AM_Generación','AM_Progresión'], 
    'Left Wing': ['WI_Tiros','WI_Generación','WI_Exterior'], 
    'Right Wing': ['WI_Tiros','WI_Generación','WI_Exterior'], 
    'Left Centre Forward': ['CF_Generación','CF_Tiros','CF_Completitud'], 
    'Centre Forward': ['CF_Generación','CF_Tiros','CF_Completitud'], 
    'Right Centre Forward': ['CF_Generación','CF_Tiros','CF_Completitud'] 
    }

det_by_secc = {
    'CB_Fisico': "**Físico:** Métricas físicas y de desempeño aéreo.",
    'CB_Defensa': "**Defensa:** Métricas de acciones defensivas.",
    'CB_Pase': "**Pase:** Métricas de pases, salida y progresión.",
    'FB_Defensa': "**Defensa:** Métricas de acciones defensivas.",
    'FB_Pase': "**Pase:** Métricas de pases.",
    'FB_Ofensiva': "**Ofensiva:** Métricas de tiros y generación de acciones de gol.",
    'WB_Defensa': "**Defensa:** Métricas de acciones defensivas.",
    'WB_Pase': "**Pase:** Métricas de pases.",
    'WB_Ofensiva': "**Ofensiva:** Métricas de tiros y generación de acciones de gol.",
    'OM_Tiros': "**Tiros:** Métricas de tiros, precisión, goles y xG.",
    'OM_Generación': "**Generación:** Métricas de pases y de generación de acciones de gol.",
    'OM_Exterior': "**Exterior:** Métricas de acciones por banda: centros, dribbles, etc.",
    'WI_Tiros': "**Tiros:** Métricas de tiros, precisión, goles y xG.",
    'WI_Generación': "**Generación:** Métricas de pases y de generación de acciones de gol.",
    'WI_Exterior': "**Exterior:** Métricas de acciones por banda: centros, dribbles, etc.",
    'CF_Generación': "**Generación:** Métricas de generación de acciones de gol",
    'CF_Tiros': "**Tiros:** Métricas de tiros, precisión, goles y xG.",
    'CF_Completitud': "**Completitud:** Métricas variadas, juego aéreo, dribble, etc.",
    'AM_Tiros': "**Tiros:** Métricas de tiros y goles.",
    'AM_Generación': "**Generación:** Métricas de generación de acciones de gol.",
    'AM_Progresión': "**Progresión:** Métricas de pases y salida de juego.",
    'DM_Defensa': "**Defensa:** Métricas de acciones defensivas.",
    'DM_Pase': "**Pase:** Métricas de pases.",
    'DM_Ofensiva': "**Ofensiva:** Métricas de tiros y generación de acciones de gol.",
    'CM_Defensa': "**Defensa:** Métricas de acciones defensivas.",
    'CM_Pase': "**Pase:** Métricas de pases.",
    'CM_Ofensiva': "**Ofensiva:** Métricas de tiros y generación de acciones de gol."
    }

nicename_by_sec = {
    'CB_Fisico': "Físico",
    'CB_Defensa': "Defensa",
    'CB_Pase': "Pase",
    'FB_Defensa': "Defensa",
    'FB_Pase': "Pase",
    'FB_Ofensiva': "Ofensiva",
    'WB_Defensa': "Defensa",
    'WB_Pase': "Pase",
    'WB_Ofensiva': "Ofensiva",
    'DM_Defensa': "Defensa",
    'DM_Pase': "Pase",
    'DM_Ofensiva': "Ofensiva",
    'OM_Tiros': "Tiros",
    'OM_Generación': "Generación",
    'OM_Exterior': "Exterior",
    'CM_Defensa': "Defensa",
    'CM_Pase': "Pase",
    'CM_Ofensiva': "Ofensiva",
    'AM_Tiros': "Tiros",
    'AM_Progresión': "Progresión",
    'AM_Generación': "Generación",
    'WI_Tiros': "Tiros",
    'WI_Generación': "Generación",
    'WI_Exterior': "Exterior",
    'CF_Generación': "Generación",
    'CF_Tiros': "Tiros",
    'CF_Completitud': "Completitud"
}

met_by_secc = {
    'CB_Fisico': ['player_height','player_season_aerial_ratio','player_season_aerial_wins_90'],
    'CB_Defensa': ['player_season_padj_tackles_90','player_season_padj_interceptions_90','player_season_dribbled_past_90','player_season_fouls_90','player_season_blocks_per_shot','player_season_ball_recoveries_90','player_season_defensive_actions_90'],
    'CB_Pase': ['player_season_obv_pass_90','player_season_forward_pass_proportion','player_season_pressured_passing_ratio','player_season_obv_dribble_carry_90','player_season_through_balls_90','player_season_op_passes_90','player_season_op_xgbuildup_90'],
    'FB_Defensa': ['player_season_padj_tackles_90','player_season_padj_interceptions_90','player_season_dribbled_past_90','player_season_fouls_90','player_season_blocks_per_shot','player_season_ball_recoveries_90','player_season_defensive_actions_90'],
    'FB_Pase': ['player_season_passes_into_box_90','player_season_op_passes_into_box_90','player_season_assists_90','player_season_op_assists_90','player_season_shots_key_passes_90','player_season_deep_completions_90','player_season_op_f3_passes_90'],
    'FB_Ofensiva':['player_season_crosses_90','player_season_crossing_ratio','player_season_deep_progressions_90','player_season_np_xg_90','player_season_np_shots_90','player_season_total_dribbles_90','player_season_dribble_ratio','player_season_carries_90'],
    'WB_Defensa':['player_season_padj_tackles_90','player_season_padj_interceptions_90','player_season_dribbled_past_90','player_season_fouls_90','player_season_blocks_per_shot','player_season_ball_recoveries_90','player_season_defensive_actions_90'],
    'WB_Pase':['player_season_passes_into_box_90','player_season_op_passes_into_box_90','player_season_assists_90','player_season_op_assists_90','player_season_shots_key_passes_90','player_season_deep_completions_90','player_season_op_f3_passes_90'],
    'WB_Ofensiva':['player_season_crosses_90','player_season_crossing_ratio','player_season_deep_progressions_90','player_season_np_xg_90','player_season_total_dribbles_90','player_season_dribble_ratio','player_season_carries_90','player_season_np_shots_90','player_season_obv_shot_90'],
    'DM_Defensa': ['player_season_padj_tackles_90','player_season_padj_interceptions_90','player_season_dribbled_past_90','player_season_fouls_90','player_season_blocks_per_shot','player_season_ball_recoveries_90','player_season_defensive_actions_90'],
    'DM_Pase':['player_season_op_passes_90','player_season_through_balls_90','player_season_xgbuildup_90','player_season_passing_ratio','player_season_turnovers_90','player_season_forward_pass_proportion'],
    'DM_Ofensiva':['player_season_assists_90','player_season_xa_90','player_season_deep_progressions_90','player_season_key_passes_90','player_season_np_xg_90','player_season_np_shots_90'],
    'OM_Tiros':['player_season_goals_90','player_season_np_shots_90','player_season_shot_on_target_ratio','player_season_np_xg_per_shot','player_season_np_xg_90','player_season_obv_shot_90'],
    'OM_Generación':['player_season_key_passes_90','player_season_assists_90','player_season_passes_into_box_90','player_season_op_passes_into_box_90','player_season_op_xa_90','player_season_op_assists_90','player_season_deep_completions_90','player_season_op_f3_passes_90'],
    'OM_Exterior':['player_season_crosses_90','player_season_crossing_ratio','player_season_deep_progressions_90','player_season_total_dribbles_90','player_season_dribble_ratio','player_season_carries_90'],
    'CM_Defensa':['player_season_padj_tackles_90','player_season_padj_interceptions_90','player_season_dribbled_past_90','player_season_fouls_90','player_season_blocks_per_shot','player_season_ball_recoveries_90','player_season_defensive_actions_90'],
    'CM_Pase':['player_season_op_passes_90','player_season_through_balls_90','player_season_xgbuildup_90','player_season_passing_ratio','player_season_turnovers_90','player_season_forward_pass_proportion'],
    'CM_Ofensiva':['player_season_assists_90','player_season_xa_90','player_season_deep_progressions_90','player_season_key_passes_90','player_season_np_xg_90','player_season_np_shots_90'],
    'AM_Tiros':['player_season_goals_90','player_season_npg_90','player_season_shot_on_target_ratio','player_season_obv_shot_90','player_season_np_xg_90','player_season_np_shots_90'],
    'AM_Progresión':['player_season_through_balls_90','player_season_op_passes_90','player_season_forward_pass_proportion','player_season_xgbuildup_90','player_season_op_xgbuildup_90','player_season_pressured_passing_ratio'],
    'AM_Generación':['player_season_xa_90','player_season_key_passes_90','player_season_assists_90','player_season_deep_progressions_90','player_season_deep_completions_90','player_season_op_xgchain_90','player_season_xgchain_90'],
    'WI_Tiros':['player_season_goals_90','player_season_np_shots_90','player_season_shot_on_target_ratio','player_season_np_xg_per_shot','player_season_np_xg_90','player_season_obv_shot_90'],
    'WI_Generación':['player_season_key_passes_90','player_season_assists_90','player_season_passes_into_box_90','player_season_op_passes_into_box_90','player_season_op_xa_90','player_season_op_assists_90','player_season_deep_completions_90','player_season_op_f3_passes_90'],
    'WI_Exterior':['player_season_crosses_90','player_season_crossing_ratio','player_season_deep_progressions_90','player_season_total_dribbles_90','player_season_dribble_ratio','player_season_carries_90'],
    'CF_Generación':['player_season_xa_90','player_season_key_passes_90','player_season_assists_90','player_season_deep_progressions_90','player_season_deep_completions_90','player_season_op_xgchain_90','player_season_xgchain_90'],
    'CF_Tiros':['player_season_np_xg_per_shot','player_season_np_xg_90','player_season_goals_90','player_season_shot_on_target_ratio','player_season_obv_shot_90','player_season_np_shots_90'],
    'CF_Completitud':['player_height','player_season_aerial_ratio','player_season_aerial_wins_90','player_season_fouls_won_90','player_season_total_dribbles_90','player_season_dribble_ratio','player_season_padj_pressures_90']
}

met_norm_by_secc = {
    'CB_Fisico': ['player_height_norm','player_season_aerial_ratio_norm','player_season_aerial_wins_90_norm'],
    'CB_Defensa': ['player_season_padj_tackles_90_norm','player_season_padj_interceptions_90_norm','player_season_dribbled_past_90_norm','player_season_fouls_90_norm','player_season_blocks_per_shot_norm','player_season_ball_recoveries_90_norm','player_season_defensive_actions_90_norm'],
    'CB_Pase': ['player_season_obv_pass_90_norm','player_season_forward_pass_proportion_norm','player_season_pressured_passing_ratio_norm','player_season_obv_dribble_carry_90_norm','player_season_through_balls_90_norm','player_season_op_passes_90_norm','player_season_op_xgbuildup_90_norm'],
    'FB_Defensa': ['player_season_padj_tackles_90_norm','player_season_padj_interceptions_90_norm','player_season_dribbled_past_90_norm','player_season_fouls_90_norm','player_season_blocks_per_shot_norm','player_season_ball_recoveries_90_norm','player_season_defensive_actions_90_norm'],
    'FB_Pase': ['player_season_passes_into_box_90_norm','player_season_op_passes_into_box_90_norm','player_season_assists_90_norm','player_season_op_assists_90_norm','player_season_shots_key_passes_90_norm','player_season_deep_completions_90_norm','player_season_op_f3_passes_90_norm'],
    'FB_Ofensiva':['player_season_crosses_90_norm','player_season_crossing_ratio_norm','player_season_deep_progressions_90_norm','player_season_np_xg_90_norm','player_season_np_shots_90_norm','player_season_total_dribbles_90_norm','player_season_dribble_ratio_norm','player_season_carries_90_norm'],
    'WB_Defensa': ['player_season_padj_tackles_90_norm','player_season_padj_interceptions_90_norm','player_season_dribbled_past_90_norm','player_season_fouls_90_norm','player_season_blocks_per_shot_norm','player_season_ball_recoveries_90_norm','player_season_defensive_actions_90_norm'],
    'WB_Pase': ['player_season_passes_into_box_90_norm','player_season_op_passes_into_box_90_norm','player_season_assists_90_norm','player_season_op_assists_90_norm','player_season_shots_key_passes_90_norm','player_season_deep_completions_90_norm','player_season_op_f3_passes_90_norm'],
    'WB_Ofensiva':['player_season_crosses_90_norm','player_season_crossing_ratio_norm','player_season_deep_progressions_90_norm','player_season_np_xg_90_norm','player_season_total_dribbles_90_norm','player_season_dribble_ratio_norm','player_season_carries_90_norm','player_season_np_shots_90_norm','player_season_obv_shot_90_norm'],
    'DM_Defensa':['player_season_padj_tackles_90_norm','player_season_padj_interceptions_90_norm','player_season_dribbled_past_90_norm','player_season_fouls_90_norm','player_season_blocks_per_shot_norm','player_season_ball_recoveries_90_norm','player_season_defensive_actions_90_norm'],
    'DM_Pase':['player_season_op_passes_90_norm','player_season_through_balls_90_norm','player_season_xgbuildup_90_norm','player_season_passing_ratio_norm','player_season_turnovers_90_norm','player_season_forward_pass_proportion_norm'],
    'DM_Ofensiva':['player_season_assists_90_norm','player_season_xa_90_norm','player_season_deep_progressions_90_norm','player_season_key_passes_90_norm','player_season_np_xg_90_norm','player_season_np_shots_90_norm'],
    'OM_Tiros':['player_season_goals_90_norm','player_season_np_shots_90_norm','player_season_shot_on_target_ratio_norm','player_season_np_xg_per_shot_norm','player_season_np_xg_90_norm','player_season_obv_shot_90_norm'],
    'OM_Generación':['player_season_key_passes_90_norm','player_season_assists_90_norm','player_season_passes_into_box_90_norm','player_season_op_passes_into_box_90_norm','player_season_op_xa_90_norm','player_season_op_assists_90_norm','player_season_deep_completions_90_norm','player_season_op_f3_passes_90_norm'],
    'OM_Exterior':['player_season_crosses_90_norm','player_season_crossing_ratio_norm','player_season_deep_progressions_90_norm','player_season_total_dribbles_90_norm','player_season_dribble_ratio_norm','player_season_carries_90_norm'],
    'CM_Defensa':['player_season_padj_tackles_90_norm','player_season_padj_interceptions_90_norm','player_season_dribbled_past_90_norm','player_season_fouls_90_norm','player_season_blocks_per_shot_norm','player_season_ball_recoveries_90_norm','player_season_defensive_actions_90_norm'],
    'CM_Pase':['player_season_op_passes_90_norm','player_season_through_balls_90_norm','player_season_xgbuildup_90_norm','player_season_passing_ratio_norm','player_season_turnovers_90_norm','player_season_forward_pass_proportion_norm'],
    'CM_Ofensiva':['player_season_assists_90_norm','player_season_xa_90_norm','player_season_deep_progressions_90_norm','player_season_key_passes_90_norm','player_season_np_xg_90_norm','player_season_np_shots_90_norm'],
    'AM_Tiros':['player_season_goals_90_norm','player_season_npg_90_norm','player_season_shot_on_target_ratio_norm','player_season_obv_shot_90_norm','player_season_np_xg_90_norm','player_season_np_shots_90_norm'],
    'AM_Progresión':['player_season_through_balls_90_norm','player_season_op_passes_90_norm','player_season_forward_pass_proportion_norm','player_season_xgbuildup_90_norm','player_season_op_xgbuildup_90_norm','player_season_pressured_passing_ratio_norm'],
    'AM_Generación':['player_season_xa_90_norm','player_season_key_passes_90_norm','player_season_assists_90_norm','player_season_deep_progressions_90_norm','player_season_deep_completions_90_norm','player_season_op_xgchain_90_norm','player_season_xgchain_90_norm'],
    'WI_Tiros':['player_season_goals_90_norm','player_season_np_shots_90_norm','player_season_shot_on_target_ratio_norm','player_season_np_xg_per_shot_norm','player_season_np_xg_90_norm','player_season_obv_shot_90_norm'],
    'WI_Generación':['player_season_key_passes_90_norm','player_season_assists_90_norm','player_season_passes_into_box_90_norm','player_season_op_passes_into_box_90_norm','player_season_op_xa_90_norm','player_season_op_assists_90_norm','player_season_deep_completions_90_norm','player_season_op_f3_passes_90_norm'],
    'WI_Exterior':['player_season_crosses_90_norm','player_season_crossing_ratio_norm','player_season_deep_progressions_90_norm','player_season_total_dribbles_90_norm','player_season_dribble_ratio_norm','player_season_carries_90_norm'],
    'CF_Generación':['player_season_xa_90_norm','player_season_key_passes_90_norm','player_season_assists_90_norm','player_season_deep_progressions_90_norm','player_season_deep_completions_90_norm','player_season_op_xgchain_90_norm','player_season_xgchain_90_norm'],
    'CF_Tiros':['player_season_np_xg_per_shot_norm','player_season_np_xg_90_norm','player_season_goals_90_norm','player_season_shot_on_target_ratio_norm','player_season_obv_shot_90_norm','player_season_np_shots_90'],
    'CF_Completitud':['player_height_norm','player_season_aerial_ratio_norm','player_season_aerial_wins_90_norm','player_season_fouls_won_90_norm','player_season_total_dribbles_90_norm','player_season_dribble_ratio_norm','player_season_padj_pressures_90_norm']
}

sbp = secc_by_pos[pos_full]

sec_1 = sbp[0]
sec_2 = sbp[1]
sec_3 = sbp[2]


dby_1 = det_by_secc[sbp[0]]
dby_2 = det_by_secc[sbp[1]]
dby_3 = det_by_secc[sbp[2]]

mbs_1 = met_by_secc[sec_1]
mbs_2 = met_by_secc[sec_2]
mbs_3 = met_by_secc[sec_3]

mnbs_1 = met_norm_by_secc[sec_1]
mnbs_2 = met_norm_by_secc[sec_2]
mnbs_3 = met_norm_by_secc[sec_3]

nbs_1 = nicename_by_sec[sec_1] 
nbs_2 = nicename_by_sec[sec_2]
nbs_3 = nicename_by_sec[sec_3]


st.header("Resultados:")

metricas = ['player_name']

metricas = metricas + mbs_1 + mbs_2 + mbs_3

metricas_norm = mbs_1 + mbs_2 + mbs_3
met_norm = mnbs_1 + mnbs_2 + mnbs_3

# Normalizados del dataframe:

# Funciones para normalizar Valores y calcular distancia:

def normalize(col):
    return (col - col.min()) / (col.max() - col.min())

def vorp(df,cols_to_norm):
    for col_name in cols_to_norm:
        df['{}_norm'.format(col_name)] = normalize(df[col_name])
    return df

def distancia(u,v):
    dist = np.sqrt(np.sum((u - v)**2))
    return dist

if cont_pripos == 'Goalkeeper':
    players_pos = player_season_stats[(player_season_stats['primary_position'] == pos_full)] 
    st.write(players_pos)
    players_pos_short = players_pos.loc[:,metricas]
else:   
    players_pos = player_season_stats[(player_season_stats['primary_position'] == pos_full) | (player_season_stats['secondary_position'] == pos_full)] 
    players_pos_short = players_pos.loc[:,metricas]

players_pos_norm = vorp(players_pos_short,metricas_norm)



# 4. Acotado de los dataframes de cada selección:

player_short = players_pos_norm[players_pos_norm.player_name == ply_selected]
profile_short = players_pos_norm[players_pos_norm.player_name == prof_selected]


# 5. DF para radares

ply_sel_radar = players_pos_short[players_pos_short.player_name == ply_selected]
pro_sel_radar = players_pos_short[players_pos_short.player_name == prof_selected]

# Ranges para radar:

rng_by_met = {}

for columna in players_pos_short.columns:
    valores = players_pos_short[columna]
    minimo = valores.min()
    maximo = valores.max()

    rng_by_met[columna] = (minimo,maximo)

def array_rng_radar(dicc_rng,metrics):
    array = []
    for column in metrics:
        array.append(dicc_rng[column])
    return array 



df_radar = pd.concat([ply_sel_radar, pro_sel_radar], ignore_index=True)


sp_rd_s1 = np.array([getattr(ply_sel_radar, attr).tolist()[0] for attr in mbs_1])
pp_rd_s1 = np.array([getattr(pro_sel_radar, attr).tolist()[0] for attr in mbs_1])

sp_rd_s2 = np.array([getattr(ply_sel_radar, attr).tolist()[0] for attr in mbs_2])
pp_rd_s2 = np.array([getattr(pro_sel_radar, attr).tolist()[0] for attr in mbs_2])

sp_rd_s3 = np.array([getattr(ply_sel_radar, attr).tolist()[0] for attr in mbs_3])
pp_rd_s3 = np.array([getattr(pro_sel_radar, attr).tolist()[0] for attr in mbs_3])

# 6. Creación de vectores para cada jugador por sección:

sp_vector_s1 = np.array([getattr(player_short, attr).tolist()[0] for attr in mnbs_1])
sp_vector_s2 = np.array([getattr(player_short, attr).tolist()[0] for attr in mnbs_2])
sp_vector_s3 = np.array([getattr(player_short, attr).tolist()[0] for attr in mnbs_3])
sp_vector_st = np.array([getattr(player_short, attr).tolist()[0] for attr in met_norm])

pp_vector_s1 = np.array([getattr(profile_short, attr).tolist()[0] for attr in mnbs_1])
pp_vector_s2 = np.array([getattr(profile_short, attr).tolist()[0] for attr in mnbs_2])
pp_vector_s3 = np.array([getattr(profile_short, attr).tolist()[0] for attr in mnbs_3])
pp_vector_st = np.array([getattr(profile_short, attr).tolist()[0] for attr in met_norm])

# Calculamos la distancia de estos vectores:

vfunc = np.vectorize(distancia)
dist_v1 = vfunc(sp_vector_s1,pp_vector_s1)
dist_v2 = vfunc(sp_vector_s2,pp_vector_s2)
dist_v3 = vfunc(sp_vector_s3,pp_vector_s3)
dist_vt = vfunc(sp_vector_st,pp_vector_st)

# Calculamos el porc. de similitud para cada sección:

simil_perc_s1 = np.sum(np.abs(dist_v1)) / len(dist_v1)
simil_perc_s1_pc = '{percent:.2%}'.format(percent=1-simil_perc_s1)

simil_perc_s2 = np.sum(np.abs(dist_v2)) / len(dist_v2)
simil_perc_s2_pc = '{percent:.2%}'.format(percent=1-simil_perc_s2)

simil_perc_s3 = np.sum(np.abs(dist_v3)) / len(dist_v3)
simil_perc_s3_pc = '{percent:.2%}'.format(percent=1-simil_perc_s3)

simil_perc_st = np.sum(np.abs(dist_vt)) / len(dist_vt)
simil_perc_st_pc = '{percent:.2%}'.format(percent=1-simil_perc_st)

# Similitud total en base al total de metricas !

simils = [simil_perc_s1,simil_perc_s2,simil_perc_s3]
simil_perc_total = sum(simils) / len(simils)

simil_perc_total_pc = '{percent:.2%}'.format(percent=1-simil_perc_total)

st.write("Afinidad, similitud entre los jugadores, usando la distancia euclidiana:")

# TABS 

css_c2 = """
.st-key-container2 {
    background-color: #0E3F5C;
    color: black;
    border-color: #0E3F5C;
    border-width: 1px;
}
"""

st.html(f"<style>{css_c2}</style>")

cont_res = st.container(horizontal=True,border=True,key="container2")

with cont_res:

    st.metric(nbs_1,simil_perc_s1_pc)
    st.metric(nbs_2,simil_perc_s2_pc)
    st.metric(nbs_3,simil_perc_s3_pc) 
    st.metric("Affinity Percentage",simil_perc_st_pc)

# Explicación de las secciones:

st.write("Se utilizaron los siguientes aspectos para calcular la afinidad o similitud del jugador seleccionado con el perfil:")

sec_exp_1 , sec_exp_2 , sec_exp_3 = st.columns(3)

with sec_exp_1:

    st.markdown(dby_1)

    params = mbs_1
    values = [
        pp_rd_s1,
        sp_rd_s1
    ]

    ranges = array_rng_radar(rng_by_met,mbs_1)

    title = dict(
        title_name=ply_selected,
        title_color='#0652cc',
        subtitle_name=cont_team,
        subtitle_color='#0652cc',
        title_name_2=prof_selected,
        title_color_2='#009e6e',
        subtitle_name_2='Audax Italiano',
        subtitle_color_2='#009e6e',
        title_fontsize=13,
        subtitle_fontsize=11,
    )

    radar = Radar(
    )

    
    fig = plt.subplots(figsize=(5, 5))
    ## plot radar -- compare
    fig, ax = radar.plot_radar(ranges=ranges , params=params, values=values, 
                            radar_color=['#049d6b', '#0652cc'], 
                            title=title,
                            compare=True)
    
    #fig.set_facecolor('#0E3F5C')
    
    st.pyplot(fig,use_container_width=False)
        
with sec_exp_2:        

    st.markdown(dby_2)

    params_2 = mbs_2
    values_2 = [
        pp_rd_s2,
        sp_rd_s2
    ]

    ranges_2 = array_rng_radar(rng_by_met,mbs_2)

    title = dict(
        title_name=ply_selected,
        title_color='#0652cc',
        subtitle_name=cont_team,
        subtitle_color='#0652cc',
        title_name_2=prof_selected,
        title_color_2='#009e6e',
        subtitle_name_2='Audax Italiano',
        subtitle_color_2='#009e6e',
        title_fontsize=13,
        subtitle_fontsize=11,
    )

    radar_2 = Radar()

    fig_2 = plt.subplots(figsize=(5, 5))
    ## plot radar -- compare
    fig_2, ax_2 = radar_2.plot_radar(ranges=ranges_2 , params=params_2, values=values_2, 
                            radar_color=['#049d6b', '#0652cc'], 
                            title=title,
                            compare=True)
    
    st.pyplot(fig_2,use_container_width=False)


with sec_exp_3:
    st.markdown(dby_3)

    params_3 = mbs_3
    values_3 = [
        pp_rd_s3,
        sp_rd_s3
    ]

    ranges_3 = array_rng_radar(rng_by_met,mbs_3)

    title = dict(
        title_name=ply_selected,
        title_color='#0652cc',
        subtitle_name=cont_team,
        subtitle_color='#0652cc',
        title_name_2=prof_selected,
        title_color_2='#009e6e',
        subtitle_name_2='Audax Italiano',
        subtitle_color_2='#009e6e',
        title_fontsize=13,
        subtitle_fontsize=11,
    )

    radar_3 = Radar()

    fig_3 = plt.subplots(figsize=(5, 5))
    ## plot radar -- compare
    fig_3, ax_3 = radar_3.plot_radar(ranges=ranges_3 , params=params_3, values=values_3, 
                            radar_color=['#049d6b', '#0652cc'], 
                            title=title,
                            compare=True)
    
    st.pyplot(fig_3,use_container_width=False)
