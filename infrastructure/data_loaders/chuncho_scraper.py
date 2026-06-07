import os
import sys
import re
import datetime
import uuid
import time
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: Faltan dependencias para el Web Scraper.")
    sys.exit(1)

from domain.models import Match, Stadium, Competition, LeagueTable, TableEntry
from infrastructure.persistence.sqlite_store import SqliteDatabase, SqliteMatchRepository, SqliteAttendanceRepository, SqliteLeagueTableRepository

TEMPORADAS_CONFIG = {
    2025: [
        {"id": "comp_nacional_2025", "name": "Campeonato Nacional 2025", "url": "https://www.chuncho.com/resulna2025.html", "season": "2025", "type": "matches"},
        {"id": "comp_libertadores_2025", "name": "Copa Libertadores 2025", "url": "https://www.chuncho.com/lib2025.html", "season": "2025", "type": "matches"},
        {"id": "comp_sudamericana_2025", "name": "Copa Sudamericana 2025", "url": "https://www.chuncho.com/sud2025.html", "season": "2025", "type": "matches"},
        {"id": "comp_supercopa_2025", "name": "Supercopa 2025", "url": "https://www.chuncho.com/resulsc2025.html", "season": "2025", "type": "matches"},
        {"id": "comp_copachile_2025", "name": "Copa Chile 2025", "url": "https://www.chuncho.com/resulch2025.html", "season": "2025", "type": "matches"},
        {"id": "comp_nacional_2025", "name": "Campeonato Nacional 2025", "url": "https://www.chuncho.com/tablana2025.html", "season": "2025", "type": "table"},
        {"id": "comp_libertadores_2025", "name": "Copa Libertadores 2025", "url": "https://www.chuncho.com/tablacl2025.html", "season": "2025", "type": "table"},
        {"id": "comp_copachile_2025", "name": "Copa Chile 2025", "url": "https://www.chuncho.com/tablach2025.html", "season": "2025", "type": "table"},
    ],
    2024: {
        "resultados": [
            {
                "id": "comp_nacional_2024",
                "name": "Campeonato Nacional 2024",
                "url": "https://www.chuncho.com/resulna2024.html",
                "season": "2024",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2024",
                "name": "Copa Chile 2024",
                "url": "https://www.chuncho.com/resulch2024.html",
                "season": "2024",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_nacional_2024",
                "name": "Campeonato Nacional 2024",
                "url": "https://www.chuncho.com/tablana2024.html",
                "season": "2024",
                "type": "table"
            }
        ]
    },
    2023: {
        "resultados": [
            {
                "id": "comp_nacional_2023",
                "name": "Campeonato Nacional 2023",
                "url": "https://www.chuncho.com/resulna2023.html",
                "season": "2023",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2023",
                "name": "Copa Chile 2023",
                "url": "https://www.chuncho.com/resulch2023.html",
                "season": "2023",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_nacional_2023",
                "name": "Campeonato Nacional 2023",
                "url": "https://www.chuncho.com/tablana2023.html",
                "season": "2023",
                "type": "table"
            }
        ]
    },
    2022: {
        "resultados": [
            {
                "id": "comp_nacional_2022",
                "name": "Campeonato Nacional 2022",
                "url": "https://www.chuncho.com/resulna2022.html",
                "season": "2022",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2022",
                "name": "Copa Chile 2022",
                "url": "https://www.chuncho.com/resulch2022.html",
                "season": "2022",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_nacional_2022",
                "name": "Campeonato Nacional 2022",
                "url": "https://www.chuncho.com/tablana2022.html",
                "season": "2022",
                "type": "table"
            }
        ]
    },
    2021: {
        "resultados": [
            {
                "id": "comp_nacional_2021",
                "name": "Campeonato Nacional 2021",
                "url": "https://www.chuncho.com/resulna2021.html",
                "season": "2021",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2021",
                "name": "Copa Chile 2021",
                "url": "https://www.chuncho.com/resulch2021.html",
                "season": "2021",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2021",
                "name": "Copa Libertadores 2021",
                "url": "https://www.chuncho.com/lib2021.html",
                "season": "2021",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_nacional_2021",
                "name": "Campeonato Nacional 2021",
                "url": "https://www.chuncho.com/tablana2021.html",
                "season": "2021",
                "type": "table"
            }
        ]
    },
    2020: {
        "resultados": [
            {
                "id": "comp_nacional_2020",
                "name": "Campeonato Nacional 2020",
                "url": "https://www.chuncho.com/resulna2020.html",
                "season": "2020",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2020",
                "name": "Copa Libertadores 2020",
                "url": "https://www.chuncho.com/lib2020.html",
                "season": "2020",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_nacional_2020",
                "name": "Campeonato Nacional 2020",
                "url": "https://www.chuncho.com/tablana2020.html",
                "season": "2020",
                "type": "table"
            }
        ]
    },
    2019: {
        "resultados": [
            {
                "id": "comp_nacional_2019",
                "name": "Campeonato Nacional 2019",
                "url": "https://www.chuncho.com/resulna2019.html",
                "season": "2019",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2019",
                "name": "Copa Chile 2019",
                "url": "https://www.chuncho.com/resulch2019.html",
                "season": "2019",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2019",
                "name": "Copa Libertadores 2019",
                "url": "https://www.chuncho.com/lib2019.html",
                "season": "2019",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_nacional_2019",
                "name": "Campeonato Nacional 2019",
                "url": "https://www.chuncho.com/tablana2019.html",
                "season": "2019",
                "type": "table"
            }
        ]
    },
    2018: {
        "resultados": [
            {
                "id": "comp_nacional_2018",
                "name": "Campeonato Nacional 2018",
                "url": "https://www.chuncho.com/resulna2018.html",
                "season": "2018",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2018",
                "name": "Copa Chile 2018",
                "url": "https://www.chuncho.com/resulch2018.html",
                "season": "2018",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2018",
                "name": "Copa Libertadores 2018",
                "url": "https://www.chuncho.com/lib2018.html",
                "season": "2018",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_nacional_2018",
                "name": "Campeonato Nacional 2018",
                "url": "https://www.chuncho.com/tablana2018.html",
                "season": "2018",
                "type": "table"
            },
            {
                "id": "comp_libertadores_2018",
                "name": "Copa Libertadores 2018",
                "url": "https://www.chuncho.com/tablacl2018.html",
                "season": "2018",
                "type": "table"
            }
        ]
    },
    2017: {
        "resultados": [
            {
                "id": "comp_clausura_2017",
                "name": "Torneo Clausura 2017",
                "url": "https://www.chuncho.com/resulcc2016_2017.html",
                "season": "2017",
                "type": "matches"
            },
            {
                "id": "comp_transicion_2017",
                "name": "Torneo Transición 2017",
                "url": "https://www.chuncho.com/resulna2017.html",
                "season": "2017",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2017",
                "name": "Copa Chile 2017",
                "url": "https://www.chuncho.com/resulch2017.html",
                "season": "2017",
                "type": "matches"
            },
            {
                "id": "comp_sudamericana_2017",
                "name": "Copa Sudamericana 2017",
                "url": "https://www.chuncho.com/sud2017.html",
                "season": "2017",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_clausura_2017",
                "name": "Torneo Clausura 2017",
                "url": "https://www.chuncho.com/tablacc2016_2017.html",
                "season": "2017",
                "type": "table"
            },
            {
                "id": "comp_transicion_2017",
                "name": "Torneo Transición 2017",
                "url": "https://www.chuncho.com/tablana2017.html",
                "season": "2017",
                "type": "table"
            }
        ]
    },
    2016: {
        "resultados": [
            {
                "id": "comp_clausura_2016",
                "name": "Torneo Clausura 2016",
                "url": "https://www.chuncho.com/resulcc2015_2016.html",
                "season": "2016",
                "type": "matches"
            },
            {
                "id": "comp_apertura_2016",
                "name": "Torneo Apertura 2016",
                "url": "https://www.chuncho.com/resulca2016_2017.html",
                "season": "2016",
                "type": "matches"
            },
            {
                "id": "comp_supercopa_2016",
                "name": "Supercopa 2016",
                "url": "https://www.chuncho.com/resulsc2016.html",
                "season": "2016",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2016",
                "name": "Copa Chile 2016",
                "url": "https://www.chuncho.com/resulch2016.html",
                "season": "2016",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2016",
                "name": "Copa Libertadores 2016",
                "url": "https://www.chuncho.com/lib2016.html",
                "season": "2016",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_clausura_2016",
                "name": "Torneo Clausura 2016",
                "url": "https://www.chuncho.com/tablacc2015_2016.html",
                "season": "2016",
                "type": "table"
            },
            {
                "id": "comp_apertura_2016",
                "name": "Torneo Apertura 2016",
                "url": "https://www.chuncho.com/tablaca2016_2017.html",
                "season": "2016",
                "type": "table"
            }
        ]
    },
    2015: {
        "resultados": [
            {
                "id": "comp_clausura_2015",
                "name": "Torneo Clausura 2015",
                "url": "https://www.chuncho.com/resulcc2014_2015.html",
                "season": "2015",
                "type": "matches"
            },
            {
                "id": "comp_apertura_2015",
                "name": "Torneo Apertura 2015",
                "url": "https://www.chuncho.com/resulca2015_2016.html",
                "season": "2015",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2015",
                "name": "Copa Libertadores 2015",
                "url": "https://www.chuncho.com/lib2015.html",
                "season": "2015",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2015",
                "name": "Copa Chile 2015",
                "url": "https://www.chuncho.com/resulch2015.html",
                "season": "2015",
                "type": "matches"
            },
            {
                "id": "comp_supercopa_2015",
                "name": "Supercopa 2015",
                "url": "https://www.chuncho.com/resulsc2015.html",
                "season": "2015",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_clausura_2015",
                "name": "Torneo Clausura 2015",
                "url": "https://www.chuncho.com/tablacc2014_2015.html",
                "season": "2015",
                "type": "table"
            },
            {
                "id": "comp_apertura_2015",
                "name": "Torneo Apertura 2015",
                "url": "https://www.chuncho.com/tablaca2015_2016.html",
                "season": "2015",
                "type": "table"
            },
            {
                "id": "comp_libertadores_2015",
                "name": "Copa Libertadores 2015",
                "url": "https://www.chuncho.com/tablacl2015.html",
                "season": "2015",
                "type": "table"
            },
            {
                "id": "comp_copachile_2015",
                "name": "Copa Chile 2015",
                "url": "https://www.chuncho.com/tablach2015.html",
                "season": "2015",
                "type": "table"
            }
        ]
    },
    2014: {
        "resultados": [
            {
                "id": "comp_clausura_2014",
                "name": "Torneo Clausura 2014",
                "url": "https://www.chuncho.com/resulcc2013_2014.html",
                "season": "2014",
                "type": "matches"
            },
            {
                "id": "comp_apertura_2014",
                "name": "Torneo Apertura 2014",
                "url": "https://www.chuncho.com/resulca2014_2015.html",
                "season": "2014",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2014",
                "name": "Copa Libertadores 2014",
                "url": "https://www.chuncho.com/lib2014.html",
                "season": "2014",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2014",
                "name": "Copa Chile 2014",
                "url": "https://www.chuncho.com/resulch2014.html",
                "season": "2014",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_clausura_2014",
                "name": "Torneo Clausura 2014",
                "url": "https://www.chuncho.com/tablacc2013_2014.html",
                "season": "2014",
                "type": "table"
            },
            {
                "id": "comp_apertura_2014",
                "name": "Torneo Apertura 2014",
                "url": "https://www.chuncho.com/tablaca2014_2015.html",
                "season": "2014",
                "type": "table"
            },
            {
                "id": "comp_libertadores_2014",
                "name": "Copa Libertadores 2014",
                "url": "https://www.chuncho.com/tablacl2014.html",
                "season": "2014",
                "type": "table"
            },
            {
                "id": "comp_copachile_2014",
                "name": "Copa Chile 2014",
                "url": "https://www.chuncho.com/tablach2014.html",
                "season": "2014",
                "type": "table"
            }
        ]
    },
    2013: {
        "resultados": [
            {
                "id": "comp_transicion_2013",
                "name": "Torneo Transición 2013",
                "url": "https://www.chuncho.com/resulna2013.html",
                "season": "2013",
                "type": "matches"
            },
            {
                "id": "comp_apertura_2013",
                "name": "Torneo Apertura 2013",
                "url": "https://www.chuncho.com/resulca2013.html",
                "season": "2013",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2013",
                "name": "Copa Libertadores 2013",
                "url": "https://www.chuncho.com/lib2013.html",
                "season": "2013",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2013",
                "name": "Copa Chile 2013",
                "url": "https://www.chuncho.com/resulch2013.html",
                "season": "2013",
                "type": "matches"
            },
            {
                "id": "comp_supercopa_2013",
                "name": "Supercopa 2013",
                "url": "https://www.chuncho.com/resulsc2013.html",
                "season": "2013",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_transicion_2013",
                "name": "Torneo Transición 2013",
                "url": "https://www.chuncho.com/tablana2013.html",
                "season": "2013",
                "type": "table"
            },
            {
                "id": "comp_apertura_2013",
                "name": "Torneo Apertura 2013",
                "url": "https://www.chuncho.com/tablaca2013.html",
                "season": "2013",
                "type": "table"
            },
            {
                "id": "comp_libertadores_2013",
                "name": "Copa Libertadores 2013",
                "url": "https://www.chuncho.com/tablacl2013.html",
                "season": "2013",
                "type": "table"
            },
            {
                "id": "comp_copachile_2013",
                "name": "Copa Chile 2013",
                "url": "https://www.chuncho.com/tablach2013.html",
                "season": "2013",
                "type": "table"
            }
        ]
    },
    2012: {
        "resultados": [
            {
                "id": "comp_apertura_2012",
                "name": "Torneo Apertura 2012",
                "url": "https://www.chuncho.com/resulca2012.html",
                "season": "2012",
                "type": "matches"
            },
            {
                "id": "comp_clausura_2012",
                "name": "Torneo Clausura 2012",
                "url": "https://www.chuncho.com/resulcc2012.html",
                "season": "2012",
                "type": "matches"
            },
            {
                "id": "comp_libertadores_2012",
                "name": "Copa Libertadores 2012",
                "url": "https://www.chuncho.com/lib2012.html",
                "season": "2012",
                "type": "matches"
            },
            {
                "id": "comp_copachile_2012",
                "name": "Copa Chile 2012",
                "url": "https://www.chuncho.com/resulch2012.html",
                "season": "2012",
                "type": "matches"
            },
            {
                "id": "comp_recopa_2012",
                "name": "Recopa Sudamericana 2012",
                "url": "https://www.chuncho.com/rec2012.html",
                "season": "2012",
                "type": "matches"
            },
            {
                "id": "comp_suruga_2012",
                "name": "Suruga Bank 2012",
                "url": "https://www.chuncho.com/sur2012.html",
                "season": "2012",
                "type": "matches"
            },
            {
                "id": "comp_sudamericana_2012",
                "name": "Copa Sudamericana 2012",
                "url": "https://www.chuncho.com/sud2012.html",
                "season": "2012",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_apertura_2012",
                "name": "Torneo Apertura 2012",
                "url": "https://www.chuncho.com/tablaca2012.html",
                "season": "2012",
                "type": "table"
            },
            {
                "id": "comp_clausura_2012",
                "name": "Torneo Clausura 2012",
                "url": "https://www.chuncho.com/tablacc2012.html",
                "season": "2012",
                "type": "table"
            },
            {
                "id": "comp_libertadores_2012",
                "name": "Copa Libertadores 2012",
                "url": "https://www.chuncho.com/tablacl2012.html",
                "season": "2012",
                "type": "table"
            },
            {
                "id": "comp_copachile_2012",
                "name": "Copa Chile 2012",
                "url": "https://www.chuncho.com/tablach2012.html",
                "season": "2012",
                "type": "table"
            }
        ]
    },
    2011: {
        "resultados": [
            {
                "id": "comp_apertura_2011",
                "name": "Torneo Apertura 2011",
                "url": "https://www.chuncho.com/resulca2011.html",
                "season": "2011",
                "type": "matches"
            },
            {
                "id": "comp_clausura_2011",
                "name": "Torneo Clausura 2011",
                "url": "https://www.chuncho.com/resulcc2011.html",
                "season": "2011",
                "type": "matches"
            },
            {
                "id": "comp_sudamericana_2011",
                "name": "Copa Sudamericana 2011",
                "url": "https://www.chuncho.com/sud2011.html",
                "season": "2011",
                "type": "matches"
            }
        ],
        "tablas": [
            {
                "id": "comp_apertura_2011",
                "name": "Torneo Apertura 2011",
                "url": "https://www.chuncho.com/tablaca2011.html",
                "season": "2011",
                "type": "table"
            },
            {
                "id": "comp_clausura_2011",
                "name": "Torneo Clausura 2011",
                "url": "https://www.chuncho.com/tablacc2011.html",
                "season": "2011",
                "type": "table"
            }
        ]
    }
}

