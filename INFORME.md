# Informe de Análisis Técnico de Arquitectura

## Delivery Platform — Arquitectura Monolítica Modular (DDD)

| Campo | Valor |
|---|---|
| **Proyecto** | Delivery Platform |
| **Versión analizada** | 1.0.0 (`src/main.py:30`) |
| **Arquitectura declarada** | Monolito Modular con Domain-Driven Design |
| **Lenguaje** | Python 3.11 |
| **Framework** | FastAPI (>= 0.100.0) |
| **Persistencia** | SQLAlchemy 2.0 (ORM) + PostgreSQL 15 |
| **Validación** | Pydantic v2 (>= 2.0.0) |
| **Servidor** | Uvicorn (>= 0.22.0) |
| **Orquestación** | Docker / Docker Compose |
| **Total de archivos** | 16 (12 `.py`, 1 `.yml`, 1 Dockerfile, 1 `.txt`, 1 `.sql`, 1 `.env`) |
| **Endpoints expuestos** | 20 |
| **Fecha del análisis** | 27 de septiembre de 2026 |
| **Alcance** | Análisis estático de estructura, código fuente y configuración de despliegue |

---

## 1. Resumen ejecutivo

El sistema analizado es una **API REST de plataforma de delivery** (comida a domicilio) construida sobre FastAPI, organizada como **monolito modular**: un único proceso de aplicación, un único despliegue y una única base de datos, pero con el código de negocio fragmentado en módulos independientes por subdomain.

La estructura de carpetas es **arquitectónicamente correcta** para un monolito modular orientado a DDD. Las decisiones de orquestación de contenedores (healthchecks, dependencias ordenadas, red dedicada) y de versionado de API son acertadas y muestran criterio.

Sin embargo, existe una **brecha significativa entre la arquitectura declarada y la implementada**. El proyecto se denomina DDD, pero **no implementa Domain-Driven Design**: no existe capa de dominio, ni entidades, ni value objects, ni agregados, ni repositorios, ni eventos de dominio. Los cinco archivos `services.py` —que representarían la capa de aplicación— están **completamente vacíos**. En su lugar, la capa de presentación responde directamente con datos hardcodeados.

Adicionalmente se identifican dos defectos con impacto en producción: el uso de `float` para valores monetarios (riesgo de descuadre contable) y un bug de *shadowing* de rutas que hace inalcanzable el endpoint de salud del módulo de pedidos. La persistencia se simula con listas en memoria, por lo que **ningún dato sobrevive a un reinicio**.

**Veredicto:** es un esqueleto arquitectónico sólido y bien documentado, en estado de prototipo. Sirve como cimiento válido, pero no debe desplegarse en producción sin las remediaciones de la Sección 9.

---

## 2. Definición de la arquitectura

### 2.1 Monolito Modular

Un monolito modular es un **único artefacto desplegable** cuyo código interno se divide en módulos con **fronteras explícitas y dependencias dirigidas**. Se diferencia de un monolito clásico ("ball of mud") en que cada módulo encapsula su propio subdominio y expone una interfaz reducida.

| Característica | Monolito clásico | Monolito modular (este proyecto) |
|---|---|---|
| Despliegue | Uno | Uno |
| Base de datos | Compartida sin reglas | Compartida con esquema por módulo |
| Acoplamiento | Alto, disperso | Dirigido, explícito |
| Migración a microservicios | Muy costosa | Costosa pero viable |
| Velocidad de desarrollo | Alta | Alta |

La ventaja estratégica es que los módulos pueden **extraerse a microservicios independientes** en el futuro con bajo costo, porque las fronteras ya están definidas desde el código.

### 2.2 Domain-Driven Design (DDD) y su ausencia

DDD es un enfoque de **modelado de software basado en el lenguaje del dominio de negocio**. Implica una separación estricta en tres capas:

```
┌─────────────────────────────────────────────────────────┐
│  CAPA DE PRESENTACIÓN                                   │
│  Recebe HTTP, valida formato de entrada, serializa      │
│  salida. No contiene lógica de negocio.                 │
│  → Archivos: src/modules/*/router.py                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  CAPA DE APLICACIÓN                                     │
│  Casos de uso: orquesta la capa de dominio, controla    │
│  transacciones, coordina módulos.                       │
│  → Archivos: src/modules/*/services.py                  │
│  ⚠️ ESTADO: VACÍA EN LOS 5 MÓDULOS                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  CAPA DE DOMINIO                                         │
│  Entidades, Value Objects, Agregados, invariantes,      │
│  eventos de dominio, repositorios. Reglas del negocio.   │
│  → Archivos: modules/*/domain/, entities, repositories   │
│  ❌ ESTADO: NO EXISTE                                    │
└─────────────────────────────────────────────────────────┘
```

**Resultado del contraste:**

| Elemento exigido por DDD | ¿Existe? | Observación |
|---|---|---|
| Capa de presentación (HTTP/routers) | ✅ Sí | 5 routers implementados |
| Capa de aplicación (casos de uso) | ❌ No | `services.py` vacíos en los 5 módulos |
| Capa de dominio | ❌ No | Ausente por completo |
| Entidades con comportamiento | ❌ No | Solo Pydantic (structs de transporte) |
| Value Objects | ❌ No | `amount: float` debería ser un VO `Money` |
| Raíces de agregado | ❌ No | Sin invariantes protegidos |
| Repositorios (abstracción) | ❌ No | Acceso directo a BD o a memoria |
| Eventos de dominio | ❌ No | Sin.publish ni outbox |
| Bounded contexts con lenguaje propio | ⚠️ Parcial | Carpetas correctas, lenguaje codificado inconsistente |
| Anti-corruption layers | ❌ No | Módulos no se comunican entre sí |

**Conclusión:** la arquitectura es un **monolito modular correcto pero sin DDD**. El esqueleto de carpetas es el correcto para DDD; el contenido de las capas internas no se implementó.

### 2.3 Capas de la estructura de carpetas

```
deliveryMono/
│
├── [RAÍZ]                 Configuración de despliegue
│   Dockerfile             Imagen de contenedor de la aplicación
│   docker-compose.yml     Orquestación: app + PostgreSQL
│   requirements.txt       Dependencias de Python
│   .env                   Variables de entorno (local)
│   init.sql               Script de inicialización de BD
│
└── src/                   CÓDIGO FUENTE
    ├── main.py            Composition root (raíz de composición)
    │
    ├── core/              NÚCLEO COMPARTIDO / TRANSVERSAL
    │   │                  Servicios técnicos comunes a todos los módulos.
    │   │                  No debe contener reglas de negocio.
    │   ├── config.py      Configuración centralizada (settings)
    │   └── database.py     Engine, Session factory, Base, dependency
    │
    └── modules/           MÓDULOS DE NEGOCIO
        │                  Cada carpeta = un bounded context.
        │                  grieving con reglas propias.
        ├── auth/          Identidad y acceso
        ├── restaurant/    Catálogo de comercios
        ├── order/         Ciclo de vida del pedido
        ├── payment/       Procesamiento de pagos
        └── tracking/      Seguimiento de la entrega
```

La distinción `core/` vs `modules/` es la decisión de diseño más importante del proyecto:

- **`core/`** contiene lo que es **técnico y transversal**: conexión a base de datos, configuración, logging. Ningún módulo debe estar ausente para que un elemento de `core/` tenga sentido.
- **`modules/`** contiene lo que es **de negocio y específico**: cada módulo existiría aunque el sistema fuera de delivery (salvo `order`/`restaurant`/`tracking`).

---

## 3. Inventario de archivos

| # | Ruta | Tipo | Estado | Responsabilidad |
|---|---|---|---|---|
| 1 | `.env` | Configuración | ⚠️ **Vacío (0 B)** | Variables de entorno locales. No se carga en ejecución. |
| 2 | `init.sql` | Script SQL | ⚠️ **Vacío (0 B)** | Script ejecutado en el primer arranque de PostgreSQL para crear el esquema. Sin contenido. |
| 3 | `Dockerfile` | Build | ✅ Implementado | Construye la imagen de la aplicación. |
| 4 | `docker-compose.yml` | Orquestación | ✅ Implementado | Levanta la app y PostgreSQL con sus redes, volúmenes y healthchecks. |
| 5 | `requirements.txt` | Dependencias | ✅ Implementado | Declara 6 dependencias Python. |
| 6 | `src/main.py` | Composition root | ✅ Implementado | Ensambla la aplicación FastAPI y registra los 5 routers. |
| 7 | `src/core/config.py` | Configuración | ❌ **Vacío (0 B)** | Debería centralizar settings tipados. No implementado. |
| 8 | `src/core/database.py` | Infraestructura | ✅ Implementado | Engine SQLAlchemy, session factory, `Base` declarativa y dependency `get_db`. |
| 9 | `src/modules/auth/router.py` | Presentación | ⚠️ Parcial | `POST /login` (mock), `GET /health`. Sin autenticación real. |
| 10 | `src/modules/auth/services.py` | Aplicación | ❌ **Vacío (0 B)** | Lógica de caso de uso de autenticación. No implementada. |
| 11 | `src/modules/restaurant/router.py` | Presentación | ⚠️ Parcial | CRUD de restaurantes con persistencia en memoria. |
| 12 | `src/modules/restaurant/services.py` | Aplicación | ❌ **Vacío (0 B)** | Lógica de negocio de restaurantes. No implementada. |
| 13 | `src/modules/order/router.py` | Presentación | ⚠️ Parcial | Crear y consultar pedidos. Respuestas hardcodeadas. |
| 14 | `src/modules/order/services.py` | Aplicación | ❌ **Vacío (0 B)** | Flujo de ciclo de vida del pedido. No implementado. |
| 15 | `src/modules/payment/router.py` | Presentación | ⚠️ Parcial | `POST /process` (mock). `float` para dinero. |
| 16 | `src/modules/payment/services.py` | Aplicación | ❌ **Vacío (0 B)** | Lógica de transacción. No implementada. |
| 17 | `src/modules/tracking/router.py` | Presentación | ⚠️ Parcial | CRUD de seguimiento + historial por pedido. Persistencia en memoria. |
| 18 | `src/modules/tracking/services.py` | Aplicación | ❌ **Vacío (0 B)** | Lógica de seguimiento. No implementada. |

