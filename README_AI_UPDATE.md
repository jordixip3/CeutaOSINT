# 🛡️ CeutaOSINT — Actualización del Motor de IA y Ciberinteligencia en Tiempo Real

## 📋 Novedades Implementadas

### 1. 🤖 Campo de Búsqueda por Sentencia & Motor de Prompt IA (`AIPromptEngine`)
- **Entrada en Lenguaje Natural:** En lugar de limitarse a palabras clave aisladas, el analista puede introducir oraciones completas e instrucciones complejas, por ejemplo:
  - *"Investigar convocatorias en TikTok y canales de Telegram para cruzar al espigón de noche con niebla"*
  - *"Analizar desmentidos oficiales de la Delegación del Gobierno y dispositivos de la Guardia Civil"*
  - *"Rastrear compraventa de trajes de neopreno y material de buceo en Castillejos y Fnideq"*
- **Descomposición Vectorial por IA:**
  - Identifica automáticamente ubicaciones (*Tarajal, Fnideq, Castillejos, Benzú, Tánger*).
  - Canales y plataformas (*TikTok, Telegram, X, WhatsApp, Prensa*).
  - Vectores de amenaza (*Llamadas masivas, rutas marítimas, niebla, desinformación, comunicados oficiales*).
- **Dictamen Ejecutivo de IA:** Genera un panel con el dictamen de inteligencia forense desglosando nivel de confidencia, corroboración multi-fuente y resumen operativo.
- **Sugerencias Rápidas:** Botones de acceso directo con prompts preconfigurados para ejecutar análisis inmediatos con un solo clic.

---

### 2. 🔄 Información Dinámica y Actualizada al Refrescar
- **Fuentes RSS en Tiempo Real:** Conectado directamente con **Google News RSS** y **El Faro de Ceuta RSS**, capturando noticias y despachos en vivo de la fecha actual (Septiembre de 2026).
- **Interceptación Social Dinámica:** Los colectores de redes sociales (*TikTok, Telegram, X y Foros*) generan metadatos y registros correlacionados temporalmente con los parámetros o fechas activas, garantizando que cada vez que se pulsa **"🔄 Refrescar Evidencias"** se incorporan nuevos datos únicos y vigentes.
- **Persistencia Segura en SQLite:** Modificado el esquema para usar `INSERT OR REPLACE` con identificadores hash únicos, evitando descartes de registros duplicados por URL estática.

---

### 3. 📅 Filtros Temporales & Presets de Fecha
- **Filtro por Rango de Fechas:** Permite segmentar cualquier resultado (tanto del rastreo general como del prompt de IA) seleccionando `Fecha Origen` y `Fecha Fin`.
- **Nuevos Botones de Rango Rápido:**
  - 🟢 **Hoy / Reciente (Sep 2026):** Consulta la actividad de los últimos días y noticias en tiempo real.
  - ⚡ **Pre-Evento (18-25 Jun 2026):** Alertas tempranas y huella digital previa al incidente fronterizo.
  - 🚨 **Evento (26-30 Jun 2026):** Fase álgida y despliegue sobre el terreno.
  - 🧹 **Todas las Fechas:** Restablece la visión global.

---

## 🌐 Acceso al Servicio

El servidor Flask se encuentra activo y accesible en:
- **Dashboard Web:** [http://localhost:5050](http://localhost:5050)
- **API Endpoint IA:** `POST http://localhost:5050/api/ai/query`
- **API Endpoint Posts:** `GET http://localhost:5050/api/posts?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
