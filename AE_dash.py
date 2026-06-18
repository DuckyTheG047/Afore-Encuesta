from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd
from PIL import Image
import streamlit as st

from AE_code import PREGUNTA, PREGUNTA_2, PREGUNTA_3, PREGUNTA_4, PREGUNTA_5, PREGUNTA_6, PREGUNTA_7, PREGUNTA_8, PREGUNTA_9, PREGUNTA_10, PREGUNTA_11, MAPA_CATEGORIAS_ESPERADAS, analizar_confianza_afores, analizar_descripcion_azteca, analizar_encuesta, calcular_metricas_mensaje, extraer_palabras


st.set_page_config(
    page_title="AFORE Encuesta",
    page_icon="AE",
    layout="wide",
)

PREGUNTA_IMAGE_MAP = {
    PREGUNTA: "IMAGENES_PREGUNTAS/pregunta_1.jpeg",
    PREGUNTA_2: "IMAGENES_PREGUNTAS/pregunta_2.jpeg",
    PREGUNTA_3: "IMAGENES_PREGUNTAS/pregunta_3.jpeg",
    PREGUNTA_4: "IMAGENES_PREGUNTAS/com_1.jpeg",
    PREGUNTA_5: "IMAGENES_PREGUNTAS/com_2.jpeg",
    PREGUNTA_6: "IMAGENES_PREGUNTAS/com_3.jpeg",
    PREGUNTA_7: "IMAGENES_PREGUNTAS/com_4.jpeg",
    PREGUNTA_8: "IMAGENES_PREGUNTAS/com_5.jpeg",
    PREGUNTA_9: "IMAGENES_PREGUNTAS/com_6.jpeg",
    PREGUNTA_10: "IMAGENES_PREGUNTAS/com_7.jpeg",
    PREGUNTA_11: "IMAGENES_PREGUNTAS/com_8.jpeg",
}


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


def build_connection_words_counter(df: pd.DataFrame, min_conexion: float = 4, max_conexion: Optional[float] = None) -> Counter:
    counter = Counter()
    if df.empty or "Conexion" not in df.columns:
        return counter

    subset = df.dropna(subset=["Conexion"]).copy()
    subset = subset[subset["Conexion"] >= min_conexion]
    if max_conexion is not None:
        subset = subset[subset["Conexion"] <= max_conexion]

    for respuesta in subset["Respuesta"]:
        if respuesta and respuesta != "[Sin respuesta]":
            counter.update(extraer_palabras(respuesta))
    return counter


def build_word_frequency_df(counter: Counter, total_counter: Counter, top_n: int = 12) -> pd.DataFrame:
    rows = []
    for palabra, frecuencia in counter.most_common(top_n):
        rows.append(
            {
                "Palabra": palabra,
                "Frecuencia alta conexion": frecuencia,
                "Frecuencia total": total_counter.get(palabra, 0),
            }
        )
    return pd.DataFrame(rows)


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


def build_results_df(resultados: List[Dict]) -> pd.DataFrame:
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


