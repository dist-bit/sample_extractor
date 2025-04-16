# Ejemplos Detallados de Respuestas de la API

Esta sección detalla los formatos de respuesta para cada endpoint principal, tanto para casos de éxito como de error. Estas respuestas servirán como referencia para integrar aplicaciones con la API de Nebuia y facilitar el debugging.

## 1. Creación de Cliente (`POST /clients`)

Este endpoint permite crear un nuevo cliente y genera sus credenciales de API.

### Solicitud

```json
{
  "email": "empresa@ejemplo.com",
  "password": "contraseña_segura",
  "name": "Empresa Ejemplo",
  "quota": 1000
}
```

### Respuesta Exitosa (201 Created)

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

### Respuesta de Error (400 Bad Request - Email Duplicado)

```json
{
  "error": true,
  "message": "A user already exists with email empresa@ejemplo.com"
}
```

### Respuesta de Error (400 Bad Request - Datos Inválidos)

```json
{
  "error": true,
  "message": "Invalid request body"
}
```

### Respuesta de Error (500 Internal Server Error)

```json
{
  "error": true,
  "message": "Error creating client: database connection error"
}
```

## 2. Obtener Cliente (`GET /clients/:client_id`)

Este endpoint recupera la información de un cliente específico.

### Respuesta Exitosa (200 OK)

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
  - Cada configuración contiene definiciones de documentos y entidades.
- `flows`: Mapa de flujos de trabajo definidos para el cliente.
  - Cada flujo incluye referencias a configuraciones y metadatos.

### Respuesta de Error (403 Forbidden)

