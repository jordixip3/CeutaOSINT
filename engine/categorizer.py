import re

UNIVERSAL_CATEGORIES = {
    "CALL_TO_ACTION": "Llamadas a la Acción, Convocatorias y Órdenes Operativas",
    "LOGISTICS_ROUTES": "Rutas, Vectores de Ataque, Logística y Armamento",
    "EARLY_WARNING": "Señales Tempranas, Alarmas y Avisos Previos",
    "OFFICIAL_DISCLAIMER": "Comunicados Oficiales, Ministerios y Fuentes Gubernamentales",
    "DISINFORMATION_PROPAGANDA": "Desinformación, Guerra Psicológica y Propaganda"
}

def categorize_post(title, content):
    """
    Universal categorizer for OSINT intelligence posts across any domain:
    Geopolitics, military conflicts, borders, cyber threats, protests, etc.
    """
    text = (title + " " + content).lower()

    # 1. Official statements
    if any(k in text for k in [
        "ministerio", "defensa", "gobierno", "portavoz", "declaración oficial",
        "comunicado oficial", "delegación", "kremlin", "pentágono", "otan",
        "casa blanca", "desmentido", "oficialmente", "según fuentes oficiales"
    ]):
        return "OFFICIAL_DISCLAIMER"

    # 2. Early Warning & Signals
    if any(k in text for k in [
        "alerta", "alarma aérea", "sirena", "radar", "satélite", "aviso previo",
        "detección temprana", "días antes", "previo al ataque", "inteligencia previa",
        "se detectó", "señal temprana", "aviso de emergencia"
    ]):
        return "EARLY_WARNING"

    # 3. Logistics, Weapons & Attack Vectors
    if any(k in text for k in [
        "drone", "dron", "shahed", "misil", "vector", "ruta", "lanzamiento",
        "espacio aéreo", "trayectoria", "infraestructura", "munición", "arsenal",
        "logística", "espigón", "neopreno", "coordenadas", "impacto", "base aérea"
    ]):
        return "LOGISTICS_ROUTES"

    # 4. Calls to action / Tactical Mobilization
    if any(k in text for k in [
        "ataque masivo", "ofensiva", "incursión", "convocatoria", "llamamiento",
        "movilización", "coordinación", "operación", "infiltración", "orden de ataque"
    ]):
        return "CALL_TO_ACTION"

    # 5. Default to Disinformation / Propaganda / Claims
    return "DISINFORMATION_PROPAGANDA"

def extract_entities(title, content):
    """
    Extracts dynamic entities: Geographic locations, military assets,
    organizations, handles, timestamps, and key entities from any text.
    """
    text = title + " " + content
    entities = []

    # Common international & regional locations
    location_pool = [
        "Ucrania", "Rusia", "Kiev", "Moscú", "Kursk", "Járkov", "Crimea", "Donetsk", "Zaporiyia", "Leipzig", "Alemania",
        "Polonia", "Bielorrusia", "Ceuta", "Melilla", "Tarajal", "Fnideq", "Castillejos", "Marruecos", "España",
        "Mar Rojo", "Gaza", "Israel", "Líbano", "Beirut", "Teherán", "Irán", "Yemen", "EEUU", "Washington", "Bruselas"
    ]

    for loc in location_pool:
        if re.search(r'\b' + re.escape(loc) + r'\b', text, re.IGNORECASE):
            entities.append({"type": "LOCATION", "value": loc, "confidence": 0.95})

    # Tactical & Military Assets
    asset_pool = ["Drone", "Dron", "Shahed", "Misil", "Patriot", "Iskander", "Kalibr", "HIMARS", "F-16", "Radar", "Neopreno", "Patrullera"]
    for asset in asset_pool:
        if re.search(r'\b' + re.escape(asset) + r'\b', text, re.IGNORECASE):
            entities.append({"type": "ASSET_TACTICAL", "value": asset, "confidence": 0.90})

    # Organizations
    org_pool = ["Guardia Civil", "Fuerzas Armadas", "OTAN", "NATO", "Kremlin", "Pentágono", "FSB", "GUR", "Policía Nacional"]
    for org in org_pool:
        if re.search(r'\b' + re.escape(org) + r'\b', text, re.IGNORECASE):
            entities.append({"type": "ORGANIZATION", "value": org, "confidence": 0.92})

    # Social Handles
    handles = re.findall(r'@[A-Za-z0-9_]+', text)
    for h in set(handles):
        entities.append({"type": "HANDLE", "value": h, "confidence": 0.90})

    # Time markers (e.g. 04:30, 22:15)
    times = re.findall(r'\b\d{2}:\d{2}\s*(?:AM|PM|hrs|h)?\b', text, re.IGNORECASE)
    for t in set(times):
        entities.append({"type": "DATE_TIME", "value": t, "confidence": 0.85})

    # Hashtags
    hashtags = re.findall(r'#[A-Za-z0-9_]+', text)
    for ht in set(hashtags):
        entities.append({"type": "HASHTAG", "value": ht, "confidence": 0.90})

    return entities
