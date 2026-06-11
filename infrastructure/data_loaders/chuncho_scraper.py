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
TEMPORADAS_CONFIG[1997] = {
    "resultados": [
        {
            "id": "comp_apertura_1997",
            "name": "Torneo Apertura 1997",
            "url": "https://www.chuncho.com/resulca97.html",
            "season": "1997",
            "type": "matches"
        },
        {
            "id": "comp_clausura_1997",
            "name": "Torneo Clausura 1997",
            "url": "https://www.chuncho.com/resulcc97.html",
            "season": "1997",
            "type": "matches"
        },
        {
            "id": "comp_conmebol_1997",
            "name": "Copa Conmebol 1997",
            "url": "https://www.chuncho.com/conme97.html",
            "season": "1997",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_1997",
            "name": "Torneo Apertura 1997",
            "url": "https://www.chuncho.com/tablaca97.html",
            "season": "1997",
            "type": "table"
        },
        {
            "id": "comp_clausura_1997",
            "name": "Torneo Clausura 1997",
            "url": "https://www.chuncho.com/tablacc97.html",
            "season": "1997",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[1998] = {
    "resultados": [
        {
            "id": "comp_nacional_1998",
            "name": "Campeonato Nacional 1998",
            "url": "https://www.chuncho.com/resulna98.html",
            "season": "1998",
            "type": "matches"
        },
        {
            "id": "comp_copachile_1998",
            "name": "Copa Chile 1998",
            "url": "https://www.chuncho.com/resulch98.html",
            "season": "1998",
            "type": "matches"
        },
        {
            "id": "comp_mercosur_1998",
            "name": "Copa Mercosur 1998",
            "url": "https://www.chuncho.com/merco98.html",
            "season": "1998",
            "type": "matches"
        },
        {
            "id": "comp_prelibertadores_1998",
            "name": "Liguilla Pre-Libertadores 1998",
            "url": "https://www.chuncho.com/resulpl98.html",
            "season": "1998",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_nacional_1998",
            "name": "Campeonato Nacional 1998",
            "url": "https://www.chuncho.com/tablana98.html",
            "season": "1998",
            "type": "table"
        },
        {
            "id": "comp_copachile_1998",
            "name": "Copa Chile 1998",
            "url": "https://www.chuncho.com/tablach98.html",
            "season": "1998",
            "type": "table",
            "caption_filter": "grupo 2"
        },
        {
            "id": "comp_mercosur_1998",
            "name": "Copa Mercosur 1998",
            "url": "https://www.chuncho.com/tablams98.html",
            "season": "1998",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[1999] = {
    "resultados": [
        {
            "id": "comp_nacional_1999",
            "name": "Campeonato Nacional 1999",
            "url": "https://www.chuncho.com/resulna99.html",
            "season": "1999",
            "type": "matches"
        },
        {
            "id": "comp_mercosur_1999",
            "name": "Copa Mercosur 1999",
            "url": "https://www.chuncho.com/merco99.html",
            "season": "1999",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_nacional_1999_fase_regular",
            "name": "Campeonato Nacional 1999 (Fase Regular)",
            "url": "https://www.chuncho.com/tablana99.html",
            "season": "1999",
            "type": "table",
            "caption_filter": "primera fase"
        },
        {
            "id": "comp_nacional_1999_octogonal",
            "name": "Campeonato Nacional 1999 (Octogonal Final)",
            "url": "https://www.chuncho.com/tablana99.html",
            "season": "1999",
            "type": "table",
            "caption_filter": "octogonal por el t"
        },
        {
            "id": "comp_mercosur_1999",
            "name": "Copa Mercosur 1999",
            "url": "https://www.chuncho.com/tablams99.html",
            "season": "1999",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2000] = {
    "resultados": [
        {
            "id": "comp_nacional_2000",
            "name": "Campeonato Nacional 2000",
            "url": "https://www.chuncho.com/resulna2000.html",
            "season": "2000",
            "type": "matches"
        },
        {
            "id": "comp_copachile_2000",
            "name": "Copa Chile 2000",
            "url": "https://www.chuncho.com/resulta2000.html",
            "season": "2000",
            "type": "matches"
        },
        {
            "id": "comp_mercosur_2000",
            "name": "Copa Mercosur 2000",
            "url": "https://www.chuncho.com/merco2000.html",
            "season": "2000",
            "type": "matches"
        },
        {
            "id": "comp_libertadores_2000",
            "name": "Copa Libertadores 2000",
            "url": "https://www.chuncho.com/lib2000.html",
            "season": "2000",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_nacional_2000",
            "name": "Campeonato Nacional 2000",
            "url": "https://www.chuncho.com/tablana2000.html",
            "season": "2000",
            "type": "table"
        },
        {
            "id": "comp_mercosur_2000",
            "name": "Copa Mercosur 2000",
            "url": "https://www.chuncho.com/tablams2000.html",
            "season": "2000",
            "type": "table"
        },
        {
            "id": "comp_libertadores_2000",
            "name": "Copa Libertadores 2000",
            "url": "https://www.chuncho.com/tablacl2000.html",
            "season": "2000",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2001] = {
    "resultados": [
        {
            "id": "comp_nacional_2001",
            "name": "Campeonato Nacional 2001",
            "url": "https://www.chuncho.com/resulna2001.html",
            "season": "2001",
            "type": "matches"
        },
        {
            "id": "comp_mercosur_2001",
            "name": "Copa Mercosur 2001",
            "url": "https://www.chuncho.com/merco2001.html",
            "season": "2001",
            "type": "matches"
        },
        {
            "id": "comp_libertadores_2001",
            "name": "Copa Libertadores 2001",
            "url": "https://www.chuncho.com/lib2001.html",
            "season": "2001",
            "type": "matches"
        },
        {
            "id": "comp_prelibertadores_2001",
            "name": "Pre-Libertadores 2001",
            "url": "https://www.chuncho.com/resulpl2001.html",
            "season": "2001",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_nacional_2001",
            "name": "Campeonato Nacional 2001",
            "url": "https://www.chuncho.com/tablana2001.html",
            "season": "2001",
            "type": "table"
        },
        {
            "id": "comp_mercosur_2001",
            "name": "Copa Mercosur 2001",
            "url": "https://www.chuncho.com/tablams2001.html",
            "season": "2001",
            "type": "table"
        },
        {
            "id": "comp_libertadores_2001",
            "name": "Copa Libertadores 2001",
            "url": "https://www.chuncho.com/tablacl2001.html",
            "season": "2001",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2002] = {
    "resultados": [
        {
            "id": "comp_apertura_2002",
            "name": "Torneo Apertura 2002",
            "url": "https://www.chuncho.com/resulca2002.html",
            "season": "2002",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2002",
            "name": "Torneo Clausura 2002",
            "url": "https://www.chuncho.com/resulcc2002.html",
            "season": "2002",
            "type": "matches"
        },
        {
            "id": "comp_presudamericana_2002",
            "name": "Pre-Sudamericana 2002",
            "url": "https://www.chuncho.com/resulps2002.html",
            "season": "2002",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2002",
            "name": "Torneo Apertura 2002",
            "url": "https://www.chuncho.com/tablaca2002.html",
            "season": "2002",
            "type": "table"
        },
        {
            "id": "comp_clausura_2002",
            "name": "Torneo Clausura 2002",
            "url": "https://www.chuncho.com/tablacc2002.html",
            "season": "2002",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2003] = {
    "resultados": [
        {
            "id": "comp_apertura_2003",
            "name": "Torneo Apertura 2003",
            "url": "https://www.chuncho.com/resulca2003.html",
            "season": "2003",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2003",
            "name": "Torneo Clausura 2003",
            "url": "https://www.chuncho.com/resulcc2003.html",
            "season": "2003",
            "type": "matches"
        },
        {
            "id": "comp_presudamericana_2003",
            "name": "Pre-Sudamericana 2003",
            "url": "https://www.chuncho.com/resulps2003.html",
            "season": "2003",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2003",
            "name": "Torneo Apertura 2003",
            "url": "https://www.chuncho.com/tablaca2003.html",
            "season": "2003",
            "type": "table"
        },
        {
            "id": "comp_clausura_2003",
            "name": "Torneo Clausura 2003",
            "url": "https://www.chuncho.com/tablacc2003.html",
            "season": "2003",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2004] = {
    "resultados": [
        {
            "id": "comp_apertura_2004",
            "name": "Torneo Apertura 2004",
            "url": "https://www.chuncho.com/resulca2004.html",
            "season": "2004",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2004",
            "name": "Torneo Clausura 2004",
            "url": "https://www.chuncho.com/resulcc2004.html",
            "season": "2004",
            "type": "matches"
        },
        {
            "id": "comp_presudamericana_2004",
            "name": "Pre-Sudamericana 2004",
            "url": "https://www.chuncho.com/resulps2004.html",
            "season": "2004",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2004",
            "name": "Torneo Apertura 2004",
            "url": "https://www.chuncho.com/tablaca2004.html",
            "season": "2004",
            "type": "table"
        },
        {
            "id": "comp_clausura_2004",
            "name": "Torneo Clausura 2004",
            "url": "https://www.chuncho.com/tablacc2004.html",
            "season": "2004",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2005] = {
    "resultados": [
        {
            "id": "comp_apertura_2005",
            "name": "Torneo Apertura 2005",
            "url": "https://www.chuncho.com/resulca2005.html",
            "season": "2005",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2005",
            "name": "Torneo Clausura 2005",
            "url": "https://www.chuncho.com/resulcc2005.html",
            "season": "2005",
            "type": "matches"
        },
        {
            "id": "comp_libertadores_2005",
            "name": "Copa Libertadores 2005",
            "url": "https://www.chuncho.com/lib2005.html",
            "season": "2005",
            "type": "matches"
        },
        {
            "id": "comp_sudamericana_2005",
            "name": "Copa Sudamericana 2005",
            "url": "https://www.chuncho.com/sud2005.html",
            "season": "2005",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2005",
            "name": "Torneo Apertura 2005",
            "url": "https://www.chuncho.com/tablaca2005.html",
            "season": "2005",
            "type": "table"
        },
        {
            "id": "comp_clausura_2005",
            "name": "Torneo Clausura 2005",
            "url": "https://www.chuncho.com/tablacc2005.html",
            "season": "2005",
            "type": "table"
        },
        {
            "id": "comp_libertadores_2005",
            "name": "Copa Libertadores 2005",
            "url": "https://www.chuncho.com/tablacl2005.html",
            "season": "2005",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2006] = {
    "resultados": [
        {
            "id": "comp_apertura_2006",
            "name": "Torneo Apertura 2006",
            "url": "https://www.chuncho.com/resulca2006.html",
            "season": "2006",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2006",
            "name": "Torneo Clausura 2006",
            "url": "https://www.chuncho.com/resulcc2006.html",
            "season": "2006",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2006",
            "name": "Torneo Apertura 2006",
            "url": "https://www.chuncho.com/tablaca2006.html",
            "season": "2006",
            "type": "table"
        },
        {
            "id": "comp_clausura_2006",
            "name": "Torneo Clausura 2006",
            "url": "https://www.chuncho.com/tablacc2006.html",
            "season": "2006",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2007] = {
    "resultados": [
        {
            "id": "comp_apertura_2007",
            "name": "Torneo Apertura 2007",
            "url": "https://www.chuncho.com/resulca2007.html",
            "season": "2007",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2007",
            "name": "Torneo Clausura 2007",
            "url": "https://www.chuncho.com/resulcc2007.html",
            "season": "2007",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2007",
            "name": "Torneo Apertura 2007",
            "url": "https://www.chuncho.com/tablaca2007.html",
            "season": "2007",
            "type": "table"
        },
        {
            "id": "comp_clausura_2007",
            "name": "Torneo Clausura 2007",
            "url": "https://www.chuncho.com/tablacc2007.html",
            "season": "2007",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2008] = {
    "resultados": [
        {
            "id": "comp_apertura_2008",
            "name": "Torneo Apertura 2008",
            "url": "https://www.chuncho.com/resulca2008.html",
            "season": "2008",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2008",
            "name": "Torneo Clausura 2008",
            "url": "https://www.chuncho.com/resulcc2008.html",
            "season": "2008",
            "type": "matches"
        },
        {
            "id": "comp_copachile_2008",
            "name": "Copa Chile 2008",
            "url": "https://www.chuncho.com/anuarios/cap2008cch.html",
            "season": "2008",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2008",
            "name": "Torneo Apertura 2008",
            "url": "https://www.chuncho.com/tablaca2008.html",
            "season": "2008",
            "type": "table"
        },
        {
            "id": "comp_clausura_2008",
            "name": "Torneo Clausura 2008",
            "url": "https://www.chuncho.com/tablacc2008.html",
            "season": "2008",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2009] = {
    "resultados": [
        {
            "id": "comp_apertura_2009",
            "name": "Torneo Apertura 2009",
            "url": "https://www.chuncho.com/resulca2009.html",
            "season": "2009",
            "type": "matches"
        },
        {
            "id": "comp_clausura_2009",
            "name": "Torneo Clausura 2009",
            "url": "https://www.chuncho.com/resulcc2009.html",
            "season": "2009",
            "type": "matches"
        },
        {
            "id": "comp_libertadores_2009",
            "name": "Copa Libertadores 2009",
            "url": "https://www.chuncho.com/lib2009.html",
            "season": "2009",
            "type": "matches"
        },
        {
            "id": "comp_sudamericana_2009",
            "name": "Copa Sudamericana 2009",
            "url": "https://www.chuncho.com/sud2009.html",
            "season": "2009",
            "type": "matches"
        },
        {
            "id": "comp_copachile_2009",
            "name": "Copa Chile 2009",
            "url": "https://www.chuncho.com/anuarios/cap2009cch.html",
            "season": "2009",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_apertura_2009",
            "name": "Torneo Apertura 2009",
            "url": "https://www.chuncho.com/tablaca2009.html",
            "season": "2009",
            "type": "table"
        },
        {
            "id": "comp_clausura_2009",
            "name": "Torneo Clausura 2009",
            "url": "https://www.chuncho.com/tablacc2009.html",
            "season": "2009",
            "type": "table"
        },
        {
            "id": "comp_libertadores_2009",
            "name": "Copa Libertadores 2009",
            "url": "https://www.chuncho.com/tablacl2009.html",
            "season": "2009",
            "type": "table"
        }
    ]
}
TEMPORADAS_CONFIG[2010] = {
    "resultados": [
        {
            "id": "comp_nacional_2010",
            "name": "Campeonato Nacional 2010",
            "url": "https://www.chuncho.com/resulna2010.html",
            "season": "2010",
            "type": "matches"
        },
        {
            "id": "comp_libertadores_2010",
            "name": "Copa Libertadores 2010",
            "url": "https://www.chuncho.com/lib2010.html",
            "season": "2010",
            "type": "matches"
        },
        {
            "id": "comp_sudamericana_2010",
            "name": "Copa Sudamericana 2010",
            "url": "https://www.chuncho.com/sud2010.html",
            "season": "2010",
            "type": "matches"
        },
        {
            "id": "comp_copachile_2010",
            "name": "Copa Chile 2010",
            "url": "https://www.chuncho.com/anuarios/cap2010cch.html",
            "season": "2010",
            "type": "matches"
        }
    ],
    "tablas": [
        {
            "id": "comp_nacional_2010",
            "name": "Campeonato Nacional 2010",
            "url": "https://www.chuncho.com/tablana2010.html",
            "season": "2010",
            "type": "table"
        },
        {
            "id": "comp_libertadores_2010",
            "name": "Copa Libertadores 2010",
            "url": "https://www.chuncho.com/tablacl2010.html",
            "season": "2010",
            "type": "table"
        }
    ]
}

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
    # 1. Normalizar eliminando acentos
    s_norm = raw_stage.lower()
    for orig, dest in [("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n")]:
        s_norm = s_norm.replace(orig, dest)
    
    # 2. Remover cualquier carácter no alfabético ni numérico (como , tildes dañadas, etc.)
    s_norm = re.sub(r'[^a-z0-9\s]', '', s_norm)
    # Reducir espacios múltiples
    s_norm = re.sub(r'\s+', ' ', s_norm).strip()
        
    replacements = {
        "primera": "1", "segunda": "2", "tercera": "3", "cuarta": "4", 
        "quinta": "5", "sexta": "6", "septima": "7", "octava": "8", 
        "novena": "9", "decima": "10", "undecima": "11", "duodecima": "12", 
        "decimoprimera": "11", "decimosegunda": "12",
        "decimotercera": "13", "decimocuarta": "14", "decimoquinta": "15", 
        "decimosexta": "16", "decimoseptima": "17", "decimoctava": "18", "decimooctava": "18",
        "decimonovena": "19", "vigesima": "20",
        "vigesimaprimera": "21", "vigesima primera": "21", "vigesimoprimera": "21",
        "vigesimosegunda": "22", "vigesima segunda": "22",
        "vigesimotercera": "23", "vigesima tercera": "23",
        "vigesimocuarta": "24", "vigesima cuarta": "24",
        "vigesimoquinta": "25", "vigesima quinta": "25",
        "vigesimosexta": "26", "vigesima sexta": "26",
        "vigesimoseptima": "27", "vigesima septima": "27",
        "vigesimooctava": "28", "vigesimoctava": "28",
        "vigesimonovena": "29", "vigesima novena": "29",
        "trigesima": "30",
        "trigesimaprimera": "31", "trigesima primera": "31",
        "trigesimosegunda": "32", "trigesima segunda": "32",
        "trigesimotercera": "33", "trigesima tercera": "33",
        "trigesimocuarta": "34", "trigesima cuarta": "34",
        # Variantes por caracteres rotos omitidos (ej: "Dcimotercera" -> "dcimotercera")
        "dcimotercera": "13", "dcimocuarta": "14", "dcimoquinta": "15",
        "dcimosexta": "16", "dcimoseptima": "17", "dcimoctava": "18", "dcimooctava": "18",
        "dcimonovena": "19", "dcima": "10", "undcima": "11", "duodcima": "12",
        "vigcima": "20", "trigcima": "30"
    }
    
    # Intentar buscar e intercambiar las palabras
    matched = False
    for word, number in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        pattern1 = re.compile(rf"\b{word}\s+fecha\b", re.IGNORECASE)
        pattern2 = re.compile(rf"\bfecha\s+{word}\b", re.IGNORECASE)
        if pattern1.search(s_norm) or pattern2.search(s_norm):
            s_norm = f"Fecha {number}"
            matched = True
            break
            
    # Si la cadena es exactamente la palabra ordinal sola:
    if not matched:
        cleaned_word = s_norm.strip()
        if cleaned_word in replacements:
            s_norm = f"Fecha {replacements[cleaned_word]}"
            matched = True
            
    if matched:
        s = s_norm.title()
    else:
        # Si no hubo match, limpiamos la cadena para que no tenga tildes rotas
        s = raw_stage.strip()
        # Reemplazar caracteres no ASCII comunes dañados en la cadena original
        s = re.sub(r'[^\x00-\x7F]+', 'e', s) # reemplazar caracteres no-ascii rotos por 'e' o vocales
        s = s.title()
        
    s = s.replace(" - Partido De Ida", " (Ida)")
    s = s.replace(" - Partido De Vuelta", " (Vuelta)")
    s = s.replace("Partido De Ida", " (Ida)")
    s = s.replace("Partido De Vuelta", " (Vuelta)")
    s = s.replace(" - Ida", " (Ida)")
    s = s.replace(" - Vuelta", " (Vuelta)")
    s = s.replace("Semifinales", "Semifinal")
    s = s.replace("Octavos De Final", "Octavos")
    s = s.replace("Cuartos De Final", "Cuartos")
    s = s.replace("Dieciseisavos De Final", "Dieciseisavos")
    
    if "octogonal final" in raw_stage.lower():
        s = f"Octogonal Final - {s}"
        
    if "suspendido" in raw_stage.lower():
        s = f"{s} (Suspendido)"
        
    if "final)" in raw_stage.lower() and "segunda fecha" in raw_stage.lower():
        s = f"{s} (Reprogramado)"
        
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
        try:
            with open(cache_path, "r", encoding=encoding_to_use) as f:
                return f.read()
        except UnicodeDecodeError:
            with open(cache_path, "r", encoding="latin-1") as f:
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

def parse_league_table(html_content: str, comp_id: str, comp_name: str, season: str, repo: SqliteLeagueTableRepository, caption_filter: str = None):
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all('table')
    if not tables:
        print("  -> [ADVERTENCIA] No se encontraron tablas HTML.")
        return 0
        
    best_entries = []
    
    for tbl in tables:
        current_entries = []
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
                            
                        pos = len(current_entries) + 1
                        dif = gf - gc
                        
                        current_entries.append(TableEntry(
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
                except Exception:
                    continue
        
        if len(current_entries) > 0:
            caption = tbl.find('caption')
            caption_text = caption.get_text().lower() if caption else ""
            
            if caption_filter:
                if caption_filter.lower() in caption_text:
                    best_entries = current_entries
                    break
            else:
                # Lógica por defecto: Dar prioridad absoluta a la tabla del octogonal por el título si no hay caption_filter específico
                if "octogonal por el t" in caption_text or "octogonal por el titulo" in caption_text:
                    best_entries = current_entries
                    break
                    
                if len(current_entries) > len(best_entries):
                    best_entries = current_entries

    if best_entries:
        lt = LeagueTable(competition_id=comp_id, competition_name=comp_name, season=season, entries=best_entries)
        repo.insert_league_table(lt)
        print(f"  [OK] Tabla importada con {len(best_entries)} equipos.")
        return len(best_entries)
    return 0

def parse_anuario_campaign_matches(html_content: str, comp_id: str, comp_name: str, season: str, repo: SqliteMatchRepository, year: int) -> int:
    soup = BeautifulSoup(html_content, "html.parser")
    tables = soup.find_all('table')
    comp_saved = 0
    
    target_table = None
    for tbl in tables:
        caption = tbl.find('caption')
        caption_text = caption.get_text() if caption else ""
        if "Campaña" in caption_text or tbl.find('tr'):
            first_row = tbl.find('tr')
            headers = [td.get_text(strip=True).upper() for td in first_row.find_all(['td', 'th'])]
            if "FECHA" in headers and "RIVAL" in headers and "RES" in headers:
                target_table = tbl
                break
                
    if not target_table:
        print("  -> [ERROR] No se encontró la tabla de partidos de campaña en el anuario.")
        return 0
        
    notes_text = soup.get_text()
    
    rows = target_table.find_all('tr')[1:] # Saltamos la cabecera
    for idx, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 4:
            continue
            
        fecha_raw = cols[0].get_text(strip=True)
        cancha = cols[1].get_text(strip=True)
        rival = cols[2].get_text(strip=True)
        res_raw = cols[3].get_text(strip=True) # ej: "2x1"
        notes_col = cols[5].get_text(strip=True) if len(cols) > 5 else ""
        
        # Limpiar rival
        rival = rival.replace("<b>", "").replace("</b>", "").strip()
        
        if not fecha_raw or not res_raw or "x" not in res_raw:
            continue
            
        # Parsear fecha D/M/YYYY
        date_parts = fecha_raw.split("/")
        if len(date_parts) == 3:
            match_date = datetime.date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
        else:
            match_date = datetime.date(year, 1, 1)
            
        # Parsear goles de la U x goles del rival
        res_parts = res_raw.split("x")
        if len(res_parts) == 2:
            try:
                goles_u = int(res_parts[0])
                goles_rival = int(res_parts[1])
            except ValueError:
                continue
        else:
            continue
            
        # Determinar localía
        local_stadiums = ["nacional", "santa laura", "el teniente", "la portada", "sausalito", "valparaiso", "monumental"]
        cancha_lower = cancha.lower()
        
        # Por defecto, asumimos visita a menos que el estadio sea conocido como local
        is_u_local = any(ls in cancha_lower for ls in local_stadiums)
        
        # Casos específicos
        if cancha_lower == "cap":
            is_u_local = False
            
        if is_u_local:
            home_team = "UNIVERSIDAD DE CHILE"
            away_team = rival.upper()
            home_score = goles_u
            away_score = goles_rival
        else:
            home_team = rival.upper()
            away_team = "UNIVERSIDAD DE CHILE"
            home_score = goles_rival
            away_score = goles_u
            
        # Parsear penales
        home_penalties = None
        away_penalties = None
        
        if "[1]" in notes_col or "[1]" in res_raw:
            # Parsear penales para la nota [1]
            pen_match = re.search(r'"U"\s*(\d+):.*?\b([A-Z]{2,4})\s*(\d+):', notes_text, re.IGNORECASE | re.DOTALL)
            if pen_match:
                u_pens = int(pen_match.group(1))
                rival_pens = int(pen_match.group(3))
                if is_u_local:
                    home_penalties = u_pens
                    away_penalties = rival_pens
                else:
                    home_penalties = rival_pens
                    away_penalties = u_pens
                    
        # Evitar duplicados
        with repo._db.get_connection() as conn:
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
            
        stadium_id = f"st_{cancha.replace(' ', '_').replace(',', '').lower()[:20]}"
        stadium = Stadium(id=stadium_id, name=cancha)
        
        competition = Competition(id=comp_id, name=comp_name, season=season)
        
        domain_match = Match(
            id=match_id, date=match_date, home_team=home_team, away_team=away_team,
            home_score=home_score, away_score=away_score,
            home_penalties=home_penalties, away_penalties=away_penalties,
            stadium=stadium, competition=competition, stage="Primera Fase", attendance_count=None
        )
        
        repo.insert_match(domain_match)
        comp_saved += 1
        print(f"  [OK] {match_date.strftime('%d/%m/%Y')} | Primera Fase             | {home_team[:15]:<15} {home_score}-{away_score} {away_team[:15]:<15} (Pens: {home_penalties}-{away_penalties})")
        
    return comp_saved

def scrape_year_config(year: int, clear: bool, force: bool):
    print(f"--- INICIANDO IMPORTACIÓN BASADA EN CONFIGURACIÓN PARA {year} ---")
    
    if year not in TEMPORADAS_CONFIG:
        print(f"ERROR: La temporada {year} aún no está implementada en TEMPORADAS_CONFIG.")
        sys.exit(1)
        
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(project_root, "udechile_stats.db")
    db = SqliteDatabase(db_path)
    db.initialize_schema()
    
    if clear:
        print("¡ATENCIÓN! Limpiando toda la base de datos histórica por orden de la flag --clear...")
        db.clear_all_data()
        
    repo = SqliteMatchRepository(db)
    table_repo = SqliteLeagueTableRepository(db)
    att_repo = SqliteAttendanceRepository(db)
    
    teams_regex = re.compile(r"^\s*(.*?)\s+(\d+)(?:\s*\((\d+)\))?\s*v/s\s*(.*?)\s+(\d+)(?:\s*\((\d+)\))?", re.IGNORECASE)
    date_regex = re.compile(r"(\d{1,2})\s+de\s+([a-zA-Z]+)\s+(?:de|del)\s+(\d{2,4})", re.IGNORECASE)
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
            parse_league_table(html_content, comp_id, comp_name, season, table_repo, torneo.get("caption_filter"))
            continue
            
        if "/anuarios/" in url or "cch.html" in url:
            comp_saved = parse_anuario_campaign_matches(html_content, comp_id, comp_name, season, repo, year)
            print(f"  -> {comp_saved} partidos importados para {comp_name}.")
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
            
            if year == 2008 and "Rangers" in text and "5 de mayo" in text and "v/s" in text:
                text = text.replace("UNIVERSIDAD DE CHILE 1 v/s Rangers", "UNIVERSIDAD DE CHILE 1 v/s Rangers 1")
                original_text = original_text.replace("UNIVERSIDAD DE CHILE 1 v/s Rangers", "UNIVERSIDAD DE CHILE 1 v/s Rangers 1")
                
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
                
                if home_penalties is None and away_penalties is None and ("penal" in text.lower() or "penales" in text.lower()):
                    match_block = original_text.split("Cancha:", 1)[0]
                    pen_matches = re.findall(r'\(\s*(\d+)\s*\)\s*:', match_block)
                    if len(pen_matches) == 2:
                        home_penalties = int(pen_matches[0])
                        away_penalties = int(pen_matches[1])
                    else:
                        u_pen_match = re.search(r'"U"\s+(\d+)\s*[\(:]', match_block, re.IGNORECASE)
                        if not u_pen_match:
                            u_pen_match = re.search(r'"U"\s*:\s*(\d+)', match_block, re.IGNORECASE)
                        if not u_pen_match:
                            u_pen_match = re.search(r'\bU\.\s+de\s+Chile\b\s+(\d+)\s*[\(:]', match_block, re.IGNORECASE)
                        if not u_pen_match:
                            u_pen_match = re.search(r'\bUCH\b\s+(\d+)\s*[\(:]', match_block, re.IGNORECASE)
                        if not u_pen_match:
                            u_pen_match = re.search(r'\bUCH\b\s*:\s*(\d+)', match_block, re.IGNORECASE)
                        if not u_pen_match:
                            u_pen_match = re.search(r'\bU\b\s+(\d+)\s*[\(:]', match_block, re.IGNORECASE)
                        if not u_pen_match:
                            u_pen_match = re.search(r'\bU\b\s*:\s*(\d+)', match_block, re.IGNORECASE)
                        
                        other_penalties = None
                        
                        rival_matches_1 = re.findall(r'\b([a-zA-ZáéíóúÁÉÍÓÚñÑ\.\s]+)\s+(\d+)\s*[\(:]', match_block)
                        for team_name_raw, pens_str in rival_matches_1:
                            team_name = team_name_raw.strip().upper()
                            team_clean = team_name.replace(".", "").strip()
                            if team_clean not in ["U", "UCH", "U DE CHILE", "EQUIPO", "DT", "GOLES", "DEFINICIÓN", "DEFINICION", "PENALES"]:
                                other_penalties = int(pens_str)
                                break
                                
                        if other_penalties is None:
                            rival_matches_2 = re.findall(r'\b([a-zA-ZáéíóúÁÉÍÓÚñÑ\.\s]+)\s*:\s*(\d+)', match_block)
                            for team_name_raw, pens_str in rival_matches_2:
                                team_name = team_name_raw.strip().upper()
                                team_clean = team_name.replace(".", "").strip()
                                if team_clean not in ["U", "UCH", "U DE CHILE", "EQUIPO", "DT", "GOLES", "DEFINICIÓN", "DEFINICION", "PENALES"]:
                                    other_penalties = int(pens_str)
                                    break
                                
                        if u_pen_match and other_penalties is not None:
                            u_pens = int(u_pen_match.group(1))
                            rival_pens = other_penalties
                            if home_team.upper() == "UNIVERSIDAD DE CHILE":
                                home_penalties = u_pens
                                away_penalties = rival_pens
                            else:
                                home_penalties = rival_pens
                                away_penalties = u_pens
                        else:
                            x_match = re.search(r'\b(U|UCH|U\.\s+de\s+Chile)\s+(\d+)\s*x\s*(\d+)\s*([A-ZáéíóúÁÉÍÓÚñÑ\.\s]+)', match_block, re.IGNORECASE)
                            if x_match:
                                u_pens = int(x_match.group(2))
                                rival_pens = int(x_match.group(3))
                                if home_team.upper() == "UNIVERSIDAD DE CHILE":
                                    home_penalties = u_pens
                                    away_penalties = rival_pens
                                else:
                                    home_penalties = rival_pens
                                    away_penalties = u_pens
                            else:
                                x_match_rev = re.search(r'\b([A-ZáéíóúÁÉÍÓÚñÑ\.\s]+)\s+(\d+)\s*x\s*(\d+)\s*(U|UCH|U\.\s+de\s+Chile)\b', match_block, re.IGNORECASE)
                                if x_match_rev:
                                    rival_pens = int(x_match_rev.group(2))
                                    u_pens = int(x_match_rev.group(3))
                                    if home_team.upper() == "UNIVERSIDAD DE CHILE":
                                        home_penalties = u_pens
                                        away_penalties = rival_pens
                                    else:
                                        home_penalties = rival_pens
                                        away_penalties = u_pens
                                else:
                                    gen_x_match = re.search(r'(?:definici.*?n a penales|def\.\s+a\s+penales)\s+(\d+)\s*x\s*(\d+)', original_text, re.IGNORECASE)
                                    if gen_x_match:
                                        pen_val_1 = int(gen_x_match.group(1))
                                        pen_val_2 = int(gen_x_match.group(2))
                                        text_lower = original_text.lower()
                                        u_won = True
                                        if "tituló campeón" in text_lower or "vencer" in text_lower or "clasifica" in text_lower:
                                            if "américa" in text_lower or "colo colo" in text_lower or "palmeiras" in text_lower or "uc" in text_lower or "católica" in text_lower:
                                                u_won = False
                                        u_pens = min(pen_val_1, pen_val_2) if not u_won else max(pen_val_1, pen_val_2)
                                        rival_pens = max(pen_val_1, pen_val_2) if not u_won else min(pen_val_1, pen_val_2)
                                        if home_team.upper() == "UNIVERSIDAD DE CHILE":
                                            home_penalties = u_pens
                                            away_penalties = rival_pens
                                        else:
                                            home_penalties = rival_pens
                                            away_penalties = u_pens
                                    else:
                                        vs_pen_match = re.search(r'(?:definici.*?n a penales|def\.\s+a\s+penales).*?([a-zA-ZáéíóúÁÉÍÓÚñÑ\.\s]+)\s+(\d+)\s*v/s\s*([a-zA-ZáéíóúÁÉÍÓÚñÑ\.\s]+)\s+(\d+)', original_text, re.IGNORECASE)
                                        if vs_pen_match:
                                            t1, s1, t2, s2 = vs_pen_match.groups()
                                            t1_clean = t1.strip().lower()
                                            if "u. de chile" in t1_clean or "uch" in t1_clean or t1_clean == "u":
                                                u_pens = int(s1)
                                                rival_pens = int(s2)
                                            else:
                                                u_pens = int(s2)
                                                rival_pens = int(s1)
                                            if home_team.upper() == "UNIVERSIDAD DE CHILE":
                                                home_penalties = u_pens
                                                away_penalties = rival_pens
                                            else:
                                                home_penalties = rival_pens
                                                away_penalties = u_pens
                
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
                    elif year == 2010 and match_date.year == 2009 and match_date.month > 1:
                        match_date = datetime.date(2010, match_date.month, match_date.day)
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
