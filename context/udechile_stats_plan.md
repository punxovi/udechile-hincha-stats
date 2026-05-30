# Plan de Arquitectura y Desarrollo: U de Chile Stats & Fan Dashboard

Este documento contiene el plan paso a paso y el prompt maestro diseñado para construir una aplicación web basada en Arquitectura Hexagonal (Domain-Driven Design), utilizando el mismo patrón exitoso de tu dashboard actual, pero enfocado en estadísticas históricas del Club Universidad de Chile.

---

## 🏗️ 1. Estructura de Directorios (Arquitectura Hexagonal)

El proyecto debe seguir esta estructura exacta para mantener la separación de responsabilidades:

```text
udechile_stats/
├── domain/                  # Lógica de negocio pura (independiente de frameworks)
│   ├── __init__.py
│   └── models.py            # Pydantic models: Match, Lineup, FanDashboard, etc.
├── application/             # Orquestación y casos de uso
│   ├── __init__.py
│   ├── ports/               # Interfaces/Protocols (ej. MatchRepository)
│   └── use_cases/           # Lógica como: CalculateFanMetricsUseCase
├── infrastructure/          # Detalles de implementación (BBDD, Web Scraping)
│   ├── __init__.py
│   ├── persistence/         # SQLite Store (ej. sqlite_match_store.py)
│   └── data_loaders/        # Scripts de carga inicial (CSV, Scrapers)
├── interfaces/              # Puntos de entrada de la app
│   ├── __init__.py
│   └── api/                 # FastAPI
│       ├── app.py           # Factory de la aplicación
│       ├── routes/          # Endpoints separados (API y Web)
│       ├── static/          # CSS y JS Vanilla
│       └── templates/       # HTML con Jinja2
├── .env.example
├── requirements.txt
└── main.py                  # Entrypoint principal
```

---

## 🛠️ 2. Paso a Paso de Implementación

### Fase 1: Core y Dominio
1. Iniciar un entorno virtual e instalar FastAPI, Uvicorn, Jinja2 y Pydantic.
2. Crear los modelos en `domain/models.py`. Deberás definir al menos un partido (`Match`), y las métricas resumidas de un usuario (`FanDashboardSnapshot`).

### Fase 2: Interfaces (Puertos) y Casos de Uso
1. Crear los repositorios base en `application/ports/` usando `typing.Protocol`. Aquí se define qué debe hacer la base de datos (ej: `get_matches_by_year`, `save_user_attendance`).
2. Programar los casos de uso en `application/use_cases/`. Por ejemplo, la lógica matemática de tomar todos los partidos a los que asistió el usuario, sumar las victorias, empates y derrotas, y calcular el rendimiento %.

### Fase 3: Infraestructura y Base de Datos
1. Implementar SQLite en `infrastructure/persistence/` que obedezca los contratos definidos en los puertos.
2. **Desafío Crítico:** Definir la fuente de datos históricos. Crear un script en `infrastructure/data_loaders/` que lea un archivo CSV histórico o ejecute un scrapper para poblar el SQLite inicial.

### Fase 4: API, Rutas y Visualización
1. Construir la API con FastAPI en `interfaces/api/routes/`.
2. Crear los templates HTML en Jinja2.
3. Conectar el Frontend inyectando la data en variables `window.dashboardData` y renderizando gráficos con Chart.js.

---

## 🤖 3. Prompt Maestro para el Agente de IA

*Copia y pega el siguiente bloque de texto como "System Prompt" o como el primer mensaje en tu editor (Cursor, Windsurf) o LLM favorito para inicializar el proyecto:*

***
