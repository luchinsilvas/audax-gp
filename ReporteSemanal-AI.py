import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from sklearn.preprocessing import MinMaxScaler
import os
from PIL import Image
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import matplotlib.colors as mcolors
import matplotlib.cm as cm

from statsbombpy import sb

# Importar funciones de gráficos de radar
#from radar_charts import display_team_radar

# Importar páginas adicionales
#import goal_performance
#import goal_performance_comparison
#import goal_performance_ranking
#import generate_csv_files
#import documentacion_kpis

# Configuración de la página
st.set_page_config(
    page_title="AUDAX GoalKPIs",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    try:
        ## Código para Home - Clasificación

        # CREDENCIALES DE API

        SB_USERNAME ="plataforma@audaxitaliano.cl"
        SB_PASSWORD ="1kC6oQjp"

        # COMPETICIÓN Y TEMPORADA

        ligacl = 103
        tempcl = 315

        creds={"user":SB_USERNAME, "passwd": SB_PASSWORD}

        from statsbombpy import sb

        # CREACION DF MATCHES
        matches = sb.matches(competition_id=103, season_id=315, creds=creds)
        # LISTA CON IDS DE TODOS LOS PARTIDOS DISPONIBLES
        ids = matches[matches['match_status'] == 'available']['match_id']

        # GENERAR DF PLAYER MATCH STATS CON ID UNICO

        player_match_stats = sb.player_match_stats(match_id = 3871964, creds=creds)

        # BUCLE PARA AGREGAR TODOS LOS PARTIDOS JUGADOS

        for id in ids:
            new_df = sb.player_match_stats(match_id = id, creds=creds)
            player_match_stats = pd.concat([player_match_stats, new_df], ignore_index=True)
            print(f'Partido {id} completado')

        # DF COMPETITIONS

        competitions = sb.competitions(creds=creds)

        # DF PLAYER SEASON STATS

        player_season_stats = sb.player_season_stats(competition_id=103, season_id=315, creds=creds)

        # DF TEAM SEASON STATS

        team_season_stats = sb.team_season_stats(competition_id=103, season_id=315, creds=creds)

        # CREACION DE DF TEAM MATCH STATS DESDE DF DE JUGADOR

        player_match_stats = player_match_stats[player_match_stats['match_id'] != 3871964]

        team_match_stats = player_match_stats.groupby(['match_id', 'team_name',
                                                    'team_id', 'account_id']).agg({'player_match_minutes':'sum',
                                                                                    'player_match_np_xg_per_shot':'sum',
                                                                                    'player_match_np_xg':'sum',
                                                                                    'player_match_np_shots':'sum',
                                                                                    'player_match_goals':'sum',
                                                                                    'player_match_xa':'sum',
                                                                                    'player_match_key_passes':'sum',
                                                                                    'player_match_np_xg':'sum',
                                                                                    'player_match_assists':'sum',
                                                                                    'player_match_through_balls':'sum',                                                                              
                                                                                    'player_match_passes_into_box':'sum',
                                                                                    'player_match_touches_inside_box':'sum',
                                                                                    'player_match_tackles':'sum',
                                                                                    'player_match_interceptions':'sum',
                                                                                    'player_match_possession':'sum',
                                                                                    'player_match_dribbles_faced':'sum',
                                                                                    'player_match_touches_inside_box':'sum',
                                                                                    'player_match_dribbles':'sum',
                                                                                    'player_match_challenge_ratio':'mean',
                                                                                    'player_match_fouls':'sum',                                                                              
                                                                                    'player_match_dispossessions':'sum',
                                                                                    'player_match_long_balls':'sum',
                                                                                    'player_match_successful_long_balls':'sum',
                                                                                    'player_match_long_ball_ratio':'mean',
                                                                                    'player_match_shots_blocked':'sum',                                                                              
                                                                                    'player_match_clearances':'sum',
                                                                                    'player_match_aerials':'sum',
                                                                                    'player_match_successful_aerials':'sum',
                                                                                    'player_match_aerial_ratio':'mean',
                                                                                    'player_match_passes':'sum',                                                                              
                                                                                    'player_match_successful_passes':'sum',
                                                                                    'player_match_passing_ratio':'mean',
                                                                                    'player_match_op_passes':'sum',
                                                                                    'player_match_forward_passes':'sum',
                                                                                    'player_match_backward_passes':'sum',                                                                              
                                                                                    'player_match_sideways_passes':'sum',
                                                                                    'player_match_op_f3_passes':'sum',
                                                                                    'player_match_op_f3_forward_passes':'sum',
                                                                                    'player_match_op_f3_backward_passes':'sum',
                                                                                    'player_match_op_f3_sideways_passes':'sum',                                                                              
                                                                                    'player_match_np_shots_on_target':'sum',
                                                                                    'player_match_crosses':'sum',
                                                                                    'player_match_successful_crosses':'sum',
                                                                                    'player_match_crossing_ratio':'mean',
                                                                                    'player_match_penalties_won':'sum',                                                                              
                                                                                    'player_match_passes_inside_box':'sum',
                                                                                    'player_match_op_xa':'sum',
                                                                                    'player_match_op_assists':'sum',
                                                                                    'player_match_pressured_long_balls':'sum',
                                                                                    'player_match_unpressured_long_balls':'sum',                                                                              
                                                                                    'player_match_aggressive_actions':'sum',
                                                                                    'player_match_turnovers':'sum',
                                                                                    'player_match_crosses_into_box':'sum',
                                                                                    'player_match_sp_xa':'sum',
                                                                                    'player_match_op_shots':'sum',                                                                              
                                                                                    'player_match_touches':'sum',
                                                                                    'player_match_pressure_regains':'sum',
                                                                                    'player_match_box_cross_ratio':'mean',
                                                                                    'player_match_deep_progressions':'sum',
                                                                                    'player_match_shot_touch_ratio':'mean',                                                                              
                                                                                    'player_match_fouls_won':'sum',
                                                                                    'player_match_xgchain':'sum',
                                                                                    'player_match_op_xgchain':'sum',
                                                                                    'player_match_xgbuildup':'sum',
                                                                                    'player_match_op_xgbuildup':'sum',                                                                              
                                                                                    'player_match_xgchain_per_possession':'sum',
                                                                                    'player_match_op_xgchain_per_possession':'sum',
                                                                                    'player_match_xgbuildup_per_possession':'sum',
                                                                                    'player_match_op_xgbuildup_per_possession':'sum',
                                                                                    'player_match_pressures':'sum',                                                                              
                                                                                    'player_match_pressure_duration_total':'sum',
                                                                                    'player_match_pressure_duration_avg':'sum',
                                                                                    'player_match_pressured_action_fails':'sum',
                                                                                    'player_match_counterpressures':'sum',
                                                                                    'player_match_counterpressure_duration_total':'sum',                                                                              
                                                                                    'player_match_counterpressure_duration_avg':'sum',
                                                                                    'player_match_counterpressured_action_fails':'sum',
                                                                                    'player_match_obv':'sum',
                                                                                    'player_match_obv_pass':'sum',
                                                                                    'player_match_obv_shot':'sum',                                                                              
                                                                                    'player_match_obv_defensive_action':'sum',
                                                                                    'player_match_obv_dribble_carry':'sum',
                                                                                    'player_match_obv_gk':'sum',
                                                                                    'player_match_deep_completions':'sum',
                                                                                    'player_match_ball_recoveries':'sum',                                                                              
                                                                                    'player_match_np_psxg':'sum',
                                                                                    'player_match_penalties_faced':'sum',
                                                                                    'player_match_penalties_conceded':'sum',
                                                                                    'player_match_fhalf_ball_recoveries':'sum'})

        team_match_stats.reset_index(inplace=True)

        team_match_stats.rename(columns={'player_match_minutes':'team_match_minutes', 
                                        'player_match_np_xg_per_shot':'team_match_np_xg_per_shot',
                                        'player_match_np_xg':'team_match_np_xg',
                                        'player_match_np_shots':'team_match_np_shots',
                                        'player_match_goals':'team_match_goals',
                                        'player_match_xa':'team_match_xa',
                                        'player_match_key_passes':'team_match_key_passes',
                                        'player_match_np_xg':'team_match_np_xg',
                                        'player_match_assists':'team_match_assists',
                                        'player_match_through_balls':'team_match_through_balls',        
                                        'player_match_passes_into_box':'team_match_passes_into_box',
                                        'player_match_touches_inside_box':'team_match_touches_inside_box',
                                        'player_match_tackles':'team_match_tackles',
                                        'player_match_interceptions':'team_match_interceptions',
                                        'player_match_possession':'team_match_possession',
                                        'player_match_dribbles_faced':'team_match_dribbles_faced',
                                        'player_match_touches_inside_box':'team_match_touches_inside_box',
                                        'player_match_dribbles':'team_match_dribbles',
                                        'player_match_challenge_ratio':'team_match_challenge_ratio',
                                        'player_match_fouls':'team_match_fouls',                 
                                        'player_match_dispossessions':'team_match_dispossessions',
                                        'player_match_long_balls':'team_match_long_balls',
                                        'player_match_successful_long_balls':'team_match_successful_long_balls',
                                        'player_match_long_ball_ratio':'team_match_long_ball_ratio',
                                        'player_match_shots_blocked':'team_match_shots_blocked',         
                                        'player_match_clearances':'team_match_clearances',
                                        'player_match_aerials':'team_match_aerials',
                                        'player_match_successful_aerials':'team_match_successful_aerials',
                                        'player_match_aerial_ratio':'team_match_aerial_ratio',
                                        'player_match_passes':'team_match_passes',                
                                        'player_match_successful_passes':'team_match_successful_passes',
                                        'player_match_passing_ratio':'team_match_passing_ratio',
                                        'player_match_op_passes':'team_match_op_passes',
                                        'player_match_forward_passes':'team_match_forward_passes',
                                        'player_match_backward_passes':'team_match_backward_passes',      
                                        'player_match_sideways_passes':'team_match_sideways_passes',
                                        'player_match_op_f3_passes':'team_match_op_f3_passes',
                                        'player_match_op_f3_forward_passes':'team_match_op_f3_forward_passes',
                                        'player_match_op_f3_backward_passes':'team_match_op_f3_backward_passes',
                                        'player_match_op_f3_sideways_passes':'team_match_op_f3_sideways_passes', 
                                        'player_match_np_shots_on_target':'team_match_np_shots_on_target',
                                        'player_match_crosses':'team_match_crosses',
                                        'player_match_successful_crosses':'team_match_successful_crosses',
                                        'player_match_crossing_ratio':'team_match_crossing_ratio',
                                        'player_match_penalties_won':'team_match_penalties_won',       
                                        'player_match_passes_inside_box':'team_match_passes_inside_box',
                                        'player_match_op_xa':'team_match_op_xa',
                                        'player_match_op_assists':'team_match_op_assists',
                                        'player_match_pressured_long_balls':'team_match_pressured_long_balls',
                                        'player_match_unpressured_long_balls':'team_match_unpressured_long_balls',
                                        'player_match_aggressive_actions':'team_match_aggressive_actions',
                                        'player_match_turnovers':'team_match_turnovers',
                                        'player_match_crosses_into_box':'team_match_crosses_into_box',
                                        'player_match_sp_xa':'team_match_sp_xa',
                                        'player_match_op_shots':'team_match_op_shots',             
                                        'player_match_touches':'team_match_touches',
                                        'player_match_pressure_regains':'team_match_pressure_regains',
                                        'player_match_box_cross_ratio':'team_match_box_cross_ratio',
                                        'player_match_deep_progressions':'team_match_deep_progressions',
                                        'player_match_shot_touch_ratio':'team_match_shot_touch_ratio',    
                                        'player_match_fouls_won':'team_match_fouls_won',
                                        'player_match_xgchain':'team_match_xgchain',
                                        'player_match_op_xgchain':'team_match_op_xgchain',
                                        'player_match_xgbuildup':'team_match_xgbuildup',
                                        'player_match_op_xgbuildup':'team_match_op_xgbuildup',          
                                        'player_match_xgchain_per_possession':'team_match_xgchain_per_possession',
                                        'player_match_op_xgchain_per_possession':'team_match_op_xgchain_per_possession',
                                        'player_match_xgbuildup_per_possession':'team_match_xgbuildup_per_possession',
                                        'player_match_op_xgbuildup_per_possession':'team_match_op_xgbuildup_per_possession',
                                        'player_match_pressures':'team_match_pressures',             
                                        'player_match_pressure_duration_total':'team_match_pressure_duration_total',
                                        'player_match_pressure_duration_avg':'team_match_pressure_duration_avg',
                                        'player_match_pressured_action_fails':'team_match_pressured_action_fails',
                                        'player_match_counterpressures':'team_match_counterpressures',
                                        'player_match_counterpressure_duration_total':'team_match_counterpressure_duration_total',
                                        'player_match_counterpressure_duration_avg':'team_match_counterpressure_duration_avg',
                                        'player_match_counterpressured_action_fails':'team_match_counterpressured_action_fails',
                                        'player_match_obv':'team_match_obv',
                                        'player_match_obv_pass':'team_match_obv_pass',
                                        'player_match_obv_shot':'team_match_obv_shot',              
                                        'player_match_obv_defensive_action':'team_match_obv_defensive_action',
                                        'player_match_obv_dribble_carry':'team_match_obv_dribble_carry',
                                        'player_match_obv_gk':'team_match_obv_gk',
                                        'player_match_deep_completions':'team_match_deep_completions',
                                        'player_match_ball_recoveries':'team_match_ball_recoveries',       
                                        'player_match_np_psxg':'team_match_np_psxg',
                                        'player_match_penalties_faced':'team_match_penalties_faced',
                                        'player_match_penalties_conceded':'team_match_penalties_conceded',
                                        'player_match_fhalf_ball_recoveries':'team_match_fhalf_ball_recoveries'},
                                inplace = True)

        # Luego modifica tus líneas de código así:
        #team_season_stats.to_excel('sb_team_season_stats_2025.xlsx', index=False)
        #team_match_stats.to_excel('/Users/sevi/Documents/Documentos - MacBook Pro de Miguel/AUDAX/sb_team_match_stats_2025.xlsx', index=False)
        #matches.to_excel('/Users/sevi/Documents/Documentos - MacBook Pro de Miguel/AUDAX/sb_matches_2025.xlsx', index=False)
        #player_match_stats.to_excel('/Users/sevi/Documents/Documentos - MacBook Pro de Miguel/AUDAX/sb_player_match_stats_2025.xlsx', index=False)
        #player_season_stats.to_excel('/Users/sevi/Documents/Documentos - MacBook Pro de Miguel/AUDAX/sb_player_season_stats_2025.xlsx', index=False)
        return matches , team_match_stats , team_season_stats
    except Exception as e:
            st.error(f"Error al cargar los datos: {e}")
            return None, None

matches , team_match_stats , team_season_stats = load_data()

st.session_state['tms'] = team_match_stats
st.session_state['matches'] = matches
st.session_state['tss'] = team_season_stats

# Creación de clasificación

# 2. Filtrar solo partidos completados
matches_jugados = matches[
        (matches['match_status'] == 'available') &
        (matches['collection_status'] == 'Complete') 
        
    ]

# 3. Inicializar diccionario para estadísticas por equipo
clasificacion = {}

def actualizar_equipo(equipo, gf, gc):
    if equipo not in clasificacion:
        clasificacion[equipo] = {
            'PJ': 0, 'V': 0, 'E': 0, 'D': 0,
            'GF': 0, 'GC': 0, 'DG': 0, 'Pts': 0
        }

    e = clasificacion[equipo]
    e['PJ'] += 1
    e['GF'] += gf
    e['GC'] += gc
    e['DG'] = e['GF'] - e['GC']

    if gf > gc:
        e['V'] += 1
        e['Pts'] += 3
    elif gf == gc:
        e['E'] += 1
        e['Pts'] += 1
    else:
        e['D'] += 1

# 4. Procesar cada partido
for _, row in matches_jugados.iterrows():
    home_team = row['home_team']
    away_team = row['away_team']
    home_score = row['home_score']
    away_score = row['away_score']

    actualizar_equipo(home_team, home_score, away_score)
    actualizar_equipo(away_team, away_score, home_score)

# 5. Convertir a DataFrame y ordenar por Pts + DG
clasif_df = pd.DataFrame.from_dict(clasificacion, orient='index').reset_index()
clasif_df.columns = ['Equipo', 'PJ', 'V', 'E', 'D', 'GF', 'GC', 'DG', 'Pts']

# 6. Añadir métricas adicionales
clasif_df['PPG'] = (clasif_df['Pts'] / clasif_df['PJ']).round(2)  # Promedio puntos por partido
clasif_df['GFPM'] = (clasif_df['GF'] / clasif_df['PJ']).round(2)  # Goles a favor por partido
clasif_df['GCPM'] = (clasif_df['GC'] / clasif_df['PJ']).round(2)   # Goles en contra por partido

# 7. Calcular RANK
clasif_df = clasif_df.sort_values(by=['Pts', 'DG'], ascending=False).reset_index(drop=True)
clasif_df['Rank'] = clasif_df.index + 1  # Posición actual

# 8. Agregar columna TOP_7 con valores 'TOP_7' o 'No_TOP_7'
clasif_df['TOP_7'] = clasif_df['Rank'].apply(lambda x: 'TOP_7' if x <= 7 else 'No_TOP_7')

# 9. Reordenar columnas finales
cols = ['Rank', 'Equipo', 'TOP_7', 'PJ', 'V', 'E', 'D', 'GF', 'GC', 'DG', 'Pts']
clasif_df = clasif_df[cols]
clasif_df['GF'] = clasif_df['GF'].astype(int)
clasif_df['GC'] = clasif_df['GC'].astype(int)
clasif_df['DG'] = clasif_df['DG'].astype(int)

st.session_state['cce'] = clasif_df

def highlight_row_condition(row):
    """
    Highlights rows where the 'Value' column is greater than 50.
    """
    if row['Equipo'] == "Audax Italiano":
        return ['background-color: lightblue;color: black'] * len(row)
    else:
        return ['background-color: #0E3F5C'] * len(row) # No special styling for other rows

 # Define a function to apply background color
def set_background_color(val):
  return 'background-color: #0050a0' # Replace 'lightblue' with your desired color
# Apply the style to the DataFrame

styled_df = clasif_df.style.apply(highlight_row_condition, axis=1)

#styled_df = clasif_df.style \
#    .set_table_styles(
#        [{'selector': 'th', 'props': [('background-color', "#02181F")]}]
#    ) \
#    .apply(highlight_row_condition, axis=1)

#styled_df_clasif = styled_df.applymap(set_background_color)

st.markdown("<h1 style='text-align: center;'>Clasificación</h1>", unsafe_allow_html=True)
st.dataframe(styled_df, hide_index=True, height = 598)