**Resumen del inventario:**

- 6 archivos con implementación sustancial
- 6 archivos **completamente vacíos** (33% del proyecto)
- 1 archivo con dependencia registrada pero nunca usada (`python-dotenv`)
- 1 archivo con dependencia registrada pero nunca llamada (`load_dotenv` no existe en el código)

---

## 4. Análisis de la capa de composición

### 4.1 `src/main.py` — Raíz de composición

**Concepto:** el *composition root* es el único lugar del sistema donde se instancian y conectan todos los componentes. Su propósito es que ninguna otra clase tenga que conocer el proceso de ensamblaje.

**Líneas 3-10 — Importaciones y ensamblaje**

```python
from src.core.database import Base, engine
from src.modules.auth.router import router as auth_router
from src.modules.order.router import router as order_router
# ...
```

Cada módulo se importa únicamente por su `router`. `main.py` **no conoce los detalles internos** de los módulos: solo sabe que cada uno expone un `APIRouter`. Esto respeta correctamente la encapsulación modular.

**Línea 17 — Creación de tablas (defecto crítico)**

```python
Base.metadata.create_all(bind=engine)
```

| Problema | Consecuencia |
|---|---|
| Se ejecuta en **tiempo de importación** | Cualquier proceso que importe `main` (tests, scripts, CLI) dispara DDL contra la BD. |
| **No hay Alembic ni migraciones** | Sin versionado de esquema, sin historial, sin rollback. |
| **No existe ningún modelo SQLAlchemy** | Búsqueda exhaustiva: 0 declaraciones de `Column`, `mapped_column`, `relationship` o `Mapped` en todo el repositorio. `Base.metadata` está **vacío**, por lo que esta línea crea **cero tablas**. |
| DDL en el arranque | Un fallo de esquema impide que la aplicación levante. |

**Consecuencia real:** la base de datos PostgreSQL que levanta Docker Compose está operativa pero **completamente sin esquema**. Ningún endpoint escribe en ella.

**Líneas 24-31 — Instancia de FastAPI**

```python
app = FastAPI(
    title="Delivery Platform - Monolito Modular",
    description="Arquitectura monolítica modular basada en DDD para un sistema de Delivery",
    version="1.0.0",
)
```

Los metadatos alimentan la documentación OpenAPI interactiva en `/docs` (Swagger UI) y `/redoc`.

**Líneas 38-66 — Registro de routers**

```python
app.include_router(auth_router,       prefix="/api/v1/auth",        tags=["AuthModule"])
app.include_router(restaurant_router, prefix="/api/v1/restaurants", tags=["RestaurantModule"])
app.include_router(order_router,      prefix="/api/v1/orders",     tags=["OrderModule"])
app.include_router(payment_router,    prefix="/api/v1/payments",   tags=["PaymentModule"])
app.include_router(tracking_router,   prefix="/api/v1/tracking",   tags=["TrackingModule"])
```

Decisiones positivas:

- **Versionado en la URL** (`/api/v1`): permite evolucionar la API manteniendo compatibilidad hacia atrás con clientes existentes.
- **Prefijos por módulo**: cada módulo es dueño de su espacio de URLs, lo que refuerza la frontera modular y evita colisiones.
- **Tags por módulo**: en Swagger UI cada módulo aparece como una sección independiente, lo que hace visible la estructura modular desde el exterior.

**Líneas 73-86 — Endpoints de sistema**

```python
@app.get("/")
def root():
    return {"status": "OK", "message": "Servidor Monolítico Modular de Delivery activo"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "delivery-platform"}
```

Ambos cumplen funciones distintas:

- `GET /` — comprobación de vida para humans (verificar que el proceso responde).
- `GET /health` — **probe de salud para orquestadores**. Es el endpoint que un *load balancer* o Kubernetes usaría para decidir si enruta tráfico al contenedor.

⚠️ **Observación:** `health_check` no verifica la conectividad con PostgreSQL. Un health check que no comprueba la dependencia crítica reporta "healthy" con la base de datos caída. Debería ejecutar un `SELECT 1`.

---

## 5. Análisis de la capa núcleo (`core/`)

### 5.1 `src/core/database.py` — Infraestructura de persistencia

Archivo completo (16 líneas), satuado de responsabilidades de infraestructura.

| Línea(s) | Código | Análisis |
|---|---|---|
| 1-3 | Imports de `os`, `create_engine`, `sessionmaker`, `declarative_base` | Dependencias mínimas y correctas. |
| 5 | `DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://delivery_user:delivery_password@localhost:5432/delivery_db")` | Lee la variable de entorno con **fallback hardcodeado** a credenciales reales. En desarrollo funciona; en producción, un `DATABASE_URL` mal definido apuntaría silenciosamente a `localhost`. |
| 7 | `engine = create_engine(DATABASE_URL)` | Crea el *engine* con el *connection pool* por defecto de SQLAlchemy (5 conexiones, 30 s de timeout). Sin `pool_pre_ping`, sin `pool_recycle`. |
| 8 | `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)` | **Configuración correcta.** `autocommit=False` delega el control transaccional al código; `autoflush=False` evita consultas inesperadas a mitad de una transacción. |
| 9 | `Base = declarative_base()` | ⚠️ **API deprecada en SQLAlchemy 2.0.** El estilo moderno es una clase `DeclarativeBase` con `Mapped[]` y `mapped_column()`. |
| 11-16 | `get_db()` — generador con `yield` y `finally` | ✅ **Implementación correcta del patrón de dependency injection.** |

#### Análisis de `get_db()` (líneas 11-16)

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

| Aspecto | Evaluación |
|---|---|
| Creación de sesión por petición | ✅ Cada request obtiene su propia sesión: aislamiento correcto. |
| `try/finally` | ✅ Garantiza el cierre incluso ante excepción. Sin esto, las sesiones se filtrarían y agotarían el pool bajo carga. |
| Cierre vs. `commit`/`rollback` | ⚠️ Cierra correctamente, pero **no hace rollback ante excepción**. La sesión se cierra y la transacción se descarta implícitamente, lo que funciona, pero un `except: db.rollback()` explícito sería más claro. |
| Inyección en routers | ⚠️ Solo `order` y `payment` la usan, y **ninguno usa la sesión** (ver Sección 6.3 y 6.4). |

**Veredicto:** el patrón es correcto y bien construido, pero **está infrautilizado**: la base de datos existe y funciona, pero la aplicación no la consulta.

### 5.2 `src/core/config.py` — Configuración centralizada

**Archivo vacío (0 bytes).**

La existencia de este archivo revela una **intención arquitectónica correcta**: centralizar la configuración en un único punto en lugar de leer variables de entorno dispersas por el código. Sin embargo, la intención no se materializó.

Consecuencias:

- `os.getenv()` se llama directamente en `database.py:5` en lugar de pasar por una capa de settings.
- La variable `APP_ENV: development` definida en `docker-compose.yml:48` **es leída por nadie**. Está muerta.
- No hay tipado, ni validación, ni valores por defecto centralizados, ni soporte a múltiples entornos (dev/staging/prod).

**Implementación recomendada:** una clase de settings con Pydantic, que valide la configuración al arrancar y falle rápido si falta un valor obligatorio.

---

## 6. Análisis de los módulos de negocio

### 6.0 Convenciones comunes

Los cinco módulos siguen una convención consistente, lo que evidencia que la estructura fue diseñada deliberadamente:

1. Declaran `router = APIRouter()`.
2. Definen los schemas Pydantic al inicio del archivo.
3. Separan las secciones con bloques de comentario (`# ===`).
4. Incluyen un endpoint `GET /health` por módulo (presente en 4 de 5).

Todos usan `from fastapi import APIRouter` y `from pydantic import BaseModel`. Ningún router contiene lógica de negocio real.

### 6.1 Módulo `auth` — Identidad y acceso

**Bounded context:**_users, credenciales, sesiones, roles.

| Método | Ruta completa | Descripción |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Autenticación de usuario |
| `GET` | `/api/v1/auth/health` | Health check del módulo |

**Schemas:** `LoginRequest` (`router.py:12`) con `email: str` y `password: str`.

**Análisis:**

| Aspecto | Evaluación |
|---|---|
| Validación de entrada | ✅ Pydantic rechaza cuerpos malformados automáticamente (422). |
| Flujo de autenticación | ❌ Devuelve `"token": "demo-token"` literal. No hay verificación de credenciales. |
| Almacenamiento de contraseñas | ❌ No hay hashing. El schema acepta el password en texto plano y nunca se persiste. |
| Emisión de tokens | ❌ Sin JWT. `python-jose` / `PyJWT` no están en `requirements.txt`. |
| Autorización | ❌ No existe. No hay roles niScopes. |
| Bounded context completo | ❌ No hay sub-dominio de usuarios, roles o perfiles. `auth` cubre solo el login. |
| Health check | ✅ Implementado y alcanzable (`/login` y `/health` no colisionan). |