def render_overview() -> None:
    resumen = analizar_confianza_afores()
    descripcion_azteca_counter = analizar_descripcion_azteca()
    menciones_df = pd.DataFrame(resumen["menciones"])
    afores_df = build_categories_df(resumen["conteo_afores"]).rename(
        columns={"Categoria": "AFORE", "Respuestas": "Menciones"}
    )
    razones_df = build_categories_df(resumen["conteo_razones"]).rename(
        columns={"Categoria": "Razon", "Respuestas": "Menciones"}
    )

    st.title("Overview")
    st.caption("Resumen general del estudio de AFORES")

    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #3a2a1f 0%, #725034 100%);
            color: #fff8ef;
            border-radius: 24px;
            padding: 28px 28px;
            margin-bottom: 22px;
        ">
            <div style="font-size:0.92rem; opacity:0.84; margin-bottom:10px;">Pagina principal</div>
            <div style="font-size:1.8rem; font-weight:700; line-height:1.2; margin-bottom:10px;">
                Panorama general sobre percepcion, comunicacion y conexion con AFORES
            </div>
            <div style="font-size:1rem; line-height:1.5; opacity:0.92;">
                Esta pagina funcionara como punto de entrada para sintetizar los hallazgos mas relevantes
                del estudio antes de entrar al detalle por anuncio y por pregunta.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_participantes = int(menciones_df["user_id"].nunique()) if not menciones_df.empty else 0
    total_afores = int(afores_df["AFORE"].nunique()) if not afores_df.empty else 0
    afore_lider = afores_df.iloc[0]["AFORE"] if not afores_df.empty else "Sin dato"
    razon_top = razones_df.iloc[0]["Razon"] if not razones_df.empty else "Sin dato"

    top_cols = st.columns(4, gap="large")
    with top_cols[0]:
        render_metric_card("Participantes con respuesta", str(total_participantes))
    with top_cols[1]:
        render_metric_card("AFOREs mencionadas", str(total_afores))
    with top_cols[2]:
        render_metric_card("AFORE lider", str(afore_lider))
    with top_cols[3]:
        render_metric_card("Razon dominante", str(razon_top))

    st.markdown("### Filtros de Confianza")
    filtro_cols = st.columns([1, 1], gap="large")
    with filtro_cols[0]:
        afore_filtro = st.selectbox(
            "Filtrar por AFORE",
            ["Todas"] + sorted(menciones_df["afore_nombre"].dropna().unique().tolist()) if not menciones_df.empty else ["Todas"],
            index=0,
        )
    with filtro_cols[1]:
        razon_filtro = st.selectbox(
            "Filtrar por motivo",
            ["Todos"] + sorted(menciones_df["razon_categoria"].dropna().unique().tolist()) if not menciones_df.empty else ["Todos"],
            index=0,
        )

    menciones_filtradas = menciones_df.copy()
    if afore_filtro != "Todas":
        menciones_filtradas = menciones_filtradas[menciones_filtradas["afore_nombre"] == afore_filtro]
    if razon_filtro != "Todos":
        menciones_filtradas = menciones_filtradas[menciones_filtradas["razon_categoria"] == razon_filtro]

    afores_df = (
        menciones_filtradas["afore_nombre"].value_counts()
        .rename_axis("AFORE")
        .reset_index(name="Menciones")
    ) if not menciones_filtradas.empty else pd.DataFrame(columns=["AFORE", "Menciones"])
    razones_df = (
        menciones_filtradas["razon_categoria"].value_counts()
        .rename_axis("Razon")
        .reset_index(name="Menciones")
    ) if not menciones_filtradas.empty else pd.DataFrame(columns=["Razon", "Menciones"])

    st.markdown("### Ranking de Confianza en AFOREs")
    rank_cols = st.columns([0.95, 1.05], gap="large")
    with rank_cols[0]:
        st.markdown("#### Top AFOREs")
        if afores_df.empty:
            st.info("No hay menciones de AFOREs disponibles.")
        else:
            for _, row in afores_df.head(6).iterrows():
                logo_path = (
                    menciones_df.loc[menciones_df["afore_nombre"] == row["AFORE"], "logo_path"]
                    .dropna()
                    .astype(str)
                    .iloc[0]
                )
                card_cols = st.columns([0.22, 0.58, 0.20], gap="small")
                with card_cols[0]:
                    if logo_path:
                        st.image(logo_path, use_container_width=True)
                with card_cols[1]:
                    st.markdown(f"**{row['AFORE']}**")
                with card_cols[2]:
                    st.metric("Menciones", int(row["Menciones"]))
    with rank_cols[1]:
        st.markdown("#### Distribucion de menciones")
        if afores_df.empty:
            st.info("No hay datos para graficar.")
        else:
            st.bar_chart(afores_df.set_index("AFORE")["Menciones"], height=360)
            st.dataframe(afores_df, use_container_width=True, hide_index=True, height=260)

    st.markdown("### Motivos de Confianza")
    razones_cols = st.columns([1, 1], gap="large")
    with razones_cols[0]:
        st.markdown("#### Razones mas frecuentes")
        if razones_df.empty:
            st.info("No hay respuestas de motivos disponibles.")
        else:
            st.bar_chart(razones_df.set_index("Razon")["Menciones"], height=320)
            st.dataframe(razones_df, use_container_width=True, hide_index=True, height=240)
    with razones_cols[1]:
        st.markdown("#### Nube de palabras de motivos")
        if menciones_filtradas.empty:
            st.info("No hay texto suficiente para construir la nube.")
        else:
            razones_counter = Counter()
            for texto in menciones_filtradas["razon_texto"].fillna(""):
                razones_counter.update(extraer_palabras(texto))
            render_word_cloud(razones_counter, top_n=40)

    st.markdown("### Cruce AFORE x Motivo")
    if menciones_filtradas.empty:
        st.info("No hay suficientes datos para el cruce.")
    else:
        matriz_df = (
            menciones_filtradas.groupby(["afore_nombre", "razon_categoria"])
            .size()
            .reset_index(name="Menciones")
        )
        heatmap_df = (
            matriz_df.pivot(index="afore_nombre", columns="razon_categoria", values="Menciones")
            .fillna(0)
            .astype(int)
        )
        cruces_cols = st.columns([1.15, 0.85], gap="large")
        with cruces_cols[0]:
            fig, ax = plt.subplots(figsize=(10, 5.8))
            im = ax.imshow(heatmap_df.values, cmap="YlOrBr", aspect="auto")
            ax.set_xticks(range(len(heatmap_df.columns)))
            ax.set_xticklabels(heatmap_df.columns, rotation=35, ha="right")
            ax.set_yticks(range(len(heatmap_df.index)))
            ax.set_yticklabels(heatmap_df.index)
            ax.set_xlabel("Motivo de confianza")
            ax.set_ylabel("AFORE")
            for i in range(len(heatmap_df.index)):
                for j in range(len(heatmap_df.columns)):
                    ax.text(j, i, int(heatmap_df.iloc[i, j]), ha="center", va="center", color="#2c2014", fontsize=8)
            fig.colorbar(im, ax=ax, fraction=0.028, pad=0.02)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        with cruces_cols[1]:
            stacked = heatmap_df.copy()
            fig2, ax2 = plt.subplots(figsize=(8, 5.8))
            stacked.plot(kind="barh", stacked=True, ax=ax2)
            ax2.set_xlabel("Menciones")
            ax2.set_ylabel("AFORE")
            fig2.tight_layout()
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)

    st.markdown("### Palabras para Describir Afore Azteca")
    render_word_cloud(descripcion_azteca_counter, top_n=40)

    st.markdown("### Evidencia de Respuestas")
    if menciones_filtradas.empty:
        st.info("No hay evidencia para mostrar.")
    else:
        evidencia_df = menciones_filtradas.rename(
            columns={
                "archivo_origen": "Archivo",
                "user_id": "User ID",
                "participant_name": "Participante",
                "status": "Status",
                "afore_nombre": "AFORE",
                "ranking_eleccion": "Orden",
                "razon_categoria": "Categoria de razon",
                "razon_texto": "Texto original",
            }
        )
        st.dataframe(
            evidencia_df[
                [
                    "Archivo",
                    "User ID",
                    "Participante",
                    "Status",
                    "AFORE",
                    "Orden",
                    "Categoria de razon",
                    "Texto original",
                ]
            ],
            use_container_width=True,
            hide_index=True,
            height=360,
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

    image_path = PREGUNTA_IMAGE_MAP.get(analisis["pregunta"])
    if image_path and Path(image_path).exists():
        st.markdown("### Imagen del Anuncio")
        image_width_ratio = 0.46
        try:
            with Image.open(image_path) as img:
                width, height = img.size
            if height > width:
                image_width_ratio = 0.30
            elif height > width * 0.8:
                image_width_ratio = 0.38
        except Exception:
            image_width_ratio = 0.46

        side_ratio = (1 - image_width_ratio) / 2
        image_cols = st.columns([side_ratio, image_width_ratio, side_ratio])
        with image_cols[1]:
            st.image(image_path, use_container_width=True)

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

    if analisis["pregunta"] in {PREGUNTA_4, PREGUNTA_5, PREGUNTA_6, PREGUNTA_7, PREGUNTA_8, PREGUNTA_9, PREGUNTA_10, PREGUNTA_11}:
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

    if analisis["pregunta"] in MAPA_CATEGORIAS_ESPERADAS:
        metricas_mensaje = calcular_metricas_mensaje(
            [
                {
                    "respuesta": row["Respuesta"] if row["Respuesta"] != "[Sin respuesta]" else "",
                    "categoria": row["Categoria"],
                    "conexion": row["Conexion"],
                }
                for _, row in filtrado.iterrows()
            ],
            analisis["pregunta"],
        )
        reconocimiento_pct = f'{metricas_mensaje["reconocimiento_correcto"] * 100:.1f}%'
        confusion_pct = f'{metricas_mensaje["tasa_confusion"] * 100:.1f}%'
        claridad_score = f'{metricas_mensaje["indice_claridad"]:.1f}'
        categorias_esperadas_texto = ", ".join(metricas_mensaje["categorias_esperadas"])

        st.markdown("### KPIs de Claridad del Mensaje")
        st.caption("Categorias principales esperadas: " + categorias_esperadas_texto)
        clarity_cols = st.columns(4, gap="large")
        with clarity_cols[0]:
            render_metric_card("Reconocimiento correcto", reconocimiento_pct)
        with clarity_cols[1]:
            render_metric_card("Tasa de confusion", confusion_pct)
        with clarity_cols[2]:
            render_metric_card("Indice de claridad", claridad_score)
        with clarity_cols[3]:
            render_metric_card("Alta conexion (4-5)", str(metricas_mensaje["conteo_alta_conexion"]))

        clarity_viz_cols = st.columns([0.9, 1.1], gap="large")
        with clarity_viz_cols[0]:
            st.markdown("#### Lectura del Mensaje")
            lectura_df = pd.DataFrame(
                [
                    {"Segmento": "Reconocimiento correcto", "Porcentaje": metricas_mensaje["reconocimiento_correcto"] * 100},
                    {"Segmento": "Confusion", "Porcentaje": metricas_mensaje["tasa_confusion"] * 100},
                    {"Segmento": "Share categoria dominante", "Porcentaje": metricas_mensaje["share_categoria_dominante"] * 100},
                ]
            )
            st.bar_chart(lectura_df.set_index("Segmento")["Porcentaje"], height=300)
            st.dataframe(lectura_df.round(1), use_container_width=True, hide_index=True, height=180)

        with clarity_viz_cols[1]:
            st.markdown("#### Reconocimiento vs Confusion")
            restante = max(
                0.0,
                100
                - (metricas_mensaje["reconocimiento_correcto"] * 100)
                - (metricas_mensaje["tasa_confusion"] * 100),
            )
            fig_kpi, ax_kpi = plt.subplots(figsize=(6.2, 4.2))
            ax_kpi.pie(
                [
                    metricas_mensaje["reconocimiento_correcto"] * 100,
                    metricas_mensaje["tasa_confusion"] * 100,
                    restante,
                ],
                labels=["Correcto", "Confusion", "Resto"],
                autopct="%1.0f%%",
                startangle=90,
                colors=["#a8732e", "#7f6042", "#e7d7c1"],
                textprops={"fontsize": 9},
            )
            ax_kpi.axis("equal")
            st.pyplot(fig_kpi, use_container_width=True)
            plt.close(fig_kpi)

        st.markdown("### Palabras Asociadas a Alta Conexion")
        alta_conexion_counter = build_connection_words_counter(filtrado, min_conexion=4)
        palabras_cols = st.columns([1.05, 0.95], gap="large")
        with palabras_cols[0]:
            render_word_cloud(alta_conexion_counter, top_n=35)
        with palabras_cols[1]:
            palabras_alta_df = build_word_frequency_df(alta_conexion_counter, top_words_filtrado_counter, top_n=12)
            if palabras_alta_df.empty:
                st.info("No hay suficientes respuestas con alta conexion para construir esta vista.")
            else:
                st.dataframe(
                    palabras_alta_df,
                    use_container_width=True,
                    hide_index=True,
                    height=300,
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
            "Overview",
            "Pregunta 1",
            "Pregunta 2",
            "Pregunta 3",
            "Comunicacion 1",
            "Comunicacion 2",
            "Comunicacion 3",
            "Comunicacion 4",
            "Comunicacion 5",
            "Comunicacion 6",
            "Comunicacion 7",
            "Comunicacion 8",
        ],
        index=0,
    )

    if pagina == "Overview":
        render_overview()
        return
    elif pagina == "Pregunta 1":
        pregunta = PREGUNTA
    elif pagina == "Pregunta 2":
        pregunta = PREGUNTA_2
    elif pagina == "Pregunta 3":
        pregunta = PREGUNTA_3
    elif pagina == "Comunicacion 1":
        pregunta = PREGUNTA_4
    elif pagina == "Comunicacion 2":
        pregunta = PREGUNTA_5
    elif pagina == "Comunicacion 3":
        pregunta = PREGUNTA_6
    elif pagina == "Comunicacion 4":
        pregunta = PREGUNTA_7
    elif pagina == "Comunicacion 5":
        pregunta = PREGUNTA_8
    elif pagina == "Comunicacion 6":
        pregunta = PREGUNTA_9
    elif pagina == "Comunicacion 7":
        pregunta = PREGUNTA_10
    else:
        pregunta = PREGUNTA_11

    analisis = analizar_encuesta(pregunta=pregunta)
    resultados_df = build_results_df(analisis["resultados"])
    top_words_df = build_top_words_df(analisis["top_palabras"])
    categories_df = build_categories_df(analisis["conteo_categorias"])
    render_dashboard(analisis, resultados_df, top_words_df, categories_df)


if __name__ == "__main__":
    main()
