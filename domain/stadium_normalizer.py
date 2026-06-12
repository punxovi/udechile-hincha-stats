"""
Normaliza nombres de estadio a una forma canónica para agrupar correctamente
las estadísticas sin importar variaciones de escritura o cambios de nombre.

Lógica: cada regla es una tupla (keywords, canonical_name, canonical_city, country).
Se busca la primera regla cuyas keywords estén TODAS presentes en el nombre
normalizado (sin tildes, en minúsculas). Las reglas más específicas van primero.
"""

import unicodedata
import re
from typing import Optional, Tuple


def _simplify(text: str) -> str:
    """Quita tildes, pasa a minúsculas, colapsa espacios."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_text.lower()).strip()


# (keywords_que_deben_aparecer, nombre_canónico, ciudad_canónica, país)
# Reglas más específicas (2+ keywords) antes de las genéricas (1 keyword).
_RULES: list[tuple[list[str], str, str, str]] = [
    # ── Nacional ─────────────────────────────────────────────────────────────
    (["nacional", "nuno"],       "Estadio Nacional, Ñuñoa",             "Santiago",    "Chile"),
    (["nacional", "santiago"],   "Estadio Nacional, Ñuñoa",             "Santiago",    "Chile"),
    (["nacional", "stgo"],       "Estadio Nacional, Ñuñoa",             "Santiago",    "Chile"),
    # Nacional sin ciudad → asumimos el de Santiago (el de Lima lleva "lima" explícito)
    (["nacional", "lima"],       "Estadio Nacional",                    "Lima",        "Perú"),

    # ── Santa Laura ──────────────────────────────────────────────────────────
    (["santa laura"],            "Estadio Santa Laura",                 "Santiago",    "Chile"),

    # ── El Teniente / Rancagua ───────────────────────────────────────────────
    (["teniente"],               "Estadio Bicentenario El Teniente",    "Rancagua",    "Chile"),

    # ── Sausalito / Viña del Mar ─────────────────────────────────────────────
    (["sausalito"],              "Estadio Bicentenario Sausalito",      "Viña del Mar","Chile"),

    # ── Monumental – Santiago (Macul) ────────────────────────────────────────
    (["monumental", "macul"],    "Estadio Monumental David Arellano",   "Santiago",    "Chile"),
    (["monumental", "santiago"], "Estadio Monumental David Arellano",   "Santiago",    "Chile"),
    (["hoyodepedrero"],          "Estadio Monumental David Arellano",   "Santiago",    "Chile"),
    # Monumental – Buenos Aires (va antes del genérico)
    (["monumental", "buenos"],   "Estadio Monumental de Núñez",         "Buenos Aires","Argentina"),

    # ── San Carlos de Apoquindo ──────────────────────────────────────────────
    (["apoquindo"],              "Estadio San Carlos de Apoquindo",     "Santiago",    "Chile"),

    # ── La Florida ───────────────────────────────────────────────────────────
    (["la florida"],             "Estadio Bicentenario La Florida",     "Santiago",    "Chile"),
    (["florida", "bicentenario"],"Estadio Bicentenario La Florida",     "Santiago",    "Chile"),

    # ── La Cisterna ──────────────────────────────────────────────────────────
    (["cisterna"],               "Estadio Municipal La Cisterna",       "Santiago",    "Chile"),

    # ── La Portada / La Serena ───────────────────────────────────────────────
    (["portada"],                "Estadio Bicentenario La Portada",     "La Serena",   "Chile"),
    (["serena"],                 "Estadio Bicentenario La Portada",     "La Serena",   "Chile"),

    # ── Sánchez Rumoroso / Coquimbo ──────────────────────────────────────────
    (["rumoroso"],               "Estadio Bicentenario Francisco Sánchez Rumoroso", "Coquimbo", "Chile"),
    (["fco", "coquimbo"],        "Estadio Bicentenario Francisco Sánchez Rumoroso", "Coquimbo", "Chile"),
    (["coquimbo"],               "Estadio Bicentenario Francisco Sánchez Rumoroso", "Coquimbo", "Chile"),

    # ── Elías Figueroa / Playa Ancha / Valparaíso ────────────────────────────
    (["figueroa"],               "Estadio Elías Figueroa Brander",      "Valparaíso",  "Chile"),
    (["playa ancha"],            "Estadio Elías Figueroa Brander",      "Valparaíso",  "Chile"),
    (["valparaiso"],             "Estadio Elías Figueroa Brander",      "Valparaíso",  "Chile"),

    # ── Ester Roa / Collao / Concepción ─────────────────────────────────────
    (["ester roa"],              "Estadio Bicentenario Ester Roa Collao","Concepción", "Chile"),
    (["collao"],                 "Estadio Bicentenario Ester Roa Collao","Concepción", "Chile"),
    (["concepcion"],             "Estadio Bicentenario Ester Roa Collao","Concepción", "Chile"),

    # ── CAP / Las Higueras / Huachipato / Talcahuano ─────────────────────────
    (["las higueras"],           "Estadio CAP Las Higueras",            "Talcahuano",  "Chile"),
    (["huachipato"],             "Estadio CAP Las Higueras",            "Talcahuano",  "Chile"),
    (["cap acero"],              "Estadio CAP Las Higueras",            "Talcahuano",  "Chile"),
    (["cap", "talcahuano"],      "Estadio CAP Las Higueras",            "Talcahuano",  "Chile"),

    # ── Lucio Fariña / Quillota ──────────────────────────────────────────────
    (["lucio"],                  "Estadio Bicentenario Lucio Fariña Fernández","Quillota","Chile"),
    (["farina"],                 "Estadio Bicentenario Lucio Fariña Fernández","Quillota","Chile"),
    (["quillota"],               "Estadio Bicentenario Lucio Fariña Fernández","Quillota","Chile"),

    # ── Germán Becker / Temuco ───────────────────────────────────────────────
    (["becker"],                 "Estadio Bicentenario Germán Becker",  "Temuco",      "Chile"),
    (["temuco"],                 "Estadio Bicentenario Germán Becker",  "Temuco",      "Chile"),

    # ── Nélson Oyarzún / Chillán ─────────────────────────────────────────────
    (["oyarzun"],                "Estadio Bicentenario Nélson Oyarzún", "Chillán",     "Chile"),
    (["chillan"],                "Estadio Bicentenario Nélson Oyarzún", "Chillán",     "Chile"),

    # ── Zorros del Desierto / Calama ─────────────────────────────────────────
    (["zorros"],                 "Estadio Zorros del Desierto",         "Calama",      "Chile"),
    (["calama"],                 "Estadio Zorros del Desierto",         "Calama",      "Chile"),

    # ── Calvo y Bascuñán / Antofagasta ───────────────────────────────────────
    # "Regional, Antofagasta" es el nombre viejo del mismo estadio
    (["bascunan"],               "Estadio Bicentenario Calvo y Bascuñán","Antofagasta","Chile"),
    (["antofagasta"],            "Estadio Bicentenario Calvo y Bascuñán","Antofagasta","Chile"),

    # ── Nicolás Chahuán / La Calera ──────────────────────────────────────────
    (["chahuan"],                "Estadio Bicentenario Nicolás Chahuán","La Calera",   "Chile"),
    (["calera"],                 "Estadio Bicentenario Nicolás Chahuán","La Calera",   "Chile"),

    # ── Fiscal de Talca ──────────────────────────────────────────────────────
    (["fiscal", "talca"],        "Estadio Bicentenario Fiscal",         "Talca",       "Chile"),

    # ── Tierra de Campeones / Iquique ────────────────────────────────────────
    (["tierra de campeones"],    "Estadio Tierra de Campeones",         "Iquique",     "Chile"),
    (["iquique"],                "Estadio Tierra de Campeones",         "Iquique",     "Chile"),

    # ── El Cobre / El Salvador ───────────────────────────────────────────────
    (["el cobre"],               "Estadio El Cobre",                    "El Salvador", "Chile"),
    (["el salvador"],            "Estadio El Cobre",                    "El Salvador", "Chile"),

    # ── Municipal San Felipe ─────────────────────────────────────────────────
    (["san felipe"],             "Estadio Municipal San Felipe",        "San Felipe",  "Chile"),

    # ── Chinquihue / Puerto Montt ────────────────────────────────────────────
    (["chinquihue"],             "Estadio Chinquihue",                  "Puerto Montt","Chile"),
    (["puerto montt"],           "Estadio Chinquihue",                  "Puerto Montt","Chile"),

    # ── Parque Schott / Osorno ───────────────────────────────────────────────
    (["schott"],                 "Estadio Parque Schott",               "Osorno",      "Chile"),
    (["osorno"],                 "Estadio Parque Schott",               "Osorno",      "Chile"),

    # ── Roberto Bravo / Melipilla ────────────────────────────────────────────
    (["melipilla"],              "Estadio Municipal Roberto Bravo",     "Melipilla",   "Chile"),

    # ── Carlos Dittborn / Arica ──────────────────────────────────────────────
    (["dittborn"],               "Estadio Carlos Dittborn",             "Arica",       "Chile"),
    (["arica"],                  "Estadio Carlos Dittborn",             "Arica",       "Chile"),

    # ── Internacional ────────────────────────────────────────────────────────
    (["azteca"],                 "Estadio Azteca",                      "Ciudad de México", "México"),
    (["mineirao"],               "Estadio Mineirão",                    "Belo Horizonte",   "Brasil"),
    (["villanueva", "lima"],     "Estadio Alejandro Villanueva",        "Lima",             "Perú"),
    (["defensores del chaco"],   "Estadio Defensores del Chaco",        "Asunción",         "Paraguay"),
    (["george capwell"],         "Estadio George Capwell",              "Guayaquil",        "Ecuador"),
    (["pacaembu"],               "Estadio Pacaembú",                    "São Paulo",        "Brasil"),
    (["olimpico", "porto alegre"],"Estadio Olímpico Monumental",        "Porto Alegre",     "Brasil"),
    (["maracana"],               "Estadio Maracaná",                    "Río de Janeiro",   "Brasil"),
    (["ugarte", "potosi"],       "Estadio Victor Agustín Ugarte",       "Potosí",           "Bolivia"),
    (["potosi"],                 "Estadio Victor Agustín Ugarte",       "Potosí",           "Bolivia"),
    (["ruminahui"],              "Estadio Rumiñahui",                   "Sangolquí",        "Ecuador"),
    (["sangolqui"],              "Estadio Rumiñahui",                   "Sangolquí",        "Ecuador"),
    (["lanus"],                  "Estadio Ciudad de Lanús",             "Buenos Aires",     "Argentina"),
    (["ciudad de lanus"],        "Estadio Ciudad de Lanús",             "Buenos Aires",     "Argentina"),
]


def normalize_stadium(name: str, city: Optional[str] = None, country: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Devuelve (nombre_canónico, ciudad_canónica, país_canónico).
    Si ninguna regla aplica, devuelve los valores originales.
    """
    key = _simplify(name)
    for keywords, canon_name, canon_city, canon_country in _RULES:
        if all(kw in key for kw in keywords):
            return canon_name, canon_city, canon_country
    # Sin match: devolver el nombre original limpio
    return name.strip(), (city or ""), (country or "Chile")
