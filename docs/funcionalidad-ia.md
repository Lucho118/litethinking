# Funcionalidad de IA — Agente conversacional RAG

El microservicio `microservices/ai-agent/` implementa un **agente conversacional** que responde preguntas en lenguaje natural sobre el catálogo de productos usando el patrón **RAG (Retrieval-Augmented Generation)**.

---

## Flujo completo

```
Usuario escribe pregunta
        │
        ▼
[1] Embedding de la pregunta
    text-embedding-3-small → vector de 1536 dimensiones
        │
        ▼
[2] Búsqueda semántica en pgvector
    cosine distance (<=>)  →  TOP 5 productos más similares
    (junto a sus precios convertidos a COP/USD/EUR)
        │
        ▼
[3] Construcción del contexto
    Los 5 productos se formatean como texto estructurado
    incluyendo nombre, características y todos los precios
        │
        ▼
[4] Generación de respuesta (LLM)
    gpt-4o-mini recibe: contexto + pregunta → respuesta en español
        │
        ▼
[5] Respuesta al usuario
    { respuesta: "...", productos_relacionados: [...], from_cache: false }
```

---

## Vectorización de productos

Antes de que el chat funcione, cada producto debe tener su **embedding** (representación numérica semántica). El proceso:

1. Se concatena `nombre + características + empresa_nit` del producto en un texto.
2. Se llama a `text-embedding-3-small` de OpenAI → vector de 1536 floats.
3. El vector se almacena en la columna `embedding` (tipo `vector(1536)` de pgvector).

La vectorización se puede disparar:
- **Manualmente:** `POST /agente/reindexar` o `python scripts/vectorizar_productos.py`
- **Automáticamente:** El signal `post_save` de `ProductoModel` en Django llama al endpoint `/agente/reindexar` en un hilo separado después de cada creación/edición de producto.

---

## Búsqueda semántica con pgvector

La búsqueda utiliza el operador `<=>` de pgvector (distancia coseno) sobre la columna `embedding`:

```sql
SELECT codigo, nombre, ...
FROM   productos
WHERE  embedding IS NOT NULL
ORDER  BY embedding <=> CAST(:emb AS vector)
LIMIT  5
```

Esto permite encontrar productos **semánticamente similares** a la pregunta, aunque no compartan palabras exactas. Por ejemplo, "equipo para trabajar desde casa" encuentra "laptop" sin que la palabra laptop aparezca en la pregunta.

---

## Estrategia de cache

Para reducir costos y latencia en preguntas repetidas:

- **TTL:** 1 hora (`cachetools.TTLCache`)
- **Key:** SHA-256 de la pregunta normalizada (`strip().lower()`)
- **Efecto:** Si dos usuarios preguntan "¿qué laptops tienen?" y "¿Qué laptops tienen?", comparten la misma entrada de cache y solo se hace una llamada a OpenAI.
- **Indicador:** La respuesta incluye `"from_cache": true/false` — visible en el chat de la demo para mostrar la diferencia de velocidad.
- **Registro de consultas:** Aunque la respuesta venga del cache, se registra qué productos fueron devueltos (para el Dashboard: "producto más consultado").

---

## Modelos de OpenAI elegidos

| Modelo | Uso | Por qué |
|---|---|---|
| `text-embedding-3-small` | Vectorización de productos y preguntas | Menor costo que `text-embedding-3-large`, dimensión de 1536 es más que suficiente para búsqueda semántica en catálogos pequeños/medianos |
| `gpt-4o-mini` | Generación de respuestas en lenguaje natural | Excelente relación costo/calidad para respuestas de catálogo; `max_tokens=512` limita el costo por llamada; `temperature=0` garantiza respuestas deterministas y verificables |

---

## Precios multi-moneda en el contexto RAG

El agente siempre incluye precios en todas las monedas disponibles para que el LLM pueda responder preguntas de conversión ("¿cuánto cuesta en USD?") sin hacer cálculos por su cuenta:

```
• [PROD-001] Laptop X1
  Precio: 2500000.00 COP (equivale a: 609.76 USD, 558.06 EUR)
  Empresa (NIT): 830514226-6
```

Las conversiones se calculan en tiempo real desde la tabla `tasas_cambio`, no se hardcodean.
