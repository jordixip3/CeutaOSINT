import os

# Project Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ceuta_intel.db")

# Intelligence Target & Threshold Config
MIN_SCORE_THRESHOLD = 7.0  # Required confidence score out of 10.0 to finish loop
MAX_AGENT_ITERATIONS = 5

# Target Investigation Event Parameters
EVENT_NAME = "Ceuta Mass Migration & Border Event - Late June / Summer"
PRIMARY_LOCATIONS = ["Ceuta", "Fnideq", "Castillejos", "Espigón del Tarajal", "Benslimane", "Tánger", "Tetuan"]

INITIAL_KEYWORDS = [
    "Ceuta", "Fnideq", "Castillejos", "Tarajal", "espigón",
    "migración Ceuta", "entrada masiva", "asalto valla", "Guardia Civil Ceuta",
    "Fuerzas Auxiliares Marruecos", "convocatoria redes", "TikTok Ceuta", "WhatsApp migración",
    "frontera Ceuta", "30 junio Ceuta", "15 septiembre Ceuta"
]

CATEGORIES = {
    "CALL_TO_ACTION": "Convocatorias y Llamamientos Masivos en Redes",
    "LOGISTICS_ROUTES": "Rutas, Logística y Métodos de Infiltración",
    "EARLY_WARNING": "Señales Tempranas y Patrones Pre-Evento",
    "OFFICIAL_DISCLAIMER": "Declaraciones Oficiales y Desmentidos Gubernamentales",
    "DISINFORMATION_PROPAGANDA": "Desinformación, Rumores y Propaganda"
}

# Scoring Weights
SCORING_WEIGHTS = {
    "source_authority": 0.30,
    "cross_corroboration": 0.30,
    "temporal_lead_time": 0.25,
    "specificity": 0.15
}
