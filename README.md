# Sistema de Detección, Análisis e Inteligencia de Amenazas con Python, MCP, n8n y Gemini LLM

Este proyecto implementa un ecosistema completo de ciberseguridad automatizado. El sistema detecta ataques web en tiempo real, registra los eventos, enriquece la información mediante un servidor **MCP (Model Context Protocol)** y orquesta un análisis forense impulsado por Inteligencia Artificial (**Google Gemini**) a través de **n8n**, finalizando con la emisión automática de alertas por correo electrónico.

---

## 📐 Diagrama de Arquitectura y Flujo de Datos

```text
 [ Usuario / Atacante ]
           │
           ▼ (Petición HTTP con SQLi: ' OR '1'='1)
 ┌─────────────────────────────────────────────────────────┐
 │  1. Aplicación Flask (`app.py`)                         │
 │     - Bloquea la petición maliciosa                    │
 │     - Guarda registro en `security_events.json`         │
 └─────────────────────────┬───────────────────────────────┘
                           │
                           ▼ (Webhook POST JSON)
 ┌─────────────────────────────────────────────────────────┐
 │  2. Orquestador de Automatización (n8n)                 │
 │     ┌─────────────────┐                                 │
 │     │  Webhook Node   │                                 │
 │     └────────┬────────┘                                 │
 │              ▼                                          │
 │     ┌─────────────────┐     ┌───────────────────────┐   │
 │     │    AI Agent     │ ◄───┤  Google Gemini Model  │   │
 │     └────────┬────────┘     └───────────────────────┘   │
 └──────────────┼──────────────────────────────────────────┘
                │
                ▼ (Reporte redactado por IA)
 ┌─────────────────────────────────────────────────────────┐
 │  3. Notificación (`Gmail Node`)                         │
 │     - Envía correo con diagnóstico y mitigación         │
 └─────────────────────────────────────────────────────────┘

 [ Componente Adicional ]
 ┌─────────────────────────────────────────────────────────┐
 │  Servidor MCP Local (`mcp_server.py`)                    │
 │  - Provee herramientas externas (Geolocalización IP)    │
 │    para consultas forenses en clientes LLM              │
 └─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Explicación Detallada de Cada Componente

### 1. Aplicación Web Vulnerable y Monitor de Seguridad (`app.py`)

* **¿Cómo funciona?**: Es un servidor web desarrollado en Python utilizando el microframework **Flask**, ejecutado localmente en `http://127.0.0.1:5000`.
* **Lógica de Detección**: Cuando un usuario envía datos a través del formulario de inicio de sesión, la función `registrar_evento_sospechoso()` inspecciona los campos en busca de patrones de ataques conocidos, como cadenas de inyección SQL (`' OR '1'='1`).
* **Acción de Bloqueo y Notificación**:
  1. Si se detecta un patrón malicioso, la aplicación intercepta y bloquea la solicitud.
  2. Escribe de forma persistente el evento dentro del archivo local `security_events.json` guardando la IP de origen, el tipo de alerta, la fecha/hora y la carga útil (*payload*).
  3. Utiliza la librería `requests` para realizar una petición HTTP `POST` hacia la URL de Webhook de n8n, enviando el objeto JSON en tiempo real para iniciar el flujo automatizado.

---

### 2. Servidor MCP - Model Context Protocol (`mcp_server.py`)

* **¿Cómo funciona?**: Desarrollado con el SDK oficial **FastMCP**, implementa el protocolo estándar de Anthropic (Model Context Protocol). MCP permite exponer herramientas localmente para que un Modelo de Lenguaje (LLM) pueda interactuar con el entorno de manera segura.
* **Herramientas Implementadas (`@mcp.tool()`)**:
  * `get_ip_info(ip: str)`: Realiza peticiones a la API pública `ip-api.com` para obtener la ubicación geográfica (país, ciudad) y el Proveedor de Servicios de Internet (ISP) asociado a la IP del atacante.
  * `get_current_time()`: Consulta y devuelve la fecha y hora exacta del sistema para fines de sincronización forense.
* **Propósito en la Arquitectura**: Demuestra cómo un LLM puede extender sus capacidades mediante la llamada a funciones (*Function Calling*), conectando modelos de inteligencia artificial con sistemas externos e infraestructura local mediante la interfaz `STDIO`.

---

### 3. Workflow de Orquestación e Inteligencia Artificial (`n8n`)

El flujo de n8n actúa como la capa de decisión del sistema, integrado por los siguientes nodos:

* **Nodo Webhook**:
  * Funciona como un endpoint receptor (escuchando mediante método `POST`). Recibe el JSON enviado por `app.py` cuando ocurre una amenaza.
* **Nodo Google Gemini Chat Model**:
  * Proporciona la capacidad de procesamiento de lenguaje natural conectándose a los modelos de Google (Gemini 1.5/3). Actúa como el "cerebro" analítico del flujo.
* **Nodo AI Agent**:
  * Recibe los datos crudos del ataque mediante la expresión `={{ JSON.stringify($json.body) }}`.
  * Utiliza un **System Message** estructurado que define la personalidad de un analista de ciberseguridad. Evalúa el payload recibido, contextualiza el vector de ataque y genera un informe conciso categorizando el riesgo y sugiriendo acciones de mitigación de forma autónoma.

---

### 4. Sistema de Alerta y Notificación (`Gmail Node`)

* **¿Cómo funciona?**: Es el nodo final de la cadena de automatización.
* **Lógica de Envío**: Toma la salida textual generada por el **AI Agent** (`={{ $json.output }}`) y la empaqueta dentro de un correo electrónico en formato HTML.
* **Resultado**: Envía una notificación inmediata al correo del analista de seguridad (`ian.delapaz7595@alumnos.udg.mx`) indicando el asunto, la gravedad del incidente, el diagnóstico del modelo de IA y los pasos recomendados para contener la amenaza.

---

## 🚀 Requisitos e Instalación

### Módulos de Python Necesarios

Instala las librerías requeridas ejecutando en la terminal de Windows:

```bash
py -m pip install flask requests mcp
```

---

## 🧪 Pasos para Ejecutar y Validar el Proyecto

1. **Iniciar el Servidor Web**:
   Abre una terminal en la carpeta del proyecto y ejecuta:
   ```bash
   py app.py
   ```

2. **Activar el Workflow en n8n**:
   Entra a n8n y presiona el botón **Test workflow** para dejar el flujo en estado de escucha.

3. **Simular el Ataque**:
   Abre un navegador web e ingresa a `http://127.0.0.1:5000`. En el formulario de inicio de sesión ingresa:
   * **Usuario**: `' OR '1'='1`
   * **Contraseña**: `1234`

4. **Verificación**:
   * En la consola de Python verás el mensaje: `🚀 ¡Alerta enviada exitosamente a n8n!`.
   * En n8n verás la ejecución fluir desde el Webhook hasta el AI Agent.
   * Revisa tu bandeja de correo de Gmail para confirmar la recepción del informe de inteligencia de amenazas.
   * ![Gmail](ruta_o_url_de_la_imagen)