**Violación crítica de seguridad:** el sistema acepta cualquier email y cualquier contraseña, y devuelve un token ficticio. Cualquier cliente que presente ese token puede acceder a cualquier endpoint sin restricción.

### 6.2 Módulo `restaurant` — Catálogo de comercios

**Bounded context:** restaurantes, direcciones, disponibilidad.

| Método | Ruta completa | Descripción | Código |
|---|---|---|---|
| `POST` | `/api/v1/restaurants/` | Crear restaurante | `router.py:37` |
| `GET` | `/api/v1/restaurants/` | Listar restaurantes | `router.py:59` |
| `GET` | `/api/v1/restaurants/{restaurant_id}` | Obtener por ID | `router.py:68` |
| `PUT` | `/api/v1/restaurants/{restaurant_id}` | Actualizar | `router.py:85` |
| `DELETE` | `/api/v1/restaurants/{restaurant_id}` | Eliminar | `router.py:116` |

Es el **módulo más completo** de los cinco. Presenta un CRUD completo y bien construido.

**Schemas:**

```python
class RestaurantCreate(BaseModel):     # Entrada
    name: str
    address: str
    phone: str | None = None
    is_open: bool = True

class Restaurant(RestaurantCreate):     # Salida (hereda y añade id)
    id: int
```

| Decisión | Evaluación |
|---|---|
| Separar schema de entrada y de salida | ✅ **Correcto.** Evita que el cliente pueda enviar un `id` al crear. Es el patrón Command/Resource. |
| `phone: str | None = None` | ✅ Correcto: un campo opcional con valor por defecto, en un modelo Pydantic v2. |
| Herencia entre schemas | ⚠️ Aceptable aquí por ser trivial, pero puede gerar acoplamiento si `Restaurant` crece. |
| `response_model` en todos los endpoints | ✅ **Buena práctica.** Valida la salida y documenta el contrato en OpenAPI. |
| `status_code=201` en creación | ✅ Semántica HTTP correcta. |
| Manejo de 404 | ✅ `HTTPException(404, detail="Restaurant not found")` explícito en los tres endpoints que lo requieren. |

**Defecto crítico — persistencia en memoria:**

```python
restaurants: List[Restaurant] = []      # router.py:28
_next_id = 1                            # router.py:30
```

| Problema | Impacto |
|---|---|
| Lista a nivel de módulo | Es un **singleton en memoria del proceso**. Los datos se pierden en cada reinicio. |
| Sin `Depends(get_db)` | El módulo **no toca la base de datos**, pese a que la infraestructura existe. |
| No thread-safe | Bajo concurrencia (async, múltiples hilos), `append` y `global _next_id` pueden producir condiciones de carrera e IDs duplicados. |
| SinInvalidación | Con varios workers de Uvicorn, cada proceso tendría su propia lista: datos inconsistentes entre réplicas. |

**Práctica almacenada (plausible como sustituto):** el módulo **no expone `GET /health`**, siendo el único de los cinco sin health check propio. Esto rompe la consistencia del patrón.

**Complejidad algorítmica:** todos los accesos son **O(n)**, con recorrido lineal buscando el ID. Aceptable para una lista en memoria; sería inviable contra una base de datos real (donde corresponde un `SELECT ... WHERE id = ?` con índice).

### 6.3 Módulo `order` — Ciclo de vida del pedido

**Bounded context:** pedidos, estados, ítems, asignación.

| Método | Ruta completa | Descripción | Código |
|---|---|---|---|
| `POST` | `/api/v1/orders/` | Crear pedido | `router.py:25` |
| `GET` | `/api/v1/orders/{order_id}` | Obtener pedido | `router.py:44` |
| `GET` | `/api/v1/orders/health` | Health check | `router.py:63` |

**Schemas:** `OrderCreate` (`router.py:15`) con `customer_id: int`, `restaurant_id: int`, `items: list[str]`.

**Análisis:**

| Aspecto | Evaluación |
|---|---|
| Validación de entrada | ✅ Pydantic. |
| Persistencia real | ❌ Devuelve `"order_id": "ORD-12345"` fijo. Ninguna escritura a BD. |
| Estados del pedido | ⚠️ `PENDING` e `IN_PREPARATION` son strings literales, sin validación. Deberían ser un **enum** o un value object `OrderStatus` con transiciones válidas. |
| Tipo de `items` | ⚠️ `list[str]` (nombres de texto libre) en lugar de `list[OrderItem]` con `product_id` y `quantity`. Impide calcular totales. |
| `Depends(get_db)` | ❌ **Dependencia muerta.** Inyectada en `router.py:28` y `router.py:47`, la sesión `db` **nunca se usa**. Abre una conexión al pool que se descarta. |
| `response_model` | ❌ Ausente. El contrato de salida no está definido ni documentado. |

#### 🔴 Defecto crítico — *Shadowing* de rutas

Este es un bug real y verificable:

```python
router.py:44    @router.get("/{order_id}")
router.py:47    def get_order(order_id: str, ...)   ← declarado PRIMERO

router.py:63    @router.get("/health")
router.py:64    def order_health():                 ← declarado DESPUÉS
```

**FastAPI evalúa las rutas en orden de declaración.** Como `/{order_id}` se registra antes que `/health` y su parámetro está tipado como `str` (que acepta cualquier texto), la petición:

```
GET /api/v1/orders/health
```

**nunca alcanza `order_health`**. En su lugar, ejecuta `get_order` con `order_id="health"`, devolviendo:

```json
{ "order_id": "health", "status": "IN_PREPARATION", "items": ["Hamburguesa", "Papas"] }
```

**Impacto:**
- El health check del módulo es **inalcanzable**.
- Un monitor de orquestación que sondee este endpoint recibirá `200 OK` con datos falsos, creyendo que el módulo está sano cuando en realidad no responde.
- Cualquier ruta estática futura bajo `/api/v1/orders/` sufrirá el mismo problema.

**Contrasta con el módulo `tracking`**, donde el mismo patrón de ruta variable + ruta estática **no** produce el bug porque están en segmentos distintos (`/tracking/order/5` tiene 2 segmentos, `/{tracking_id}` tiene 1). Esto confirma que la causa es puramente el **orden de declaración**.

**Corrección:** declarar `GET /health` **antes** de `GET /{order_id}`.

### 6.4 Módulo `payment` — Procesamiento de pagos

**Bounded context:** transacciones, métodos de pago, reembolsos, conciliación.

| Método | Ruta completa | Descripción | Código |
|---|---|---|---|
| `POST` | `/api/v1/payments/process` | Procesar pago | `router.py:25` |
| `GET` | `/api/v1/payments/health` | Health check | `router.py:43` |

**Schemas:** `PaymentRequest` (`router.py:15`) con `order_id: str`, `amount: float = Field(gt=0)`, `payment_method: str`.

#### ✅ Decisión positiva — validación con `Field(gt=0)`

Es el **único uso de reglas de validación de negocio** en todo el proyecto:

```python
amount: float = Field(gt=0)
```

Un monto de `0`, `-1` o `-500.00` será **rechazado con 422** antes de alcanzar la lógica del handler. Este es el uso correcto de Pydantic v2 para expresar una invariante del dominio directamente en el contrato de entrada.

#### 🔴 Defecto crítico — `float` para valores monetarios

```python
amount: float = Field(gt=0)     # router.py:17
```

Usar punto flotante IEEE-754 para dinero es un **error de modelado de dominio**, no un detalle menor:

| Problema | Ejemplo |
|---|---|
| Los decimales no tienen representación exacta en binario | `0.1 + 0.2 == 0.30000000000000004` |
| Acumulación de error por sumas repetidas | Un total de 100 líneas a `0.07` no cuadra |
| Riesgo de descuadre contable | El total cobrado ≠ total debido |
| `Field(gt=0)` no detecta este problema | Valida el signo, no la exactitud |

**Impacto en un sistema de delivery real:** discrepancias en los cobros a clientes, comisiones de repartidor incorrectas, y fallos en la conciliación bancaria.

**Corrección:** representar el dinero como un **value object `Money`**, no como un primitivo:

- Python: `Decimal` (nunca `float`).
- Persistencia: `NUMERIC(12,2)` en PostgreSQL.
- Regla DDD: el dinero tiene unidades y precisión distintas según la moneda; un float no puede expresar eso.

**Otros aspectos del módulo:**

| Aspecto | Evaluación |
|---|---|
| Persistencia | ❌ Devuelve `"transaction_id": "TXN-998877"` y `"status": "APPROVED"` fijos. |
| Integración con pasarela | ❌ Ninguna. Sin Stripe, PayPal ni similar. |
| Idempotencia | ❌ Crítico ausente. Un reintento de `POST /process` desde el cliente generaría un cobro duplicado. Un sistema de pagos **debe** ser idempotente (clave de idempotencia + restricción de unicidad). |
| `Depends(get_db)` | ❌ Dependencia muerta, igual que en `order`. |
| Estado `APPROVED` fijo | 🔴 Nunca se rechazan pagos. No hay manejo de declined, insufficient funds ni timeout. |

### 6.5 Módulo `tracking` — Seguimiento de la entrega