```json
{
  "error": true,
  "message": "Forbidden"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 3. Crear Configuración (`POST /clients/:client_id/configurations/:config_name`)

Este endpoint crea o actualiza una configuración para un cliente específico.

### Solicitud

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
        },
        {
          "structure": {
            "objeto_social": "",
            "domicilio": "",
            "duracion": ""
          },
          "query": "Extrae detalles adicionales de la empresa",
          "name_to_show": "Detalles Corporativos"
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

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Configuration dictaminación added successfully"
}
```

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Invalid request body"
}
```

### Respuesta de Error (403 Forbidden)

```json
{
  "error": true,
  "message": "Forbidden"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

### Respuesta de Error (500 Internal Server Error)

```json
{
  "error": true,
  "message": "Error serializing configurations: json: unsupported type"
}
```

## 4. Listar Configuraciones (`GET /clients/:client_id/configurations`)

Este endpoint recupera todas las configuraciones disponibles para un cliente.

### Respuesta Exitosa (200 OK)

```json
{
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
          },
          {
            "structure": {
              "objeto_social": "",
              "domicilio": "",
              "duracion": ""
            },
            "query": "Extrae detalles adicionales de la empresa",
            "name_to_show": "Detalles Corporativos"
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
  },
  "fiscal": {
    "documents": {
      "declaracion_anual": {
        "required": true,
        "entities": [
          {
            "structure": {
              "ejercicio_fiscal": "",
              "ingresos_totales": "",
              "impuesto_declarado": ""
            },
            "query": "Extrae información fiscal de la declaración anual",
            "name_to_show": "Información Fiscal"
          }
        ]
      }
    }
  }
}
```

### Respuesta de Error (403 Forbidden)

```json
{
  "error": true,
  "message": "Forbidden"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 5. Eliminar Configuración (`DELETE /clients/:client_id/configurations/:config_name`)

Este endpoint elimina una configuración específica de un cliente.

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Configuration dictaminación deleted successfully"
}
```

### Respuesta de Error (403 Forbidden)

```json
{
  "error": true,
  "message": "Forbidden"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Configuration not found"
}
```

### Respuesta de Error (409 Conflict)

```json
{
  "error": true,
  "message": "Configuration 'dictaminación' is referenced by flow 'dictaminación_fiscal' and cannot be deleted"
}
```

## 6. Crear un Registro (`POST /clients/:client_id/records/create`)

Este endpoint crea un nuevo registro para procesar documentos.

### Solicitud

```json
{
  "configuration_ref": "dictaminación",
  "with_email": true,
  "email": "usuario@ejemplo.com",
  "flow_name": "dictaminación_fiscal"
}
```

### Respuesta Exitosa (201 Created)

```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "message": "Record created successfully"
}
```

**Descripción de campos:**
- `id`: Identificador único del registro creado.
- `message`: Mensaje de confirmación.

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Configuration dictaminacion_fiscal not found"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 7. Crear URL de Registro (`POST /clients/:client_id/records/create-record-url`)

Este endpoint crea un nuevo registro y genera una URL para acceso directo.

### Solicitud

```
flow_name=dictaminación_fiscal
```

### Respuesta Exitosa (201 Created)

```json
{
  "id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "url": "https://extractor-admin.nebuia.com/mortgage?client_id=c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890&flow_name=dictaminación_fiscal&api_key=temp_83f7c9b512345678abcdef0123456789&record_id=r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "message": "Record created successfully"
}
```

**Descripción de campos:**
- `id`: Identificador único del registro creado.
- `url`: URL para acceder directamente al registro.
- `message`: Mensaje de confirmación.

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Flow name is required"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Flow not found"
}
```

## 8. Agregar Documento a un Registro (`POST /clients/:client_id/records/:record_id/documents`)

Este endpoint añade un documento a un registro existente.

### Solicitud

Formulario multipart con los siguientes campos:
- `file`: Archivo PDF del documento
- `document_type`: Tipo de documento (e.g., "acta_constitutiva")
- `process_document`: Bool (opcional, default: false)

### Respuesta Exitosa (Sin Procesamiento, 200 OK)

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

### Respuesta Exitosa (Con Procesamiento Automático, 200 OK)

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

### Respuesta de Error (400 Bad Request - Tipo de Documento No Permitido)

```json
{
  "error": true,
  "message": "Document type acta_fiscal not allowed"
}
```

### Respuesta de Error (400 Bad Request - Archivo Faltante)

```json
{
  "error": true,
  "message": "File is required"
}
```

### Respuesta de Error (400 Bad Request - Tipo de Documento Faltante)

```json
{
  "error": true,
  "message": "document_type is required"
}
```

### Respuesta de Error (404 Not Found - Cliente)

```json
{
  "error": true,
  "message": "Client not found"
}
```

### Respuesta de Error (404 Not Found - Registro)

```json
{
  "error": true,
  "message": "Record not found"
}
```

### Respuesta de Error (500 Internal Server Error - Procesamiento de PDF)

```json
{
  "error": true,
  "message": "Error processing the PDF: invalid file format"
}
```

## 9. Añadir Documento desde Google Storage (`POST /clients/:client_id/records/:record_id/google`)

Este endpoint añade un documento desde una URL de Google Storage.

### Solicitud

```
document_type=acta_constitutiva&document_url=https://storage.googleapis.com/bucket/documento.pdf&process_document=true
```

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Document added to record successfully",
  "document": {
    "document_type": "acta_constitutiva",
    "document_id": "doc_12345678abcdef0123456789",
    "document_url": "https://storage.googleapis.com/bucket/documento.pdf",
    "structure": {},
    "created_at": "2025-04-16T10:30:45Z"
  }
}
```

**Descripción de campos:**
- Similar a la respuesta de agregar documento, pero con el campo adicional:
  - `document_url`: URL de Google Storage desde donde se obtuvo el documento.

### Respuesta de Error (400 Bad Request - URL Inválida)

```json
{
  "error": true,
  "message": "The URL must be from Google Storage"
}
```

### Respuesta de Error (400 Bad Request - No es PDF)

```json
{
  "error": true,
  "message": "The document must be a PDF"
}
```

## 10. Eliminar Documento de un Registro (`DELETE /clients/:client_id/records/:record_id/:document_id`)