# (Se mantienen las configuraciones anteriores de 2002-2012 para completitud, aunque omitidas por brevedad o re-agregadas)
# ... las re-agregaré por completitud.
for y in [2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009]:
    TEMPORADAS_CONFIG[y] = [
        {"id": f"comp_apertura_{y}", "name": f"Torneo Apertura {y}", "url": f"https://www.chuncho.com/resulca{y}.html", "season": str(y), "type": "matches"},
        {"id": f"comp_clausura_{y}", "name": f"Torneo Clausura {y}", "url": f"https://www.chuncho.com/resulcc{y}.html", "season": str(y), "type": "matches"},
    ]
TEMPORADAS_CONFIG[2010] = [{"id": "comp_nacional_2010", "name": "Campeonato Nacional 2010", "url": "https://www.chuncho.com/resulna2010.html", "season": "2010", "type": "matches"}]

MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

def parse_spanish_date(day_str: str, month_str: str, year_str: str) -> datetime.date:
    day = int(day_str)
    month = MONTHS.get(month_str.lower(), 1)
    year = int(year_str)
    if year < 100: year += 1900
    return datetime.date(year, month, day)

def format_stage(raw_stage: str) -> str:
    s = raw_stage.title().strip()
    replacements = {
        "Primera": "1", "Segunda": "2", "Tercera": "3", "Cuarta": "4", 
        "Quinta": "5", "Sexta": "6", "Séptima": "7", "Septima": "7", 
        "Octava": "8", "Novena": "9", "Décima": "10", "Decima": "10",
        "Undécima": "11", "Duodécima": "12", "Decimotercera": "13", 
        "Decimocuarta": "14", "Decimoquinta": "15", "Decimosexta": "16", 
        "Decimoséptima": "17", "Decimoseptima": "17", "Decimoctava": "18", 
        "Decimonovena": "19", "Vigésima": "20", "Vigesima": "20",
        "Vigesimoprimera": "21", "Vigésima Primera": "21", "Vigesima Primera": "21",
        "Vigesimosegunda": "22", "Vigésima Segunda": "22", "Vigesima Segunda": "22",
        "Vigesimotercera": "23", "Vigésima Tercera": "23", "Vigesima Tercera": "23",
        "Vigesimocuarta": "24", "Vigésima Cuarta": "24", "Vigesima Cuarta": "24",
        "Vigesimoquinta": "25", "Vigésima Quinta": "25", "Vigesima Quinta": "25",
        "Vigesimosexta": "26", "Vigésima Sexta": "26", "Vigesima Sexta": "26",
        "Vigesimoséptima": "27", "Vigesimoseptima": "27", "Vigésima Séptima": "27", "Vigesima Septima": "27",
        "Vigesimooctava": "28", "Vigesimoctava": "28", "Vigésima Octava": "28", "Vigesima Octava": "28",
        "Vigesimonovena": "29", "Vigésima Novena": "29", "Vigesima Novena": "29",
        "Trigésima": "30", "Trigesima": "30",
        "Trigesimoprimera": "31", "Trigésima Primera": "31", "Trigesima Primera": "31",
        "Trigesimosegunda": "32", "Trigésima Segunda": "32", "Trigesima Segunda": "32",
        "Trigesimotercera": "33", "Trigésima Tercera": "33", "Trigesima Tercera": "33",
        "Trigesimocuarta": "34", "Trigésima Cuarta": "34", "Trigesima Cuarta": "34",
    }
    
    for word in sorted(replacements.keys(), key=len, reverse=True):
        number = replacements[word]
        # Usamos \b para asegurar que "Octava" no intercepte el final de "Vigesimoctava"
        pattern = re.compile(rf"\b{word}\s+Fecha", re.IGNORECASE)
        s = pattern.sub(f"Fecha {number}", s)
        
    s = s.replace(" - Ida", " (Ida)")
    s = s.replace(" - Vuelta", " (Vuelta)")
    s = s.replace("Semifinales", "Semifinal")
    s = s.replace("Octavos De Final", "Octavos")
    s = s.replace("Cuartos De Final", "Cuartos")
    return s

