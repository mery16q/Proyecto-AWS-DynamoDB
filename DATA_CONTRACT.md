# Contrato de Datos: Catálogo de Libros (DynamoDB)

Este documento define la estructura estricta que deben seguir los datos al ser insertados en la tabla `CatalogoLibros`. Cualquier desviación impedirá que las consultas y los Índices Secundarios (GSI) funcionen correctamente.

### 1. Claves Primarias (La base del diseño)
Todos los ítems deben tener estas dos claves obligatorias:

| Atributo | Significado | Valor esperado |
| :--- | :--- | :--- |
| **PK** | Partition Key | `LIBRO#{ISBN}` (Ej: `LIBRO#978-0123456`) |
| **SK** | Sort Key | `METADATOS` |

---

### 2. Esquema de Atributos por Tipo de Contenido
Dependiendo de si el material es un libro físico, un e-book o un audiolibro, los atributos varían. **Los campos en negrita son obligatorios.**

| Atributo | Libro Físico | E-book | Audiolibro |
| :--- | :--- | :--- | :--- |
| **TipoItem** | `FISICO` | `EBOOK` | `AUDIO` |
| **Autor** | (Obligatorio) | (Obligatorio) | (Obligatorio) |
| **Titulo** | (Obligatorio) | (Obligatorio) | (Obligatorio) |
| Paginas | (Opcional) | - | - |
| Formato | - | (Opcional: PDF/EPUB) | - |
| DuracionMinutos | - | - | (Opcional: 120) |
| Narrador | - | - | (Opcional) |

---

### 3. Ejemplos de Inserción (JSON)

Para insertar los datos, tu código de Python debe preparar el diccionario siguiendo este patrón:

#### Ejemplo: Audiolibro
```json
{
    "PK": "LIBRO#978-0000001",
    "SK": "METADATOS",
    "Autor": "Gabriel García Márquez",
    "Titulo": "Crónica de una muerte anunciada",
    "TipoItem": "AUDIO",
    "DuracionMinutos": 240,
    "Narrador": "Actor Profesional"
}