**Bounded context:** ubicación del repartidor, hitos de entrega, historial de estados.

| Método | Ruta completa | Descripción | Código |
|---|---|---|---|
| `POST` | `/api/v1/tracking/` | Crear registro de tracking | `router.py:36` |
| `GET` | `/api/v1/tracking/` | Listar todos los registros | `router.py:58` |
| `GET` | `/api/v1/tracking/{tracking_id}` | Obtener por ID | `router.py:67` |
| `GET` | `/api/v1/tracking/order/{order_id}` | Historial de un pedido | `router.py:85` |
| `PUT` | `/api/v1/tracking/{tracking_id}` | Actualizar estado | `router.py:101` |
| `DELETE` | `/api/v1/tracking/{tracking_id}` | Eliminar registro | `router.py:132` |

Es el módulo con **más endpoints** (6) y cubre un CRUD completo más una consulta especializada.

**Análisis del endpoint destacado — historial por pedido:**

```python
@router.get("/order/{order_id}", response_model=List[Tracking])
def get_order_tracking(order_id: int):
    records = [
        tracking for tracking in tracking_records
        if tracking.order_id == order_id
    ]
    return records
```

| Aspecto | Evaluación |
|---|---|
| Orden de declaración | ✅ **Correcto.** `/{tracking_id}` (línea 67) se declara antes que `/order/{order_id}` (línea 85), pero **no hay conflicto**: `/order/5` tiene 2 segmentos y solo puede coincidir con la ruta de 2 segmentos. Este módulo resuelve correctamente el problema que `order` sufre. |
| Filtrado | ✅ Devuelve solo los registros del pedido solicitado. |
| `response_model=List[Tracking]` | ✅ Contrato tipado. |
| Complejidad | ⚠️ O(n) sobre la lista completa. A escala, correspondería un índice sobre `order_id` + `WHERE`. |

**Defectos:**

| Problema | Ubicación | Detalle |
|---|---|---|
| Persistencia en memoria | `router.py:27` | `tracking_records: List[Tracking] = []`. Mismo defecto que `restaurant`: datos volátiles, no thread-safe, no compartidos entre workers. |
| Sin `Depends(get_db)` | — | El módulo no usa la base de datos. |
| **Contrato de datos inconsistente** | `router.py:14` vs `order/router.py:16` | `TrackingCreate.order_id: int` pero `OrderCreate` no declara `order_id` y `PaymentRequest.order_id: str`. **El mismo identificador de pedido es `int` en un módulo y `str` en otro.** Viola la consistencia del modelo de dominio compartido. |
| Sin validación de estado | `router.py:15` | `status: str` acepta cualquier texto (`"inventado"`, `"foo"`). Debería ser un enum. |
| `location: str \| None` | `router.py:16` | Para tracking geográfico se esperaría latitud/longitud numéricas, no un string. |

**Ausencia conceptual relevante:** el módulo `tracking` modela *hitos* discretos del envío, pero no hay **integración con un proveedor de mapas** ni actualización de posición del repartidor en tiempo real, que es la función central de este dominio.

### 6.6 Análisis transversal de módulos

#### Tabla resumen de módulos

| Módulo | Endpoints | Persistencia real | DB utilizada | `response_model` | Health check | Auth |
|---|---|---|---|---|---|---|
| `auth` | 2 | ❌ No | No | ❌ No | ✅ Sí | N/A |
| `restaurant` | 5 | ❌ Memoria | No | ✅ Sí | ❌ **No** | N/A |
| `order` | 3 | ❌ No | No (inyectada sin uso) | ❌ No | ⚠️ **Inalcanzable** | N/A |
| `payment` | 2 | ❌ No | No (inyectada sin uso) | ❌ No | ✅ Sí | N/A |
| `tracking` | 6 | ❌ Memoria | No | ✅ Sí | ✅ Sí | N/A |
| **Sistema** | 2 | N/A | No | ❌ No | ✅ Sí | N/A |
| **TOTAL** | **20** | | | | | |

#### Ausencia de colaboración entre módulos

El hallazgo más relevante a nivel de arquitectura es que **los módulos no se comunican entre sí**. En una plataforma de delivery real, el flujo es:

```
Cliente pide  →  order  necesita validar el restaurante (restaurant)
                        →  order calcula el total
                        →  order dispara el cobro (payment)
                        →  order inicia el seguimiento (tracking)
```

En esta implementación, cada módulo es una **isla aislada** con respuestas hardcodeadas. `order` no consulta `restaurant`, no invoca `payment` y no crea registros en `tracking`. El sistema no implementa ningún proceso de negocio end-to-end.

Esto significa que:
- No existe **acoplamiento dirigido** (ni desirable ni observable).
- No hay **integración entre bounded contexts**.
- No hay **eventos de dominio** que coordinen los módulos.
- La modularidad es puramente **estructural de carpetas**, no conductual.

---

## 7. Infraestructura y despliegue

### 7.1 `docker-compose.yml` — Orquestación

Define **dos servicios** en una red bridge privada `delivery-network`.

#### Servicio 1: `postgres-db`

| Propiedad | Valor | Evaluación |
|---|---|---|
| Imagen | `postgres:15-alpine` | ✅ Versión fijada (reproducible) y variante Alpine (de menor tamaño). |
| `container_name` | `delivery-monolith-db` | Nomenclatura consistente. |
| `restart` | `unless-stopped` | ✅ Reinicio automático ante caída. |
| Credenciales | `delivery_user` / `delivery_password` en texto plano | 🔴 **Fallo de seguridad.** |
| Puertos | `5432:5432` | ⚠️ Expuesto al host; en producción debería restringirse. |
| Volumen nombrado | `postgres_data:/var/lib/postgresql/data` | ✅ **Persistencia de datos** entre reinicios. Correcto: no usar un bind mount del sistema de archivos del host. |
| Bind mount | `./init.sql:/docker-entrypoint-initdb.d/init.sql:ro` | Script de arranque del contenedor, montado en solo lectura. **Pero el archivo está vacío.** |
| Healthcheck | `pg_isready -U delivery_user -d delivery_db` cada 5 s, 10 reintentos, 10 s de inicio | ✅ **Excelente práctica.** |
| Red | `delivery-network` | ✅ Aislamiento de red. |

**Excelencia particular del healthcheck + `depends_on`:**

```yaml
delivery-app:
  depends_on:
    postgres-db:
      condition: service_healthy
```

Este patrón garantiza que el contenedor de la aplicación **no se inicia hasta que PostgreSQL responde correctamente a `pg_isready`**. Sin él, la aplicación arrancaría, fallaría al conectar y, dependiendo de la política de reinicio, podría entrar en un ciclo de fallos. Es una de las buenas prácticas más recomendadas en orquestación de contenedores y está correctamente implementada.

**Sobre `init.sql`:** PostgreSQL ejecuta los scripts de `/docker-entrypoint-initdb.d/` **únicamente en el primer arranque** (cuando el volumen de datos está vacío). Al estar el archivo vacío, **no se crea ningún esquema, usuario ni tabla**. Además, como `init.sql` está vacío pero montado, cualquier esquema que existiera en él tampoco se aplicaría.

#### Servicio 2: `delivery-app`

| Propiedad | Valor | Evaluación |
|---|---|---|
| Build | Contexto `.`, `Dockerfile` | Construcción local reproducible. |
| Puertos | `8000:8000` | Expone la API. |
| `DATABASE_URL` | Apunta al host `postgres-db` | ✅ **Correcto**: usa el nombre del servicio de Compose para la resolución DNS interna. |
| `APP_ENV` | `development` | ⚠️ **Declarada y nunca leída** (consecuencia de `config.py` vacío). |
| `PYTHONUNBUFFERED` | `"1"` | ✅ Logs sin buffer, aparece en `docker logs` en tiempo real. |
| Volumen | `./src:/app/src` | ⚠️ Monta el código fuente sobre la imagen, habilitando hot-reload en desarrollo. En producción **deshabilitaría la imagen** ya que el código vendría del host. |
| `depends_on` | `condition: service_healthy` | ✅ Ver arriba. |
| Red | `delivery-network` | ✅ Comunicación interna por nombre de servicio. |

#### Recursos de Docker Compose

```yaml
networks:
  delivery-network:
    driver: bridge

volumes:
  postgres_data:
```

Ambos correctamente declarados. `postgres_data` se crea automáticamente en el primer `up`.

#### Flujo de arranque resultante

```
docker compose up
        │
        ├─→ [1] Arranca postgres-db
        │      ├─ Inicializa volumen postgres_data
        │      ├─ Ejecuta /docker-entrypoint-initdb.d/init.sql  (VACÍO → nada)
        │      └─ pg_isready OK
        │
        └─→ [2] Arranca delivery-app  (solo cuando [1] está healthy)
               ├─ Copia requirements.txt → pip install
               ├─ COPY ./src ./src
               ├─ Monta volumen ./src:/app/src
               ├─ Base.metadata.create_all()  → 0 tablas (no hay modelos)
               └─ Uvicorn en 0.0.0.0:8000
```

### 7.2 `Dockerfile` — Imagen de contenedor