Este endpoint elimina un documento específico de un registro.

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Document removed successfully"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Document not found in record"
}
```

## 11. Actualizar Entidades de un Documento (`PATCH /clients/:client_id/records/:record_id/:document_id/entities`)

Este endpoint actualiza las entidades extraídas de un documento.

### Solicitud

```json
{
  "entities": [
    {
      "nombre_empresa": "Corporación Ejemplo S.A. de C.V.",
      "fecha_constitucion": "2020-01-15",
      "capital_social": "1,000,000.00"
    }
  ]
}
```

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Entities updated successfully",
  "document_id": "doc_12345678abcdef0123456789",
  "updated_entities": [
    {
      "nombre_empresa": "Corporación Ejemplo S.A. de C.V.",
      "fecha_constitucion": "2020-01-15",
      "capital_social": "1,000,000.00"
    }
  ]
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Document not found in record"
}
```

## 12. Verificar Tipo de Documento (`GET /clients/:client_id/records/:record_id/type/:document_id`)

Este endpoint verifica si un documento es del tipo declarado.

### Respuesta Exitosa (Documento Verificado, 200 OK)

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

### Respuesta Fallida (Documento de Tipo Incorrecto, 200 OK)

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

**Descripción de campos:**
- `status`: `false` indica que la verificación falló.
- `type_document_found`: El tipo de documento que el sistema cree que es realmente.
- `points`: Lista de razones por las que falló la verificación.

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Document not found in record"
}
```

## 13. Procesar Todos los Tipos de Documento (`POST /clients/:client_id/records/:record_id/process-all-types`)

Este endpoint inicia el procesamiento en segundo plano de todos los documentos en un registro.

### Respuesta Exitosa (202 Accepted)

```json
{
  "status": "processing",
  "message": "Processing started in the background. Results will be saved automatically.",
  "record_id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "document_count": 3
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Record not found"
}
```

## 14. Procesar Documento para Extracción de Información (`POST /clients/:client_id/records/:record_id/single/inference/record`)

Este endpoint procesa un documento específico para extraer información estructurada.

### Solicitud

```json
{
  "doc_id": "doc_12345678abcdef0123456789",
  "query": "Extrae la información básica de la empresa",
  "data": {
    "additional_context": "Documento de constitución de sociedad mercantil"
  }
}
```

### Respuesta Exitosa (200 OK)

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

**Descripción de campos:**
- `structure`: Objeto con la información extraída del documento según la consulta.
- `pages`: Información por página del documento procesado:
  - `page_number`: Número de página.
  - `text`: Texto extraído de la página.
  - `confidence`: Nivel de confianza en la extracción (0-1).

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Record not found"
}
```

### Respuesta de Error (500 Internal Server Error)

```json
{
  "error": true,
  "message": "Error processing document: inference error"
}
```

## 15. Crear un Trabajo de Procesamiento (`POST /clients/:client_id/records/:record_id/process`)

Este endpoint crea un trabajo para procesar todos los documentos en un registro.

### Respuesta Exitosa (Trabajo Creado, 200 OK)

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

### Respuesta (Registro Ya en Procesamiento, 200 OK)

```json
{
  "job_id": "job_12345678abcdef0123456789",
  "message": "Record is already being processed",
  "status": "already_processing"
}
```

### Respuesta (Estado del Registro No Permite Procesamiento, 200 OK)

```json
{
  "message": "Record status 'completed' does not allow processing",
  "status": "invalid_status"
}
```

### Respuesta (Documentos Requeridos Faltantes, 200 OK)

```json
{
  "message": "Missing required documents: [\"acta_constitutiva\",\"actas_de_asamblea\"]",
  "status": "missing_documents",
  "missing_documents": ["acta_constitutiva", "actas_de_asamblea"]
}
```

**Descripción de campos:**
- `message`: Mensaje explicativo del error.
- `status`: Estado específico del error.
- `missing_documents`: Lista de documentos requeridos que faltan.

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Record not found"
}
```

## 16. Obtener Detalles de un Registro (`GET /clients/:client_id/records/:record_id`)

Este endpoint recupera los detalles completos de un registro específico.

### Respuesta Exitosa (200 OK)

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
- `status`: Estado actual del registro ("waiting", "processing", "completed", "error").
- `created_at`: Fecha de creación del registro.
- `response_client`: Datos adicionales para el cliente (puede estar vacío).
- `allowed_documents`: Documentos permitidos según la configuración, con sus entidades.
- `is_processing`: Indica si el registro está siendo procesado actualmente.
- `keys_not_found`: Lista de claves de configuración no encontradas (si las hay).
- `current_document_id`: ID del documento que se está procesando actualmente (si aplica).

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Record not found"
}
```

