import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mplsoccer import PyPizza
from mplsoccer.utils import add_image
import os
from matplotlib.offsetbox import OffsetImage, AnnotationBbox, TextArea, VPacker
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Goal Performance Profile",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

#st.header("Perfil Goal Performance - Audax Italiano")
#st.divider()



# === CONFIGURACIÓN DINÁMICA ===

# INCLUIR SELECT BOX PARA ELEGIR EL EQUIPO A RESALTAR

logos_dir = 'img/Chile Primeradivision'
selected_team = 'Audax Italiano'  # <- CAMBIA AQUÍ EL EQUIPO A RESALTAR
df = st.session_state['gtv']
df = df[~df['team_name'].str.contains('TopValues', na=False)]

x_col = 'GoalOpenPlay Performance Index'
y_col = 'GoalSetPiece Performance Index'

fig, ax = plt.subplots(figsize=(14, 10))
fig.patch.set_facecolor('#0E3F5C')
ax.set_facecolor('#0E3F5C')

# === FUNCIONES ===

def load_and_resize_logo(image_path, zoom):
    try:
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        base_size = 100
        scale = zoom * base_size / max(width, height)
        return OffsetImage(img, zoom=scale)
    except Exception as e:
        print(f"Error con {image_path}: {e}")
        return None

def add_logo_with_label(ax, image_path, x, y, zoom, label):
    imagebox = load_and_resize_logo(image_path, zoom)
    if imagebox:
        text = TextArea(label, textprops=dict(color="white", fontsize=8, ha='center'))
        vpack = VPacker(children=[imagebox, text], align="center", pad=0, sep=2)
        ab = AnnotationBbox(vpack, (x, y), frameon=False)
        ax.add_artist(ab)

# === PLOT DE ESCUDOS CON ETIQUETA ===

for idx, row in df.iterrows():
    team = row['team_name']
    x = row[x_col]
    y = row[y_col]
    
    logo_path = os.path.join(logos_dir, f"{team}.png")
    
    zoom = 0.6 if team == selected_team else 0.4
    add_logo_with_label(ax, logo_path, x, y, zoom, team)

# === ESTILO DEL GRÁFICO ===

ax.set_xlabel('Goal OpenPlay Performance Index', fontsize=13, color='white')
ax.set_ylabel('Goal SetPiece Performance Index', fontsize=13, color='white')
ax.set_title('Scatter de rendimiento ofensivo (Open Play vs Set Piece)', fontsize=15, color='white', weight='bold')

for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(colors='white')
ax.grid(True, linestyle='--', linewidth=0.5, color='white', alpha=0.4)

# Línea diagonal
x_min, x_max = df[x_col].min(), df[x_col].max()
y_min, y_max = df[y_col].min(), df[y_col].max()
ax.plot([x_min, x_max], [y_min, y_max], linestyle='-', color='orange', linewidth=1.5, alpha=0.8)

# Límites
ax.set_xlim(x_min - 0.3, x_max + 0.3)
ax.set_ylim(y_min - 0.3, y_max + 0.3)

# Gráfico de Pizza:

df_p = st.session_state["gtv"]

# 2. Columnas exactas a usar
display_cols = [
    "team_name",
    "GoalOpenPlay Performance Index", "Goal Envolvement Index",
    "Goal Conversion Index", "Possession GoalChance Index",
    "corner Efficiency", "freekick Efficiency",
    "directfk Efficiency", "throw in Efficiency",
    "SetPiece Eficcacy Index", "GoalSetPiece Performance Index"
]

# 3. Lista de equipos (excluyendo TopValues)
teams = sorted(df["team_name"].unique())
teams = [t for t in teams if not t.startswith("TopValues")]

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

st.markdown("<h1 style='text-align: center;'>Goal Performance Profile</h1>", unsafe_allow_html=True)

team_selected_gtv = st.selectbox(
    "Selecciona el equipo a analizar",
        teams,
        index=0,
        placeholder="Selecciona un equipo",
        accept_new_options=True,
)

