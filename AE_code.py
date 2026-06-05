import pandas as pd
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime

df = pd.read_csv("ARCHIVOS/online-a_04-06-2026 19-25-50-003091_V1.csv", encoding="utf-8-sig")
df.columns


CSV_PATHS = [
    "ARCHIVOS/online-a_04-06-2026 19-25-50-003091_V1.csv",
    "ARCHIVOS/comunicacion_05-06-2026 15-52-49-807016.csv",
]
PREGUNTA = "¿Qué producto crees que promociona la imagen del siguiente anuncio?"
PREGUNTA_2 = "¿Qué producto crees que promociona la imagen del siguiente anuncio? 1"
PREGUNTA_3 = "¿Qué producto crees que promociona la imagen del siguiente anuncio? 2"
PREGUNTA_4 = "¿Qué te comunica el anuncio anterior?"
PREGUNTA_5 = "¿Qué te comunica el anuncio anterior? 1"
PREGUNTA_CONEXION_1 = "¿Qué tanto conectó contigo? (out of 5)"
PREGUNTA_CONEXION_2 = "¿Qué tanto conectó contigo? (out of 5) 1"
PREGUNTA_CONEXION_3 = "¿Qué tanto conectó contigo? (out of 5) 2"

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
        financiamiento, financiamientos
    """,
    "Auto / seguro / movilidad": """
        auto, autos, carro, carros, viaje, viajes, viajar, movilidad,
        seguro, seguros, seguro de auto, seguro de vida, vacaciones, automoviles,
        venta automotriz, automotriz, coche, coches, transporte
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
        bienestar, bienestar personal, seguridad personal, confort, comfort, emoción, emociones
    """,
    "Uso personal / Cuidado personal": """
        tintes, tintes, tinte para el cabello, tinte para el pelo, tinte para canas, máquina, 
        máquina cortadora, hombres, cuidado personal,
        tinte para barba, coloracion, productos de limpieza, productos de limpieza, 
        limpieza del hogar, limpieza para el hogar, Máquina cortadora para hombres, minoxidil
    """,
}

# Categorias para preguntas sobre que comunica el anuncio.
CATEGORIAS_COMUNICACION_RAW = {
    "Ahorro / retiro / futuro": """
        ahorro, ahorrar, ahorros, retiro, jubilacion, pension, futuro,
        vejez, despues de trabajar, ahorro voluntario, tu vejez, afores, afore
    """,
    "Confianza / seguridad / respaldo": """
        confianza, confiable, seguridad, seguro, tranquilidad, respaldo,
        apoyo, protegido, protegida, estable, estabilidad, segura, calidad, bueno, confiado,
        sonrisa, felicidad, felicidades, inversión, inversion, mejor
    """,
    "Urgencia / conciencia / tiempo": """
        tiempo, tarde, temprano, ahora, hoy, urgencia, conciencia,
        no dejarlo al ultimo, antes, despues, aprovechar el tiempo
    """,
    "Facilidad / accesibilidad": """
        facil, facilidad, sencillo, sencilla, accesible, cambiar,
        cambiarte, ayuda, sucursales, atencion, acompanamiento, resolver dudas
    """,
    "Accion concreta / ahorro voluntario": """
        empezar, comenzar, aportaciones, aportacion, voluntario, voluntarias,
        pesos, invertir, meter dinero, ahorrar desde hoy, mover, mueva, mueva a,
        cambies, cambiar
    """,
    "Bienestar / calidad de vida": """
        vivir bien, vida, disfrutar, viajar, libertad financiera, negocio,
        emprendimiento, tranquilidad futura, calidad de vida, productiva, feliz
    """,
    "Percepcion negativa / confusion": """
        fraude, estafa, inseguridad, miedo, desconfianza, confusion, confuso,
        cuestionamientos, dudoso, complicado
    """,
}

MAPA_CATEGORIAS_POR_PREGUNTA = {
    PREGUNTA: CATEGORIAS_PRODUCTO_RAW,
    PREGUNTA_2: CATEGORIAS_PRODUCTO_RAW,
    PREGUNTA_3: CATEGORIAS_PRODUCTO_RAW,
    PREGUNTA_4: CATEGORIAS_COMUNICACION_RAW,
    PREGUNTA_5: CATEGORIAS_COMUNICACION_RAW,
}

MAPA_CONEXION_POR_PREGUNTA = {
    PREGUNTA: PREGUNTA_CONEXION_1,
    PREGUNTA_2: PREGUNTA_CONEXION_2,
    PREGUNTA_3: PREGUNTA_CONEXION_3,
    PREGUNTA_4: PREGUNTA_CONEXION_1,
    PREGUNTA_5: PREGUNTA_CONEXION_2,
}

STOPWORDS = {
    "de", "la", "el", "y", "a", "que", "en", "un", "una", "para", "por",
    "con", "del", "las", "los", "al", "se", "es", "lo", "como", "mas",
    "su", "sus", "mi", "mis", "tu", "tus", "ya", "o", "si", "no",
    "me", "te", "le", "les", "hay", "muy", "pero", "porque", "que",
    "algun", "alguna", "tipo", "creo", "parece", "hacer", "ponen",
    "generalmente", "gente", "servicio", "anuncio", "producto"
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
    return edad


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
        return int(edad_reclutamiento)

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