## 17. Listar Registros (`GET /clients/:client_id/records`)

Este endpoint lista todos los registros asociados a un cliente, con paginación.

### Solicitud

```
?page=1&page_size=10
```

### Respuesta Exitosa (200 OK)

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
    },
    {
      "id": "t3d4c5e6-g7h8-9012-c3d4-e5f6g7h89012",
      "configuration_ref": "fiscal",
      "created_at": "2025-04-10T09:45:18Z",
      "status": "waiting",
      "document_count": 0
    }
  ],
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 3,
    "total_pages": 1
  }
}
```

**Descripción de campos:**
- `data`: Array de registros, cada uno con información resumida:
  - `id`: Identificador único del registro.
  - `configuration_ref`: Referencia a la configuración utilizada.
  - `created_at`: Fecha de creación del registro.
  - `status`: Estado actual del registro.
  - `document_count`: Número de documentos en el registro.
- `pagination`: Información de paginación:
  - `current_page`: Página actual.
  - `page_size`: Tamaño de página.
  - `total_items`: Total de registros.
  - `total_pages`: Total de páginas.

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 18. Eliminar un Registro (`DELETE /clients/:client_id/records/:record_id`)

Este endpoint elimina un registro y todos sus documentos asociados.

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Record and associated documents deleted successfully",
  "record_id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "documents_deleted": 2,
  "deletion_results": [
    {
      "document_id": "doc_12345678abcdef0123456789",
      "success": true,
      "status_code": 200
    },
    {
      "document_id": "doc_98765432abcdef0123456789",
      "success": true,
      "status_code": 200
    }
  ]
}
```

**Descripción de campos:**
- `message`: Mensaje de confirmación.
- `record_id`: ID del registro eliminado.
- `documents_deleted`: Número de documentos eliminados.
- `deletion_results`: Resultados detallados de la eliminación de cada documento:
  - `document_id`: ID del documento.
  - `success`: Indica si la eliminación fue exitosa.
  - `status_code`: Código de estado HTTP de la operación de eliminación.

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Record not found"
}
```

## 19. Actualizar Estado de un Registro (`PATCH /clients/:client_id/records/:record_id/status`)

Este endpoint actualiza el estado de un registro.

### Solicitud

```json
{
  "status": "waiting"
}
```

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Status updated to waiting"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Record not found"
}
```

## 20. Crear un Flujo (`POST /clients/:client_id/flows/:flow_name`)

Este endpoint crea un nuevo flujo de trabajo.

### Solicitud

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

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Flow dictaminación_fiscal created successfully"
}
```

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Configuration dictaminación_inexistente not found"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 21. Obtener un Flujo (`GET /clients/:client_id/flows/:flow_identifier`)

Este endpoint recupera los detalles de un flujo específico.

### Respuesta Exitosa (200 OK)

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
  ],
  "created_at": "2025-02-10T14:22:10Z",
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
      },
      "type": "primary"
    },
    "fiscal": {
      "documents": {
        "declaracion_anual": {
          "required": true,
          "entities": [
            {
              "structure": {
                "ejercicio_fiscal": "",
                "ingresos_totales": "",
                "impuesto_declarado": ""
              },
              "query": "Extrae información fiscal de la declaración anual",
              "name_to_show": "Información Fiscal"
            }
          ]
        }
      },
      "type": "secondary"
    }
  }
}
```