def fetch_html_with_cache(url: str, year: int, force: bool) -> str:
    """Implementa capa de caché HTML offline profesional."""
    cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cache", str(year))
    os.makedirs(cache_dir, exist_ok=True)
    
    filename = url.split("/")[-1]
    cache_path = os.path.join(cache_dir, filename)
    
    encoding_to_use = 'utf-8' if year >= 2024 else 'latin-1'
    
    if not force and os.path.exists(cache_path):
        print(f"  [CACHÉ] Leyendo {filename} desde disco local...")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()
            
    print(f"  [RED] Descargando {url}...")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = httpx.get(url, headers=headers, timeout=15.0, follow_redirects=True)
    if response.status_code == 404:
        raise Exception("404 Not Found")
    response.raise_for_status()
    
    try:
        # Intentamos decodificar como UTF-8 estrictamente.
        # Las páginas nuevas de chuncho.com podrían venir en UTF-8 reales.
        html_content = response.content.decode('utf-8', errors='strict')
    except UnicodeDecodeError:
        # Si falla (ej. resulch2025.html con la palabra "Curicó"), 
        # significa que el archivo realmente está en latin-1 aunque su meta tag diga otra cosa.
        html_content = response.content.decode('latin-1')
    
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    return html_content

def parse_league_table(html_content: str, comp_id: str, comp_name: str, season: str, repo: SqliteLeagueTableRepository):
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all('table')
    if not tables:
        print("  -> [ADVERTENCIA] No se encontraron tablas HTML.")
        return 0
        
    entries = []
    
    for tbl in tables:
        rows = tbl.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            # Buscamos filas que parezcan estadísticas (al menos 8-9 columnas con números)
            if len(cols) >= 8:
                row_text = " ".join([c.get_text(strip=True) for c in cols])
                if "Pts" in row_text or "PTS" in row_text:
                    continue # Header
                
                try:
                    # Normalmente el formato de Chuncho es:
                    # N° | Equipo | PJ | PG | PE | PP | GF | GC | PTS
                    # o similar, a veces con un dif_goles.
                    
                    # Asumimos que los que tienen al menos un dígito son posiciones.
                    col_texts = [c.get_text(separator=" ", strip=True) for c in cols]
                    col_texts = [c.replace("\xa0", " ").strip() for c in col_texts if c.strip() != ""]
                    
                    if len(col_texts) >= 8:
                        team_idx = -1
                        team_name = ""
                        for i, c in enumerate(col_texts):
                            if not re.match(r'^\d+$', c) and not re.match(r'^[+-]?\d+$', c):
                                team_name = c
                                team_idx = i
                                break
                                
                        if team_idx == -1 or len(col_texts) < team_idx + 8:
                            continue
                            
                        try:
                            pj = int(col_texts[team_idx + 1].replace("+", ""))
                            pg = int(col_texts[team_idx + 2].replace("+", ""))
                            pe = int(col_texts[team_idx + 3].replace("+", ""))
                            pp = int(col_texts[team_idx + 4].replace("+", ""))
                            gf = int(col_texts[team_idx + 5].replace("+", ""))
                            gc = int(col_texts[team_idx + 6].replace("+", ""))
                            pts = int(col_texts[team_idx + 7].replace("+", ""))
                        except ValueError:
                            continue
                            
                        pos = len(entries) + 1
                        dif = gf - gc
                        
                        entries.append(TableEntry(
                            position=pos,
                            team_name=team_name,
                            played=pj,
                            won=pg,
                            drawn=pe,
                            lost=pp,
                            goals_for=gf,
                            goals_against=gc,
                            points=pts,
                            goal_difference=dif
                        ))
                except Exception as e:
                    continue

    if entries:
        lt = LeagueTable(competition_id=comp_id, competition_name=comp_name, season=season, entries=entries)
        repo.insert_league_table(lt)
        print(f"  [OK] Tabla importada con {len(entries)} equipos.")
        return len(entries)
    return 0