| Línea(s) | Instrucción | Evaluación |
|---|---|---|
| 2 | `FROM python:3.11-slim` | ✅ Versión exacta (no `latest`), variante slim. |
| 5 | `ENV PYTHONDONTWRITEBYTECODE=1` | ✅ Evita archivos `.pyc`, reduce tamaño de imagen. |
| 6 | `ENV PYTHONUNBUFFERED=1` | ✅ Salida de logs sin buffer. |
| 9 | `WORKDIR /app` | Directorio de trabajo explícito. |
| 12-15 | `apt-get install build-essential libpq-dev` | ⚠️ `build-essential` solo es necesario para **compilar** driver. Con `psycopg2-binary` (wheels precompilados) es peso innecesario en la imagen final. |
| 15 | `rm -rf /var/lib/apt/lists/*` | ✅ Buena higiene: limpia caché de paquetes. |
| 18-19 | `COPY requirements.txt` → `pip install --no-cache-dir` | ✅ **Optimización correcta de la caché de Docker:** al copiar primero solo los requisitos, la capa de dependencias se reutiliza mientras el código cambie. |
| 22 | `COPY ./src ./src` | Copia el código. ⚠️ Invalida la capa en cada cambio de código. |
| 25 | `EXPOSE 8000` | Documenta el puerto. |
| 28 | `CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]` | 🔴 **Defecto de producción.** |

#### 🔴 Defecto — `--reload` en la imagen de contenedor

`--reload` activa el **watchdog de Uvicorn**, que:

| Impacto | Detalle |
|---|---|
| Rendimiento | Añade un proceso supervisor y un hilo de monitoreo de archivos. Consumo de CPU y memoria constante. |
| Seguridad | Un escaneo de archivos en caliente puede responder en segundos con código no válido. |
| Intención | Está pensado para **desarrollo con recarga en caliente**. |
| Contexto | Aquí se combina con el volumen `./src:/app/src` de `docker-compose.yml:52`, lo que sugiere intención de desarrollo. Pero si esta imagen se despliega en otro entorno **sin quitar el flag**, el comportamiento sería incorrecto. |

**Corrección recomendada:** usar una etapa de build separada o un flag por entorno, de modo que `--reload` solo se aplique a desarrollo.

#### Otras ausencias del Dockerfile

- Sin usuario no-root: el proceso corre como **root** dentro del contenedor.
- Sin `.dockerignore`: el contexto de build envía `.env`, `__pycache__` y el `.git` completo al daemon.
- Sin `HEALTHCHECK`: existe en Compose para PostgreSQL, pero no para la aplicación.

### 7.3 `requirements.txt` — Dependencias

```
fastapi>=0.100.0
uvicorn[standard]>=0.22.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.6
pydantic>=2.0.0
python-dotenv>=1.0.0
```

| Dependencia | Función | Uso real en el código |
|---|---|---|
| `fastapi` | Framework web / routing / DI | ✅ Amplio |
| `uvicorn[standard]` | Servidor ASGI | ✅ En el `CMD` del Dockerfile |
| `sqlalchemy` | ORM y motor de base de datos | ⚠️ Solo en `database.py`; **ningún modelo definido** |
| `psycopg2-binary` | Driver PostgreSQL | ⚠️ Registrado, nunca se establece una conexión real |
| `pydantic` | Validación y schemas | ✅ Amplio (todos los routers) |
| `python-dotenv` | Carga de `.env` | ❌ **Nunca se usa** — `load_dotenv()` no aparece en el código |

**Observaciones:**

- Las 6 dependencias son **mínimas y pertinentes**: no hay dependencias innecesarias.
- ⚠️ **Versiones con `>=` en lugar de `==` o `~=`**: las builds **no son reproducibles**. Una actualización mayor de FastAPI o Pydantic en el futuro puede romper la aplicación sin previo aviso. Para un proyecto con DDD y versionado `/v1`, conviene fijar versiones o usar un lock file.
- ❌ **Faltan dependencias necesarias** para completar la arquitectura: Alembic (migraciones), PyJWT + passlib/bcrypt (auth), y Decimal no requiere dependencia pero sí el driver de pasarela de pagos.

### 7.4 `.env` y `init.sql` — Archivos inertes

| Archivo | Estado | Problema |
|---|---|---|
| `.env` | 0 bytes | Existe pero `python-dotenv` nunca se invoca, así que **nunca se lee**. Además, las credenciales están hardcodeadas en `docker-compose.yml`, no aquí — que es exactamente lo contrario de la práctica recomendada. |
| `init.sql` | 0 bytes | Se monta en PostgreSQL pero está vacío. Se ejecuta en cada arranque y no hace nada. |

Ambos representan **intención no materializada** de separación de configuración y de inicialización de esquema.

---

## 8. Diagramas y flujos

### 8.1 Flujo de una petición HTTP

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENTE (app móvil / web)              │
└────────────────────────────┬─────────────────────────────┘
                             │  HTTP/1.1
                             ▼
