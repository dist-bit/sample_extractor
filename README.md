# Guía Completa: Cliente API de Nebuia para Procesamiento de Documentos

## Índice
1. [Introducción](#introducción)
2. [¿Qué hace este código?](#qué-hace-este-código)
3. [Estructura del Código](#estructura-del-código)
4. [Componentes Principales](#componentes-principales)
   - [Clase `NebuiaCredentials`](#clase-nebuiacredentials)
   - [Clase `NebuiaClient`](#clase-nebuiaclient)
   - [Clase `NebuiaHandler`](#clase-nebuiahandler)
5. [Flujo de Trabajo](#flujo-de-trabajo)
6. [Funciones Clave](#funciones-clave)
7. [Registro de Comandos cURL](#registro-de-comandos-curl)
8. [Ejemplos de Uso](#ejemplos-de-uso)
9. [Ejemplos de Respuestas de la API](#ejemplos-de-respuestas-de-la-api)
10. [Solución de Problemas](#solución-de-problemas)
11. [Glosario](#glosario)

## Introducción

Este código es un cliente para interactuar con la API de Nebuia, un servicio que permite procesar, verificar y extraer información de documentos. El cliente está diseñado para facilitar tareas como:

- Subir documentos PDF a la plataforma Nebuia
- Verificar tipos de documentos
- Procesar documentos para extraer información
- Monitorear el estado de procesamiento
- Obtener resultados estructurados

El código está escrito en Python y utiliza la biblioteca `requests` para manejar las comunicaciones HTTP con la API de Nebuia.

## ¿Qué hace este código?

En términos simples, este código permite:

1. **Cargar documentos**: Enviar archivos PDF a la plataforma Nebuia
2. **Verificar documentos**: Comprobar que los documentos son del tipo esperado
3. **Procesar documentos**: Extraer información relevante de los documentos
4. **Monitorear**: Seguir el progreso del procesamiento
5. **Obtener resultados**: Recuperar la información extraída de forma estructurada

Todo esto se hace mediante llamadas a la API de Nebuia, que es un servicio externo especializado en procesamiento de documentos.

## Estructura del Código

El código está organizado en dos archivos principales:

1. **nebuia_client.py**: Contiene las clases base y la lógica de comunicación con la API
   - `NebuiaCredentials`: Gestiona las credenciales de autenticación
   - `NebuiaClient`: Maneja todas las comunicaciones con la API de Nebuia
   - Clases de errores personalizados

2. **nebuia_handler.py**: Proporciona una capa de abstracción más amigable
   - `NebuiaHandler`: Facilita operaciones de alto nivel y mejora la experiencia de usuario

## Componentes Principales

### Clase `NebuiaCredentials`

Esta clase almacena y valida las credenciales necesarias para acceder a la API de Nebuia:

- `client_id`: Identificador único del cliente en Nebuia
- `api_key`: Clave de API para autenticación
- `api_secret`: Secreto de API para autenticación

La clase verifica que todas las credenciales estén presentes y sean válidas. Si falta alguna, lanzará un error ValueError con un mensaje claro.

### Clase `NebuiaClient`

Esta es la clase principal que maneja todas las comunicaciones con la API de Nebuia. Sus características incluyen:

- **Gestión de autenticación**: Usa las credenciales para autenticar todas las peticiones
- **Operaciones CRUD**: Crear, leer, actualizar y eliminar recursos en Nebuia
- **Manejo de errores**: Captura y procesa errores de la API
- **Registro de comandos cURL**: Guarda equivalentes cURL de cada petición HTTP para depuración
- **Operaciones asíncronas**: Permite esperar a que se completen operaciones de larga duración

Las funciones principales incluyen:

- `create_record`: Crea un nuevo registro para asociar documentos
- `upload_document`: Sube un documento PDF a un registro
- `verify_document_type`: Verifica que un documento sea del tipo esperado
- `create_processing_job`: Inicia el procesamiento de los documentos
- `wait_for_record_completion`: Espera a que se complete el procesamiento

### Clase `NebuiaHandler`

Esta clase proporciona una interfaz más amigable y de alto nivel para trabajar con la API de Nebuia:

- Simplifica flujos de trabajo complejos
- Mejora el manejo de errores y la retroalimentación
- Proporciona información visual sobre el progreso
- Extrae información relevante de los resultados

## Flujo de Trabajo Detallado

El procesamiento de documentos sigue un flujo completo que es importante entender. A continuación se detalla paso a paso:

### 1. Inicialización del Cliente

```python
handler = NebuiaHandler(client_id="...", api_key="...", api_secret="...")
```

Al inicializar el cliente, se configuran:
- Las credenciales de autenticación
- El registro (logging)
- La sesión HTTP para comunicación con la API

### 2. Definir Documentos a Procesar

```python
documents = {
    "acta_constitutiva": "./documentos/acta.pdf",
    "actas_de_asamblea": "./documentos/asamblea.pdf"
}
```

En este paso:
- Se especifican las rutas a los archivos PDF
- Se asocia cada documento con un tipo específico según la configuración de Nebuia

### 3. Validación de Documentos

Internamente, el método `process_documents` valida cada documento:
- Verifica que el archivo exista en el sistema
- Comprueba que sea un archivo PDF válido
- Filtra cualquier documento inválido

### 4. Creación del Registro (Record)

Se crea un nuevo registro en Nebuia mediante:
```python
record_response = client.create_record(config_name)
```

Esto devuelve:
- `id`: Identificador único del registro
- Otros metadatos del registro

### 5. Carga de Documentos

Para cada documento validado:
```python
upload_response = client.upload_document(record_id, file_path, doc_type)
```

Este paso:
- Sube el archivo PDF al servidor de Nebuia
- Asocia el documento con el tipo especificado
- Obtiene un identificador único para cada documento

### 6. Espera por Embedding

El sistema espera a que Nebuia procese inicialmente los documentos:
```python
embedding_success = self._wait_for_embedding(document_ids, interval, timeout)
```

Durante este proceso:
- Se consulta periódicamente el estado de cada documento
- Se muestra el progreso en la consola
- Se espera hasta que todos los documentos están en estado "complete"

### 7. Verificación de Tipos de Documento

Una vez procesados los documentos, se verifica que sean del tipo correcto:
```python
verification_results, verification_passed = self._verify_all_documents(record_id, document_ids)
```

En este paso crítico:
- Se verifica cada documento contra su tipo esperado
- Se muestran los resultados de verificación
- Se determina si todos los documentos son válidos para continuar

### 8. Creación del Trabajo de Procesamiento

Si la verificación es exitosa y auto_process=True:
```python
job_response = self.client.create_processing_job(record_id)
```

Esto:
- Inicia el procesamiento profundo de los documentos
- Crea un trabajo asíncrono en Nebuia
- Devuelve un identificador de trabajo

### 9. Espera por Finalización (Opcional)

Si wait_for_completion=True:
```python
completed_record = self.client.wait_for_record_completion(record_id, timeout, status_callback)
```

Durante este tiempo:
- Se monitorea periódicamente el estado del registro
- Se muestra el progreso mediante callbacks
- Se espera hasta la finalización o timeout

### 10. Obtención de Resultados

Finalmente:
```python
extracted_info = handler.extract_document_entities(result)
```

Esto:
- Extrae la información estructurada de los documentos
- Organiza los datos por tipo de documento
- Limpia los datos para facilitar su uso

## Tipos de Respuesta en la Verificación de Documentos

La verificación de tipos de documentos es un paso crucial. Cuando se llama a `verify_document_type`, se pueden obtener diferentes tipos de respuesta:

### Respuesta Exitosa

Si el documento coincide con el tipo esperado:

```json
{
    "status": true
}
```

### Respuesta Fallida

Si el documento no coincide con el tipo esperado:

```json
{
    "status": false,
    "points": [
        "El documento no contiene las secciones esperadas para un acta constitutiva",
        "No se encontró la sección de estatutos",
        "No se identificaron las firmas requeridas"
    ],
    "type_document_found": "otro_tipo_documento"
}
```

Donde:
- `status`: Indica si la verificación fue exitosa (false en este caso)
- `points`: Lista de razones por las que falló la verificación
- `type_document_found`: El tipo de documento que Nebuia cree que es realmente

### Visualización de los Resultados

El método `_display_verification_points` muestra estos resultados de forma legible:

```
✅ VERIFICACIÓN EXITOSA ✅
============================================================
📄 Tipo de documento: acta_constitutiva

🔍 CRITERIOS DE VERIFICACIÓN:
------------------------------------------------------------
  01. El documento contiene todas las secciones requeridas
  02. Se identificaron estatutos correctamente
  03. Firmas validadas correctamente
------------------------------------------------------------
```

O en caso de fallo:

```
❌ VERIFICACIÓN FALLIDA ❌
============================================================
📄 Tipo de documento: otro_tipo_documento

🔍 CRITERIOS DE VERIFICACIÓN:
------------------------------------------------------------
  01. El documento no contiene las secciones esperadas para un acta constitutiva
  02. No se encontró la sección de estatutos
  03. No se identificaron las firmas requeridas
------------------------------------------------------------
```

### Implicaciones de la Verificación

- Si **todos** los documentos pasan la verificación, se crea automáticamente un trabajo de procesamiento
- Si **algún** documento falla la verificación, no se crea el trabajo (a menos que auto_process=True)
- Los resultados de verificación se añaden a los resultados finales en `verification_results`

## Funciones Clave

### En `NebuiaClient`

#### `_make_request`
Esta función es la base de todas las comunicaciones con la API:
- Construye la URL completa
- Añade los encabezados de autenticación
- Registra el comando cURL equivalente
- Maneja errores de la API y de red
- Procesa y devuelve la respuesta JSON

#### `upload_document`
Permite subir un documento PDF a un registro:
- Verifica que el archivo exista y sea un PDF
- Prepara los datos del formulario multipart
- Gestiona el cierre del archivo después de la carga

#### `wait_for_record_completion`
Espera a que se complete el procesamiento de un registro:
- Consulta periódicamente el estado del registro
- Invoca callbacks para informar del progreso
- Maneja tiempos de espera y errores

### En `NebuiaHandler`

#### `process_documents`
Esta es la función principal que orquesta todo el proceso:
1. Valida los documentos
2. Crea un registro y sube los documentos
3. Espera a que los documentos sean procesados por el motor de embeddings
4. Verifica los tipos de documentos
5. Crea un trabajo de procesamiento
6. Espera a que se complete el procesamiento
7. Devuelve los resultados

#### `_verify_all_documents`
Verifica que todos los documentos sean del tipo esperado:
- Llama a la API para verificar cada documento
- Muestra los resultados de verificación
- Determina si todos los documentos pasaron la verificación

#### `extract_document_entities`
Extrae información relevante de los resultados:
- Procesa cada documento en los resultados
- Extrae las estructuras de entidades
- Limpia los datos para facilitar su uso

## Registro de Comandos cURL

Una característica interesante de este código es el registro de comandos cURL. Para cada petición a la API, el código:

1. Convierte la petición HTTP a su equivalente en cURL
2. Registra el comando en un archivo de registro
3. Opcionalmente lo muestra en la consola

Esto es útil para:
- Depurar problemas de comunicación con la API
- Reproducir peticiones fuera del código
- Compartir ejemplos de uso de la API

El registro incluye detalles como:
- Nombre de la operación
- Marca de tiempo
- Comando cURL completo

## Ejemplos de Uso

### Ejemplo básico

```python
from nebuia_handler import NebuiaHandler

# Inicializar el handler
handler = NebuiaHandler(
    client_id="tu_client_id",
    api_key="tu_api_key",
    api_secret="tu_api_secret"
)

# Definir documentos a procesar
documents = {
    "acta_constitutiva": "./documentos/acta.pdf",
    "actas_de_asamblea": "./documentos/asamblea.pdf"
}

# Procesar documentos
result = handler.process_documents(
    documents=documents,
    config_name="dictaminación",
    wait_for_completion=True
)

# Extraer información relevante
extracted_info = handler.extract_document_entities(result)
print(extracted_info)
```

### Listar configuraciones disponibles

```python
handler.list_configurations()
```

### Procesar documentos y analizar verificación

```python
# Definir documentos a procesar
documents = {
    "acta_constitutiva": "./documentos/acta.pdf",
    "actas_de_asamblea": "./documentos/asamblea.pdf"
}

# Procesar documentos sin procesamiento automático
result = handler.process_documents(
    documents=documents,
    config_name="dictaminación",
    wait_for_completion=False,
    auto_process=False  # No procesar automáticamente, solo verificar
)

# Analizar resultados de verificación
for doc_type, verification in result.get("verification_results", {}).items():
    status = verification.get("status", False)
    print(f"Documento {doc_type}: {'Verificado' if status else 'Rechazado'}")
    
    if not status and "points" in verification:
        print("  Razones de rechazo:")
        for point in verification["points"]:
            print(f"  - {point}")
```

### Subir un documento y crear un job manualmente

```python
# Crear un registro
record_response = handler.client.create_record("dictaminación")
record_id = record_response["id"]

# Subir un documento
handler.client.upload_document(
    record_id=record_id,
    file_path="./documentos/acta.pdf",
    document_type="acta_constitutiva"
)

# Obtener detalles del registro
record_details = handler.client.get_record_details(record_id)
document_id = None

# Encontrar el ID del documento
for document in record_details.get("documents", []):
    if document.get("document_type") == "acta_constitutiva":
        document_id = document.get("document_id")
        break

# Verificar el tipo de documento
if document_id:
    verification_result = handler.verify_document_type(record_id, document_id)
    
    # Si la verificación es exitosa, crear un job
    if verification_result[0]:  # El primer elemento es un booleano que indica éxito
        job_response = handler.client.create_processing_job(record_id)
        job_id = job_response.get("job_id")
        print(f"Job creado con ID: {job_id}")
```

## Ejemplos de Respuestas de la API

### 1. Creación de Cliente

**Respuesta Exitosa:**
```json
{
  "id": "c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "api_keys": {
    "public_key": "pub_83f7c9b512345678abcdef0123456789",
    "secret_key": "sec_83f7c9b512345678abcdef0123456789"
  }
}
```

**Respuesta de Error:**
```json
{
  "error": true,
  "message": "A user already exists with email example@test.com"
}
```

### 2. Crear Configuración

**Respuesta Exitosa:**
```json
{
  "message": "Configuration dictaminación added successfully"
}
```

**Respuesta de Error:**
```json
{
  "error": true,
  "message": "Client not found"
}
```

### 3. Agregar Documento a un Registro

**Respuesta Exitosa (sin procesamiento):**
```json
{
  "message": "Document added to record successfully",
  "document": {
    "document_type": "acta_constitutiva",
    "document_id": "doc_12345678abcdef0123456789",
    "structure": {},
    "created_at": "2025-04-16T10:30:45Z"
  }
}
```

**Respuesta Exitosa (con procesamiento):**
```json
{
  "message": "Document successfully processed",
  "job_id": "job_12345678abcdef0123456789",
  "document": {
    "document_type": "acta_constitutiva",
    "document_id": "doc_12345678abcdef0123456789",
    "structure": {},
    "created_at": "2025-04-16T10:30:45Z"
  }
}
```

**Respuesta de Error:**
```json
{
  "error": true,
  "message": "Document type acta_fiscal not allowed"
}
```

### 4. Crear un Registro

**Respuesta Exitosa:**
```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "message": "Record created successfully"
}
```

**Respuesta de Error:**
```json
{
  "error": true,
  "message": "Configuration dictaminacion_fiscal not found"
}
```

### 5. Crear un Flujo

**Respuesta Exitosa:**
```json
{
  "message": "Flow dictaminación_fiscal created successfully"
}
```

**Respuesta de Error:**
```json
{
  "error": true,
  "message": "Configuration dictaminación_fiscal not found"
}
```

### 6. Crear un Trabajo de Procesamiento

**Respuesta Exitosa:**
```json
{
  "job_id": "job_12345678abcdef0123456789",
  "message": "Processing job created successfully",
  "status": "created"
}
```

**Respuesta (ya procesando):**
```json
{
  "job_id": "job_12345678abcdef0123456789",
  "message": "Record is already being processed",
  "status": "already_processing"
}
```

**Respuesta de Error (documentos faltantes):**
```json
{
  "message": "Missing required documents: [\"acta_constitutiva\",\"actas_de_asamblea\"]",
  "status": "missing_documents",
  "missing_documents": ["acta_constitutiva", "actas_de_asamblea"]
}
```

### 7. Verificar Tipo de Documento

**Respuesta Exitosa:**
```json
{
  "status": true,
  "type_document_found": "acta_constitutiva",
  "points": [
    "El documento contiene todas las secciones requeridas",
    "Se identificaron estatutos correctamente",
    "Firmas validadas correctamente"
  ]
}
```

**Respuesta Fallida (documento de tipo incorrecto):**
```json
{
  "status": false,
  "type_document_found": "otro_tipo_documento",
  "points": [
    "El documento no contiene las secciones esperadas para un acta constitutiva",
    "No se encontró la sección de estatutos",
    "No se identificaron las firmas requeridas"
  ]
}
```

### 8. Obtener Detalles de un Registro

**Respuesta Exitosa:**
```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "configuration_ref": "dictaminación",
  "documents": [
    {
      "document_type": "acta_constitutiva",
      "document_id": "doc_12345678abcdef0123456789",
      "created_at": "2025-04-16T10:30:45Z",
      "document_predict": {
        "status": true,
        "type_document_found": "acta_constitutiva",
        "points": [
          "El documento contiene todas las secciones requeridas",
          "Se identificaron estatutos correctamente",
          "Firmas validadas correctamente"
        ]
      },
      "entities": [
        {
          "structure": {
            "nombre_empresa": "Corporación Ejemplo S.A. de C.V.",
            "fecha_constitucion": "2020-01-15",
            "capital_social": "1,000,000.00"
          },
          "query": "Extrae la información básica de la empresa",
          "name_to_show": "Información Básica"
        }
      ]
    }
  ],
  "status": "completed",
  "created_at": "2025-04-16T10:15:30Z",
  "response_client": {},
  "allowed_documents": {
    "acta_constitutiva": {
      "required": true,
      "entities": [
        {
          "structure": {
            "nombre_empresa": "",
            "fecha_constitucion": "",
            "capital_social": ""
          },
          "query": "Extrae la información básica de la empresa",
          "name_to_show": "Información Básica"
        }
      ]
    },
    "actas_de_asamblea": {
      "required": false,
      "entities": [
        {
          "structure": {
            "fecha_asamblea": "",
            "tipo_asamblea": "",
            "acuerdos": []
          },
          "query": "Extrae la información de la asamblea",
          "name_to_show": "Información de Asamblea"
        }
      ]
    }
  },
  "is_processing": false,
  "current_document_id": null
}
```

**Respuesta de Error:**
```json
{
  "error": true,
  "message": "Record not found"
}
```

### 9. Obtener Todos los Registros de un Cliente

**Respuesta Exitosa:**
```json
{
  "data": [
    {
      "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
      "configuration_ref": "dictaminación",
      "created_at": "2025-04-16T10:15:30Z",
      "status": "completed",
      "document_count": 2
    },
    {
      "id": "s2c3b4d5-f6g7-8901-b2c3-d4e5f6g78901",
      "configuration_ref": "dictaminación",
      "created_at": "2025-04-15T14:22:10Z",
      "status": "processing",
      "document_count": 1
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 2,
    "total_pages": 1
  }
}
```

### 10. Login de Usuario

**Respuesta Exitosa:**
```json
{
  "temporal_key": "temp_83f7c9b512345678abcdef0123456789"
}
```

**Respuesta de Error:**
```json
{
  "error": true,
  "message": "Invalid credentials"
}
```

## Solución de Problemas

### Problema: Error de autenticación

**Mensaje de error:**
```
API Error (401): Request failed: Unauthorized
```

**Solución:**
- Verifica que las credenciales (client_id, api_key, api_secret) sean correctas
- Comprueba que la cuenta tenga acceso al servicio de Nebuia
- Asegúrate de que las credenciales no estén caducadas

### Problema: Timeout durante el procesamiento

**Mensaje de error:**
```
Timeout exceeded for record xxx after 300 seconds
```

**Solución:**
- Aumenta el parámetro `timeout` al llamar a `process_documents`
- Verifica el estado del documento manualmente usando `get_record_details`
- Considera procesar documentos más pequeños o dividir documentos grandes

### Problema: Fallo en la verificación del tipo de documento

**Comportamiento:**
La función `process_documents` devuelve un resultado, pero no se crea un trabajo de procesamiento.

**Solución:**
- Revisa los resultados de verificación para entender por qué falló
- Asegúrate de que los documentos son del tipo correcto
- Usa el parámetro `auto_process=True` para forzar el procesamiento sin importar la verificación

### Problema: Documento en estado "waiting" permanentemente

**Comportamiento:**
El documento queda en estado "waiting" y nunca pasa a "complete".

**Solución:**
- Verifica que el documento sea legible y no esté dañado
- Comprueba que el documento no esté protegido con contraseña
- Intenta optimizar el PDF (reducir tamaño, mejorar calidad de escaneo)
- Contacta al soporte de Nebuia si el problema persiste

### Problema: Errores en el formato de los resultados

**Comportamiento:**
La estructura de los datos extraídos no es la esperada.

**Solución:**
- Utiliza la función `extract_document_entities` para limpiar y estructurar los resultados
- Verifica la configuración en Nebuia para asegurarte de que está configurada correctamente
- Revisa la documentación de la API para entender el formato de respuesta actual

### Problema: Error al subir archivos grandes

**Mensaje de error:**
```
API Error (413): Request failed: Request Entity Too Large
```

**Solución:**
- Comprime el PDF antes de subirlo
- Aumenta el timeout para la carga: `upload_document(..., timeout=1800)`
- Divide el documento en partes más pequeñas si es posible

## Glosario

- **API**: Interfaz de Programación de Aplicaciones - Permite que diferentes sistemas se comuniquen
- **Cliente**: Software que interactúa con un servicio remoto (en este caso, la API de Nebuia)
- **Autenticación**: Proceso de verificar la identidad del cliente
- **Registro (Record)**: Contenedor para agrupar documentos relacionados
- **Documento**: Archivo PDF que se sube para procesamiento
- **Entidad**: Información extraída de un documento
- **cURL**: Herramienta de línea de comandos para transferir datos con URLs
- **Callback**: Función que se llama cuando ocurre un evento específico
- **Tiempo de espera**: Tiempo máximo que el código esperará a que se complete una operación
