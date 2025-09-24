import streamlit as st

st.markdown("<h1 style='text-align: center;'>Glosario</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: left;'>Clasificación</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Tabla de posiciones con métricas variadas del rendimiento de los equipos.</p>", unsafe_allow_html=True)

c1 , c2 = st.columns(2)

with c1:
    st.markdown("**Rank:** Posición en la tabla")
    st.markdown("**TOP_7:** Si el equipo está entre los 7 primeros de la tabla")
    st.markdown("**PJ:** Partidos jugados")
    st.markdown("**V:** N° de Victorias")
    st.markdown("**E:** N° de Empates")

with c2:    
    st.markdown("**D:** N° de Derrotas")
    st.markdown("**GF:** Goles a Favor")
    st.markdown("**GC:** Goles en contra")
    st.markdown("**DG:** Diferencia de Goles")
    st.markdown("**Pts:** Puntos obtenidos")

st.divider()

st.markdown("<h2 style='text-align: left;'>KPIs Top 7</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Columnas de métricas de Goal Performance para cada equipo, ordenados de mayor a menor en cada columna. Destacado en color a Audax Italiano.</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Si la posición en la clasificación es más alta, será más verde, de lo contrario, será rojo.</p>", unsafe_allow_html=True)

c3 , c4 = st.columns(2)

with c3:

    st.markdown("<h5 style='text-align: left;'>Goal Performance Team</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Rendimiento final entorno al gol.</p>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: left;'>Goal OpenPlay Performance </h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Rendimiento en juego dinámico o jugadas de balón vivo.</p>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: left;'>Goal Envolvement</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Participación en jugadas de gol.</p>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: left;'>Goal Conversion</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Eficacia en la finalización.</p>", unsafe_allow_html=True)

with c4:
    st.markdown("<h5 style='text-align: left;'>Possession GoalChance</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Ocasiones de gol con posesión.</p>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: left;'>SetPiece Eficcacy</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Eficacia a través de balón parado.</p>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: left;'>GoalSetPiece Performance</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Rendimiento de gol a través de balón parado.</p>", unsafe_allow_html=True)

st.divider()

st.markdown("<h2 style='text-align: left;'>Perfil GP</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Columnas de métricas de Goal Performance para cada equipo, ordenados de mayor a menor en cada columna. Destacado en color a Audax Italiano.</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Si la posición en la clasificación es más alta, será más verde, de lo contrario, será rojo.</p>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: left;'>Advanced Performance Keys</h3>", unsafe_allow_html=True)
c5 , c6 = st.columns(2)
with c5:
    st.markdown("<h5 style='text-align: left;'>Improvement Area</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Espacio para mejorar ... .</p>", unsafe_allow_html=True)
with c6:
    st.markdown("<h5 style='text-align: left;'>xPerformance Potential</h5>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>expected bla bla.</p>", unsafe_allow_html=True)

st.divider()

st.markdown("<h2 style='text-align: left;'>Match Report</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Columnas de métricas de Goal Performance para cada equipo, ordenados de mayor a menor en cada columna. Destacado en color a Audax Italiano.</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Si la posición en la clasificación es más alta, será más verde, de lo contrario, será rojo.</p>", unsafe_allow_html=True)

st.divider()

st.markdown("<h2 style='text-align: left;'>Affinity Index</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: left;'>Perfil del equipo construido a partir de métricas de Goal Performance.</p>", unsafe_allow_html=True)



