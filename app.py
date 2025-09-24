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

pages = [
    st.Page(page="ReporteSemanal-AI.py", title="Clasificación", default=True),
    st.Page(page="pages/kpis_top7.py", title="KPIs Top 7"),
    st.Page(page="pages/perfil_gp.py", title="Perfil GP" ),
    st.Page(page="pages/match_report.py", title="Match Report"),
    st.Page(page="pages/AIT_Index.py", title= "Affinity Index"),
    st.Page(page="pages/glosario.py" , title="Glosario")
]

pg = st.navigation(pages=pages , position='sidebar', expanded=True)
pg.run()

st.logo("img\Chile Primeradivision\Insignia_Audax_Italiano.png")