**Descripción de campos:**
- `name`: Nombre descriptivo del flujo.
- `description`: Descripción del flujo.
- `configuration_refs`: Referencias a las configuraciones utilizadas.
- `created_at`: Fecha de creación del flujo.
- `configurations`: Detalles completos de las configuraciones referenciadas.

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Flow not found"
}
```

## 22. Listar Flujos (`GET /clients/:client_id/flows`)

Este endpoint recupera todos los flujos disponibles para un cliente.

### Respuesta Exitosa (200 OK)

```json
{
  "dictaminación_fiscal": {
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
    ],
    "created_at": "2025-02-10T14:22:10Z",
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
        },
        "type": "primary"
      },
      "fiscal": {
        "documents": {
          "declaracion_anual": {
            "required": true,
            "entities": [
              {
                "structure": {
                  "ejercicio_fiscal": "",
                  "ingresos_totales": "",
                  "impuesto_declarado": ""
                },
                "query": "Extrae información fiscal de la declaración anual",
                "name_to_show": "Información Fiscal"
              }
            ]
          }
        },
        "type": "secondary"
      }
    }
  },
  "dictaminación_legal": {
    "name": "Dictaminación Legal",
    "description": "Flujo para dictaminar documentos legales",
    "configuration_refs": [
      {
        "name": "dictaminación",
        "type": "primary"
      }
    ],
    "created_at": "2025-03-15T09:30:12Z",
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
        },
        "type": "primary"
      }
    }
  }
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 23. Eliminar un Flujo (`DELETE /clients/:client_id/flows/:flow_name`)

Este endpoint elimina un flujo específico.

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Flow dictaminación_fiscal deleted successfully"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Flow not found"
}
```

## 24. Obtener Estado de Trabajos del Cliente (`GET /clients/:client_id/records/jobs/status/metrics`)

Este endpoint recupera métricas sobre los trabajos de procesamiento de un cliente.

### Solicitud (Resumen)

```
?detailed=false
```

### Respuesta Exitosa (Resumen, 200 OK)

```json
{
  "is_processing": true,
  "job_id": "job_12345678abcdef0123456789",
  "record_id": "r1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "document_id": "doc_12345678abcdef0123456789",
  "started_at": "2025-04-16T10:30:45Z"
}
```

**Descripción de campos:**
- `is_processing`: Indica si hay algún trabajo en procesamiento.
- `job_id`: ID del trabajo en procesamiento.
- `record_id`: ID del registro asociado al trabajo.
- `document_id`: ID del documento que se está procesando actualmente.
- `started_at`: Fecha de inicio del procesamiento.

### Solicitud (Detallada)

```
?detailed=true&status_filter=completed&page=1&page_size=10
```

### Respuesta Exitosa (Detallada, 200 OK)

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
    "pending": [
      {
        "job_id": "job_23456789abcdef0123456789",
        "record_id": "s2c3b4d5-f6g7-8901-b2c3-d4e5f6g78901",
        "document_id": "doc_23456789abcdef0123456789",
        "status": "pending",
        "created_at": "2025-04-16T11:15:22Z"
      }
    ],
    "completed": [
      {
        "job_id": "job_34567890abcdef0123456789",
        "record_id": "t3d4c5e6-g7h8-9012-c3d4-e5f6g7h89012",
        "document_id": "doc_34567890abcdef0123456789",
        "status": "completed",
        "created_at": "2025-04-15T09:45:18Z",
        "completed_at": "2025-04-15T10:15:30Z",
        "processing_time": "0:30:12"
      }
    ],
    "failed": [],
    "cancelled": []
  },
  "metrics": {
    "total_jobs": 3,
    "processing_count": 1,
    "pending_count": 1,
    "completed_count": 1,
    "failed_count": 0,
    "cancelled_count": 0,
    "average_processing_time": "0:30:12",
    "success_rate": 100
  },
  "pagination": {
    "current_page": 1,
    "page_size": 10,
    "total_items": 3,
    "total_pages": 1
  }
}
```

**Descripción de campos:**
- `jobs`: Objeto con listas de trabajos agrupados por estado:
  - `processing`: Trabajos en procesamiento.
  - `pending`: Trabajos pendientes.
  - `completed`: Trabajos completados.
  - `failed`: Trabajos fallidos.
  - `cancelled`: Trabajos cancelados.
- `metrics`: Estadísticas agregadas sobre los trabajos.
- `pagination`: Información de paginación.

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 25. Cancelar un Trabajo (`DELETE /clients/:client_id/records/jobs/cancel/:job_id`)

