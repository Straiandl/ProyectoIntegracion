# Sistema de Detección e Inteligencia de Amenazas de Ciberseguridad con n8n, MCP y LLM

Este proyecto implementa una solución integral de ciberseguridad que combina una aplicación web vulnerable simulada en Python, un **Servidor MCP (Model Context Protocol)** para herramientas de geolocalización de amenazas, y un pipeline de automatización en **n8n** impulsado por Inteligencia Artificial (Google Gemini) para el análisis forense y la notificación en tiempo real.

---

## 🛠️ Arquitectura del Sistema

El flujo de trabajo del sistema sigue los siguientes pasos:

1. **Detección Local (`app.py`)**: Una aplicación web Flask simula un entorno vulnerable a inyecciones SQL (SQLi). Al detectar un patrón malicioso, bloquea la solicitud, genera un registro JSON local (`security_events.json`) y activa un evento Webhook.
2. **Servidor MCP (`mcp_server.py`)**: Implementado con **FastMCP**, expone herramientas forenses independientes (`get_ip_info` para geolocalización mediante API pública e `get_current_time` para estampados de tiempo) utilizables por modelos de lenguaje (LLM).
3. **Orquestación de IA en n8n**:
   - **Webhook**: Recibe el evento de seguridad en formato JSON.
   - **AI Agent + Google Gemini**: Analiza la carga útil (*payload*) y la IP atacante, generando un diagnóstico técnico y medidas de mitigación.
   - **Gmail Node**: Envía automáticamente un reporte forense al correo del analista de seguridad.

---

## 📋 Requisitos Previos

- **Python 3.10+** (con el lanzador `py` en Windows).
- Cuenta activa en **n8n** (Cloud o Auto-hospedado).
- Credenciales configuradas en n8n para:
  - Google Gemini Chat Model.
  - Servicio de correo Gmail.

---

## 📦 Instalación y Configuración

### 1. Clonar el repositorio e instalar dependencias

Asegúrate de instalar los módulos requeridos de Python:

```bash
py -m pip install flask requests mcp
```

### 2. Configurar el Servidor MCP

El archivo `mcp_server.py` define las herramientas estándar de MCP:

```bash
py mcp_server.py
```

*Nota: Para conectar este servidor con clientes MCP compatibles como Claude Desktop, agrega la ruta del ejecutable en tu archivo `%APPDATA%\Claude\claude_desktop_config.json`.*

### 3. Configurar la Aplicación Flask (`app.py`)

Asegúrate de reemplazar la variable `WEBHOOK_URL_N8N` en `app.py` con la URL generada por tu nodo Webhook en n8n:

```python
WEBHOOK_URL_N8N = "https://tu-instancia.n8n.cloud/webhook-test/tu-id-de-webhook"
```

Ejecuta el servidor web local:

```bash
py app.py
```

La aplicación estará disponible en `http://127.0.0.1:5000`.

---

## ⚙️ Flujo de Automatización en n8n

El flujo en n8n se compone de 4 nodos principales:

```text
[ Webhook (POST) ] ──> [ AI Agent ] ──> [ Gmail (Send Message) ]
                            │
              [ Google Gemini Chat Model ]
```

### Configuración de Nodos:

- **Webhook**: Configurado en método `POST` escuchando eventos en `/webhook-test/...`.
- **AI Agent**: 
  - **Prompt (User Message)**: `={{ JSON.stringify($json.body) }}`
  - **System Message**: Instruye al modelo como analista de ciberseguridad para categorizar el ataque y proponer mitigaciones.
- **Google Gemini Chat Model**: Conectado a la entrada de modelo (*Chat Model*) del AI Agent.
- **Gmail**: 
  - **Subject**: `Alerta de Seguridad: Intento de ataque detectado`
  - **Message**: `={{ $json.output }}`

---

## 🧪 Validación y Pruebas de Funcionamiento

1. Activa el modo de prueba en n8n haciendo clic en **Test workflow**.
2. Abre un navegador e ingresa a `http://127.0.0.1:5000`.
3. Ingresa un payload de prueba en el formulario de inicio de sesión:
   - **Usuario**: `' OR '1'='1`
   - **Contraseña**: `1234`
4. **Resultado esperado**:
   - La consola de Python mostrará la alerta de bloqueo y la confirmación del envío a n8n.
   - El evento quedará registrado en `security_events.json`.
   - n8n procesará la solicitud a través del agente Gemini.
   - Recibirás un correo en tu bandeja de Gmail con el análisis forense redactado por la IA.
