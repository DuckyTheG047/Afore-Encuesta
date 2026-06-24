import csv
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path


CSV_PATHS = [
    "ARCHIVOS/VF/Encuesta_1.csv",
    "ARCHIVOS/VF/Encuesta_2.csv",
    "ARCHIVOS/VF/Encuesta_3.csv",
]
PREGUNTA = "¿Qué producto crees que promociona la imagen del siguiente anuncio?"
PREGUNTA_2 = "¿Qué producto crees que promociona la imagen del siguiente anuncio? 1"
PREGUNTA_3 = "¿Qué producto crees que promociona la imagen del siguiente anuncio? 2"
PREGUNTA_4 = "¿Qué te comunica el anuncio anterior?"
PREGUNTA_5 = "¿Qué te comunica el anuncio anterior? 1"
PREGUNTA_6 = "¿Qué te comunica el anuncio anterior? 2"
PREGUNTA_7 = "¿Qué te comunica el anuncio anterior? 3"
PREGUNTA_8 = "¿Qué te comunica el anuncio anterior? 4"
PREGUNTA_9 = "¿Qué te comunica el anuncio anterior? 5"
PREGUNTA_10 = "¿Qué te comunica el anuncio anterior? 6"
PREGUNTA_11 = "¿Qué te comunica el anuncio anterior? 7"
PREGUNTA_CONEXION_1 = "¿Qué tanto conectó contigo? (out of 5)"
PREGUNTA_CONEXION_2 = "¿Qué tanto conectó contigo? (out of 5) 1"
PREGUNTA_CONEXION_3 = "¿Qué tanto conectó contigo? (out of 5) 2"
PREGUNTA_CONEXION_4 = "¿Qué tanto conectó contigo? (out of 5) 3"
PREGUNTA_CONEXION_5 = "¿Qué tanto conectó contigo? (out of 5) 4"
PREGUNTA_CONEXION_6 = "¿Qué tanto conectó contigo? (out of 5) 5"
PREGUNTA_CONEXION_7 = "¿Qué tanto conectó contigo? (out of 5) 6"
PREGUNTA_CONEXION_8 = "¿Qué tanto conectó contigo? (out of 5) 7"
PREGUNTA_CONFIANZA_AFORE = "¿Qué AFORE te da más confianza? \nEscoge máximo 3 "
PREGUNTA_CONFIANZA_POR_QUE = "¿Por qué?"
PREGUNTA_DESCRIPCION_AZTECA = "¿Cuáles son las 3 palabras con las que describirías Afore Azteca?"

# Categorias para preguntas sobre que producto creen que promociona el anuncio.
CATEGORIAS_PRODUCTO_RAW = {
    "AFORE / ahorro / retiro": """
        afore, afores, ahorro, ahorros, retiro, jubilacion, pension,
        futuro, vejez, ahorro para el retiro, plan de retiro, fondo de ahorro,
        seguro de vida
    """,
    "Banco / financiero": """
        banco, bancos, tarjeta, tarjetas, tarjeta de credito, credito,
        financiera, dinero, rendimiento, rendimientos, servicio bancario, inversiones, inversion,
        financiamiento, financiamientos, prestamo, prestamos
    """,
    "Auto / seguro / movilidad": """
        auto, autos, carro, carros, viaje, viajes, viajar, movilidad,
        seguro, seguros, seguro de auto, seguro de vida, vacaciones, automoviles,
        venta automotriz, automotriz, coche, coches, transporte, vehículo, automóvil
    """,
    "Apuestas / casino / juegos": """
        apuestas, apuesta, casino, monedas, moneda, juegos, juego,
        apuestas en linea, casino en linea, bitcoin, bitcoins,
        criptomoneda, criptomonedas
    """,
    "Tecnologia / celular / app": """
        celular, celulares, telefono, telefonos, app, apps, plataforma,
        aplicacion, aplicaciones, electronica, electronico, electronicos, tecnologia, tecnología,
        electrónica
    """,
    "Salud / dentista": """
        pasta, pasta dental, pasta de dientes, dientes, diente, dentista,
        dentistas, deentistas, dental, odontologia, odontologico,
        dentadura, blanqueamiento, whitening, teeth cleaning
    """,
    "Emocional / estilo de vida": """
        feliz, felicidad, sonrisa, sonriente, vida, persona, personas,
        bienestar, bienestar personal, seguridad personal, confort, comfort, emoción, emociones,
        descanso
    """,
    "Uso personal / Cuidado personal": """
        tintes, tintes, tinte para el cabello, tinte para el pelo, tinte para canas, máquina, 
        máquina cortadora, hombres, cuidado personal,
        tinte para barba, coloracion, productos de limpieza, productos de limpieza, 
        limpieza del hogar, limpieza para el hogar, Máquina cortadora para hombres, minoxidil,
        tele, teles, electrodoméstico, electrodomésticos, hogar, cuidado personal, cuidado del hogar
    """,
}

