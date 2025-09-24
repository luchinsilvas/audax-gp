import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from math import pi
import os
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as path_effects
import streamlit as st
from matplotlib.lines import Line2D

df = st.session_state["df_final"]

available_teams = sorted([t for t in df["team_name"].unique() if t != "ALL_TEAMS_AVG"])

st.markdown(
    """
    <style>
    /* Change background color of the selected option */
    div[data-baseweb="select"] > div {
        background-color: #0E3F5C;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='text-align: center;'>Match Report</h1>", unsafe_allow_html=True)

def get_jornada_options(equipo):
    sub = df[df["team_name"] == equipo][["match_week", "match_id"]].drop_duplicates()
    opts = []
    jorns = []
    for _, r in sub.iterrows():
        mw, mid = r["match_week"], r["match_id"]
        mdf = df[df["match_id"] == mid]
        if mdf.shape[0] != 2: continue
        t1, t2 = mdf.iloc[0], mdf.iloc[1]
        local, visita = (t1, t2) if t1["team_name"] == t1["home_team"] else (t2, t1)
        marcador = f"{int(local['goals'])}-{int(visita['goals'])}"
        label = f"J{mw} - {local['team_name']} {marcador} {visita['team_name']}"
        opts.append((label, mw))
    return opts

s1 , s2 = st.columns(2)

with s1:
    team_selected_mr = st.selectbox(
    "Selecciona el equipo a analizar",
        available_teams,
        index=0,
        placeholder="Selecciona un equipo",
        accept_new_options=True,
    )

jornadas = get_jornada_options(team_selected_mr)
jornadas = sorted(jornadas,key=lambda x: x[1])



with s2:
    jornada_selected_mr = st.selectbox(
    "Selecciona la jornada a analizar",
        jornadas,
        index=0,
        placeholder="Selecciona un equipo",
        accept_new_options=True,
    )[1]

ESCUDOS_PATH = "img/Chile Primeradivision/"

# --- Función para añadir imagen en coordenadas absolutas ---
def add_image(img_path, fig, left, bottom, width, height):
    try:
        new_ax = fig.add_axes([left, bottom, width, height], anchor='C', zorder=1)
        new_ax.imshow(mpimg.imread(img_path))
        new_ax.axis("off")
    except FileNotFoundError:
        print(f"⚠️ Imagen no encontrada: {img_path}")

df = st.session_state['df_final']

match_df = df[df["match_id"] != "AVG"].copy()
match_df["match_id"] = match_df["match_id"].astype(str)
match_df["x_label"] = match_df.apply(lambda row: f"J{row['match_week']}: {row['match_score']}", axis=1)

# --- MÉTRICAS ---
metrics_dict = {
    'np_xg': 'npXG',
    'np_shots': 'Shots',
    'obv_shot': 'OBV Shots',
    'xgchain': 'xG Chance',
    'goals': 'Goals',
    'Goal Envolvement Index (norm)': 'Goal Envolvement',
    'Goal Conversion Index (norm)': 'Goal Conversion',
    'Possession GoalChance Index (norm)': 'Poss. GoalChance',
    'GoalOpenPlay Performance Index': 'GoalOpenPlay Perform.'
}
metrics = list(metrics_dict.keys())
clean_labels = [metrics_dict[m] for m in metrics]

# Añadir columnas percentil
for col in metrics:
    df[col + "_pctl"] = df[col].rank(pct=True) * 100
pctl_metrics = [m + "_pctl" for m in metrics]

# --- KPIs Evolutivos ---
kpi_list = [
    "Goal Envolvement Index (norm)",
    "Goal Conversion Index (norm)",
    "Possession GoalChance Index (norm)",
    "GoalOpenPlay Performance Index"
]

def calcular_GP(team_df, jornada):
    df_filtrado = team_df[team_df["match_week"] == jornada]
    
    if df_filtrado.empty:
        return None
    
    # Valor puntual de esa jornada
    valor_openplay = df_filtrado["GoalOpenPlay Performance Index"].values[0]
    promedio_setpiece = 7.92  # fijo

      # Goles del equipo en esa jornada
    goles = df_filtrado["goals"].values[0]
    
    GP = (0.7 * valor_openplay) + (0.3 * promedio_setpiece)

    # Bonus por goles
    if goles == 1:
        GP += 0.5
    elif  goles == 2:
        GP += 0.75
    elif  goles >= 3:
        GP += 1
    
    return round(GP, 2)

# --- FUNCIONES ---

def plot_radar_and_kpis(equipo, jornada):
        md = df[(df["team_name"] == equipo) & (df["match_week"] == jornada)]
        if md.empty:
            print("❌ No se encontró ese equipo en esa jornada.")
            return
        mid = md.iloc[0]["match_id"]
        mdf = df[df["match_id"] == mid]
        if mdf.shape[0] != 2:
            print("❌ Datos incompletos.")
            return

        team_row = mdf[mdf["team_name"] == equipo].iloc[0]
        rival_row = mdf[mdf["team_name"] != equipo].iloc[0]

        team_vals = [team_row[m] for m in pctl_metrics] + [team_row[pctl_metrics[0]]]
        rival_vals = [rival_row[m] for m in pctl_metrics] + [rival_row[pctl_metrics[0]]]
        angles = [n / float(len(metrics)) * 2 * pi for n in range(len(metrics))] + [0]

        local, visita = (team_row, rival_row) if team_row["team_name"] == team_row["home_team"] else (rival_row, team_row)
        marcador = f"{int(local['goals'])}-{int(visita['goals'])}"
        title = f"{local['team_name']} {marcador} {visita['team_name']} - Jornada {jornada}"

        fig = plt.figure(figsize=(20, 30), facecolor="#0E3F5C")
        gs = gridspec.GridSpec(3, 1, height_ratios=[1.6, 0.6, 1.4], figure=fig)

        # Subtítulo
        fig.text(0.5, 0.91, "GoalPerformance Team Comparison", ha='center', va='center', color='lightgray', fontsize=26, fontweight='bold')

        # --- RADAR ---
        radar_ax = fig.add_subplot(gs[0], polar=True, facecolor="#0E3F5C")

        radar_ax.spines['polar'].set_color((0.8, 0.8, 0.8, 0.2))
        radar_ax.spines['polar'].set_linewidth(1.5)

        radar_ax.plot(angles, team_vals, linewidth=3, label=equipo, color='gold')
        radar_ax.fill(angles, team_vals, color='gold', alpha=0.4)
        radar_ax.plot(angles, rival_vals, linewidth=3, label=rival_row["team_name"], color='lightgray')
        radar_ax.fill(angles, rival_vals, color='lightgray', alpha=0.4)
        radar_ax.set_xticks(angles[:-1])
        radar_ax.set_xticklabels(clean_labels, color='white', size=15)
        radar_ax.set_yticklabels([])
        radar_ax.grid(True, color="white", linestyle='--', alpha=0.3)
        radar_ax.set_title(title, color="white", fontsize=20, pad=30)

         # Texto en el centro con Audax y GP
        team_df = match_df[match_df["team_name"] == equipo].sort_values("match_week")
        gp_val = calcular_GP(team_df, jornada)
        radar_ax.text(0, 0, "Audax\nGP:" + str(gp_val), ha='center', va='center', fontsize=28, fontweight='bold', color='palegreen')

        legend = radar_ax.legend(loc='lower left', fontsize=20, frameon=False, bbox_to_anchor=(-0.3, -0.1))
        for text in legend.get_texts():
            text.set_color('white')
        
        fig.text(0.97, 0.5, "Data StatsBomb Teams GoalPerformance | code by: @Sevi", color='lightgray', fontsize=12, ha='right', va='bottom')
        
        add_image(os.path.join(ESCUDOS_PATH, f"{local['team_name']}.png"), fig, 0.05, 0.82, 0.12, 0.12)
        add_image(os.path.join(ESCUDOS_PATH, f"{visita['team_name']}.png"), fig, 0.83, 0.82, 0.12, 0.12)

        # --- TABLA ---
        tabla_ax = fig.add_subplot(gs[1])
        tabla_ax.axis("off")
        df_tabla = pd.DataFrame(
            [[equipo] + [round(team_row[m], 2) for m in pctl_metrics],
             [rival_row["team_name"]] + [round(rival_row[m], 2) for m in pctl_metrics]],
            columns=["Equipo"] + clean_labels
        )

        def color_cells(value):
            if value < 40: return '#f4d03f'
            elif 40 <= value < 65: return '#82e0aa'
            elif 65 <= value < 85: return '#28b463'
            else: return '#196f3d'

        def text_color(name): return 'gold' if name == equipo else '#E0E0E0'
        colores = [[color_cells(val) for val in row] for row in df_tabla.iloc[:, 1:].values]
        colores_final = [['#0E3F5C'] + row for row in colores]

        tabla = tabla_ax.table(
            cellText=df_tabla.values,
            colLabels=df_tabla.columns,
            cellColours=colores_final,
            cellLoc='center',
            loc='center'
        )
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(11)
        tabla.scale(1.3, 2)

        for (i, j), cell in tabla.get_celld().items():
            cell.set_edgecolor('white')
            if i == 0:
                cell.set_text_props(color='white', weight='bold')
                cell.set_facecolor('#0050a0')
            else:
                if j == 0:
                    cell.set_text_props(color=text_color(df_tabla.iloc[i-1, 0]), weight='bold')
                    cell.set_facecolor('#0050a0')
                else:
                    cell.set_text_props(color='white', weight='bold')

        # --- KPIs EVOLUTIVOS ---
        team_df = match_df[match_df["team_name"] == equipo].sort_values("match_week")
        kpi_ax = fig.add_subplot(gs[2])
        kpi_ax.axis("off")

        legend_lines = []

        fig.text(0.5, 0.43, "Evolución de KPIs", ha='center', va='center', color='lightgray', fontsize=26, fontweight='bold')

        for i, kpi in enumerate(kpi_list):
            sub_ax = fig.add_axes([0.07 + (i % 2) * 0.46, 0.04 + (1 - i // 2) * 0.2, 0.4, 0.15], facecolor="#0E3F5C")
            team_avg = team_df[kpi].mean()
            all_avg = match_df[kpi].mean()

            # Graficar todos los puntos normales
            sub_ax.plot(team_df["x_label"], team_df[kpi], marker='o', color='lime', label=equipo, markersize=6)

            # Resaltar nodo de la jornada seleccionada
            if jornada in team_df["match_week"].values:
                idx = team_df[team_df["match_week"] == jornada].index[0]
                x = team_df.loc[idx, "x_label"]
                y = team_df.loc[idx, kpi]
                sub_ax.plot(x, y, marker='o', markersize=13, markeredgewidth=2, markeredgecolor='black', markerfacecolor='greenyellow', zorder=5)

            # Líneas promedio
            sub_ax.axhline(team_avg, color='palegreen', linestyle='--', label=f'Prom. {equipo}')
            sub_ax.axhline(all_avg, color='lightgray', linestyle=':', label='Prom.Liga')

            if i == 0:
                 legend_lines = [
                     Line2D([0], [0], color='lime', marker='o', label=equipo),
                     Line2D([0], [0], color='palegreen', linestyle='--', label=f'Prom. {equipo}'),
                     Line2D([0], [0], color='lightgray', linestyle=':', label='Prom. Liga')
                ]

            sub_ax.set_title(kpi.replace(" (norm)", ""), color="white", fontsize=10)
            sub_ax.tick_params(colors='white', labelsize=10)

            jornadas_labels = team_df["match_week"].apply(lambda x: f"J{x}").tolist()
            sub_ax.set_xticks(team_df["x_label"])
            sub_ax.set_xticklabels(jornadas_labels, rotation=30, ha='right')
            sub_ax.grid(color='white', linestyle='--', alpha=0.2)

        for text in legend.get_texts():
            text.set_color('lightgray')

        fig.legend(handles=legend_lines, loc='upper center', bbox_to_anchor=(0.5, 0.42), ncol=3, fontsize=18, frameon=False)

        return fig

fig_tl = plot_radar_and_kpis(team_selected_mr,jornada_selected_mr)

st.pyplot(fig=fig_tl)


