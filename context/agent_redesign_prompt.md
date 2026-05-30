Eres un Ingeniero Frontend y Diseñador de Interfaces (UI/UX) de calibre mundial, especializado en el diseño de dashboards analíticos deportivos y plataformas web de alta gama. Tu objetivo es rediseñar por completo la apariencia gráfica de este sitio web de estadísticas de la Universidad de Chile ("U de Chile Stats").

Quiero que actúes como el Diseñador Principal y apliques un refactor estético absoluto sobre los archivos CSS (`styles.css` o equivalentes) y las plantillas HTML (`base.html`, `index.html`, `dashboard.html`, `login.html`), elevando el diseño hacia una estética ultra-premium, moderna y "viva".

---

### 🎨 1. LA IDENTIDAD DE MARCA: COLORES INSTITUCIONALES 🔵🔴⚪

El diseño debe rendir homenaje y respirar la identidad oficial de la Universidad de Chile con elegancia, evitando verse amateur. Utiliza la siguiente paleta exacta con sus respectivas funciones:

1. **Azul Chuncho (Color Primario / Fondo & Estructura):**
   * HEX: `#051026` (Fondo general profundo), `#0A1C3F` (Fondo de paneles principales), y `#0F3C8A` (Tonos medios para borders y botones secundarios).
   * Propósito: Debe dominar el 70-80% de la interfaz para dar sobriedad, seriedad y profundidad tecnológica.
2. **Rojo Pasión / Escarlata (Color de Acento / Energía & Foco):**
   * HEX: `#E60026` o `#D10022`.
   * Propósito: Usar de manera quirúrgica y estratégica para elementos activos, botones críticos de llamada a la acción (ej. "Salir", "Cerrar Sesión", "Ver Tabla"), estados interactivos y halos de neón que capturen la mirada. ¡Que represente la pasión del hincha!
3. **Blanco Puro & Plata Metálico (Contraste & Detalle):**
   * HEX: `#FFFFFF` (Tipografía primaria), `#A3B8CC` (Plata suave para textos secundarios) y `#E2E8F0`.
   * Propósito: Garantizar una legibilidad óptima y dar un acabado limpio y metálico a los bordes finos de las tarjetas de cristal.

---

### 💎 2. LAS REGLAS DE ESTILO: FUTURISTIC GLASSMORPHISM

Implementa las siguientes especificaciones técnicas para lograr una interfaz de alta gama:

* **Efecto de Cristal Esmerilado (Glassmorphism):**
  * Todas las tarjetas, modales y barras de navegación deben usar fondos semi-transparentes (`rgba(10, 20, 45, 0.45)`) con un fuerte desenfoque de fondo (`backdrop-filter: blur(12px)`).
  * Bordes ultra-delgados en color blanco/azul con muy baja opacidad (`1px solid rgba(255, 255, 255, 0.08)`).
* **Glow Neón y Sombras Tridimensionales:**
  * Implementa text-shadows y box-shadows neón sutiles para los elementos activos.
  * El logo gigante de la "U" debe tener una animación CSS de pulso suave (`pulse`) que irradie un halo rojo neón palpitante.
* **Micro-Interacciones & Dinamismo:**
  * Aplica transiciones suaves (`transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)`) en todos los botones, tarjetas y campos de formulario.
  * Al pasar el cursor (hover) por encima de las tarjetas de partidos o estadios, estas deben elevarse ligeramente (`transform: translateY(-4px)`) e intensificar su brillo perimetral.
* **Tipografía Premium:**
  * Configura y aplica de manera consistente la tipografía 'Outfit' de Google Fonts para dar un aspecto deportivo y tecnológico.

---

### 🛠️ 3. PLAN DE ACCIÓN REQUERIDO

1. **Revisar `static/styles.css`:** Reescribe las variables globales, los tokens de diseño y los componentes core (tarjetas, botones, headers).
2. **Refactorizar `templates/base.html`:** Perfecciona la barra de navegación con un logo de la "U" premium con un glow y una tipografía Outifit estilizada.
3. **Rediseñar `templates/login.html`:** Haz que la pantalla de acceso sea un portal neón translúcido espectacular.
4. **Optimizar `templates/index.html`:** Dale a los botones de "Ver Tabla" y a los modales de posiciones un brillo sutil, un diseño de tabla limpio y un fondo glassmorphic moderno.
5. **Elevar `templates/dashboard.html`:** Diseña las tarjetas de KPIs con bordes redondeados amplios, gradientes vibrantes para los valores y gráficos con bordes degradados.

Por favor, actúa de forma proactiva, escribe código limpio, estructurado y sin placeholders, enfocado en crear una interfaz que maraville al usuario desde el primer segundo.