# Categorias para preguntas sobre que comunica el anuncio.
CATEGORIAS_COMUNICACION_RAW = {
    "Ahorro / retiro / futuro": """
        ahorro, ahorrar, ahorros, retiro, jubilacion, pension, futuro,
        vejez, despues de trabajar, ahorro voluntario, tu vejez, afores, afore, dinero, ahorre,
        expectativa, expectativas, afire, sueño, sueños, tranquilidad, bienestar, bienestar futuro, seguridad futura, calidad de vida futura,
        elahorro, paz, posibilidades
    """,
    "Confianza / seguridad / respaldo": """
        confianza, confiable, seguridad, seguro, tranquilidad, respaldo,
        apoyo, protegido, protegida, estable, estabilidad, segura, calidad, bueno, confiado,
        sonrisa, felicidad, felicidades, inversión, inversion, mejor, claridad, atractivo,
        interesante, solvente, comprar, poder, oportunidad, empatico, empatia, alentador, confiables,
        reconocidos, reconocidas, rendimiento, beneficios, beneficioso, beneficiosa, respaldo institucional, respaldo del gobierno,
        sincero, informacion, que quiere, que quieren, familia, familiar, oportunidad, oportunidades,
        agradable, seguimiento
    """,
    "Urgencia / conciencia / tiempo": """
        tiempo, tarde, temprano, ahora, hoy, urgencia, conciencia,
        no dejarlo al ultimo, antes, despues, aprovechar el tiempo, prevencion, prevision, esperar,
        plan, early age, small amounts, retire, retiro, consciencia, no tiene que estar uno estresado,
        you can still make your contributions, importante hacerlo pronto, puntualidad, nostalgia, al estar viejo

    """,
    "Facilidad / accesibilidad": """
        facil, facilidad, sencillo, sencilla, accesible, cambiar,
        cambiarte, ayuda, sucursales, atencion, acompanamiento, resolver dudas, accesible, 
        accesibilidad, informativo, disponible, disponibilidad, accessibility, cualquier momento,
        facil, faciles, ideal, cercania del producto, que puedo acudir rápido a cualquier sucursal,
        opciones

    """,
    "Accion concreta / ahorro voluntario": """
        empezar, comenzar, aportaciones, aportacion, voluntario, voluntarias,
        pesos, invertir, meter dinero, ahorrar desde hoy, mover, mueva, mueva a,
        cambies, cambiar, sugerencia, hacer, haz, haga, hazlo, ahora, esperar, future, cambio,
        meterme a profuturo, curioso, curiosidad, trabajo
    """,
    "Bienestar / calidad de vida": """
        vivir bien, vida, disfrutar, viajar, libertad financiera, negocio,
        emprendimiento, tranquilidad futura, calidad de vida, productiva, feliz, yo de mas grande,
        viaje, viajes, ventas, delicadeza, gusto, tranquilidad, tranquiidad, servicio, colgate, movilidad,
        deseo
    """,
    "Percepcion negativa / confusion": """
        fraude, estafa, inseguridad, miedo, desconfianza, confusion, confuso,
        cuestionamientos, dudoso, complicado, confusión, angustia, ansiedad, preocupacion, no me gusto,
        desenfocado, desenfoque, malo, nada, mala, tristeza, duda, mucho texto, aburrido,
        malestar, estres, cansancio, indiferencia, indiferente, no termine, no se entiende, no entendi,
        no esta claro, mal, confunde, confuso, confusa, difícil visualizar, promocionar, informar, no confio,
        desesperanza, no me gusta, no le entendi, no lo entendi, extraño, comunicacion, no pude, no lo pude
    """,
}

