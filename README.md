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
9. [Ejemplos Detallados de Métodos Principales](#ejemplos-detallados-de-métodos-principales)
10. [Ejemplos de Respuestas de la API](#ejemplos-de-respuestas-de-la-api)
11. [Solución de Problemas](#solución-de-problemas)
12. [Glosario](#glosario)

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

## Ejemplos Detallados de Métodos Principales

### 1. Inicialización del Cliente

El primer paso es inicializar el cliente con las credenciales correctas.

#### Método: `NebuiaHandler.__init__()`

```python
from nebuia_handler import NebuiaHandler
import logging

# Configurar logging (opcional pero recomendado)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Inicializar el handler
handler = NebuiaHandler(
    client_id="c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
    api_key="pub_83f7c9b512345678abcdef0123456789",
    api_secret="sec_83f7c9b512345678abcdef0123456789",
    log_curl=True,  # Registrar comandos cURL para depuración
    log_level=logging.INFO,  # Nivel de detalle del logging
    base_url="https://api.nebuia.com/v1"  # URL base de la API (opcional)
)
```

**¿Qué hace este código?**
1. Importa la clase `NebuiaHandler` que encapsula toda la funcionalidad.
2. Configura el sistema de logging para obtener información útil durante el proceso.
3. Inicializa el cliente con las credenciales necesarias:
   - `client_id`: Identificador único del cliente en Nebuia.
   - `api_key`: Clave pública para las solicitudes a la API.
   - `api_secret`: Clave secreta para autenticación.
4. Habilita el registro de comandos cURL para facilitar la depuración.
5. Establece el nivel de detalle de los mensajes de log.
6. Opcionalmente, especifica la URL base de la API.

**Respuesta de la API:** No hay respuesta directa, ya que este método inicializa el cliente localmente.

### 2. Creación de un Registro

Un registro (record) es un contenedor que agrupa documentos relacionados.

#### Método: `NebuiaClient.create_record()`

```python
try:
    # Crear un nuevo registro usando una configuración específica
    record_response = handler.client.create_record(
        config_name="dictaminación_fiscal"
    )
    
    # Extraer el ID del registro para su uso posterior
    record_id = record_response["id"]
    
    print(f"Registro creado con ID: {record_id}")
    print(f"Detalles del registro: {record_response}")
    
except Exception as e:
    print(f"Error al crear el registro: {str(e)}")
```

**¿Qué hace este código?**
1. Llama al método `create_record()` del cliente Nebuia.
2. Especifica la configuración que se utilizará para este registro mediante `config_name`.
3. Recibe la respuesta de la API y extrae el ID del registro para uso futuro.
4. Maneja posibles errores durante el proceso.

**Respuesta de la API:**
```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "client_id": "c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "configuration_ref": "dictaminación_fiscal",
  "status": "waiting",
  "created_at": "2025-04-16T10:15:30Z",
  "documents": []
}
```

### 3. Subida de Documentos

Una vez creado el registro, se pueden subir documentos asociados a tipos específicos.

#### Método: `NebuiaClient.upload_document()`

```python
# Definir la ruta al archivo PDF
file_path = "./documentos/acta_constitutiva.pdf"
document_type = "acta_constitutiva"

try:
    # Subir el documento al registro creado anteriormente
    upload_response = handler.client.upload_document(
        record_id=record_id,
        file_path=file_path,
        document_type=document_type,
        timeout=300  # Tiempo máximo de espera en segundos
    )
    
    # Extraer el ID del documento
    document_id = upload_response["document_id"]
    
    print(f"Documento subido con ID: {document_id}")
    print(f"Detalles de la carga: {upload_response}")
    
except Exception as e:
    print(f"Error al subir el documento: {str(e)}")
```

**¿Qué hace este código?**
1. Define la ruta al archivo PDF que se va a subir y su tipo según la configuración.
2. Llama al método `upload_document()` con los parámetros necesarios:
   - `record_id`: ID del registro al que pertenecerá el documento.
   - `file_path`: Ruta completa al archivo PDF.
   - `document_type`: Tipo de documento según la configuración.
   - `timeout`: Tiempo máximo de espera para la operación.
3. Extrae el ID del documento para referencia futura.
4. Maneja posibles errores en el proceso de carga.

**Respuesta de la API:**
```json
{
  "document_id": "doc_12345678abcdef0123456789",
  "document_type": "acta_constitutiva",
  "status": "waiting",
  "created_at": "2025-04-16T10:30:45Z"
}
```

#### Subida de Múltiples Documentos

```python
# Definir un diccionario de documentos a subir
documents = {
    "acta_constitutiva": "./documentos/acta_constitutiva.pdf",
    "actas_de_asamblea": "./documentos/actas_asamblea.pdf",
    "poder_notarial": "./documentos/poder_notarial.pdf"
}

document_ids = {}  # Para almacenar los IDs de los documentos

# Iterar a través de los documentos y subirlos
for doc_type, file_path in documents.items():
    try:
        # Verificar que el archivo existe y es accesible
        if not os.path.isfile(file_path):
            print(f"El archivo {file_path} no existe o no es accesible.")
            continue
            
        # Subir el documento
        response = handler.client.upload_document(
            record_id=record_id,
            file_path=file_path,
            document_type=doc_type
        )
        
        # Guardar el ID del documento
        document_ids[doc_type] = response["document_id"]
        
        print(f"Documento {doc_type} subido con ID: {document_ids[doc_type]}")
        
    except Exception as e:
        print(f"Error al subir el documento {doc_type}: {str(e)}")
```

**¿Qué hace este código?**
1. Define un diccionario donde las claves son los tipos de documentos y los valores son las rutas a los archivos.
2. Crea un diccionario vacío para almacenar los IDs de los documentos subidos.
3. Itera a través de cada documento:
   - Verifica que el archivo exista y sea accesible.
   - Sube el documento al registro.
   - Almacena el ID del documento para uso posterior.
4. Maneja los errores individualmente para cada documento.

### 4. Espera por Procesamiento de Embeddings

Después de subir los documentos, es necesario esperar a que el motor de embeddings los procese inicialmente.

#### Método: `NebuiaHandler._wait_for_embedding()`

```python
# Esta función es parte de process_documents(), pero se puede usar independientemente
def wait_for_embedding_example(handler, record_id, document_ids):
    print("Esperando a que los documentos sean procesados por el motor de embeddings...")
    
    # Callback para mostrar progreso
    def status_callback(progress, total, completed_docs):
        percentage = (progress / total) * 100 if total > 0 else 0
        print(f"Progreso: {percentage:.2f}% ({progress}/{total} documentos procesados)")
        for doc_id, status in completed_docs.items():
            print(f"  - Documento {doc_id}: {status}")
    
    try:
        # Esperar a que todos los documentos estén en estado "complete"
        embedding_success = handler._wait_for_embedding(
            record_id=record_id,
            document_ids=list(document_ids.values()),
            interval=5,  # Intervalo de consulta en segundos
            timeout=300,  # Tiempo máximo de espera en segundos
            status_callback=status_callback
        )
        
        if embedding_success:
            print("Todos los documentos han sido procesados correctamente.")
            return True
        else:
            print("No se pudieron procesar todos los documentos en el tiempo establecido.")
            return False
            
    except Exception as e:
        print(f"Error durante la espera por embeddings: {str(e)}")
        return False

# Uso del ejemplo
wait_for_embedding_example(handler, record_id, document_ids)
```

**¿Qué hace este código?**
1. Define una función de ejemplo para esperar por el procesamiento de embeddings.
2. Crea una función de callback para mostrar el progreso durante la espera.
3. Llama al método `_wait_for_embedding()` con los parámetros necesarios:
   - `record_id`: ID del registro que contiene los documentos.
   - `document_ids`: Lista de IDs de documentos a monitorear.
   - `interval`: Tiempo entre consultas de estado en segundos.
   - `timeout`: Tiempo máximo de espera en segundos.
   - `status_callback`: Función para reportar el progreso.
4. Devuelve un booleano que indica si todos los documentos se procesaron exitosamente.

**Respuesta de la API (durante monitoreo):**
```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "status": "waiting",
  "documents": [
    {
      "document_id": "doc_12345678abcdef0123456789",
      "document_type": "acta_constitutiva",
      "status": "processing",
      "progress": 0.45
    },
    {
      "document_id": "doc_98765432abcdef0123456789",
      "document_type": "actas_de_asamblea",
      "status": "waiting",
      "progress": 0.0
    }
  ]
}
```

### 5. Verificación de Tipos de Documentos

Una vez procesados los documentos, es necesario verificar que sean del tipo correcto.

#### Método: `NebuiaClient.verify_document_type()`

```python
def verify_single_document(handler, record_id, document_id, expected_type):
    try:
        # Verificar el tipo de documento
        verification_result = handler.client.verify_document_type(
            record_id=record_id,
            document_id=document_id
        )
        
        # Analizar el resultado
        is_valid = verification_result.get("status", False)
        
        if is_valid:
            print(f"✅ Documento verificado como: {expected_type}")
            return True
        else:
            print(f"❌ Documento inválido. Verificación fallida.")
            print(f"   Tipo encontrado: {verification_result.get('type_document_found', 'desconocido')}")
            
            if "points" in verification_result:
                print("   Razones:")
                for i, point in enumerate(verification_result["points"], 1):
                    print(f"   {i}. {point}")
                    
            return False
            
    except Exception as e:
        print(f"Error durante la verificación: {str(e)}")
        return False

# Ejemplo de uso con un documento individual
doc_id = document_ids["acta_constitutiva"]
verify_single_document(handler, record_id, doc_id, "acta_constitutiva")
```

**¿Qué hace este código?**
1. Define una función para verificar un documento individual.
2. Llama al método `verify_document_type()` con los parámetros necesarios:
   - `record_id`: ID del registro que contiene el documento.
   - `document_id`: ID del documento a verificar.
3. Analiza el resultado de la verificación:
   - Comprueba si el documento es válido (status=true).
   - Si no es válido, muestra el tipo detectado y las razones del fallo.

**Respuesta de la API (verificación exitosa):**
```json
{
  "status": true,
  "type_document_found": "acta_constitutiva",
  "points": [
    "El documento contiene todas las secciones requeridas para un acta constitutiva",
    "Se identificaron estatutos correctamente",
    "Firmas validadas correctamente"
  ]
}
```

**Respuesta de la API (verificación fallida):**
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

#### Método: `NebuiaHandler._verify_all_documents()`

```python
def verify_all_documents_example(handler, record_id, document_ids):
    print("Verificando todos los documentos...")
    
    try:
        # Preparar el mapeo de document_id -> document_type
        document_types = {}
        for doc_type, doc_id in document_ids.items():
            document_types[doc_id] = doc_type
        
        # Verificar todos los documentos
        verification_results, all_passed = handler._verify_all_documents(
            record_id=record_id,
            document_ids=list(document_ids.values())
        )
        
        # Analizar resultados
        print(f"\nResumen de verificación:")
        print(f"Todos los documentos verificados: {all_passed}")
        
        for doc_id, result in verification_results.items():
            doc_type = document_types.get(doc_id, "tipo desconocido")
            status = result.get("status", False)
            print(f"\nDocumento: {doc_type} (ID: {doc_id})")
            print(f"Estado: {'✅ Verificado' if status else '❌ Rechazado'}")
            
            if not status:
                print(f"Tipo detectado: {result.get('type_document_found', 'desconocido')}")
                if "points" in result:
                    print("Razones:")
                    for i, point in enumerate(result["points"], 1):
                        print(f"  {i}. {point}")
        
        return all_passed, verification_results
            
    except Exception as e:
        print(f"Error durante la verificación de documentos: {str(e)}")
        return False, {}

# Uso del ejemplo
verification_passed, results = verify_all_documents_example(handler, record_id, document_ids)
```

**¿Qué hace este código?**
1. Define una función para verificar todos los documentos en un registro.
2. Prepara un mapeo entre IDs de documentos y sus tipos para referencia.
3. Llama al método `_verify_all_documents()` con los parámetros necesarios.
4. Analiza y muestra los resultados de verificación para cada documento.
5. Devuelve un booleano que indica si todos los documentos pasaron la verificación y los resultados detallados.

### 6. Creación de un Trabajo de Procesamiento

Si la verificación es exitosa, el siguiente paso es crear un trabajo de procesamiento para extraer información de los documentos.

#### Método: `NebuiaClient.create_processing_job()`

```python
def create_processing_job_example(handler, record_id):
    print(f"Creando trabajo de procesamiento para el registro {record_id}...")
    
    try:
        # Crear el trabajo de procesamiento
        job_response = handler.client.create_processing_job(record_id)
        
        # Extraer información relevante
        job_id = job_response.get("job_id")
        status = job_response.get("status")
        
        print(f"Trabajo creado exitosamente.")
        print(f"ID del trabajo: {job_id}")
        print(f"Estado inicial: {status}")
        
        return job_id
            
    except Exception as e:
        print(f"Error al crear el trabajo de procesamiento: {str(e)}")
        return None

# Uso del ejemplo (solo si la verificación fue exitosa)
if verification_passed:
    job_id = create_processing_job_example(handler, record_id)
else:
    print("No se puede procesar debido a errores en la verificación de documentos.")
```

**¿Qué hace este código?**
1. Define una función para crear un trabajo de procesamiento.
2. Llama al método `create_processing_job()` con el ID del registro.
3. Extrae información relevante de la respuesta, como el ID del trabajo y su estado.
4. Solo ejecuta la creación del trabajo si todos los documentos pasaron la verificación.

**Respuesta de la API:**
```json
{
  "job_id": "job_12345678abcdef0123456789",
  "record_id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "status": "created",
  "message": "Processing job created successfully"
}
```

### 7. Espera por Finalización del Procesamiento

Una vez creado el trabajo, es necesario esperar a que se complete el procesamiento de todos los documentos.

#### Método: `NebuiaClient.wait_for_record_completion()`

```python
def wait_for_processing_completion(handler, record_id):
    print(f"Esperando a que se complete el procesamiento del registro {record_id}...")
    
    # Callback para mostrar progreso
    def status_callback(status, progress, elapsed_time):
        if progress is not None:
            percentage = progress * 100
            print(f"Progreso: {percentage:.2f}% | Estado: {status} | Tiempo transcurrido: {elapsed_time:.2f}s")
        else:
            print(f"Estado: {status} | Tiempo transcurrido: {elapsed_time:.2f}s")
    
    try:
        # Esperar a que el registro complete su procesamiento
        completed_record = handler.client.wait_for_record_completion(
            record_id=record_id,
            timeout=1800,  # 30 minutos
            interval=10,   # Consultar cada 10 segundos
            status_callback=status_callback
        )
        
        print("\nProcesamiento completado exitosamente.")
        print(f"Estado final: {completed_record.get('status')}")
        
        return completed_record
            
    except Exception as e:
        print(f"Error durante la espera por procesamiento: {str(e)}")
        return None

# Uso del ejemplo
processed_record = wait_for_processing_completion(handler, record_id)
```

**¿Qué hace este código?**
1. Define una función para esperar la finalización del procesamiento.
2. Crea una función de callback para mostrar el progreso durante la espera.
3. Llama al método `wait_for_record_completion()` con los parámetros necesarios:
   - `record_id`: ID del registro a monitorear.
   - `timeout`: Tiempo máximo de espera en segundos.
   - `interval`: Tiempo entre consultas de estado en segundos.
   - `status_callback`: Función para reportar el progreso.
4. Devuelve el registro completo una vez finalizado el procesamiento.

**Respuesta de la API (durante monitoreo):**
```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "status": "processing",
  "progress": 0.65,
  "documents": [
    {
      "document_id": "doc_12345678abcdef0123456789",
      "document_type": "acta_constitutiva",
      "status": "completed",
      "progress": 1.0
    },
    {
      "document_id": "doc_98765432abcdef0123456789",
      "document_type": "actas_de_asamblea",
      "status": "processing",
      "progress": 0.3
    }
  ]
}
```

**Respuesta de la API (procesamiento finalizado):**
```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "status": "completed",
  "progress": 1.0,
  "documents": [
    {
      "document_id": "doc_12345678abcdef0123456789",
      "document_type": "acta_constitutiva",
      "status": "completed",
      "progress": 1.0,
      "entities": [
        {
          "nombre_empresa": "Corporación Ejemplo S.A. de C.V.",
          "fecha_constitucion": "2020-01-15",
          "capital_social": "1,000,000.00"
        }
      ]
    },
    {
      "document_id": "doc_98765432abcdef0123456789",
      "document_type": "actas_de_asamblea",
      "status": "completed",
      "progress": 1.0,
      "entities": [
        {
          "fecha_asamblea": "2023-08-12",
          "tipo_asamblea": "Ordinaria",
          "acuerdos": ["Aprobación de estados financieros", "Nombramiento de nuevo consejero"]
        }
      ]
    }
  ]
}
```

### 8. Extracción de Entidades de Documentos

Una vez completado el procesamiento, es posible extraer y estructurar la información relevante de los documentos.

#### Método: `NebuiaHandler.extract_document_entities()`

```python
def extract_entities_example(handler, processed_record):
    if not processed_record or processed_record.get('status') != 'completed':
        print("El registro no está completado, no se pueden extraer entidades.")
        return {}
    
    print("Extrayendo entidades de los documentos procesados...")
    
    try:
        # Extraer las entidades de todos los documentos
        extracted_info = handler.extract_document_entities(processed_record)
        
        # Mostrar información extraída por tipo de documento
        for doc_type, entities in extracted_info.items():
            print(f"\n📄 Documento: {doc_type}")
            
            if isinstance(entities, list):
                # Si hay múltiples entidades para este tipo de documento
                for i, entity in enumerate(entities, 1):
                    print(f"  Entidad {i}:")
                    for key, value in entity.items():
                        print(f"    - {key}: {value}")
            else:
                # Si hay una sola entidad para este tipo de documento
                for key, value in entities.items():
                    print(f"  - {key}: {value}")
        
        return extracted_info
            
    except Exception as e:
        print(f"Error durante la extracción de entidades: {str(e)}")
        return {}

# Uso del ejemplo
if processed_record:
    extracted_data = extract_entities_example(handler, processed_record)
```

**¿Qué hace este código?**
1. Define una función para extraer entidades de los documentos procesados.
2. Verifica que el registro esté en estado "completed".
3. Llama al método `extract_document_entities()` con el registro procesado.
4. Muestra la información extraída, organizada por tipo de documento.
5. Maneja diferentes estructuras de datos según el documento tenga una o múltiples entidades.

**Estructura de los datos extraídos:**
```python
{
    "acta_constitutiva": {
        "nombre_empresa": "Corporación Ejemplo S.A. de C.V.",
        "fecha_constitucion": "2020-01-15",
        "capital_social": "1,000,000.00",
        "objeto_social": "Desarrollo de software y servicios de tecnología"
    },
    "actas_de_asamblea": [
        {
            "fecha_asamblea": "2023-08-12",
            "tipo_asamblea": "Ordinaria",
            "acuerdos": ["Aprobación de estados financieros", "Nombramiento de nuevo consejero"]
        }
    ]
}
```

### 9. Flujo Completo con process_documents()

El método `process_documents()` de `NebuiaHandler` encapsula todo el flujo anterior en una sola llamada.

#### Método: `NebuiaHandler.process_documents()`

```python
def process_documents_complete_example():
    # Inicializar el handler
    handler = NebuiaHandler(
        client_id="c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
        api_key="pub_83f7c9b512345678abcdef0123456789",
        api_secret="sec_83f7c9b512345678abcdef0123456789",
        log_curl=True
    )
    
    # Definir documentos a procesar
    documents = {
        "acta_constitutiva": "./documentos/acta_constitutiva.pdf",
        "actas_de_asamblea": "./documentos/actas_asamblea.pdf",
        "poder_notarial": "./documentos/poder_notarial.pdf"
    }
    
    try:
        # Callback para mostrar progreso del procesamiento
        def status_callback(status, progress, elapsed_time):
            if progress is not None:
                percentage = progress * 100
                print(f"Progreso: {percentage:.2f}% | Estado: {status} | Tiempo transcurrido: {elapsed_time:.2f}s")
            else:
                print(f"Estado: {status} | Tiempo transcurrido: {elapsed_time:.2f}s")
        
        # Procesar todos los documentos en un solo paso
        result = handler.process_documents(
            documents=documents,
            config_name="dictaminación_fiscal",
            wait_for_completion=True,
            auto_process=True,  # Procesar incluso si la verificación falla
            timeout=1800,       # 30 minutos máximo
            status_callback=status_callback
        )
        
        print("\n✅ Procesamiento completado.")
        
        # Verificar si hay resultados de verificación
        if "verification_results" in result:
            print("\n📋 Resultados de verificación:")
            for doc_type, verification in result["verification_results"].items():
                status = verification.get("status", False)
                print(f"  - {doc_type}: {'✅ Verificado' if status else '❌ Rechazado'}")
        
        # Extraer información procesada
        extracted_info = handler.extract_document_entities(result)
        
        # Mostrar información extraída
        print("\n📊 Información extraída:")
        for doc_type, entities in extracted_info.items():
            print(f"\n  📄 {doc_type}:")
            
            if isinstance(entities, list):
                for i, entity in enumerate(entities, 1):
                    print(f"    Entidad {i}:")
                    for k, v in entity.items():
                        print(f"      - {k}: {v}")
            else:
                for k, v in entities.items():
                    print(f"    - {k}: {v}")
        
        return result, extracted_info
            
    except Exception as e:
        print(f"❌ Error durante el procesamiento: {str(e)}")
        return None, {}

# Ejecutar el ejemplo completo
result, extracted_data = process_documents_complete_example()
```

**¿Qué hace este código?**
1. Define una función que implementa el flujo completo de procesamiento.
2. Inicializa el handler con las credenciales necesarias.
3. Define un diccionario de documentos a procesar.
4. Crea una función de callback para mostrar el progreso.
5. Llama al método `process_documents()` con todos los parámetros necesarios:
   - `documents`: Diccionario de documentos a procesar.
   - `config_name`: Nombre de la configuración a utilizar.
   - `wait_for_completion`: Si debe esperar a que se complete el procesamiento.
   - `auto_process`: Si debe procesar incluso si la verificación falla.
   - `timeout`: Tiempo máximo de espera en segundos.
   - `status_callback`: Función para reportar el progreso.
6. Muestra los resultados de verificación.
7. Extrae y muestra la información procesada.

**Estructura de resultado completo:**
```python
{
    "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
    "status": "completed",
    "verification_results": {
        "acta_constitutiva": {
            "status": true,
            "type_document_found": "acta_constitutiva",
            "points": [...]
        },
        "actas_de_asamblea": {
            "status": true,
            "type_document_found": "actas_de_asamblea",
            "points": [...]
        },
        "poder_notarial": {
            "status": false,
            "type_document_found": "otro_tipo_documento",
            "points": [...]
        }
    },
    "documents": [
        {
            "document_type": "acta_constitutiva",
            "document_id": "doc_12345678abcdef0123456789",
            "status": "completed",
            "entities": [...]
        },
        ...
    ],
    "job_id": "job_12345678abcdef0123456789",
    "created_at": "2025-04-16T10:15:30Z",
    "completed_at": "2025-04-16T10:45:20Z"
}
```

### 10. Manejo de Errores

Es importante implementar un manejo robusto de errores al trabajar con la API de Nebuia.

#### Ejemplo de Manejo de Errores Específicos

```python
from nebuia_client import NebuiaAPIError, NebuiaTimeoutError, NebuiaValidationError

def robust_document_processing(handler, documents, config_name):
    try:
        result = handler.process_documents(
            documents=documents,
            config_name=config_name,
            wait_for_completion=True
        )
        return True, result
        
    except NebuiaValidationError as e:
        print(f"❌ Error de validación: {str(e)}")
        print("   → Este error ocurre cuando hay problemas con los documentos o su formato.")
        print("   → Verifica que los documentos sean PDFs válidos y accesibles.")
        return False, {"error": "validation", "message": str(e)}
        
    except NebuiaTimeoutError as e:
        print(f"⏱️ Error de tiempo de espera: {str(e)}")
        print("   → El procesamiento ha tomado demasiado tiempo.")
        print("   → Puedes intentar nuevamente o aumentar el timeout.")
        return False, {"error": "timeout", "message": str(e)}
        
    except NebuiaAPIError as e:
        print(f"🌐 Error de API: {str(e)}")
        print(f"   → Código HTTP: {e.status_code}")
        print(f"   → Respuesta: {e.response}")
        
        if e.status_code == 401:
            print("   → Verifica tus credenciales de API.")
        elif e.status_code == 404:
            print("   → Recurso no encontrado. Verifica los IDs utilizados.")
        elif e.status_code == 429:
            print("   → Límite de tasa excedido. Espera un momento e intenta nuevamente.")
        
        return False, {"error": "api", "code": e.status_code, "message": str(e)}
        
    except Exception as e:
        print(f"⚠️ Error inesperado: {str(e)}")
        print("   → Este es un error no controlado específicamente.")
        return False, {"error": "unknown", "message": str(e)}

# Uso de la función robusta
success, result = robust_document_processing(
    handler,
    documents={"acta_constitutiva": "./documentos/acta.pdf"},
    config_name="dictaminación_fiscal"
)

if success:
    print("✅ Procesamiento exitoso!")
    extracted_info = handler.extract_document_entities(result)
    # Hacer algo con la información extraída
else:
    print(f"❌ Procesamiento fallido: {result['error']} - {result['message']}")
    # Implementar lógica de recuperación o reintento
```

**¿Qué hace este código?**
1. Define una función que implementa manejo robusto de errores específicos.
2. Captura diferentes tipos de excepciones que pueden ocurrir durante el procesamiento:
   - `NebuiaValidationError`: Problemas con los documentos o su formato.
   - `NebuiaTimeoutError`: El procesamiento ha tomado demasiado tiempo.
   - `NebuiaAPIError`: Errores específicos de la API, con códigos HTTP.
   - `Exception`: Cualquier otro error no controlado específicamente.
3. Proporciona mensajes informativos y sugerencias para cada tipo de error.
4. Devuelve una estructura uniforme para facilitar el manejo de errores.
5. Demuestra cómo usar la función y manejar sus resultados de manera apropiada.

## Ejemplos de Respuestas de la API

A continuación se detallan los formatos de respuesta para cada endpoint principal, tanto para casos de éxito como de error.

### 1. Creación de Cliente (`POST /clients`)

Este endpoint permite crear un nuevo cliente y genera sus credenciales de API.

#### Solicitud

```json
{
  "email": "empresa@ejemplo.com",
  "password": "contraseña_segura",
  "name": "Empresa Ejemplo",
  "quota": 1000
}
```

#### Respuesta Exitosa (201 Created)

```json
{
  "id": "c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "api_keys": {
    "public_key": "pub_83f7c9b512345678abcdef0123456789",
    "secret_key": "sec_83f7c9b512345678abcdef0123456789"
  }
}
```

**Descripción de campos:**
- `id`: Identificador único del cliente (UUID) en la plataforma Nebuia.
- `api_keys`: Objeto que contiene las claves de API para autenticación:
  - `public_key`: Clave pública que debe usarse en solicitudes a la API.
  - `secret_key`: Clave secreta que debe mantenerse segura y usarse para autenticación.

#### Respuesta de Error (400 Bad Request - Email Duplicado)

```json
{
  "error": true,
  "message": "A user already exists with email empresa@ejemplo.com"
}
```

### 2. Obtener Cliente (`GET /clients/:client_id`)

Este endpoint recupera la información de un cliente específico.

#### Respuesta Exitosa (200 OK)

```json
{
  "id": "c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "name": "Empresa Ejemplo",
  "api_key": "pub_83f7c9b512345678abcdef0123456789",
  "secret_key": "sec_83f7c9b512345678abcdef0123456789",
  "quota": 1000,
  "used_quota": 42,
  "created_at": "2025-01-15T10:30:45Z",
  "configurations": {
    "dictaminación": {
      "documents": {
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
      }
    }
  },
  "flows": {
    "dictaminación_fiscal": {
      "name": "Dictaminación Fiscal",
      "description": "Flujo para dictaminar documentos fiscales",
      "configuration_refs": [
        {
          "name": "dictaminación",
          "type": "primary"
        }
      ],
      "created_at": "2025-02-10T14:22:10Z"
    }
  }
}
```

**Descripción de campos:**
- `id`: Identificador único del cliente.
- `name`: Nombre del cliente.
- `api_key`: Clave pública para autenticación en la API.
- `secret_key`: Clave secreta para autenticación.
- `quota`: Cuota total asignada al cliente.
- `used_quota`: Cuota utilizada hasta el momento.
- `created_at`: Fecha de creación del cliente.
- `configurations`: Mapa de configuraciones disponibles para el cliente.
- `flows`: Mapa de flujos de trabajo definidos para el cliente.

#### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

### 3. Crear Configuración (`POST /clients/:client_id/configurations/:config_name`)

Este endpoint crea o actualiza una configuración para un cliente específico.

#### Solicitud

```json
{
  "documents": {
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
  }
}
```

#### Respuesta Exitosa (200 OK)

```json
{
  "message": "Configuration dictaminación added successfully"
}
```

#### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

### 4. Agregar Documento a un Registro (`POST /clients/:client_id/records/:record_id/documents`)

Este endpoint añade un documento a un registro existente.

#### Solicitud

Formulario multipart con los siguientes campos:
- `file`: Archivo PDF del documento
- `document_type`: Tipo de documento (e.g., "acta_constitutiva")
- `process_document`: Bool (opcional, default: false)

#### Respuesta Exitosa (Sin Procesamiento, 200 OK)

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

**Descripción de campos:**
- `message`: Mensaje de confirmación.
- `document`: Objeto que representa el documento añadido:
  - `document_type`: Tipo de documento según la configuración.
  - `document_id`: Identificador único del documento.
  - `structure`: Estructura inicial vacía (se llenará durante el procesamiento).
  - `created_at`: Fecha y hora de creación del documento.

#### Respuesta Exitosa (Con Procesamiento Automático, 200 OK)

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

**Campos adicionales:**
- `job_id`: Identificador del trabajo de procesamiento creado.

#### Respuesta de Error (400 Bad Request - Tipo de Documento No Permitido)

```json
{
  "error": true,
  "message": "Document type acta_fiscal not allowed"
}
```

### 5. Crear un Registro (`POST /clients/:client_id/records/create`)

Este endpoint crea un nuevo registro para procesar documentos.

#### Solicitud

```json
{
  "configuration_ref": "dictaminación",
  "with_email": true,
  "email": "usuario@ejemplo.com",
  "flow_name": "dictaminación_fiscal"
}
```

#### Respuesta Exitosa (201 Created)

```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "message": "Record created successfully"
}
```

**Descripción de campos:**
- `id`: Identificador único del registro creado.
- `message`: Mensaje de confirmación.

#### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Configuration dictaminacion_fiscal not found"
}
```

### 6. Crear un Flujo (`POST /clients/:client_id/flows/:flow_name`)

Este endpoint crea un nuevo flujo de trabajo.

#### Solicitud

```json
{
  "name": "Dictaminación Fiscal",
  "description": "Flujo para dictaminar documentos fiscales",
  "configuration_refs": [
    {
      "name": "dictaminación",
      "type": "primary"
    },
    {
      "name": "fiscal",
      "type": "secondary"
    }
  ]
}
```

#### Respuesta Exitosa (200 OK)

```json
{
  "message": "Flow dictaminación_fiscal created successfully"
}
```

#### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Configuration dictaminación_inexistente not found"
}
```

### 7. Crear un Trabajo de Procesamiento (`POST /clients/:client_id/records/:record_id/process`)

Este endpoint crea un trabajo para procesar todos los documentos en un registro.

#### Respuesta Exitosa (Trabajo Creado, 200 OK)

```json
{
  "job_id": "job_12345678abcdef0123456789",
  "message": "Processing job created successfully",
  "status": "created"
}
```

**Descripción de campos:**
- `job_id`: Identificador único del trabajo de procesamiento.
- `message`: Mensaje de confirmación.
- `status`: Estado del trabajo ("created").

#### Respuesta (Registro Ya en Procesamiento, 200 OK)

```json
{
  "job_id": "job_12345678abcdef0123456789",
  "message": "Record is already being processed",
  "status": "already_processing"
}
```

#### Respuesta (Documentos Requeridos Faltantes, 200 OK)

```json
{
  "message": "Missing required documents: [\"acta_constitutiva\",\"actas_de_asamblea\"]",
  "status": "missing_documents",
  "missing_documents": ["acta_constitutiva", "actas_de_asamblea"]
}
```

### 8. Verificar Tipo de Documento (`GET /clients/:client_id/records/:record_id/type/:document_id`)

Este endpoint verifica si un documento es del tipo declarado.

#### Respuesta Exitosa (Documento Verificado, 200 OK)

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

**Descripción de campos:**
- `status`: Boolean que indica si la verificación fue exitosa.
- `type_document_found`: Tipo de documento identificado por el sistema.
- `points`: Lista de puntos o criterios que confirman el tipo de documento.

#### Respuesta Fallida (Documento de Tipo Incorrecto, 200 OK)

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

### 9. Obtener Detalles de un Registro (`GET /clients/:client_id/records/:record_id`)

Este endpoint recupera los detalles completos de un registro específico.

#### Respuesta Exitosa (200 OK)

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
    },
    {
      "document_type": "actas_de_asamblea",
      "document_id": "doc_98765432abcdef0123456789",
      "created_at": "2025-04-16T11:15:22Z",
      "document_predict": {
        "status": true,
        "type_document_found": "actas_de_asamblea",
        "points": [
          "El documento contiene todas las secciones esperadas de un acta de asamblea",
          "Se identificaron los acuerdos correctamente",
          "Se validaron las firmas de los asistentes"
        ]
      },
      "entities": [
        {
          "structure": {
            "fecha_asamblea": "2023-08-12",
            "tipo_asamblea": "Ordinaria",
            "acuerdos": [
              "Aprobación de estados financieros",
              "Nombramiento de nuevo consejero"
            ]
          },
          "query": "Extrae la información de la asamblea",
          "name_to_show": "Información de Asamblea"
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
  "keys_not_found": [],
  "current_document_id": null
}
```

**Descripción de campos:**
- `id`: Identificador único del registro.
- `configuration_ref`: Referencia a la configuración utilizada.
- `documents`: Array de documentos procesados, cada uno con:
  - `document_type`: Tipo de documento.
  - `document_id`: Identificador único del documento.
  - `created_at`: Fecha de creación.
  - `document_predict`: Resultado de la verificación del tipo de documento.
  - `entities`: Información extraída del documento.
- `status`: Estado actual del registro.
- `created_at`: Fecha de creación del registro.
- `allowed_documents`: Documentos permitidos según la configuración.
- `is_processing`: Indica si el registro está siendo procesado actualmente.

### 10. Listar Registros (`GET /clients/:client_id/records`)

Este endpoint lista todos los registros asociados a un cliente, con paginación.

#### Solicitud

```
?page=1&page_size=10
```

#### Respuesta Exitosa (200 OK)

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

### 11. Procesar Documento para Extracción de Información (`POST /clients/:client_id/records/:record_id/single/inference/record`)

Este endpoint procesa un documento específico para extraer información estructurada.

#### Solicitud

```json
{
  "doc_id": "doc_12345678abcdef0123456789",
  "query": "Extrae la información básica de la empresa",
  "data": {
    "additional_context": "Documento de constitución de sociedad mercantil"
  }
}
```

#### Respuesta Exitosa (200 OK)

```json
{
  "structure": {
    "nombre_empresa": "Corporación Ejemplo S.A. de C.V.",
    "fecha_constitucion": "2020-01-15",
    "capital_social": "1,000,000.00",
    "objeto_social": "Desarrollo de software y servicios de tecnología"
  },
  "pages": [
    {
      "page_number": 1,
      "text": "ACTA CONSTITUTIVA...",
      "confidence": 0.95
    },
    {
      "page_number": 2,
      "text": "CLÁUSULAS...",
      "confidence": 0.97
    }
  ]
}
```

### 12. Login de Usuario (`POST /clients/auth/login`)

Este endpoint permite autenticar a un usuario y obtener una clave temporal.

#### Solicitud

```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

#### Respuesta Exitosa (200 OK)

```json
{
  "temporal_key": "temp_83f7c9b512345678abcdef0123456789"
}
```

#### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "User not found"
}
```

### 13. Obtener Estado de Trabajos del Cliente (`GET /clients/:client_id/records/jobs/status/metrics`)

Este endpoint recupera métricas sobre los trabajos de procesamiento de un cliente.

#### Solicitud (Resumen)

```
?detailed=false
```

#### Respuesta Exitosa (Resumen, 200 OK)

```json
{
  "is_processing": true,
  "job_id": "job_12345678abcdef0123456789",
  "record_id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "document_id": "doc_12345678abcdef0123456789",
  "started_at": "2025-04-16T10:30:45Z"
}
```

#### Solicitud (Detallada)

```
?detailed=true&status_filter=completed&page=1&page_size=10
```

#### Respuesta Exitosa (Detallada, 200 OK)

```json
{
  "jobs": {
    "processing": [
      {
        "job_id": "job_12345678abcdef0123456789",
        "record_id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
        "document_id": "doc_12345678abcdef0123456789",
        "current_document_id": "doc_12345678abcdef0123456789",
        "status": "processing",
        "started_at": "2025-04-16T10:30:45Z",
        "created_at": "2025-04-16T10:30:40Z"
      }
    ],
    "pending": [],
    "completed": [],
    "failed": [],
    "cancelled": []
  },
  "metrics": {
    "total_jobs": 1,
    "processing_count": 1,
    "pending_count": 0,
    "completed_count": 0,
    "failed_count": 0,
    "cancelled_count": 0,
    "average_processing_time": "0:00:00",
    "success_rate": 0
  },
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 1,
    "total_pages": 1
  }
}
```

### 14. Cancelar un Trabajo (`DELETE /clients/:client_id/records/jobs/cancel/:job_id`)

Este endpoint cancela un trabajo de procesamiento en curso.

#### Respuesta Exitosa (200 OK)

```json
{
  "status": "success",
  "message": "Job canceled successfully"
}
```

#### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "You can't cancel a job with status completed"
}
```

### 15. Eliminar un Trabajo (`DELETE /clients/:client_id/records/jobs/delete/:job_id`)

Este endpoint elimina un trabajo de procesamiento que no está en curso.

#### Respuesta Exitosa (200 OK)

```json
{
  "status": "success",
  "message": "Job deleted successfully"
}
```

#### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Cannot delete a job that is currently processing. Cancel it first."
}
```

### 16. Reprocesar un Trabajo (`POST /clients/:client_id/records/:record_id/reprocess/job/:job_id`)

Este endpoint crea un nuevo trabajo para reprocesar un registro basado en un trabajo anterior.

#### Respuesta Exitosa (200 OK)

```json
{
  "job_id": "job_45678901abcdef0123456789"
}
```

### 17. Obtener Información de Cuota (`GET /clients/:client_id/quota`)

Este endpoint obtiene la información actual de cuota de un cliente.

#### Respuesta Exitosa (200 OK)

```json
{
  "quota": 1000,
  "used_quota": 42,
  "remaining_quota": 958
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