┌──────────────────────────────────────────────────────────┐
│  CAPA 1 · TRANSPORTE                                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Uvicorn (0.0.0.0:8000)                            │  │
│  │  Dockerfile:28                                      │  │
│  └───────────────────────┬────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────┐
│  CAPA 2 · COMPOSICIÓN                                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │  src/main.py                                       │  │
│  │  · find app = FastAPI()          (línea 24)        │  │
│  │  · include_router(prefix=/api/v1/*)  (líneas 38-66) │  │
│  │  · Base.metadata.create_all()     (línea 17) ⚠️ 0 tablas│
│  └───────────────────────┬────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────┐
│  CAPA 3 · PRESENTACIÓN  (por módulo)                      │
│  ┌────────────────────────────────────────────────────┐  │
│  │  modules/<nombre>/router.py                       │  │
│  │                                                    │  │
│  │  1. Pydantic valida el cuerpo de entrada  ✅        │  │
│  │  2. Resolver Depends(get_db)  → core/database.py  │  │
│  │  3. Ejecutar handler                              │  │
│  │  4. Validar salida con response_model (parcial)   │  │
│  └───────────────────────┬────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────┘
                           ▼
                  ╔════════════════════════╗
                  ║  CAPA 4 · APLICACIÓN    ║
                  ║  services.py            ║
                  ║                        ║
                  ║   ⚠️ ARCHIVO VACÍO      ║
                  ║   Cadena rota aquí     ║
                  ╚═══════════════════════╝╝
                           ▼
                  ╔════════════════════════╗
                  ║  CAPA 5 · DOMINIO      ║
                  ║                        ║
                  ║   ❌ NO EXISTE         ║
                  ╚═══════════════════════╝╝
                           ▼
┌──────────────────────────────────────────────────────────┐
│  CAPA 6 · INFRAESTRUCTURA                                │
│  ┌────────────────────────────────────────────────────┐  │
│  │  src/core/database.py                             │  │
│  │  · get_db() genera sesión  (líneas 11-16)  ✅      │  │
│  │  · PostgreSQL 15 (contenedor)                     │  │
│  │      → ⚠️ NUNCA ALCANZADO: la sesión se inyecta    │  │
│  │        pero no se ejecuta ninguna consulta        │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**Lectura del diagrama:** las capas 1, 2, 3 y 6 están construidas y funcionan. **La cadena se rompe en la capa 4**: al no existir `services.py` con contenido, el flujo salta directamente de la capa de presentación a un literal de diccionario, y la capa 6 nunca se consume. La base de datos es un recurso conectado pero ocioso.

### 8.2 Mapa de módulos y sus dependencias

```
                         ┌──────────────┐
                         │     core/    │
                         │  database.py │
                         │  config.py   │
                         └──────┬───────┘
                                │
        ┌───────────┬───────────┼───────────┬───────────┐
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
   ┌─────────┐ ┌──────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐
   │  auth   │ │restaurant│ │ order  │ │ payment │ │tracking │
   └─────────┘ └──────────┘ └────────┘ └─────────┘ └─────────┘
        │           │           │           │           │
        │           │           │           │           │
        └───────────┴───────────┴───────────┴───────────┘
                                │
                    ✗ SIN NINGUNA CONEXIÓN
                    Los módulos no se invocan entre sí
```

Observaciones:
- Los cinco módulos dependen de `core/` (**dependencia dirigida unidireccional hacia la infraestructura compartida**). Esto es correcto: la infraestructura no depende del negocio.
- **No existe ninguna arista entre módulos.** En una arquitectura DDD madura existirían dependencias de collaboration (como las que definen los *context maps* de Strangler Fig), o mejor aún, comunicación por eventos de dominio.
- La ausencia de dependencias entre módulos evita hoy el acoplamiento, pero también significa que **no hay lógica de negocio compuesta**: el sistema no resuelve ningún caso de uso de principio a fin.

### 8.3 Flujo de un caso de uso real vs. implementado

**Flujo real esperado — "Cliente realiza un pedido":**

```
   [order]  Crear pedido
      │
      ├─→ [restaurant]  Verificar que existe y está abierto
      ├─→ [order]       Validar disponibilidad de items
      ├─→ [order]       Calcular total
      ├─→ [payment]     Procesar cobro
      │      └─→ pasarela de pago externa
      ├─→ [order]       Persistir pedido (estado PENDING → PAID)
      └─→ [tracking]    Crear registro de seguimiento inicial
```

**Flujo implementado actualmente:**

```
   [order]  POST /api/v1/orders/
      │
      └─→ db = get_db()          ← abre sesión (nunca se usa)
      └─→ return {...}           ← diccionario literal
```

El módulo devuelve un `order_id` fijo y nada más. No hay consulta al restaurante, ni cobro, ni persistencia, ni evento de seguimiento. **El caso de uso no está implementado.**

---

## 9. Análisis de hallazgos

### 9.1 Fortalezas

| # | Fortaleza | Justificación arquitectónica |
|---|---|---|
| 1 | **Separación clara `core/` vs `modules/`** | Distingue explícitamente lo transversal de lo de negocio. Es la decisión de diseño más acertada del proyecto y define una frontera clara de responsabilidades. |
| 2 | **Composición externalizada en `main.py`** | Los módulos no se importan entre sí; solo `main.py` conoce a todos. Esto mantiene el acoplamiento nulo y facilita la extracción futura a microservicios. |
| 3 | **Versionado de API en la URL** (`/api/v1`) | Permite evolucionar el contrato sin romper clientes. Es práctica estándar en APIs REST de producción. |
| 4 | **Tags por módulo en OpenAPI** | La estructura modular es **visible desde el exterior** (Swagger UI agrupa por módulo). Facilita el descubrimiento y la documentación. |
| 5 | **Patrón `get_db()` con `yield`/`finally`** | Implementación correcta de dependency injection con alcance por petición y liberación garantizada de recursos. |
| 6 | **`depends_on: condition: service_healthy`** | Control de dependencias robusto: la aplicación no arranca hasta que PostgreSQL está verificado como listo. |
| 7 | **Volumen nombrado para PostgreSQL** | `postgres_data` garantiza persistencia entre reinicios sin acoplar al sistema de archivos del host. |
| 8 | **Optimización de caché en el Dockerfile** | `COPY requirements.txt` separado del código permite reutilizar la capa de dependencias. |
| 9 | **Uso de `response_model` en 2 módulos** | `restaurant` y `tracking` validan y documentan correctamente el contrato de salida. |
| 10 | **Validación declarativa en pagos** | `Field(gt=0)` expresa una invariante de negocio directamente en el schema, con la validación gestionada por el framework. |
| 11 | **Convención consistente en los 5 módulos** | Todos siguen la misma estructura (router → schemas → handlers → health). La uniformidad reduce la carga cognitiva. |
| 12 | **Separación input/output en schemas** | `RestaurantCreate` vs `Restaurant` demuestra comprensión del patrón Command/Resource. |

### 9.2 Deuda técnica priorizada

| # | Sev. | Hallazgo | Ubicación | Impacto |
|---|---|---|---|---|
| 1 | 🔴 Crítico | **DDD no implementado.** Sin capa de dominio, entidades, value objects, agregados, repositorios ni eventos | Todo `src/modules/` | El sistema no puede modificarse siguiendo el dominio sin reescribir la lógica. El modelo de negocio está en los handlers HTTP. |
| 2 | 🔴 Crítico | **`float` para valores monetarios** | `payment/router.py:17` | Descuadres contables, cobros incorrectos, fallos de conciliación. Inaceptable en un sistema de pagos. |
| 3 | 🔴 Crítico | **Sin Alembic.** `create_all()` en tiempo de importación, y con 0 modelos = **0 tablas creadas** | `main.py:17` | Sin control de esquema. Cualquier cambio de modelo exige destruir y recrear la base de datos. |
| 4 | 🔴 Crítico | **Sin autenticación real.** Token demo literal; cualquier credencial es aceptada | `auth/router.py:25` | El sistema es completamente público. Los datos de pedidos de cualquier usuario serían accesibles. |
| 5 | 🔴 Alto | **Bug de shadowing:** `GET /api/v1/orders/health` inalcanzable, devuelve datos falsos | `order/router.py:44,63` | El health check del módulo no funciona. Un monitor creería que el módulo está sano. |
| 6 | 🟠 Alto | **Persistencia en memoria** en `restaurant` y `tracking` | `restaurant/router.py:28`, `tracking/router.py:27` | Pérdida total de datos en cada reinicio. Comportamiento divergente con múltiples workers. |
| 7 | 🟠 Alto | **`services.py` vacíos** en los 5 módulos (33% de los archivos del proyecto) | 5 archivos | Hueco arquitectónico declarado y no implementado. La capa de aplicación no existe. |
| 8 | 🟠 Alto | **Credenciales en texto plano** versionadas en el repositorio | `docker-compose.yml:9-10` | Expuestas a todo el que tenga acceso al código. Requiere rotación inmediata. |
| 9 | 🟠 Alto | **Sin idempotencia en pagos** | `payment/router.py:25` | Un reintento de red genera un cobro duplicado al cliente. |
| 10 | 🟠 Medio | **Dependencias `db` muertas** — abren conexión sin usarse | `order/router.py:28,47`, `payment/router.py:28` | Consumo innecesario del pool de conexiones y confusión sobre el estado real de la persistencia. |
| 11 | 🟠 Medio | **Ausencia total de `__init__.py`** (0 en todo `src/`) | Todo `src/` | El proyecto funciona por *namespace packages* implícitos (Python ≥ 3.3), pero esto es frágil: rompe `pytest`, empaquetado, y herramientas de análisis estático. |
| 12 | 🟠 Medio | **Sin tests** (0 archivos de prueba) | Proyecto | Sin red de seguridad para refactorizar. Cualquier cambio es de riesgo máximo. |
| 13 | 🟡 Medio | **Contrato de datos inconsistente:** `order_id` es `int` en tracking y `str` en payment | `tracking/router.py:14`, `payment/router.py:16` | Imposible compartir modelos entre módulos. Violación de consistencia del dominio compartido. |
| 14 | 🟡 Medio | **Sin colaboración entre módulos** | Todo `src/modules/` | Ningún proceso de negocio end-to-end. La modularidad es solo de carpetas. |
| 15 | 🟡 Medio | **`--reload` en la imagen de contenedor** | `Dockerfile:28` | Rendimiento degradado y riesgo de seguridad si se despliega fuera de desarrollo. |
| 16 | 🟡 Medio | **Estados de dominio como strings libres** | `order/router.py:33,51`, `tracking/router.py:15` | Se aceptan estados inventados. Deberían ser enums con transiciones validadas. |
| 17 | 🟡 Medio | **Sin CORS** | `main.py` | El navegador bloqueará llamadas desde cualquier origen distinto al del servidor. |
| 18 | 🟡 Medio | **Sin logging estructurado ni correlation IDs** | Proyecto | Imposible trazar una petición de extremo a extremo o auditar operaciones. |
| 19 | 🟡 Bajo | **`declarative_base()` deprecado** en SQLAlchemy 2.0 | `database.py:9` | Advertencia en cada arranque. El estilo 2.0 usa `DeclarativeBase`. |
| 20 | 🟡 Bajo | **Dependencias con `>=` en vez de fijar** | `requirements.txt` | Builds no reproducibles; una actualización mayor puede romper la aplicación. |
| 21 | 🟡 Bajo | **`.env`, `config.py`, `init.sql` vacíos** | 3 archivos | Intención arquitectónica no materializada. `APP_ENV` y `python-dotenv` son código muerto. |
| 22 | 🟡 Bajo | **Health check global sin verificación de BD** | `main.py:81-86` | Reporta "healthy" con la base de datos caída. |
| 23 | 🟡 Bajo | **`build-essential` innecesario** en la imagen final | `Dockerfile:12-15` | Imagen más grande sin necesidad. |
| 24 | 🟡 Bajo | **Sin usuario no-root** en el contenedor | `Dockerfile` | Riesgo de escalamiento de privilegios si el proceso resulta comprometido. |
| 25 | 🟡 Bajo | **Sin `.dockerignore`** | Proyecto raíz | El contexto de build incluye `.env` y `.git`. |
| 26 | 🟡 Bajo | **Ausencia de `GET /health`** en el módulo `restaurant` | `restaurant/router.py` | Rompe la consistencia del patrón entre módulos. |
| 27 | 🟡 Bajo | **Sin linters ni formateadores** configurados | Proyecto | Sin control automático de estilo (el código sí sigue PEP 8 consistentemente). |

**Estadísticas:**

| Severidad | Cantidad |
|---|---|
| 🔴 Crítico | 4 |
| 🟠 Alto | 5 |
| 🟡 Medio | 9 |
| 🟡 Bajo | 9 |
| **Total** | **27** |

### 9.3 Vacíos DDD — Contraste detallado

| Concepto DDD | Estado | Qué falta |
|---|---|---|
| **Bounded Context** | ⚠️ Parcial | Las carpetas existen y los nombres son correctos, pero no hay lenguaje ubicuo codificado ni contratos entre contextos. |
| **Entidad** | ❌ Ausente | Clases con identidad, ciclo de vida y comportamiento. Hay Pydantic models, que son estructuras de transporte, no entidades. |
| **Value Object** | ❌ Ausente | `amount: float` debería ser `Money(Decimal, currency)`. `status: str` debería ser `OrderStatus(value)`. |
| **Agregado** | ❌ Ausente | Sin raíz de agregado que proteja invariantes. `Order` debería ser la raíz y proteger que un pedido pagado no pueda cancelarse. |
| **Repositorio** | ❌ Ausente | Sin abstracción de persistencia. `restaurant` accede a una lista; `order` no accede a nada. |
| **Unidad de Trabajo** | ⚠️ Parcial | `get_db()` provee la sesión, pero no hay `commit`/`rollback` transaccional explícito. |
| **Evento de dominio** | ❌ Ausente | Sin `publish`, sin outbox pattern, sin integración de módulos. |
| **Servicio de dominio** | ❌ Ausente | Lógica de negocio que cruza agregados sin pertenecer a ninguno. |
| **Lenguaje ubicuo** | ❌ Ausente | `"Hamburguesa"`, `"Papas"` hardcodeados; `status` con strings en inglés y mensajes en español. |
| **Anti-corruption layer** | ❌ Ausente | Sin protección frente a modelo de datos de terceros (pasarela de pago). |
| **Módulo de aplicación** | ❌ Ausente | `services.py` vacíos. Sin casos de uso ni orquestación. |
| **Pruebas de dominio** | ❌ Ausente | 0 tests. Sin verificación de invariantes. |

### 9.4 Análisis de riesgos

#### Riesgo de negocio

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| **Cobro incorrecto al cliente** por `float` monetario | Alta | Crítico | Value object `Money` con `Decimal` |
| **Disponibilidad total de la API** sin autenticación | Alta | Crítico | JWT + hashing + autorización |
| **Pérdida de todos los datos** en cada reinicio | Alta | Crítico | Persistencia real vía repositorios |
| **Imposible entregar a un cliente real** (no hay cobro ni confirmación de restaurante) | Actual | Crítico | Implementar capa de aplicación y dominio |
| **Incumplimiento de datos personales** (restaurantes y tracking sin control de acceso) | Media | Crítico | Autorización por recurso y logging de auditoría |

#### Riesgo de seguridad

| Riesgo | Severidad | Ubicación |
|---|---|---|
| Credenciales de BD en texto plano versionadas | 🔴 Crítica | `docker-compose.yml:9-10` |
| Sin autenticación (token demo) | 🔴 Crítica | `auth/router.py:25` |
| Sin autorización: cualquier cliente ve cualquier pedido | 🔴 Crítica | `order/router.py:44` |
| Sin CORS configurado | 🟡 Media | `main.py` |
| Proceso corriendo como root | 🟡 Media | `Dockerfile` |
| `--reload` expuesto si se despliega fuera de desarrollo | 🟡 Media | `Dockerfile:28` |
| Sin rate limiting en `/login` (permite fuerza bruta) | 🟡 Media | `auth/router.py:21` |
| Sin validación de `order_id` en la consulta (IDOR potencial) | 🟡 Media | `order/router.py:44` |

#### Riesgo técnico y de datos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Sin migraciones: cualquier cambio de modelo pierde datos | 🔴 Crítica | Alembic |
| Bug de shadowing oculta el estado real del módulo | 🔴 Alta | Reordenar rutas + tests de contrato |
| Contrato `order_id` inconsistente entre módulos | 🟠 Media | Modelo compartido en `core/domain` |
| Sin tests: refactorizar es de riesgo máximo | 🟠 Alta | Suite de tests antes de refactorizar |
| Versiones no fijadas: builds irreproducibles | 🟠 Media | Fijar versiones o lock file |

### 9.5 Consistencia y estilo del código

**Aspectos positivos en la legibilidad:**

- **Convenciones consistentes**: los 5 módulos usan la misma estructura, separadores de sección (`# ===`) y formato.
- **PEP 8 consistente**: imports agrupados, nombres en `snake_case`, líneas de longitud razonable.
- **Comentarios explicativos** de la intención de cada sección.
- **Aliasing de imports en `main.py`**: `from src.modules.auth.router import router as auth_router` evita colisiones de nombre y es explícito.
- **Nombres de funciones autoexplicativos**: `create_restaurant`, `get_tracking_by_id`, `order_health`.

**Observaciones menores:**

- Mezcla de `typing.List` (`restaurant/router.py:3`, `tracking/router.py:3`) con sintaxis moderna `str | None` (`restaurant/router.py:16`). En Python 3.11, `List[Restaurant]` es redundante: `list[Restaurant]` funciona.
- Tipos de retorno **no declarados** en las funciones handler. Con `response_model` esto es tolerable, pero no en los 3 módulos que no lo usan.
- `global _next_id` con variable mutable de nivel de módulo (`restaurant/router.py:39`, `tracking/router.py:38`): patrón inseguro bajo concurrencia.

---

## 10. Conclusiones

### 10.1 Valoración de la arquitectura

La arquitectura de carpetas es **acertada y bien pensada**. La decisión de separar `core/` (transversal) de `modules/` (negocio), con un `main.py` como raíz de composición que solo conoce routers, es exactamente el patrón de un monolito modular. La nomenclatura de los bounded contexts (`auth`, `restaurant`, `order`, `payment`, `tracking`) refleja un dominio de delivery correctamente desmembrado.

La infraestructura de despliegue —Dockerfile con caché optimizada, healthchecks, `depends_on` condicional, volumen nombrado, red dedicada— demuestra **madurez operacional por encima del promedio** para un proyecto en esta etapa.

### 10.2 Distancia entre estructura e implementación

Sin embargo, el proyecto presenta una **brecha grande entre lo que la estructura promete y lo que el código hace**:

| La estructura declara | La implementación ofrece |
|---|---|
| 5 módulos de DDD | 5 carpetas con CRUD REST |
| Una capa de aplicación (`services.py`) | 5 archivos vacíos |
| Una capa de dominio | No existe |
| Persistencia en `core/database.py` | Una sesión que se abre y se descarta |
| PostgreSQL operativo | Una base de datos con 0 tablas |
| `init.sql` para el esquema | Un archivo vacío |
| `config.py` para configuración | Un archivo vacío |
| `python-dotenv` en requisitos | Nunca invocado |
| Un sistema de pagos | Un `transaction_id` hardcodeado |
| Autenticación | Un token demo literal |

**Nótese que esta brecha es de *contenido*, no de *diseño*.** El esqueleto está bien construido; lo que falta es la implementación de las capas internas. Esto es una buena noticia: **no hay que rediseñar, hay que construir sobre lo ya hecho**.

### 10.3 Veredicto final

> El proyecto es un **esqueleto arquitectónico sólido y correctamente orientado**, en estado de **prototipo funcional**. Sirve como cimiento válido para construir el sistema real, pero **no debe desplegarse en producción** sin remediar los 4 hallazgos críticos: ausencia de DDD, `float` monetario, falta de migraciones y ausencia de autenticación.

La ruta hacia microservicios se ve facilitada por la estructura modular existente: cuando un módulo madure y requiera escalado independiente, podrá extraerse conservando sus fronteras, sus endpoints y su base de datos, tal como está diseñado.

---

## 11. Recomendaciones

### 11.1 Fase 1 — Saneamiento (bloqueante para producción)

Objetivo: eliminar los defectos que vuelven el sistema inseguro o inconsistente.

| # | Acción | Archivo | Esfuerzo |
|---|---|---|---|
| 1 | **Corregir el shadowing de rutas:** mover `GET /health` antes de `GET /{order_id}` | `order/router.py:63` → antes de línea 44 | 1 línea |
| 2 | **Reemplazar `float` por `Decimal`:** `amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)` | `payment/router.py:17` | Bajo |
| 3 | **Introducir Alembic:** `alembic init`, migrar `create_all()` a un comando explícito | Nuevo + `main.py:17` | Medio |
| 4 | **Externalizar secretos:** mover credenciales a `.env` con `${POSTGRES_PASSWORD}` y `.gitignore` | `docker-compose.yml:9-10` | Bajo |
| 5 | **Implementar autenticación real:** JWT (`PyJWT`) + hashing (`passlib[bcrypt]`) + dependency `get_current_user` | `auth/services.py` | Medio |
| 6 | **Implementar `core/config.py`** con Pydantic Settings; llamar `load_dotenv()` | `core/config.py` | Bajo |
| 7 | **Añadir `__init__.py`** en todos los paquetes | Todo `src/` | Muy bajo |
| 8 | **Quitar `--reload`** del `CMD` de producción | `Dockerfile:28` | 1 línea |
| 9 | **Añadir CORS middleware** con orígenes configurados | `main.py` | Bajo |
| 10 | **Health check global** que ejecute `SELECT 1` contra PostgreSQL | `main.py:81` | Bajo |

### 11.2 Fase 2 — Persistencia real (transición de prototipo a funcional)

Objetivo: sustituir el estado en memoria por la base de datos ya operativa.

Por cada módulo, en este orden interno (de dentro hacia afuera):

1. **Definir la entidad de dominio** en `modules/<m>/domain/entities.py` con comportamiento e invariantes.
2. **Definir el repositorio** como interfaz en `modules/<m>/domain/repositories.py`.
3. **Implementar el repositorio** con SQLAlchemy en `modules/<m>/infrastructure/repositories.py`.
4. **Definir el modelo ORM** en `modules/<m>/infrastructure/models.py` (tabla por módulo, esquema propio).
5. **Implementar los casos de uso** en `modules/<m>/services.py` con control transaccional explícito.
6. **Simplificar el router** para que solo valide entrada, delegue al servicio y serialice salida.

| # | Acción | Detalle |
|---|---|---|
| 11 | Crear estructura `domain/`, `application/`, `infrastructure/` por módulo | Separación DDD real de las 3 capas |
| 12 | Implementar el patrón **Unit of Work** | `get_db()` debe hacer `commit`/`rollback` |
| 13 | Modelar `Money` como value object | `Decimal` + moneda, con validación de escala |
| 14 | Modelar `OrderStatus` como enum | `PENDING, PAID, IN_PREPARATION, OUT_FOR_DELIVERY, DELIVERED, CANCELLED` |
| 15 | Unificar el contrato `order_id` | Un tipo compartido en `core/domain/types.py` |
| 16 | Añadir pruebas | Tests de dominio primero; luego de contrato de las rutas |

### 11.3 Fase 3 — Colaboración y robustez (madurez del dominio)

Objetivo: que el sistema resuelva casos de uso completos.

| # | Acción | Detalle |
|---|---|---|
| 17 | **Publicar eventos de dominio** | `order.py:publish(OrderCreated)` |
| 18 | **Conectar módulos con eventos** | `payment` escucha `OrderCreated`; `tracking` escucha `OrderPaid` |
| 19 | **Implementar el patrón Outbox** | Garantía de entrega de eventos sin acoplamiento temporal |
| 20 | **Añadir idempotencia en pagos** | Clave de idempotencia + restricción de unicidad en BD |
| 21 | **Integrar una pasarela real** | Capa anticorrupción sobre Stripe/PayPal |
| 22 | **Versionado de API en dependency groups** | Additive; evita romper clientes existentes |
| 23 | **Fijar versiones** en `requirements.txt` o usar lock file | Builds reproducibles |
| 24 | **Dockerfile de múltiples etapas** | Imagen final sin `build-essential`, con usuario no-root y `.dockerignore` |
| 25 | **Logging estructurado + correlation ID** | Trazabilidad de extremo a extremo y auditoría |
| 26 | **Rate limiting y observabilidad** | Protección de `/login`, métricas y alertas |

### 11.4 Estructura objetivo propuesta

```
src/
├── main.py                          Composition root + middleware
│
├── core/                            Technical core (cross-cutting)
│   ├── config.py                    Settings tipados y validados
│   ├── database.py                  Engine, session, UoW
│   ├── middleware.py                CORS, logging, correlation ID
│   ├── events.py                    Bus de eventos de dominio
│   └── types.py                     Tipos compartidos (OrderId, Money, Status)
│
├── shared/                          Utilidades puras
│   ├── errors.py                    Excepciones de dominio
│   └── pagination.py
│
└── modules/
    └── restaurant/                  ← Ejemplo: módulo DDD completo
        ├── domain/                  ◀ CAPA DE DOMINIO (reglas del negocio)
        │   ├── entities.py          Restaurant, con comportamiento e invariantes
        │   ├── value_objects.py     Address, PhoneNumber
        │   ├── repositories.py      Repository (interfaz abstracta)
        │   ├── services.py          RestaurantService (servicio de dominio)
        │   └── events.py            RestaurantCreated, RestaurantClosed
        │
        ├── application/             ◀ CAPA DE APLICACIÓN (casos de uso)
        │   └── services.py          CreateRestaurant, ListRestaurants
        │
        ├── infrastructure/          ◀ CAPA DE INFRAESTRUCTURA (adaptadores)
        │   ├── models.py            Modelo SQLAlchemy
        │   ├── repositories.py      Implementación concreta del repositorio
        │   └── mappers.py           Entidad <-> Modelo
        │
        └── router.py                ◀ CAPA DE PRESENTACIÓN (HTTP)
            └── schemas.py           Pydantic: Request / Response
```

**Reglas de dependencia** (Direction of Dependency):

```
        router.py  ──depends on──▶  application/services.py
                                         │
                                         ▼
                                     domain/  ◀── no depende de nada
                                         ▲
                                         │
                    infrastructure/repositories.py
```

Regla fundamental: **las dependencias apuntan hacia adentro**. El dominio no importa nada de las otras capas. Esto es lo que permite cambiar PostgreSQL por otro motor, o FastAPI por otro framework, sin tocar las reglas de negocio.

### 11.5 Resumen de prioridades

```
AHORA  ──▶  [1-10]  Saneamiento        (bloqueante: seguridad y corrección)
            │
            ▼
SIGUIENTE ─▶  [11-16] Persistencia real (funcionalidad mínima viable)
            │
            ▼
DESPUÉS ──▶  [17-26] Colaboración      (madurez del dominio y operación)
```

**Regla de oro para el plan:** *corregir antes de extender*. Añadir un sexto módulo a un sistema sin autenticación, sin migraciones y con `float` para dinero amplifica cada defecto existente.

---

## Anexo A — Matriz completa de endpoints

| # | Método | Ruta | Módulo | Descripción | Respuesta | Estado | DB |
|---|---|---|---|---|---|---|---|
| 1 | `GET` | `/` | Sistema | Raíz informativa | `status`, `message` | Real | No |
| 2 | `GET` | `/health` | Sistema | Probe de salud | `status`, `service` | Real (no verifica BD) | No |
| 3 | `POST` | `/api/v1/auth/login` | auth | Autenticación | `message`, `token`, `email` | **Mock** (`demo-token`) | No |
| 4 | `GET` | `/api/v1/auth/health` | auth | Salud del módulo | `module`, `status` | Real | No |
| 5 | `POST` | `/api/v1/restaurants/` | restaurant | Crear restaurante | `Restaurant` | Real (memoria) | No |
| 6 | `GET` | `/api/v1/restaurants/` | restaurant | Listar restaurantes | `List[Restaurant]` | Real (memoria) | No |
| 7 | `GET` | `/api/v1/restaurants/{id}` | restaurant | Obtener por ID | `Restaurant` | Real (memoria) | No |
| 8 | `PUT` | `/api/v1/restaurants/{id}` | restaurant | Actualizar | `Restaurant` | Real (memoria) | No |
| 9 | `DELETE` | `/api/v1/restaurants/{id}` | restaurant | Eliminar | `message` | Real (memoria) | No |
| 10 | `POST` | `/api/v1/orders/` | order | Crear pedido | `message`, `order_id`, `status` | **Mock** (`ORD-12345`) | Inyectada sin uso |
| 11 | `GET` | `/api/v1/orders/{order_id}` | order | Obtener pedido | `order_id`, `status`, `items` | **Mock** | Inyectada sin uso |
| 12 | `GET` | `/api/v1/orders/health` | order | Salud del módulo | `module`, `status` | 🔴 **Inalcanzable** (bug de shadowing) | No |
| 13 | `POST` | `/api/v1/payments/process` | payment | Procesar pago | `transaction_id`, `status` | **Mock** (`TXN-998877`) | Inyectada sin uso |
| 14 | `GET` | `/api/v1/payments/health` | payment | Salud del módulo | `module`, `status` | Real | No |
| 15 | `POST` | `/api/v1/tracking/` | tracking | Crear registro | `Tracking` | Real (memoria) | No |
| 16 | `GET` | `/api/v1/tracking/` | tracking | Listar registros | `List[Tracking]` | Real (memoria) | No |
| 17 | `GET` | `/api/v1/tracking/{tracking_id}` | tracking | Obtener por ID | `Tracking` | Real (memoria) | No |
| 18 | `GET` | `/api/v1/tracking/order/{order_id}` | tracking | Historial por pedido | `List[Tracking]` | Real (memoria) | No |
| 19 | `PUT` | `/api/v1/tracking/{tracking_id}` | tracking | Actualizar estado | `Tracking` | Real (memoria) | No |
| 20 | `DELETE` | `/api/v1/tracking/{tracking_id}` | tracking | Eliminar | `message` | Real (memoria) | No |

**Leyenda de estado:**

| Estado | Significado |
|---|---|
| Real | Funcionalmente correcto (aunque con persistencia en memoria) |
| Real (memoria) | Funciona, pero los datos no persisten y no son seguros bajo concurrencia |
| **Mock** | Devuelve datos hardcodeados; la lógica real no existe |
| 🔴 **Inalcanzable** | La ruta existe pero es imposible de invocar por colisión de orden |

**Ninguno de los 20 endpoints requiere autenticación.** Ninguno verifica propiedad del recurso: cualquier cliente puede consultar el pedido de otro.

## Anexo B — Glosario de términos técnicos

| Término | Definición |
|---|---|
| **Monolito modular** | Arquitectura de un único despliegue con módulos de negocio separados y dependencias dirigidas. |
| **Bounded Context** (Contexto Delimitado) | Frontera conceptual donde un término del negocio tiene un significado único y preciso. |
| **Lenguaje ubicuo** (Ubiquitous Language) | Vocabulario común compartido entre desarrolladores y expertos del dominio. |
| **Agregado** | Conjunto de objetos tratados como una unidad única de consistencia, gobernada por una raíz. |
| **Entidad** | Objeto de dominio con identidad propia, persistente a lo largo del tiempo. |
| **Value Object** | Objeto de dominio sin identidad, definido por sus atributos e inmutable. |
| **Invariante** | Regla de negocio que debe cumplirse siempre. |
| **Raíz de agregado** | Entidad que controla el acceso y la consistencia de su agregado. |
| **Repositorio** | Abstracción que encapsula el acceso a la persistencia de un agregado. |
| **Unit of Work** | Patrón que agrupa operaciones en una única transacción. |
| **Evento de dominio** | Registro inmutable de un hecho de negocio relevante. |
| **Anti-corruption layer** | Capa que aísla un modelo de negocio de sistemas externos. |
| **Composition root** | Único lugar donde se ensamblan los componentes de la aplicación. |
| **Dependency injection** | Patrón donde las dependencias se proporcionan externamente en lugar de construirse internamente. |
| **Shadowing de rutas** | Error donde una ruta con parámetro se registra antes que una ruta estática y la absorbe. |
| **Value Object `Money`** | Representación de dinero con `Decimal` y moneda, en lugar de un número de punto flotante. |
| **Outbox pattern** | Patrón que garantiza la entrega de eventos escribiendo en una tabla de salida en la misma transacción. |

---

*Fin del informe. Análisis realizado sobre la versión 1.0.0 del Delivery Platform — Arquitectura Monolítica Modular (DDD).*