MAPA_CATEGORIAS_POR_PREGUNTA = {
    PREGUNTA: CATEGORIAS_PRODUCTO_RAW,
    PREGUNTA_2: CATEGORIAS_PRODUCTO_RAW,
    PREGUNTA_3: CATEGORIAS_PRODUCTO_RAW,
    PREGUNTA_4: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_5: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_6: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_7: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_8: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_9: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_10: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_11: CATEGORIAS_COMUNICACION_RAW,
}

MAPA_CONEXION_POR_PREGUNTA = {
    PREGUNTA: PREGUNTA_CONEXION_1,
    PREGUNTA_2: PREGUNTA_CONEXION_2,
    PREGUNTA_3: PREGUNTA_CONEXION_3,
    PREGUNTA_4: PREGUNTA_CONEXION_1,
    PREGUNTA_5: PREGUNTA_CONEXION_2,
    PREGUNTA_6: PREGUNTA_CONEXION_3,
    PREGUNTA_7: PREGUNTA_CONEXION_4,
    PREGUNTA_8: PREGUNTA_CONEXION_5,
    PREGUNTA_9: PREGUNTA_CONEXION_6,
    PREGUNTA_10: PREGUNTA_CONEXION_7,
    PREGUNTA_11: PREGUNTA_CONEXION_8,
}

MAPA_CATEGORIAS_ESPERADAS = {
    PREGUNTA_7: [
        "Facilidad / accesibilidad",
        "Accion concreta / ahorro voluntario",
        "Ahorro / retiro / futuro",
    ],
    PREGUNTA_8: [
        "Accion concreta / ahorro voluntario",
        "Ahorro / retiro / futuro",
    ],
    PREGUNTA_9: [
        "Ahorro / retiro / futuro",
        "Urgencia / conciencia / tiempo",
    ],
    PREGUNTA_10: [
        "Confianza / seguridad / respaldo",
        "Facilidad / accesibilidad",
    ],
    PREGUNTA_11: [
        "Bienestar / calidad de vida",
        "Ahorro / retiro / futuro",
    ],
}

STOPWORDS = {
    "de", "la", "el", "y", "a", "que", "en", "un", "una", "para", "por",
    "con", "del", "las", "los", "al", "se", "es", "lo", "como", "mas",
    "su", "sus", "mi", "mis", "tu", "tus", "ya", "o", "si", "no",
    "me", "te", "le", "les", "hay", "muy", "pero", "porque", "que",
    "algun", "alguna", "tipo", "creo", "parece", "hacer", "ponen",
    "generalmente", "gente", "servicio", "anuncio", "producto", "son", "otras",
    "the", "and", "has", "han", "tiene", "that", "lot", "their"
}

AFORE_MAP = {
    "image1": "Banamex Afore",
    "image2": "Afore XXI Banorte",
    "image3": "Inbursa Afore",
    "image4": "PENSIONISSSTE",
    "image5": "Profuturo",
    "image6": "SURA",
    "image7": "Principal",
    "image8": "InverCap Afore",
    "image9": "Afore Coppel",
    "image10": "Afore Azteca",
}

AFORE_LOGO_MAP = {
    "image1": "AFORES_LOGOS/IMAGEN_1.png",
    "image2": "AFORES_LOGOS/IMAGEN_2.jpeg",
    "image3": "AFORES_LOGOS/IMAGEN_3.png",
    "image4": "AFORES_LOGOS/IMAGEN_4_extracted.png",
    "image5": "AFORES_LOGOS/IMAGEN_5.webp",
    "image6": "AFORES_LOGOS/IMAGEN_6.png",
    "image7": "AFORES_LOGOS/IMAGEN_7.avif.png",
    "image8": "AFORES_LOGOS/IMAGEN_8.webp",
    "image9": "AFORES_LOGOS/IMAGEN_9.png",
    "image10": "AFORES_LOGOS/IMAGEN_10.png",
}

