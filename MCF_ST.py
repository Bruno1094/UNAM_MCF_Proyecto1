'''
1er proyecto de MCF :D

Autores:
- López Fuentes Paula Juliana
- Olavarria Guerra Bruno
- Reyes Díaz Axel Gabriel
- Toledo Camargo Ulises

'''

import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import kurtosis, skew, norm, t
import Funciones as MCF

st.title("Análisis de Riesgo Financiero")

# ----------------------------------------------- #
#                      INPUT                      #
# ----------------------------------------------- #

# Lista de acciones
stocks_lista = ['BIMBOA.MX','AMX', 'GMEXICOB.MX']

with st.spinner("Descargando datos..."):
    df_precios = MCF.obtener_datos(stocks_lista)
    df_rend = MCF.calcular_rendimientos(df_precios)

# Selector de acción
ticker = st.selectbox("Selecciona una acción:", stocks_lista)

# Pestañas para subdividir la info
tabs = st.tabs([
    "Información del Activo",
    "Métricas de Riesgo",
    "VaR y CVaR",
    "Rolling VaR y CVaR",
    "Volatilidad Móvil"
])

if ticker:
    with tabs[0]:
        st.subheader("Información del Activo")
        # ----------------------------------------------------- #
        #                      INFO PREVIA                      #
        # ----------------------------------------------------- #
        st.write("Fecha inicial:", df_precios[ticker].index.min())
        st.write("Fecha final:", df_precios[ticker].index.max())
        st.write("Número de observaciones:", df_precios[ticker].shape[0])

        st.subheader("Serie de rendimientos diarios")
        serie1 = df_rend[[ticker]].dropna().reset_index()
        serie1.columns = ['Fecha', 'Rendimiento']

        nearest = alt.selection_point(
            nearest=True,
            on='mouseover',
            fields=['Fecha'],
            empty=False
        )

        line = alt.Chart(serie1).mark_line(
            color="#4FC3F7",
            strokeWidth=1.5
        ).encode(
            x='Fecha:T',
            y='Rendimiento:Q'
        )

        points = alt.Chart(serie1).mark_circle(size=60).encode(
            x='Fecha:T',
            y='Rendimiento:Q',
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        ).add_params(nearest)

        rules = alt.Chart(serie1).mark_rule(color='gray').encode(
            x='Fecha:T',
            tooltip=[
                alt.Tooltip('Fecha:T', title='Fecha'),
                alt.Tooltip('Rendimiento:Q', format='.4f')
            ]
        ).transform_filter(nearest)

        st.altair_chart(line + points + rules, use_container_width=True)

    with tabs[1]:
        st.subheader("Métricas de Riesgo")

        # --------------------------------------------------- #
        #                     b) MÉTRICAS                     #
        # --------------------------------------------------- #

        mean = float(df_rend[ticker].mean())
        skewness = float(skew(df_rend[ticker]))
        kurt = float(kurtosis(df_rend[ticker]))

        col1, col2, col3 = st.columns(3)
        col1.metric("Media", f"{mean:.4%}")
        col2.metric("Sesgo", f"{skewness:.4f}")
        col3.metric("Exceso de Curtosis", f"{kurt:.4f}")

        # --------------------------------------------------- #
        #                      HISTOGRAMA                     #
        # --------------------------------------------------- #

        st.subheader("Distribución de Rendimientos")

        serie_hist = df_rend[[ticker]].dropna().reset_index(drop=True)
        serie_hist.columns = ['Rendimiento']

        hist = alt.Chart(serie_hist).mark_bar(
            color="#66BB6A",
            opacity=0.8
        ).encode(
            x=alt.X('Rendimiento:Q', bin=alt.Bin(maxbins=50), title='Rendimiento'),
            y=alt.Y('count()', title='Frecuencia'),
            tooltip=['count()']
        ).properties(
            height=400
        )

        st.altair_chart(hist, use_container_width=True)

    with tabs[2]:
        # --------------------------------------------------- #
        #                    c) VaR y CVaR                    #
        # --------------------------------------------------- #

        
        st.subheader("VaR y CVaR")

        niveles = [0.95, 0.975, 0.99]
        
        alpha = st.selectbox(
            "Selecciona el nivel de confianza:",
            niveles,
            index=0
        )

        serie = df_rend[ticker].dropna()

        mean = float(serie.mean())
        stdev = float(serie.std())

        # VaR
        VaR_norm = norm.ppf(1 - alpha, mean, stdev)

        df_t, loc_t, scale_t = t.fit(serie)
        VaR_t = t.ppf(1 - alpha, df_t, loc_t, scale_t)

        VaR_hist = serie.quantile(1 - alpha)

        sim = np.random.normal(mean, stdev, 100000)
        VaR_mc = np.percentile(sim, (1 - alpha) * 100)

        # CVaR
        CVaR_norm = serie[serie <= VaR_norm].mean()
        CVaR_t = serie[serie <= VaR_t].mean()
        CVaR_hist = serie[serie <= VaR_hist].mean()
        CVaR_mc = serie[serie <= VaR_mc].mean()

        st.write("Nota: Para los cálculos del VaR paramétrico se hacen supuestos de normalidad y t-student.")
        st.write("Los valores de VaR y ES se reportan como rendimientos negativos. "
                 "Mientras más negativo sea el valor, mayor es la pérdida potencial estimada.")

        # ---------------------------------------------------- #
        #                      TABLA FINAL                     #
        # ---------------------------------------------------- #
        tabla = pd.DataFrame({
            "Histórico": [VaR_hist, CVaR_hist],
            "Normal": [VaR_norm, CVaR_norm],
            "t-Student": [VaR_t, CVaR_t],
            "Monte Carlo": [VaR_mc, CVaR_mc]
        }, index=["VaR", "CVaR"])

        st.dataframe(tabla, use_container_width=True)

        # -------------------------------------------------- #
        #                   GRÁFICA CON VaR                  #
        # -------------------------------------------------- #

        serie_alt = pd.DataFrame({'Rendimiento': serie})

        bins = 50
        hist_range = serie.max() - serie.min()
        bin_width = hist_range / bins
        N = len(serie)

        # HISTOGRAMA
        hist = alt.Chart(serie_alt).mark_bar(opacity=0.5).encode(
            x=alt.X('Rendimiento:Q',
                    bin=alt.Bin(maxbins=bins),
                    title='Rendimiento'),
            y=alt.Y('count()', title='Frecuencia'),
            color=alt.condition(
                alt.datum.Rendimiento < VaR_hist,
                alt.value('#EF5350'),
                alt.value('#90CAF9')
            )
        )

        # CURVAS ESCALADAS
        x = np.linspace(serie.min(), serie.max(), 400)

        bins = 50
        hist_range = serie.max() - serie.min()
        bin_width = hist_range / bins
        N = len(serie)

        pdf_norm = norm.pdf(x, mean, stdev) * N * bin_width
        pdf_t = t.pdf(x, df_t, loc_t, scale_t) * N * bin_width

        df_curvas = pd.DataFrame({
            'x': np.concatenate([x, x]),
            'pdf': np.concatenate([pdf_norm, pdf_t]),
            'Tipo': ['Normal'] * len(x) + ['t-Student'] * len(x)
        })

        line_curves = alt.Chart(df_curvas).mark_line(strokeWidth=3).encode(
            x='x:Q',
            y='pdf:Q',
            color=alt.Color(
                'Tipo:N',
                scale=alt.Scale(
                    domain=['Normal', 't-Student'],
                    range=['#1E88E5', '#8E24AA']
                ),
                legend=alt.Legend(title="Distribuciones")
            )
        )

        # SOMBREADO VaR (cola)
        df_tail = df_curvas[df_curvas['x'] <= VaR_hist]

        tail_area = alt.Chart(df_tail[df_tail['Tipo'] == 'Normal']).mark_area(
            opacity=0.35,
            color='#FF5252'
        ).encode(
            x='x:Q',
            y='pdf:Q'
        )

        # Líneas VaR
        df_var = pd.DataFrame({
            'Metric': ['VaR Normal', 'VaR t', 'VaR Hist', 'VaR MC'],
            'valor': [VaR_norm, VaR_t, VaR_hist, VaR_mc],
            'Color': ['#1E88E5', '#8E24AA', '#000000', '#43A047']
        })

        var_lines = alt.Chart(df_var).mark_rule(
            strokeDash=[6, 4],
            size=2
        ).encode(
            x='valor:Q',
            color=alt.Color(
                'Metric:N',
                scale=alt.Scale(
                    domain=df_var['Metric'].tolist(),
                    range=df_var['Color'].tolist()
                ),
                legend=alt.Legend(title="VaR")
            ),
            tooltip=['Metric', 'valor']
        )

        # Líneas CVaR
        df_cvar = pd.DataFrame({
            'Metric': ['CVaR Normal', 'CVaR t', 'CVaR Hist', 'CVaR MC'],
            'valor': [CVaR_norm, CVaR_t, CVaR_hist, CVaR_mc],
            'Color': ['#1E88E5', '#8E24AA', '#000000', '#43A047']
        })

        cvar_lines = alt.Chart(df_cvar).mark_rule(
            size=3
        ).encode(
            x='valor:Q',
            color=alt.Color(
                'Metric:N',
                scale=alt.Scale(
                    domain=df_cvar['Metric'].tolist(),
                    range=df_cvar['Color'].tolist()
                ),
                legend=alt.Legend(title="CVaR")
            ),
            tooltip=['Metric', 'valor']
        )

        # GRAFICA FINAL   
        chart = (
            hist +
            tail_area +
            line_curves +
            var_lines +
            cvar_lines
        ).resolve_scale(
            color='independent'
        ).properties(
            height=500,
            title=f"Distribución con VaR y CVaR ({alpha*100}%)"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

    with tabs[3]:
        # ----------------------------------------------- #
        #              d) ROLLING VaR Y CVaR              #
        # ----------------------------------------------- #

        st.subheader("Rolling VaR y CVaR")

        ventana_sel = 252

        niveles = [0.95, 0.99]

        serie = df_rend[ticker].dropna()

        rolling_mean = serie.rolling(window=ventana_sel).mean()
        rolling_std = serie.rolling(window=ventana_sel).std()

        df_rolling = pd.DataFrame({
            "Fecha fin": serie.index,
            "Rendimiento": serie.values,
            "Media Rolling": rolling_mean,
            "Volatilidad Rolling": rolling_std
        })

        for alpha_sel in niveles:

            suf = int(alpha_sel * 100)

            # PARAMÉTRICO
            df_rolling[f"VaR Param {suf}"] = norm.ppf(
                1 - alpha_sel,
                rolling_mean,
                rolling_std
            )

            z = norm.ppf(1 - alpha_sel)

            df_rolling[f"CVaR Param {suf}"] = rolling_mean - (
                rolling_std * norm.pdf(z) / (1 - alpha_sel)
            )

            # HISTÓRICO
            df_rolling[f"VaR Hist {suf}"] = serie.rolling(window=ventana_sel).quantile(1 - alpha_sel)

            df_rolling[f"CVaR Hist {suf}"] = serie.rolling(window=ventana_sel).apply(
                lambda x: x[x <= np.quantile(x, 1 - alpha_sel)].mean(),
                raw=False
            )

        df_rolling["Fecha inicio"] = df_rolling["Fecha fin"].shift(ventana_sel - 1)

        df_rolling = df_rolling.dropna()

        df_rolling["Fecha inicio"] = df_rolling["Fecha inicio"].dt.date
        df_rolling["Fecha fin"] = df_rolling["Fecha fin"].dt.date

        cols = [col for col in df_rolling.columns if col not in ["Fecha inicio", "Fecha fin"]]

        for col in cols:
            df_rolling[col + " %"] = df_rolling[col] * 100

        st.data_editor(
            df_rolling[[
                "Fecha inicio", "Fecha fin",
                "Rendimiento %",
                "VaR Param 95 %", "CVaR Param 95 %",
                "VaR Hist 95 %", "CVaR Hist 95 %",
                "VaR Param 99 %", "CVaR Param 99 %",
                "VaR Hist 99 %", "CVaR Hist 99 %"
            ]],
            use_container_width=True,
            hide_index=True,
            disabled=True
        )

        # ----------------------------------------------- #
        #                     GRÁFICA                     #
        # ----------------------------------------------- #

        st.subheader(f"Rolling Risk ({ticker} - {ventana_sel} días)")

        df_plot = df_rolling.copy()

        rend = df_plot[["Fecha fin", "Rendimiento %"]]

        var_cols = [
            "VaR Param 95 %", "VaR Param 99 %",
            "VaR Hist 95 %", "VaR Hist 99 %"
        ]

        cvar_cols = [
            "CVaR Param 95 %", "CVaR Param 99 %",
            "CVaR Hist 95 %", "CVaR Hist 99 %"
        ]

        df_var = df_plot.melt(
            id_vars="Fecha fin",
            value_vars=var_cols,
            var_name="Serie",
            value_name="Valor"
        )

        df_cvar = df_plot.melt(
            id_vars="Fecha fin",
            value_vars=cvar_cols,
            var_name="Serie",
            value_name="Valor"
        )

        # COLORES
        color_domain = var_cols + cvar_cols

        color_range = [
            "#EF5350", "#B71C1C",  # VaR Param
            "#42A5F5", "#0D47A1",  # VaR Hist
            "#EF5350", "#B71C1C",  # CVaR Param
            "#42A5F5", "#0D47A1"   # CVaR Hist
        ]

        color_scale = alt.Scale(domain=color_domain, range=color_range)

        # RENDIMIENTOS
        line_rend = alt.Chart(rend).mark_line(
            color="#959595",
            opacity=0.6,
            strokeWidth=1.5
        ).encode(
            x="Fecha fin:T",
            y="Rendimiento %:Q"
        )

        # VaR (PUNTEADO)
        line_var = alt.Chart(df_var).mark_line(
            strokeDash=[6, 4],
            strokeWidth=2
        ).encode(
            x="Fecha fin:T",
            y="Valor:Q",
            color=alt.Color("Serie:N", scale=color_scale, legend=alt.Legend(title="VaR / CVaR")),
            tooltip=["Serie", "Valor"]
        )

        # CVaR (SÓLIDO)
        line_cvar = alt.Chart(df_cvar).mark_line(
            strokeWidth=3
        ).encode(
            x="Fecha fin:T",
            y="Valor:Q",
            color=alt.Color("Serie:N", scale=color_scale)
        )

        # LÍNEA CERO
        zero_line = alt.Chart(pd.DataFrame({"y":[0]})).mark_rule(
            color="black"
        ).encode(
            y="y:Q"
        )

        # FINAL
        nearest = alt.selection_point(
            nearest=True,
            on="mouseover",
            fields=["Fecha fin"],
            empty=False
        )
        
        points = alt.Chart(rend).mark_circle(size=60).encode(
            x="Fecha fin:T",
            y="Rendimiento %:Q",
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        ).add_params(nearest)

        rules = alt.Chart(df_plot).mark_rule(color='gray').encode(
            x="Fecha fin:T",
            tooltip=[
                alt.Tooltip("Fecha fin:T"),
                alt.Tooltip("Rendimiento %:Q", format=".2f"),
            ]
        ).transform_filter(nearest)

        chart = (
            line_rend +
            line_var +
            line_cvar +
            points +
            rules +
            zero_line
        ).properties(
            height=500
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # ----------------------------------------------- #
        #                  e) VIOLACIONES                 #
        # ----------------------------------------------- #

        st.subheader("Violaciones de VaR y CVaR")

        serie = df_rend[ticker].dropna()
        ventana = 252
        niveles_bt = [0.95, 0.99]

        resultados = []

        for alpha in niveles_bt:

            df_bt = MCF.calcular_violaciones(serie, ventana, alpha)

            n = len(df_bt)

            for col, nombre in zip(
                ["VaR Param", "CVaR Param", "VaR Hist", "CVaR Hist"],
                ["VaR Param", "CVaR Param", "VaR Hist", "CVaR Hist"]
            ):

                violaciones = (df_bt["Rendimiento"] < df_bt[col]).sum()
                porcentaje = violaciones / n * 100

                resultados.append({
                    "Nivel": f"{int(alpha*100)}%",
                    "Modelo": nombre,
                    "Violaciones": violaciones,
                    "Porcentaje": porcentaje
                })

        tabla = pd.DataFrame(resultados)

        st.write("Nota: Una buena estimación genera un porcentaje de violaciones menores al 2.5%."
                 " En caso de no cumplir con ello, sugerimos verificar el modelo.")

        st.dataframe(
            tabla.style
            .format({"Porcentaje": "{:.2f}%"})
            .apply(MCF.color_filas, axis=1),
            use_container_width=True,
            hide_index=True
        )

    with tabs[4]:
        # -------------------------------------------------- #
        #     f) VaR con volatilidad móvil normal            #
        # -------------------------------------------------- #

        st.subheader("VaR con Volatilidad Móvil")

        serie = df_rend[ticker].dropna()

        ventana_vol = 252

        niveles_significancia = [0.05, 0.01]

        mapping = {0.05: "95%", 0.01: "99%"}

        sigma_movil = serie.rolling(window=ventana_vol).std()

        df_var_vol = pd.DataFrame({
            "Fecha": serie.index,
            "Rendimiento": serie.values,
            "Volatilidad móvil": sigma_movil.values
        })

        for alpha_f in niveles_significancia:
            q_alpha = norm.ppf(alpha_f)

            nombre = mapping[alpha_f]

            df_var_vol[f"VaR Vol Móvil {nombre}"] = (
                q_alpha * sigma_movil
            ).shift(1).values

        df_var_vol = df_var_vol.dropna()

        df_var_vol["Rendimiento %"] = df_var_vol["Rendimiento"] * 100

        for alpha_f in niveles_significancia:
            nombre = mapping[alpha_f]

            df_var_vol[f"VaR Vol Móvil {nombre}"] = (
                df_var_vol[f"VaR Vol Móvil {nombre}"] * 100
            )

        st.write(
            "Se calcula el VaR usando una volatilidad móvil de 252 días y cuantiles de la normal estándar""" \
            " para niveles de significancia del 95% y 99%."
        )

        # ------------------------------------------- #
        #               TABLA Y GRÁFICA               #
        # ------------------------------------------- #

        df_plot = df_var_vol.copy()

        # DATASETS
        rend = df_plot[["Fecha", "Rendimiento %"]]

        var_cols = ["VaR Vol Móvil 95%", "VaR Vol Móvil 99%"]

        df_var = df_plot.melt(
            id_vars="Fecha",
            value_vars=var_cols,
            var_name="Serie",
            value_name="Valor"
        )

        # COLORES CONSISTENTES
        color_scale = alt.Scale(
            domain=["VaR Vol Móvil 95%", "VaR Vol Móvil 99%"],
            range=["#EF5350", "#B71C1C"]  # rojo claro / oscuro
        )

        # RENDIMIENTOS
        line_rend = alt.Chart(rend).mark_line(
            color="#959595",
            opacity=0.6,
            strokeWidth=1.5
        ).encode(
            x=alt.X("Fecha:T", title="Fecha"),
            y=alt.Y("Rendimiento %:Q", title="Rendimiento (%)"),
            tooltip=["Fecha:T", "Rendimiento %"]
        )

        # VaR (PUNTEADO)
        line_var = alt.Chart(df_var).mark_line(
            strokeDash=[6, 4],
            strokeWidth=2.5
        ).encode(
            x="Fecha:T",
            y="Valor:Q",
            color=alt.Color(
                "Serie:N",
                scale=color_scale,
                legend=alt.Legend(title="VaR (Volatilidad Móvil)")
            ),
            tooltip=["Serie", "Valor"]
        )

        # LÍNEA CERO
        zero_line = alt.Chart(pd.DataFrame({"y":[0]})).mark_rule(
            color="black"
        ).encode(
            y="y:Q"
        )

        # FINAL       
        nearest = alt.selection_point(
            nearest=True,
            on="mouseover",
            fields=["Fecha"],
            empty=False
        )
       
        points = alt.Chart(rend).mark_circle(size=60).encode(
            x="Fecha:T",
            y="Rendimiento %:Q",
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        ).add_params(nearest)

        rules = alt.Chart(df_plot).mark_rule(color='gray').encode(
            x="Fecha:T",
            tooltip=[
                alt.Tooltip("Fecha:T"),
                alt.Tooltip("Rendimiento %:Q", format=".2f"),
            ]
        ).transform_filter(nearest)

        
        chart = (
            line_rend +
            line_var +
            points +
            rules +
            zero_line
        ).properties(
            height=500,
            title="VaR con Volatilidad Móvil"
        ).interactive()

        st.altair_chart(chart, use_container_width=True)

        # --------------------------------------- #
        #               VIOLACIONES               #
        # --------------------------------------- #

        resultados_f = []

        n_f = len(df_var_vol)

        for alpha_f in niveles_significancia:

            columna = f"VaR Vol Móvil {mapping[alpha_f]}"

            violaciones = df_var_vol["Rendimiento %"] < df_var_vol[columna]

            numero_violaciones = int(violaciones.sum())
            porcentaje_violaciones = (numero_violaciones / n_f) * 100

            resultados_f.append([
                mapping[alpha_f],
                columna,
                numero_violaciones,
                porcentaje_violaciones
            ])

        tabla_violaciones_f = pd.DataFrame(
            resultados_f,
            columns=[
                "Nivel",
                "Medida",
                "Número de violaciones",
                "Porcentaje de violaciones"
            ]
        )

        st.subheader("Violaciones del VaR con Volatilidad Móvil")

        st.dataframe(
            tabla_violaciones_f.style
            .format({"Porcentaje de violaciones": "{:.2f}%"}),
            use_container_width=True,
            hide_index=True
        )