Este endpoint cancela un trabajo de procesamiento en curso.

### Respuesta Exitosa (200 OK)

```json
{
  "status": "success",
  "message": "Job canceled successfully"
}
```

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "You can't cancel a job with status completed"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Job not found"
}
```

## 26. Eliminar un Trabajo (`DELETE /clients/:client_id/records/jobs/delete/:job_id`)

Este endpoint elimina un trabajo de procesamiento que no está en curso.

### Respuesta Exitosa (200 OK)

```json
{
  "status": "success",
  "message": "Job deleted successfully"
}
```

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Cannot delete a job that is currently processing. Cancel it first."
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Job not found"
}
```

## 27. Reprocesar un Trabajo (`POST /clients/:client_id/records/:record_id/reprocess/job/:job_id`)

Este endpoint crea un nuevo trabajo para reprocesar un registro basado en un trabajo anterior.

### Respuesta Exitosa (200 OK)

```json
{
  "job_id": "job_45678901abcdef0123456789"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Record not found"
}
```

## 28. Establecer Cuota del Cliente (`PUT /clients/:client_id/quota`)

Este endpoint establece una nueva cuota para un cliente.

### Solicitud

```json
{
  "quota": 2000
}
```

### Respuesta Exitosa (200 OK)

```json
{
  "message": 200,
  "success": "Quota updated to 2000"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 29. Aumentar Cuota Utilizada (`POST /clients/:client_id/increase`)

Este endpoint incrementa la cuota utilizada por un cliente.

### Solicitud

```json
{
  "amount": 5
}
```

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Used quota increased by 5"
}
```

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Quota exceeded"
}
```

## 30. Reiniciar Cuota Utilizada (`POST /clients/:client_id/quota/reset`)

Este endpoint reinicia a cero la cuota utilizada por un cliente.

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Used quota reset to 0"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 31. Obtener Información de Cuota (`GET /clients/:client_id/quota`)

Este endpoint obtiene la información actual de cuota de un cliente.

### Respuesta Exitosa (200 OK)

```json
{
  "quota": 1000,
  "used_quota": 42,
  "remaining_quota": 958
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "Client not found"
}
```

## 32. Login de Usuario (`POST /clients/auth/login`)

Este endpoint permite autenticar a un usuario y obtener una clave temporal.

### Solicitud

```json
{
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura"
}
```

### Respuesta Exitosa (200 OK)

```json
{
  "temporal_key": "temp_83f7c9b512345678abcdef0123456789"
}
```

### Respuesta de Error (404 Not Found)

```json
{
  "error": true,
  "message": "User not found"
}
```

### Respuesta de Error (401 Unauthorized)

```json
{
  "error": true,
  "message": "Invalid credentials"
}
```

## 33. Invalidar Token (`GET /clients/auth/invalidate`)

Este endpoint invalida un token temporal.

### Respuesta Exitosa (200 OK)

```json
{
  "message": "Token invalidated successfully"
}
```

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "Only temporary tokens can be invalidated"
}
```

## 34. Crear Usuario (`POST /clients/:client_id/users`)

Este endpoint crea un nuevo usuario para un cliente.

### Solicitud

```json
{
  "email": "nuevo_usuario@ejemplo.com",
  "password": "contraseña_segura",
  "role": "admin",
  "permissions": {
    "all": true
  }
}
```

### Respuesta Exitosa (200 OK)

```json
{
  "id": "u1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "email": "nuevo_usuario@ejemplo.com",
  "client_id": "c1b2a3d4-e5f6-7890-a1b2-c3d4e5f67890",
  "role": "admin",
  "permissions": {
    "all": true
  },
  "created_at": "2025-04-16T13:45:30Z",
  "updated_at": "2025-04-16T13:45:30Z"
}
```

### Respuesta de Error (400 Bad Request)

```json
{
  "error": true,
  "message": "A user already exists with email nuevo_usuario@ejemplo.com"
}
```

### Respuesta de Error (403 Forbidden)

```json
{
  "error": true,
  "message": "Forbidden: Only permanent tokens can create users"
}
```