RAZONES_CONFIANZA_RAW = {
    "Trayectoria / marca conocida": """
        años, anos, conocida, conocidas, popular, populares, reconocida, reconocidas,
        escuchadas, marca, marcas, fama, trayectoria, conocida en mexico, establecida, establecidas,
        establecido, establecidos, organizaciones, banco, bancos, fuertes, renombre, institucion
    """,
    "Uso personal / experiencia propia": """
        uso actualmente, la tengo, tengo, manejo, he usado, mi afore, experiencia propia,
        uso, actualmete manejo, actualmente manejo, experiencia,
        experiencias, familiar, familiares
    """,
    "Seguridad / confianza": """
        confianza, confiable, seguras, segura, seguridad, respaldo, real, reales,
        estabilidad, solidas, sólida, formality, support, apoyarme, publicidad, formalidad, seriedad,
        seguro, seguros, seguras
    """,
    "Rendimiento / beneficios": """
        rendimiento, rendimientos, ganancia, ganancias, mejor rendimiento, jubilacion,
        buena jubilacion, beneficios, inversion, inversión, crecer el dinero, mejores, rendimiento,
        rendimeinto, mejor, mejores
    """,
    "Recomendacion / referencias": """
        comentarios, recomendacion, recomendaciones, recomendado, recomendada,
        referencia, referencias, cercanos, personas, por comentarios, gusta, gustan, diseno, diseño,
        recomendar, recomendaron, recomendacion, escucho, escuchado
    """,
    "Respaldo institucional / gobierno": """
        gobierno, respaldado por el gobierno, backed by the government, recursos,
        estado, maestros, issste
    """,
    "Servicio / atencion": """
        servicio, atencion, customer service, prompt customer service, informativa,
        informativeness, ayuda, sucursales, atienden, atender
    """,
    "Percepcion negativa de otras": """
        no les tengo confianza, dueños, otras no, desconfianza, fraude, estafa, fallado
    """,
}


def calcular_edad(fecha_nacimiento):
    fecha_nacimiento = (fecha_nacimiento or "").strip()
    if not fecha_nacimiento:
        return None

    try:
        nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
    except ValueError:
        return None

    hoy = date.today()
    edad = hoy.year - nacimiento.year
    if (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day):
        edad -= 1
    return edad if 0 < edad < 100 else None


def normalizar_genero(row):
    genero = (
        row.get("recruit: gender")
        or row.get("¿Cuál es tu género?")
        or ""
    ).strip()
    genero_limpio = limpiar_texto(genero)

    if genero_limpio in {"male", "hombre", "masculino"}:
        return "Hombre"
    if genero_limpio in {"female", "mujer", "femenino"}:
        return "Mujer"
    if genero:
        return genero.strip()
    return "Sin dato"


def normalizar_edad(row):
    edad_reclutamiento = (row.get("recruit: age") or "").strip()
    if edad_reclutamiento.isdigit():
        edad = int(edad_reclutamiento)
        return edad if 0 < edad < 100 else None

    return calcular_edad(row.get("¿Cuál es tu fecha de nacimiento?", ""))


def normalizar_conexion(valor):
    valor = (valor or "").strip()
    if not valor:
        return None
    try:
        return float(valor)
    except ValueError:
        return None