def scrape_year_config(year: int, clear: bool, force: bool):
    print(f"--- INICIANDO IMPORTACIÓN BASADA EN CONFIGURACIÓN PARA {year} ---")
    
    if year not in TEMPORADAS_CONFIG:
        print(f"ERROR: La temporada {year} aún no está implementada en TEMPORADAS_CONFIG.")
        sys.exit(1)
        
    db = SqliteDatabase("udechile_stats.db")
    db.initialize_schema()
    
    if clear:
        print("¡ATENCIÓN! Limpiando toda la base de datos histórica por orden de la flag --clear...")
        db.clear_all_data()
        
    repo = SqliteMatchRepository(db)
    table_repo = SqliteLeagueTableRepository(db)
    att_repo = SqliteAttendanceRepository(db)
    
    teams_regex = re.compile(r"^\s*(.*?)\s+(\d+)(?:\s*\((\d+)\))?\s*v/s\s*(.*?)\s+(\d+)(?:\s*\((\d+)\))?", re.IGNORECASE)
    date_regex = re.compile(r"(\d{1,2})\s+de\s+([a-zA-Z]+)\s+de\s+(\d{2,4})", re.IGNORECASE)
    stadium_regex = re.compile(r"Cancha:\s*(.*?)(?:\.|$)", re.IGNORECASE)
    
    torneos_raw = TEMPORADAS_CONFIG[year]
    
    if isinstance(torneos_raw, dict):
        torneos = torneos_raw.get("resultados", []) + torneos_raw.get("tablas", [])
    else:
        torneos = torneos_raw
        
    for torneo in torneos:
        comp_id = torneo["id"]
        comp_name = torneo["name"]
        url = torneo["url"]
        season = torneo["season"]
        t_type = torneo.get("type", "matches")
        
        print(f"\nProcesando: {comp_name} ({t_type})")
        print(f"Fuente URL: {url}")
        
        try:
            html_content = fetch_html_with_cache(url, year, force)
        except Exception as e:
            print(f"  -> Error al descargar/leer: {e}")
            continue
            
        if t_type == "table":
            parse_league_table(html_content, comp_id, comp_name, season, table_repo)
            continue
            
        # Parseo de Matches
        soup = BeautifulSoup(html_content, "html.parser")
        tags = soup.find_all(['h2', 'h3', 'h4', 'h5', 'p', 'b'])
        
        comp_saved = 0
        current_stage = "Fase Regular"
        active_comp_id = comp_id
        active_comp_name = comp_name
        
        for idx, tag in enumerate(tags):
            original_text = tag.get_text(separator="\n").strip()
            text = tag.get_text(separator=" ").strip()
            text = re.sub(r'\s+', ' ', text)
            
            # Normalizar erratas tipográficas en el separador 'v/s' (por ejemplo 'v/a', 'v/e', 'vs', etc.)
            text = re.sub(r'\s+v/[saecdp]\s+', ' v/s ', text, flags=re.IGNORECASE)
            text = re.sub(r'\s+vs\s+', ' v/s ', text, flags=re.IGNORECASE)
            text = re.sub(r'\s+v\.s\.\s+', ' v/s ', text, flags=re.IGNORECASE)
            
            original_text = re.sub(r'\s+v/[saecdp]\s+', ' v/s ', original_text, flags=re.IGNORECASE)
            original_text = re.sub(r'\s+vs\s+', ' v/s ', original_text, flags=re.IGNORECASE)
            original_text = re.sub(r'\s+v\.s\.\s+', ' v/s ', original_text, flags=re.IGNORECASE)
            
            if not text: continue
            
            # Exclusión Absoluta de Fechas Libres (Bye Weeks)
            if text.lower().startswith("libre"):
                continue
                
            if "v/s" not in text:
                if "Copa de Verano Coquimbo" in text:
                    active_comp_id = f"comp_amistoso_{year}"
                    active_comp_name = f"Amistoso {year}"
                    current_stage = "Copa de Verano Coquimbo"
                elif "Torneo de Verano" in text:
                    active_comp_id = f"comp_amistoso_{year}"
                    active_comp_name = f"Amistoso {year}"
                    current_stage = format_stage(text)
                elif "Amistoso" in text or "Noche" in text:
                    active_comp_id = f"comp_amistoso_{year}"
                    active_comp_name = f"Amistoso {year}"
                    current_stage = "Amistoso"
                else:
                    if "resulcc2011.html" in url and "Copa Chile" in text:
                        active_comp_id = "comp_copachile_2011"
                        active_comp_name = "Copa Chile 2011"
                    else:
                        # Regresa a la competición base en caso de que fuera otra etapa normal
                        if active_comp_id != comp_id and "amistoso" not in text.lower():
                            active_comp_id = comp_id
                            active_comp_name = comp_name
                    current_stage = format_stage(text)
                continue
                
            try:
                home_penalties = None
                away_penalties = None
                
                teams_match = teams_regex.search(text)
                if not teams_match:
                    if "v/s" not in text:
                        continue
                        
                    clean_text = re.sub(r'\[.*?\]', '', text)
                    clean_text = re.sub(r'\(.*?\)', '', clean_text)
                    parts = clean_text.split("v/s")
                    if len(parts) < 2:
                        continue
                        
                    home_team_raw = parts[0].strip()
                    home_team = re.sub(r'\s+\d+$', '', home_team_raw).strip()
                    
                    day_words = r'(?:Lunes|Martes|Miércoles|Miercoles|Jueves|Viernes|Sábado|Sabado|Domingo)'
                    away_part = re.split(day_words, parts[1], flags=re.IGNORECASE)[0].strip()
                    away_part = away_part.split("Fecha:")[0].strip()
                    away_team = re.sub(r'^\d+\s+', '', away_part).strip()
                    away_team = re.sub(r'\s+\d+$', '', away_team).strip()
                    
                    goal_matches = re.findall(r'(\d+)x(\d+)', text)
                    if goal_matches:
                        home_score, away_score = int(goal_matches[-1][0]), int(goal_matches[-1][1])
                    elif "no hubo" in text.lower():
                        home_score, away_score = 0, 0
                    else:
                        continue
                else:
                    home_team = teams_match.group(1).strip()
                    home_score = int(teams_match.group(2))
                    home_penalties = int(teams_match.group(3)) if teams_match.group(3) else None
                    away_team = teams_match.group(4).strip()
                    away_score = int(teams_match.group(5))
                    away_penalties = int(teams_match.group(6)) if teams_match.group(6) else None
                
                if home_penalties is None and away_penalties is None and "penal" in text.lower():
                    match_block = original_text.split("Cancha:", 1)[0]
                    pen_matches = re.findall(r'\(\s*(\d+)\s*\)\s*:', match_block)
                    if len(pen_matches) == 2:
                        home_penalties = int(pen_matches[0])
                        away_penalties = int(pen_matches[1])
                
                date_match = date_regex.search(text)
                if date_match:
                    match_date = parse_spanish_date(date_match.group(1), date_match.group(2), date_match.group(3))
                else:
                    slash_date_match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
                    if slash_date_match:
                        match_date = datetime.date(int(slash_date_match.group(3)), int(slash_date_match.group(2)), int(slash_date_match.group(1)))
                    else:
                        match_date = datetime.date(year, 1, 1)
                
                if match_date.year != year:
                    if year == 2021 and match_date.year == 2020:
                        match_date = datetime.date(2021, match_date.month, match_date.day)
                    elif match_date.year not in [year - 1, year, year + 1]:
                        print(f"  [WARN] Año anómalo detectado ({match_date.year}). Corrigiendo a {year}...")
                        match_date = datetime.date(year, match_date.month, match_date.day)
                    
                stadium_match = re.search(r"Cancha:\s*([^\n\.]+)", original_text, re.IGNORECASE)
                if stadium_match:
                    stadium_name = stadium_match.group(1).strip()
                else:
                    stadium_name = "Estadio Desconocido"
                    
                # Comprobar si ya existe un partido con la misma fecha, local y visita para evitar duplicados
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id FROM matches 
                        WHERE date = ? AND home_team = ? AND away_team = ?
                    """, (match_date.isoformat(), home_team, away_team))
                    existing_match = cursor.fetchone()
                
                if existing_match:
                    match_id = existing_match["id"]
                else:
                    match_id = f"chuncho_{match_date.strftime('%Y%m%d')}_{uuid.uuid4().hex[:4]}"
                    
                stadium_id = f"st_{stadium_name.replace(' ', '_').replace(',', '').lower()[:20]}"
                stadium = Stadium(id=stadium_id, name=stadium_name)
                
                competition = Competition(id=active_comp_id, name=active_comp_name, season=season)
                
                domain_match = Match(
                    id=match_id, date=match_date, home_team=home_team, away_team=away_team,
                    home_score=home_score, away_score=away_score, 
                    home_penalties=home_penalties, away_penalties=away_penalties,
                    stadium=stadium, competition=competition, stage=current_stage, attendance_count=None
                )
                
                repo.insert_match(domain_match)
                comp_saved += 1
                
                print(f"  [OK] {match_date.strftime('%d/%m/%Y')} | {current_stage[:25]:<25} | {home_team[:15]:<15} {home_score}-{away_score} {away_team[:15]:<15}")
                
            except Exception as e:
                print(f"  [ERROR] Fila omitida por error: {e} | {text[:50]}")
                pass
                
        print(f"  -> {comp_saved} partidos importados para {comp_name}.")
        time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper Basado en Configuración (Con Caché y Tablas)")
    parser.add_argument("--year", type=int, required=True, help="Año a importar")
    parser.add_argument("--clear", action="store_true", help="Limpia la BD antes")
    parser.add_argument("--force", action="store_true", help="Fuerza descarga de internet ignorando caché")
    
    args = parser.parse_args()
    scrape_year_config(args.year, args.clear, args.force)
