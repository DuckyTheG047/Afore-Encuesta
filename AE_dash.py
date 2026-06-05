from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from AE_code import PREGUNTA, PREGUNTA_2, PREGUNTA_3, PREGUNTA_4, PREGUNTA_5, analizar_encuesta, extraer_palabras


st.set_page_config(
    page_title="AFORE Encuesta",
    page_icon="AE",
    layout="wide",
)


def build_top_words_df(counter: Counter, top_n: int = 15) -> pd.DataFrame:
    data = counter.most_common(top_n)
    return pd.DataFrame(data, columns=["Palabra", "Frecuencia"])


def build_top_words_counter_from_df(df: pd.DataFrame) -> Counter:
    counter = Counter()
    if df.empty:
        return counter

    for respuesta in df["Respuesta"]:
        if respuesta and respuesta != "[Sin respuesta]":
            counter.update(extraer_palabras(respuesta))
    return counter


def build_categories_df(counter_source) -> pd.DataFrame:
    if hasattr(counter_source, "most_common"):
        pairs = counter_source.most_common()
    else:
        pairs = list(counter_source.items())

    rows = [
        {"Categoria": categoria, "Respuestas": total}
        for categoria, total in pairs
    ]
    return pd.DataFrame(rows)


def build_results_df(resultados: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(resultados)
    if df.empty:
        return df

    df = df.rename(
        columns={
            "archivo_origen": "Archivo",
            "user_id": "User ID",
            "participant_name": "Participante",
            "status": "Status",
            "device": "Device",
            "genero": "Genero",
            "edad": "Edad",
            "conexion": "Conexion",
            "respuesta": "Respuesta",
            "categoria": "Categoria",
            "score": "Score",
            "coincidencias_texto": "Palabras detectadas",
        }
    )
    df["Respuesta"] = df["Respuesta"].fillna("").replace("", "[Sin respuesta]")
    df["Palabras detectadas"] = df["Palabras detectadas"].fillna("").replace("", "Sin coincidencias")
    return df[
        [
            "Archivo",
            "User ID",
            "Participante",
            "Status",
            "Genero",
            "Edad",
            "Device",
            "Conexion",
            "Categoria",
            "Score",
            "Palabras detectadas",
            "Respuesta",
        ]
    ]


def render_metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #fff8ef 0%, #f7eee0 100%);
            border: 1px solid #ead7bf;
            border-radius: 16px;
            padding: 12px 16px;
            min-height: 82px;
        ">
            <div style="
                font-size: 0.8rem;
                color: #7b5d3c;
                margin-bottom: 6px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            ">{label}</div>
            <div style="
                font-size: 1.65rem;
                font-weight: 700;
                color: #2c2014;
                line-height: 1.1;
                white-space: nowrap;
            ">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_word_cloud(counter: Counter, top_n: int = 35) -> None:
    palabras = counter.most_common(top_n)
    if not palabras:
        st.info("No hay palabras suficientes para construir la nube.")
        return

    max_freq = max(freq for _, freq in palabras)
    min_freq = min(freq for _, freq in palabras)
    spread = max(max_freq - min_freq, 1)
    palette = ["#6b4f2f", "#8a6338", "#a8732e", "#c08b3c", "#7f6042"]

    spans = []
    for idx, (palabra, freq) in enumerate(palabras):
        ratio = (freq - min_freq) / spread
        font_size = 0.95 + (ratio * 1.85)
        weight = 500 if ratio < 0.45 else 700
        rotation = "-2deg" if idx % 4 == 0 else "2deg" if idx % 5 == 0 else "0deg"
        color = palette[idx % len(palette)]
        spans.append(
            f'<span style="display:inline-block;font-size:{font_size:.2f}rem;'
            f'font-weight:{weight};color:{color};margin:0.2rem 0.55rem;'
            f'line-height:1.15;transform:rotate({rotation});white-space:nowrap;">'
            f"{palabra}</span>"
        )

    st.markdown(
        """
        <style>
        .word-cloud-box {
            background: #fffdf8;
            border: 1px solid #e4d4bd;
            border-radius: 20px;
            padding: 20px 18px;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .word-cloud-inner {
            text-align: center;
            max-width: 100%;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        (
            '<div class="word-cloud-box"><div class="word-cloud-inner">'
            + "".join(spans)
            + "</div></div>"
        ),
        unsafe_allow_html=True,
    )


def apply_base_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top right, rgba(235, 196, 138, 0.22), transparent 28%),
                linear-gradient(180deg, #f7f2e8 0%, #f2ebe0 45%, #efe5d8 100%);
        }
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 1.2rem;
            max-width: 96vw;
            padding-left: 1.2rem;
            padding-right: 1.2rem;
        }
        h1, h2, h3 {
            color: #2c2014;
        }
        div[data-testid="stDataFrame"] {
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid #e4d4bd;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(
    analisis: dict,
    resultados_df: pd.DataFrame,
    top_words_df: pd.DataFrame,
    categories_df: pd.DataFrame,
) -> None:
    st.title("Analisis de Respuestas de Encuesta")
    st.caption("Vista exploratoria para Afore Azteca")
    st.caption("Archivos integrados: " + " | ".join(analisis["archivos"]))

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #3a2a1f 0%, #68472d 100%);
            color: #fff8ef;
            border-radius: 24px;
            padding: 24px 26px;
            margin-bottom: 22px;
        ">
            <div style="font-size:0.9rem; opacity:0.82; margin-bottom:8px;">Pregunta en analisis</div>
            <div style="font-size:1.5rem; font-weight:700; line-height:1.3;">{analisis["pregunta"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Filtros")
    filter_cols = st.columns([1, 1, 1, 1.1], gap="large")
    with filter_cols[0]:
        categoria_seleccionada = st.selectbox(
            "Categoria",
            ["Todas"] + resultados_df["Categoria"].drop_duplicates().tolist(),
            index=0,
        )
    with filter_cols[1]:
        score_minimo = int(
            st.slider(
                "Score minimo",
                min_value=int(resultados_df["Score"].min()) if not resultados_df.empty else 0,
                max_value=int(resultados_df["Score"].max()) if not resultados_df.empty else 0,
                value=int(resultados_df["Score"].min()) if not resultados_df.empty else 0,
                step=1,
            )
        )
    with filter_cols[2]:
        genero_seleccionado = st.selectbox(
            "Genero",
            ["Todos"] + resultados_df["Genero"].drop_duplicates().tolist(),
            index=0,
        )
    with filter_cols[3]:
        status_seleccionado = st.selectbox(
            "Status",
            ["Todos"] + resultados_df["Status"].drop_duplicates().tolist(),
            index=0,
        )

    filtrado = resultados_df.copy()
    if categoria_seleccionada != "Todas":
        filtrado = filtrado[filtrado["Categoria"] == categoria_seleccionada]
    filtrado = filtrado[filtrado["Score"] >= score_minimo]
    if genero_seleccionado != "Todos":
        filtrado = filtrado[filtrado["Genero"] == genero_seleccionado]
    if status_seleccionado != "Todos":
        filtrado = filtrado[filtrado["Status"] == status_seleccionado]

    total_respuestas = len(filtrado)
    respuestas_con_registro = int((filtrado["Respuesta"] != "[Sin respuesta]").sum())
    categorias_detectadas = int(filtrado["Categoria"].nunique()) if not filtrado.empty else 0
    score_promedio = f'{filtrado["Score"].mean():.2f}' if not filtrado.empty else "0.00"
    if filtrado.empty:
        respuesta_top = "Sin datos"
    else:
        respuesta_top = filtrado["Categoria"].value_counts().index[0]

    metric_cols = st.columns(5)
    with metric_cols[0]:
        render_metric_card("Total de respuestas", str(total_respuestas))
    with metric_cols[1]:
        render_metric_card("Con respuesta registrada", str(respuestas_con_registro))
    with metric_cols[2]:
        render_metric_card("Score promedio", score_promedio)
    with metric_cols[3]:
        render_metric_card("Numero de categorias", str(categorias_detectadas))
    with metric_cols[4]:
        render_metric_card("Categoria dominante", str(respuesta_top))

    categories_filtrado_df = build_categories_df(filtrado["Categoria"].value_counts())
    top_words_filtrado_counter = build_top_words_counter_from_df(filtrado)

    st.subheader("Distribucion de Categorias")
    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        if categories_filtrado_df.empty:
            st.info("No hay respuestas para analizar.")
        else:
            st.bar_chart(
                categories_filtrado_df.set_index("Categoria")["Respuestas"],
                height=430,
            )

    with chart_right:
        if categories_filtrado_df.empty:
            st.info("No hay respuestas para analizar.")
        else:
            fig, ax = plt.subplots(figsize=(6, 4.3))
            ax.pie(
                categories_filtrado_df["Respuestas"],
                labels=categories_filtrado_df["Categoria"],
                autopct="%1.0f%%",
                startangle=90,
                textprops={"fontsize": 9},
            )
            ax.axis("equal")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    table_left, table_right = st.columns(2, gap="large")

    with table_left:
        st.markdown("#### Tabla de Categorias")
        st.dataframe(
            categories_filtrado_df,
            use_container_width=True,
            hide_index=True,
            height=320,
        )

    with table_right:
        st.markdown("#### Respuestas Clasificadas")
        if filtrado.empty:
            st.info("No se encontraron respuestas en la pregunta seleccionada.")
        else:
            st.dataframe(
                filtrado,
                use_container_width=True,
                hide_index=True,
                height=320,
            )

    st.subheader("Palabras Mas Repetidas")
    render_word_cloud(top_words_filtrado_counter)

    st.markdown("### Demograficos")
    chart_cols = st.columns(3, gap="large")

    with chart_cols[0]:
        st.markdown("#### Edad")
        edades_validas = filtrado["Edad"].dropna()
        if edades_validas.empty:
            st.info("No hay edades disponibles para el filtro actual.")
        else:
            edad_bins = pd.cut(
                edades_validas,
                bins=[17, 24, 34, 44, 54, 64, 100],
                labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
                include_lowest=True,
            )
            edad_chart = edad_bins.value_counts().sort_index().rename("Participantes")
            st.bar_chart(edad_chart, height=320)
            st.dataframe(
                edad_chart.reset_index().rename(columns={"index": "Rango de edad"}),
                hide_index=True,
                use_container_width=True,
            )

    with chart_cols[1]:
        st.markdown("#### Genero")
        genero_chart = filtrado["Genero"].fillna("Sin dato").value_counts().rename("Participantes")
        st.bar_chart(genero_chart, height=320)
        st.dataframe(
            genero_chart.reset_index().rename(columns={"index": "Genero"}),
            hide_index=True,
            use_container_width=True,
        )

    with chart_cols[2]:
        st.markdown("#### Device")
        device_chart = (
            filtrado["Device"]
            .fillna("Sin dato")
            .replace("", "Sin dato")
            .value_counts()
            .rename("Participantes")
        )
        st.bar_chart(device_chart, height=320)
        st.dataframe(
            device_chart.reset_index().rename(columns={"index": "Device"}),
            hide_index=True,
            use_container_width=True,
        )

    if analisis["pregunta"] in {PREGUNTA_4, PREGUNTA_5}:
        st.markdown("### Conexion con el Anuncio")
        conexion_validas = filtrado.dropna(subset=["Conexion"]).copy()
        promedio_conexion = (
            f'{conexion_validas["Conexion"].mean():.2f}'
            if not conexion_validas.empty
            else "Sin dato"
        )
        conexion_cols = st.columns([0.9, 1.1, 1.1], gap="large")

        with conexion_cols[0]:
            render_metric_card("Promedio de conexion", str(promedio_conexion))

        with conexion_cols[1]:
            st.markdown("#### Categoria vs Conexion Promedio")
            if conexion_validas.empty:
                st.info("No hay respuestas de conexion para el filtro actual.")
            else:
                categoria_conexion = (
                    conexion_validas.groupby("Categoria", dropna=False)["Conexion"]
                    .mean()
                    .sort_values(ascending=False)
                    .round(2)
                )
                fig_cat, ax_cat = plt.subplots(figsize=(6, 4.2))
                x_cat = list(range(len(categoria_conexion.index)))
                y_cat = categoria_conexion.values
                ax_cat.scatter(
                    x_cat,
                    y_cat,
                    s=140,
                    color="#a8732e",
                    edgecolors="#6b4f2f",
                    linewidths=1.2,
                    alpha=0.9,
                )
                ax_cat.set_xticks(x_cat)
                ax_cat.set_xticklabels(categoria_conexion.index, rotation=35, ha="right")
                ax_cat.set_ylabel("Promedio de conexion")
                ax_cat.set_xlabel("Categoria")
                ax_cat.set_ylim(0, 5.2)
                ax_cat.grid(axis="y", linestyle="--", alpha=0.3)
                st.pyplot(fig_cat, use_container_width=True)
                plt.close(fig_cat)
                st.dataframe(
                    categoria_conexion.reset_index().rename(columns={"Conexion": "Promedio de conexion"}),
                    hide_index=True,
                    use_container_width=True,
                )

        with conexion_cols[2]:
            st.markdown("#### Edad vs Conexion Promedio")
            if conexion_validas.empty or conexion_validas["Edad"].dropna().empty:
                st.info("No hay edades con dato de conexion para el filtro actual.")
            else:
                edad_bins_conexion = pd.cut(
                    conexion_validas["Edad"],
                    bins=[17, 24, 34, 44, 54, 64, 100],
                    labels=["18-24", "25-34", "35-44", "45-54", "55-64", "65+"],
                    include_lowest=True,
                )
                edad_conexion = (
                    conexion_validas.assign(Rango_Edad=edad_bins_conexion)
                    .dropna(subset=["Rango_Edad"])
                    .groupby("Rango_Edad", observed=False)["Conexion"]
                    .mean()
                    .round(2)
                )
                fig_age, ax_age = plt.subplots(figsize=(6, 4.2))
                x_age = list(range(len(edad_conexion.index)))
                y_age = edad_conexion.values
                ax_age.scatter(
                    x_age,
                    y_age,
                    s=140,
                    color="#7f6042",
                    edgecolors="#3a2a1f",
                    linewidths=1.2,
                    alpha=0.9,
                )
                ax_age.set_xticks(x_age)
                ax_age.set_xticklabels(edad_conexion.index, rotation=0)
                ax_age.set_ylabel("Promedio de conexion")
                ax_age.set_xlabel("Rango de edad")
                ax_age.set_ylim(0, 5.2)
                ax_age.grid(axis="y", linestyle="--", alpha=0.3)
                st.pyplot(fig_age, use_container_width=True)
                plt.close(fig_age)
                st.dataframe(
                    edad_conexion.reset_index().rename(
                        columns={"Rango_Edad": "Rango de edad", "Conexion": "Promedio de conexion"}
                    ),
                    hide_index=True,
                    use_container_width=True,
                )

    st.markdown("### Tabla Base Filtrada")
    st.dataframe(
        filtrado[
            [
                "Archivo",
                "User ID",
                "Status",
                "Genero",
                "Edad",
                "Device",
                "Conexion",
                "Categoria",
                "Score",
                "Respuesta",
            ]
        ],
        use_container_width=True,
        hide_index=True,
        height=360,
    )


def main() -> None:
    apply_base_styles()

    pagina = st.sidebar.radio(
        "Paginas",
        [
            "Pregunta 1",
            "Pregunta 2",
            "Pregunta 3",
            "Comunicacion 1",
            "Comunicacion 2",
        ],
        index=0,
    )

    if pagina == "Pregunta 1":
        pregunta = PREGUNTA
    elif pagina == "Pregunta 2":
        pregunta = PREGUNTA_2
    elif pagina == "Pregunta 3":
        pregunta = PREGUNTA_3
    elif pagina == "Comunicacion 1":
        pregunta = PREGUNTA_4
    else:
        pregunta = PREGUNTA_5

    analisis = analizar_encuesta(pregunta=pregunta)
    resultados_df = build_results_df(analisis["resultados"])
    top_words_df = build_top_words_df(analisis["top_palabras"])
    categories_df = build_categories_df(analisis["conteo_categorias"])
    render_dashboard(analisis, resultados_df, top_words_df, categories_df)


if __name__ == "__main__":
    main()