def limpiar_texto(texto):
    texto = str(texto).lower().strip()
    texto = "".join(
        char
        for char in unicodedata.normalize("NFD", texto)
        if unicodedata.category(char) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def clasificar_razon_confianza(texto):
    texto_limpio = limpiar_texto(texto)
    if not texto_limpio:
        return "Sin razon"

    categorias = preparar_categorias(RAZONES_CONFIANZA_RAW)
    mejor_categoria = "Otras razones"
    mejor_score = 0

    for categoria, terminos in categorias.items():
        coincidencias = obtener_coincidencias_limpias(texto_limpio, terminos)
        score = puntuar_coincidencias(coincidencias)
        if score > mejor_score:
            mejor_categoria = categoria
            mejor_score = score

    return mejor_categoria


def preparar_categorias(categorias_raw):
    categorias = {}
    for categoria, bloque in categorias_raw.items():
        terminos = []
        for termino in bloque.replace("\n", ",").split(","):
            termino = limpiar_texto(termino)
            if termino:
                terminos.append(termino)

        # Frases largas primero para que el desempate tenga mejor señal.
        terminos = sorted(set(terminos), key=lambda item: (-len(item.split()), item))
        categorias[categoria] = terminos
    return categorias


def extraer_palabras(texto):
    palabras = []
    for palabra in limpiar_texto(texto).split():
        if len(palabra) < 3:
            continue
        if palabra in STOPWORDS:
            continue
        if palabra.isdigit():
            continue
        palabras.append(palabra)
    return palabras


def obtener_coincidencias_limpias(texto, terminos):
    """
    Detecta palabras y frases sin repetir palabras ya cubiertas por una frase.
    Ejemplo: si aparece 'pasta de dientes', no muestra tambien 'pasta' o
    'dientes' para esa misma categoria.
    """
    texto_limpio = limpiar_texto(texto)
    tokens = texto_limpio.split()

    coincidencias_frases = []
    coincidencias_palabras = []

    for termino in terminos:
        if " " in termino:
            if termino in texto_limpio:
                coincidencias_frases.append(termino)
        else:
            if termino in tokens:
                coincidencias_palabras.append(termino)

    palabras_bloqueadas = set()
    for frase in coincidencias_frases:
        palabras_bloqueadas.update(frase.split())

    coincidencias_palabras = [
        palabra for palabra in coincidencias_palabras if palabra not in palabras_bloqueadas
    ]

    return coincidencias_frases + coincidencias_palabras


def puntuar_coincidencias(coincidencias):
    """
    Da mas peso a frases completas que a palabras sueltas.
    """
    score = 0
    for item in coincidencias:
        if " " in item:
            score += 2
        else:
            score += 1
    return score


def asignar_categoria_principal(respuesta, categorias):
    texto_limpio = limpiar_texto(respuesta)

    mejor_categoria = "Sin categoria"
    mejor_score = 0
    mejor_num_coincidencias = 0
    mejores_coincidencias = []

    for categoria, terminos in categorias.items():
        coincidencias = obtener_coincidencias_limpias(texto_limpio, terminos)
        score = puntuar_coincidencias(coincidencias)
        num_coincidencias = len(coincidencias)

        if score > mejor_score:
            mejor_categoria = categoria
            mejor_score = score
            mejor_num_coincidencias = num_coincidencias
            mejores_coincidencias = coincidencias
            continue

        if score == mejor_score and score > 0:
            # Desempate: preferir la categoria con mas coincidencias totales.
            if num_coincidencias > mejor_num_coincidencias:
                mejor_categoria = categoria
                mejor_num_coincidencias = num_coincidencias
                mejores_coincidencias = coincidencias
                continue

            # Segundo desempate: preferir la categoria con la frase mas larga.
            mejor_actual = max((len(item.split()) for item in mejores_coincidencias), default=0)
            mejor_nuevo = max((len(item.split()) for item in coincidencias), default=0)
            if mejor_nuevo > mejor_actual:
                mejor_categoria = categoria
                mejor_num_coincidencias = num_coincidencias
                mejores_coincidencias = coincidencias

    return mejor_categoria, mejor_score, mejores_coincidencias


def imprimir_detalle(detalle_categorias):
    print("\nDetalle final por categoria:\n")
    for categoria, respuestas in detalle_categorias.items():
        print(categoria)
        for item in respuestas:
            print(f"  - user {item['user_id']}: {item['respuesta']}")
            if item["coincidencias"]:
                print(
                    "    palabras/frases detectadas: "
                    + ", ".join(item["coincidencias"])
                )
            else:
                print("    palabras/frases detectadas: sin coincidencias")
        print()


def analizar_encuesta(pregunta=None):
    pregunta = pregunta or PREGUNTA
    categorias_raw = MAPA_CATEGORIAS_POR_PREGUNTA.get(pregunta, CATEGORIAS_PRODUCTO_RAW)
    categorias = preparar_categorias(categorias_raw)
    pregunta_conexion = MAPA_CONEXION_POR_PREGUNTA.get(pregunta)

    contador = Counter()
    conteo_categorias = Counter()
    ejemplos = defaultdict(list)
    detalle_categorias = defaultdict(list)
    resultados = []

    for csv_path in CSV_PATHS:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as archivo:
            reader = csv.DictReader(archivo)

            for row in reader:
                respuesta = (row.get(pregunta) or "").strip()
                user_id = row.get("user id", "")
                status = row.get("status", "")
                conexion = normalizar_conexion(row.get(pregunta_conexion, "")) if pregunta_conexion else None
                if respuesta:
                    contador.update(extraer_palabras(respuesta))

                categoria, score, coincidencias = asignar_categoria_principal(
                    respuesta, categorias
                )
                conteo_categorias[categoria] += 1

                if len(ejemplos[categoria]) < 5:
                    ejemplos[categoria].append(
                        f"user {user_id} | score={score} | {respuesta}"
                    )

                detalle_categorias[categoria].append(
                    {
                        "user_id": user_id,
                        "respuesta": respuesta,
                        "coincidencias": coincidencias,
                        "archivo_origen": csv_path,
                        "status": status,
                    }
                )

                resultados.append(
                    {
                        "archivo_origen": csv_path.split("/")[-1],
                        "user_id": user_id,
                        "participant_name": row.get("participant name", ""),
                        "status": status,
                        "device": row.get("device", ""),
                        "os": row.get("OS", ""),
                        "genero": normalizar_genero(row),
                        "edad": normalizar_edad(row),
                        "conexion": conexion,
                        "respuesta": respuesta,
                        "categoria": categoria,
                        "score": score,
                        "coincidencias": coincidencias,
                        "coincidencias_texto": ", ".join(coincidencias) if coincidencias else "",
                    }
                )

    return {
        "pregunta": pregunta,
        "pregunta_conexion": pregunta_conexion,
        "archivos": CSV_PATHS,
        "top_palabras": contador,
        "conteo_categorias": conteo_categorias,
        "ejemplos": dict(ejemplos),
        "detalle_categorias": dict(detalle_categorias),
        "resultados": resultados,
    }


def analizar_confianza_afores():
    menciones = []
    conteo_afores = Counter()
    conteo_razones = Counter()
    matriz_afores_razones = defaultdict(Counter)

    for csv_path in CSV_PATHS:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as archivo:
            reader = csv.DictReader(archivo)

            for row in reader:
                seleccion = (row.get(PREGUNTA_CONFIANZA_AFORE) or "").strip()
                razon_texto = (row.get(PREGUNTA_CONFIANZA_POR_QUE) or "").strip()
                razon_categoria = clasificar_razon_confianza(razon_texto)

                if not seleccion:
                    continue

                for item in seleccion.split("|"):
                    if ":" in item:
                        image_code, choice_code = item.split(":", 1)
                    else:
                        image_code, choice_code = item, ""

                    afore_nombre = AFORE_MAP.get(image_code, image_code)
                    ranking = None
                    if choice_code.startswith("choice"):
                        try:
                            ranking = int(choice_code.replace("choice", ""))
                        except ValueError:
                            ranking = None

                    conteo_afores[afore_nombre] += 1
                    conteo_razones[razon_categoria] += 1
                    matriz_afores_razones[afore_nombre][razon_categoria] += 1

                    menciones.append(
                        {
                            "archivo_origen": Path(csv_path).name,
                            "user_id": row.get("user id", ""),
                            "participant_name": row.get("participant name", ""),
                            "status": row.get("status", ""),
                            "afore_codigo": image_code,
                            "afore_nombre": afore_nombre,
                            "logo_path": AFORE_LOGO_MAP.get(image_code, ""),
                            "ranking_eleccion": ranking,
                            "razon_texto": razon_texto,
                            "razon_categoria": razon_categoria,
                        }
                    )

    return {
        "menciones": menciones,
        "conteo_afores": conteo_afores,
        "conteo_razones": conteo_razones,
        "matriz_afores_razones": {
            afore: dict(razones)
            for afore, razones in matriz_afores_razones.items()
        },
        "afores_mapeadas": AFORE_MAP,
        "logos": AFORE_LOGO_MAP,
    }


def analizar_descripcion_azteca():
    contador = Counter()

    for csv_path in CSV_PATHS:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as archivo:
            reader = csv.DictReader(archivo)
            for row in reader:
                texto = (row.get(PREGUNTA_DESCRIPCION_AZTECA) or "").strip()
                if texto:
                    contador.update(extraer_palabras(texto))

    return contador


def calcular_metricas_mensaje(resultados, pregunta):
    categorias_esperadas = MAPA_CATEGORIAS_ESPERADAS.get(pregunta, [])
    if not categorias_esperadas:
        return {
            "aplica": False,
            "categorias_esperadas": [],
            "total_con_respuesta": 0,
            "reconocimiento_correcto": 0.0,
            "tasa_confusion": 0.0,
            "share_categoria_dominante": 0.0,
            "indice_claridad": 0.0,
            "conexion_promedio": None,
            "conteo_alta_conexion": 0,
            "conteo_baja_conexion": 0,
        }

    respuestas_con_texto = [
        item
        for item in resultados
        if (item.get("respuesta") or "").strip()
    ]
    total_con_respuesta = len(respuestas_con_texto)

    if total_con_respuesta == 0:
        return {
            "aplica": True,
            "categorias_esperadas": categorias_esperadas,
            "total_con_respuesta": 0,
            "reconocimiento_correcto": 0.0,
            "tasa_confusion": 0.0,
            "share_categoria_dominante": 0.0,
            "indice_claridad": 0.0,
            "conexion_promedio": None,
            "conteo_alta_conexion": 0,
            "conteo_baja_conexion": 0,
        }

    correctas = 0
    confusas = 0
    conteo_categorias = Counter()
    conexiones = []
    conteo_alta_conexion = 0
    conteo_baja_conexion = 0

    for item in respuestas_con_texto:
        categoria = item.get("categoria", "Sin categoria")
        conteo_categorias[categoria] += 1

        if categoria in categorias_esperadas:
            correctas += 1
        if categoria not in categorias_esperadas or categoria in {"Sin categoria", "Percepcion negativa / confusion"}:
            confusas += 1

        conexion = item.get("conexion")
        if conexion is not None:
            conexiones.append(conexion)
            if conexion >= 4:
                conteo_alta_conexion += 1
            elif conexion <= 2:
                conteo_baja_conexion += 1

    reconocimiento_correcto = correctas / total_con_respuesta
    tasa_confusion = confusas / total_con_respuesta
    share_categoria_dominante = (
        conteo_categorias.most_common(1)[0][1] / total_con_respuesta
        if conteo_categorias
        else 0.0
    )
    indice_claridad = (
        (0.5 * reconocimiento_correcto)
        + (0.3 * (1 - tasa_confusion))
        + (0.2 * share_categoria_dominante)
    ) * 100
    conexion_promedio = sum(conexiones) / len(conexiones) if conexiones else None

    return {
        "aplica": True,
        "categorias_esperadas": categorias_esperadas,
        "total_con_respuesta": total_con_respuesta,
        "reconocimiento_correcto": reconocimiento_correcto,
        "tasa_confusion": tasa_confusion,
        "share_categoria_dominante": share_categoria_dominante,
        "indice_claridad": indice_claridad,
        "conexion_promedio": conexion_promedio,
        "conteo_alta_conexion": conteo_alta_conexion,
        "conteo_baja_conexion": conteo_baja_conexion,
    }


def procesar_encuesta():
    analisis = analizar_encuesta()

    contador = analisis["top_palabras"]
    conteo_categorias = analisis["conteo_categorias"]
    ejemplos = analisis["ejemplos"]
    detalle_categorias = analisis["detalle_categorias"]

    print(f"\nPregunta analizada:\n{analisis['pregunta']}\n")
    print("Palabras mas repetidas:\n")
    for palabra, frecuencia in contador.most_common(20):
        print(f"{palabra}: {frecuencia}")

    print(f"\nPregunta analizada:\n{analisis['pregunta']}\n")
    print("Conteo por categoria principal:\n")
    for categoria, total in conteo_categorias.most_common():
        print(f"{categoria}: {total}")

    print("\nEjemplos por categoria:\n")
    for categoria, lista in ejemplos.items():
        print(categoria)
        for item in lista:
            print(f"  - {item}")
        print()

    imprimir_detalle(detalle_categorias)


if __name__ == "__main__":
    procesar_encuesta()

############################