def plot_team(team_name):
    
    team_data = df_p[df_p["team_name"] == team_name][display_cols]
    values = team_data.iloc[0, 1:].astype(float).values
    
    top_min = df_p[df_p["team_name"] == "TopValues (min)"][display_cols[1:]].astype(float).values[0]
    slice_colors = [
        "lightgreen" if values[i] < top_min[i] else "darkgreen"
        for i in range(len(values))
    ]
    params = [
    "Goal\nOpenPlay", "Goal\nEnvolvement",
    "Goal\nConversion", "Possession\nGoalChance",
    "corner\nEfficiency", "freekick\nEfficiency",
    "directfk\nEfficiency", "throw in\nEfficiency",
    "SetPiece\nEficcacy", "Goal\nSetPiece"  
    ]

    
    min_values = [0.5] * len(params)
    max_values = [9.5] * len(params)
    
    baker = PyPizza(
        params=params,
        min_range=min_values,
        max_range=max_values,
        background_color='#0E3F5C',
        straight_line_color="white",
        last_circle_color="white",
        last_circle_lw=1.5,
        straight_line_lw=1,
        other_circle_lw=0,
        other_circle_color="white",
        inner_circle_size=12,
    )
    
    fig_p, ax_p = baker.make_pizza(
        values,
        figsize=(8, 4),
        color_blank_space="same",
        blank_alpha=0.3,
        param_location=110,
        slice_colors=slice_colors,
        kwargs_slices=dict(facecolor="lightgreen", edgecolor="lightgreen", zorder=1, linewidth=1),
        kwargs_params=dict(color="lightgreen", fontsize=5, va="center"),
        kwargs_values=dict(color="white", fontsize=5, 
                           bbox=dict(edgecolor="lightgreen", facecolor="green",
                                     boxstyle="round,pad=0.2", lw=1))
    )
    
    fig_p.text(0.5, 0.97, team_name, size=12, ha="center", color="white")
    fig_p.text(0.5, 0.94,
             "Chile - Primera División | Tactical SetPiece Profile",
             size=6, ha="center", color="white")
    fig_p.text(0.99, 0.005,
             "Data from StatsBomb | Code by @Sevi | TPAC Methodology",
             size=6, color="#F2F2F2", ha="right")
    
    # 8. Escudo central y Liga
    badge_path = f"img/Chile Primeradivision/{team_name}.png"
    ligueName_path = f"img/Chile Primeradivision/Liga de Primera.png"

    badge = Image.open(badge_path)
    add_image(badge, fig_p, left=0.451, bottom=0.438, width=0.12, height=0.12)
    ligueName = Image.open(ligueName_path)
    add_image(ligueName, fig_p, left=0.02, bottom=0.01, width=0.15, height=0.15 )

    return fig_p

fig_p = plot_team(team_selected_gtv)

# Creación de métricas:

df_m = st.session_state["gtv"]
# KPIs y rangos
kpi_cols = [
    "Goal Performance Team Index", "GoalOpenPlay Performance Index", "Goal Envolvement Index",
    "Goal Conversion Index", "Possession GoalChance Index",
    "corner Efficiency", "freekick Efficiency",
    "directfk Efficiency", "throw in Efficiency",
    "SetPiece Eficcacy Index", "GoalSetPiece Performance Index"
]
top_min = df_m.loc[df_m["team_name"] == "TopValues (min)", kpi_cols].iloc[0].astype(float)
top_max = df_m.loc[df_m["team_name"] == "TopValues (max)", kpi_cols].iloc[0].astype(float)

def team_performance_metrics(team_name):
    row = df.loc[df["team_name"] == team_name, kpi_cols].iloc[0].astype(float)
    
    # Métricas
    goal_team_perf = row["Goal Performance Team Index"]
    goal_openplay = row["GoalOpenPlay Performance Index"]
    goal_setpiece = row["GoalSetPiece Performance Index"]
    below = (row < top_min).sum()
    total = len(kpi_cols)
    improvement_pct = (below / total) * 100
    x_perf = (row / top_max).mean() * (9.5 - 0.5) + 0.5

    metrics = [
        ("Goal\nPerformance", goal_team_perf),
        ("GoalOpenPlay\nPerformance", goal_openplay),
        ("GoalSetPiece\nPerformance", goal_setpiece),
        ("Improvement\nArea (%)", improvement_pct),
        ("xPerformance\nPotential", x_perf)
    ]

    return metrics

adv_met = team_performance_metrics(team_selected_gtv)

# Columnas de Gráficas:

css_c1 = """
.st-key-containerapk {
    background-color: #0E3F5C;
    border-radius: 10px;
}
"""

st.html(f"<style>{css_c1}</style>")

cont_apk = st.container(key="containerapk")
with cont_apk:
    cont_2 = st.container(key="container2",horizontal=True,horizontal_alignment="center",vertical_alignment="center")
    with cont_2:
            st.image('img\Chile Primeradivision\Audax Italiano.png',width=65)
        
            st.markdown("""
                            <style>
                            .big-font {
                                font-size:40px !important;
                                vertical-align:bottom;
                            }
                            </style>
                            """, unsafe_allow_html=True)
            st.markdown('<p class="big-font">Advanced Performance Keys</p>', unsafe_allow_html=True)
                
            st.image('img\Chile Primeradivision\Liga de Primera.png',width=65)
    cont_mt = st.container(horizontal=True , border=True, horizontal_alignment="center", gap="medium")
    with cont_mt:
        st.metric(label="Goal\nPerformance",value=round(adv_met[0][1],2))
        st.metric(label="GoalOpenPlay Performance",value=round(adv_met[1][1],2))
        st.metric(label="GoalSetPiece Performance",value=round(adv_met[2][1],2))
        st.metric(label="Improvement Area",value=f"{round(adv_met[3][1],2)}%")
        st.metric(label="xPerformance Potential" , value=round(adv_met[4][1],2))

st.pyplot(fig=fig_p)

st.pyplot(fig=fig)
        



