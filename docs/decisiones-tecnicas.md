# Decisiones técnicas

Justificación de las principales decisiones de diseño tomadas durante el desarrollo.

---

## 1. El Inventario no es una tabla/entidad propia

**Decisión:** El inventario de una empresa es una **consulta sobre `Producto`** filtrada por `empresa_nit`, no una tabla adicional.

**Por qué:** Crear una entidad `Inventario` separada sería redundante — los datos que la formarían (nombre, precio, cantidad) ya existen en `Producto`. Mantener dos copias de la misma información crea riesgo de desincronización y obliga a operaciones de sincronización que añaden complejidad sin valor. El campo `cantidad` en `Producto` cumple exactamente la función de stock del inventario.

---

## 2. "Blockchain" como log de auditoría hash-chain

**Decisión:** La funcionalidad de "blockchain" se implementó como un **log de auditoría encadenado por hashes SHA-256** en PostgreSQL, no como una red blockchain distribuida.

**Por qué:** Una red blockchain real (Ethereum, Hyperledger) requeriría nodos, consenso, wallets y complejidad operacional completamente desproporcionada para una prueba técnica. El principio fundamental de blockchain que tiene valor aquí es la **inmutabilidad verificable**: cada bloque contiene el hash del anterior, por lo que cualquier alteración de un registro histórico se detecta inmediatamente al recalcular la cadena. Este mismo principio se aplica sin necesitar infraestructura distribuida.

---

## 3. Precios en varias monedas: moneda base + tabla de tasas

**Decisión:** Cada producto almacena un `precio_base` con su `moneda_base` (COP, USD, EUR). Las conversiones se calculan en tiempo real usando la tabla `tasas_cambio` en PostgreSQL.

**Por qué:** Almacenar el precio en todas las monedas simultáneamente generaría inconsistencias cuando cambian las tasas. Mantener solo el precio base y convertir en el momento de la consulta garantiza consistencia, y la tabla de tasas permite actualizarlas sin tocar los productos. En producción, un job periódico actualizaría las tasas desde una API externa (ej. `exchangerate-api.com`).

---

## 4. Roles Admin/Externo vía Django Groups

**Decisión:** Los roles se implementan como **grupos de Django** (`Administrador`, `Externo`) en vez de un modelo de usuario custom con campo `rol`.

**Por qué:** Django Groups es el mecanismo oficial del framework para control de acceso basado en roles. Usar la infraestructura existente evita migraciones adicionales, es compatible con el admin de Django, y los permisos se verifican con `user.groups.filter(name=...).exists()` — una sola línea. Un modelo custom añadiría código sin beneficio adicional para este alcance.

---

## 5. Cache en memoria para el agente IA (no Redis)

**Decisión:** Se usa `cachetools.TTLCache` (TTL = 1 hora) en el proceso del microservicio, no Redis.

**Por qué:** Redis requeriría un servicio adicional de infraestructura (instalación, conexión, serialización). Para una prueba técnica donde el servicio corre en una sola instancia, un cache en memoria es suficiente y no añade complejidad operacional. La estrategia de reemplazar `RespuestaCache` por una implementación Redis en producción es trivial: la interfaz (`obtener/guardar`) está aislada en `services/cache.py`. El TTL de 1 hora balancea costo de llamadas a OpenAI con frescura del catálogo de productos.

---

## 6. Generación de PDF desde el backend

**Decisión:** El PDF del inventario se genera en `backend/apps/empresas/pdf.py` con `reportlab` y se devuelve como respuesta binaria. No se genera desde el frontend.

**Por qué:** Generar el PDF desde el frontend (ej. con `jspdf`) expone todos los datos de la empresa al cliente y depende de que el navegador renderice correctamente. Generarlo en el backend permite: (1) controlar el formato exacto del documento, (2) aplicar permisos antes de generar, (3) enviar el mismo PDF por email sin re-generarlo, y (4) no exponer datos sensibles al cliente más allá de lo necesario.
