# SISTEMA DE DELIVERY

## 1. INTRODUCCIÓN

El presente proyecto tiene como finalidad implementar y experimentar con diferentes arquitecturas de software mediante el desarrollo de una solución basada en un modelo de negocio de delivery, diseñado y estructurado por los integrantes del proyecto. Este modelo contempla los procesos y flujos necesarios para representar las operaciones principales de un servicio de entrega, considerando actores como clientes, restaurantes, repartidores y administradores.

El enfoque principal del proyecto consiste en aplicar tres tipos de arquitecturas de software: monolítica modular, cliente-servidor y microservicios, mediante la implementación y puesta en funcionamiento de sus respectivos servidores. Para ello, se utilizarán tecnologías y herramientas que permitan estructurar los componentes, establecer la comunicación entre ellos y gestionar las operaciones definidas en el modelo de negocio.

A través de esta implementación se busca comprender las características de cada arquitectura, identificar sus diferencias y analizar cómo influye cada enfoque en aspectos como la escalabilidad, modularidad, organización y mantenibilidad del software. De esta manera, el proyecto permitirá llevar a la práctica los conocimientos adquiridos en ingeniería de software, utilizando un mismo contexto de negocio para experimentar con distintas soluciones arquitectónicas.

### 1.1. Herramientas Tecnologicas:

| Tecnologia             | Proposito                                                                                                                                                                                                                                                                                     |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Python 3.10            | Lenguaje base del monolito. La versión la fija el Dockerfile (python:3.10-slim) y permite usar type hints modernos, dataclasses y match-style unions que sostienen toda la arquitectura por capas.                                                                                            |
| FastAPI 0.110.0        | Framework web que expone los 5 módulos como API REST. Aporta APIRouter (un router por módulo), Depends (inyección de dependencias que conecta servicios con repositorios), response_model (contrato de salida), HTTPException y los códigos de estado (201, 204, 400, 402, 404, 409).         |
| SQLAlchemy 2.0.28      | ORM y capa de acceso a datos: define las 12 tablas en los infrastructure/models_db.py (Base, Column, ForeignKey, relationship), gestiona las sesiones (sessionmaker) y ejecuta las consultas dentro de los repository_impl.py. Su aislamiento es deliberado: solo aparece en infraestructura. |
| Git & GitHub           | Control de versiones del proyecto                                                                                                                                                                                                                                                             |
| SQL                    | Fuente de verdad del esquema. Crea el schema delivery, las 12 tablas en orden de dependencias y siembra los catálogos rol y estado. Se monta como volumen de inicialización de Postgres, por eso la app usa search_path=delivery,public.                                                      |
| PostgreSQL 15 (Alpine) | Motor de base de datos relacional. Aporta lo que el modelo necesita: esquemas (delivery), SERIAL, NUMERIC(10,2) para dinero exacto, CHECK para los enums del negocio, UNIQUE para "un pago por pedido" y ON DELETE CASCADE/SET NULL para la integridad entre módulos.                         |
| Docker                 | Empaqueta la aplicación con sus dependencias en una imagen reproducible, de modo que el proyecto corra igual en cualquier máquina sin instalar Python ni Postgres localmente.                                                                                                                 |
| Docker Compose         | Orquesta los dos servicios (postgres-db y delivery-app), la red delivery-network, el volumen persistente y el depends_on con healthcheck (pg_isready) para que la API no arranque antes que la base.                                                                                          |

### 1.2. Arquitectura del proyecto (Esquema):

```
delivery-monolith/
│
├── src/                                ● CÓDIGO FUENTE (paquete raíz de la app)
│   │
│   ├── main.py                         ● COMPOSITION ROOT — punto de entrada de FastAPI
│   │                                     · Importa los 5 models_db (registro de tablas)
│   │                                     · create_all() y montaje de routers
│   │                                     · Endpoints de sistema: GET / y GET /health
│   │
│   ├── core/                           ● KERNEL COMPARTIDO (no es un módulo de negocio)
│   │   ├── config.py                   ○ Settings centralizados  → VACÍO (deuda)
│   │   ├── database.py                 ● Engine, SessionLocal, Base, get_db()
│   │   └── types.py                    ● Tipos transversales (Dinero: Decimal→float)
│   │
│   └── modules/                        ● MÓDULOS DE NEGOCIO (bounded contexts)
│       │
│       ├── auth/                       ● Identidad: usuarios, roles, estados, contacto, dirección
│       │   ├── domain/                 ── CAPA 1: el "qué" del negocio, sin tecnología
│       │   │   ├── models.py           ● Entidades puras: Usuario
│       │   │   ├── repositories.py     ● Contratos ABC de persistencia (puertos)
│       │   │   └── exceptions.py       ● Errores de negocio del módulo
│       │   ├── application/            ── CAPA 2: el "cómo" se orquesta
│       │   │   ├── services.py         ● Casos de uso (AuthService)
│       │   │   └── dtos.py             ○ DTOs de entrada → VACÍO (deuda)
│       │   ├── infrastructure/         ── CAPA 3: la tecnología concreta
│       │   │   ├── models_db.py        ● Tablas ORM: rol, estado, usuario, contacto, direccion
│       │   │   ├── repository_impl.py  ● AuthRepositorySqlAlchemy (implementa el puerto)
│       │   │   └── external_adapters.py○ Puertos hacia otros módulos → VACÍO (no los necesita)
│       │   └── presentation/           ── CAPA 4: la puerta de entrada HTTP
│       │       ├── router.py           ● 3 endpoints + factoría get_auth_service()
│       │       └── schemas.py          ● Contratos Pydantic de entrada/salida
│       │
│       ├── restaurant/                 ● Catálogo: restaurantes y sus productos
│       │   ├── domain/                 · models.py (Restaurante, Producto) · repositories.py (2 ABC)
│       │   │                           · exceptions.py (recurso no encontrado, datos inválidos…)
│       │   ├── application/            · services.py (RestaurantService) · dtos.py
│       │   ├── infrastructure/         · models_db.py (restaurante, producto)
│       │   │                           · repository_impl.py (2 repos) · external_adapters.py ○ VACÍO
│       │   └── presentation/           · router.py (11 endpoints + _a_http) · schemas.py
│       │
│       ├── order/                      ● Pedidos: el agregado central del sistema
│       │   ├── domain/                 · models.py (Pedido, DetallePedido + máquina de estados
│       │   │                           ·           + objetos de valor RestauranteInfo/ProductoInfo)
│       │   │                           · repositories.py (1 repo + 3 puertos: catálogo, usuario, repartidor)
│       │   │                           · exceptions.py (transiciones inválidas, no cancelable…)
│       │   ├── application/            · services.py (OrderService) · dtos.py
│       │   ├── infrastructure/         · models_db.py (pedido, detalle_pedido)
│       │   │                           · repository_impl.py (PedidoRepositorySqlAlchemy)
│       │   │                           · external_adapters.py ● CAPA ANTICORRUPCIÓN (auth/restaurant/tracking)
│       │   └── presentation/           · router.py (7 endpoints) · schemas.py
│       │
│       ├── payment/                    ● Cobros: un pago por pedido
│       │   ├── domain/                 · models.py (Pago, PedidoInfo, ResultadoPasarela)
│       │   │                           · repositories.py (1 repo + 2 puertos: pedido y pasarela)
│       │   │                           · exceptions.py (pago duplicado, rechazado…)
│       │   ├── application/            · services.py (PaymentService) · dtos.py
│       │   ├── infrastructure/         · models_db.py (pago)
│       │   │                           · repository_impl.py (PagoRepositorySqlAlchemy)
│       │   │                           · external_adapters.py ● PedidoOrderAdapter + PasarelaPagoSimulada
│       │   └── presentation/           · router.py (6 endpoints) · schemas.py
│       │
│       └── tracking/                   ● Repartidores y GPS
│           ├── domain/                 · models.py (Repartidor, UbicacionTracking)
│           │                           · repositories.py (2 ABC) · exceptions.py
│           ├── application/            · services.py (TrackingService) · dtos.py
│           ├── infrastructure/         · models_db.py (repartidor, ubicacion_tracking)
│           │                           · repository_impl.py (2 repos) · external_adapters.py ○ VACÍO
│           └── presentation/           · router.py (10 endpoints) · schemas.py
│
├── init.sql                            ● ESQUEMA REAL de BD (12 tablas, schema `delivery`)
├── docker-compose.yml                  ● Orquestación: postgres:15 + app, healthcheck, red, volumen
├── Dockerfile                          ● Imagen python:3.10-slim → uvicorn src.main:app
├── requirements.txt                    ● Dependencias fijadas
├── INFORME.md                          ● Documentación de arquitectura (78 KB)
├── DDD_modulo_Auth.ipynb               · Notebook de origen (ignorado)
└── .claude/settings.local.json         · Config local de herramienta
```

#### 1.2.1. Modulos del proyecto:

| Modulo     | Responsabilidad                                         |
| ---------- | ------------------------------------------------------- |
| auth       | Usuarios, login con JWT, roles, contacto y direcciones. |
| restaurant | Restaurantes, horarios y menú de productos.             |
| order      | Pedidos, detalle y ciclo de vida del pedido.            |
| payment    | Pagos (efectivo, tarjeta, QR).                          |
| tracking   | Repartidores, ubicación GPS y seguimiento del pedido.   |

### 1.3. Entidades del sistemas:

Estas son las entidades que participan dentro del sistema con sus respectivos atributos:

| Entidad                                      | Módulo       | Atributos                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| -------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Usuario**                                  | `auth`       | `usuario_id` (PK, autogenerado) · `nombre_usuario`: str · `email`: str (único) · `contrasenia`: str · `rol_id`: int (FK → `rol`) · `estado_id`: int (FK → `estado`) — _Método:_ `cambiar_password()`                                                                                                                                                                                                                                                                                                                                                   |
| **Direccion**                                | `auth`       | `direccion_id` (PK) · `direccion_texto`: str · `latitud`: Decimal(10,8) opcional · `longitud`: Decimal(11,8) opcional · `referencia`: str opcional · `etiqueta`: str opcional · `es_temporal`: bool = `False` · `usuario_id`: int (FK → `usuario`) — _Solo existe como modelo ORM_                                                                                                                                                                                                                                                                     |
| **Restaurante** (`Restaurant`)               | `restaurant` | `restaurant_id` (PK) · `nombre`: str · `direccion`: str · `contacto`: str opcional · `horario_apertura`: time opcional · `horario_cierre`: time opcional · `estado`: str = `"Abierto"` \| `"Cerrado"` — _Métodos:_ `abrir()`, `cerrar()`, `esta_abierto()`                                                                                                                                                                                                                                                                                             |
| **Producto**                                 | `restaurant` | `producto_id` (PK) · `nombre`: str · `descripcion`: str opcional · `precio`: Decimal(10,2) ≥ 0 · `disponible`: bool = `True` · `categoria`: str · `restaurant_id`: int (FK → `restaurante`) — _Método:_ `cambiar_disponibilidad()`                                                                                                                                                                                                                                                                                                                     |
| **Pedido** (raíz de agregado)                | `order`      | `pedido_id` (PK) · `usuario_id`: int (FK → `usuario`) · `restaurant_id`: int (FK → `restaurante`) · `repartidor_id`: int opcional (FK → `repartidor`) · `detalles`: List[DetallePedido] · `notas_cliente`: str opcional · `estado`: str = `"Pendiente"` · `sum_total`: Decimal(10,2) = `0.00` · `tiempo_estimado_min`: int = `30` · `permite_cancelacion`: bool = `True` · `fecha_hora`: datetime (asignada por el servidor) — _Métodos:_ `crear()`, `calcular_total()`, `cambiar_estado()`, `cancelar()`, `asignar_repartidor()`, `esta_finalizado()` |
| **DetallePedido** (línea del pedido)         | `order`      | `detalle_pedido_id` (PK) · `pedido_id`: int (FK → `pedido`) · `producto_id`: int (FK → `producto`) · `cantidad`: int > 0 · `precio_unitario`: Decimal(10,2) · `subtotal`: Decimal(10,2) — **calculado** (`precio_unitario × cantidad`), nunca recibido del cliente                                                                                                                                                                                                                                                                                     |
| **Pago**                                     | `payment`    | `pago_id` (PK) · `pedido_id`: int (FK → `pedido`, **único**: un pago por pedido) · `monto`: Decimal(10,2) > 0 · `metodo_pago`: str = `Efectivo` \| `Tarjeta` \| `QR` · `estado_pago`: str = `Pendiente` \| `Completado` \| `Fallido` · `transaccion_id`: str opcional (único) · `fecha`: date (asignada por el servidor) — _Métodos:_ `completar()`, `marcar_fallido()`                                                                                                                                                                                |
| **Repartidor**                               | `tracking`   | `repartidor_id` (PK) · `tipo_vehiculo`: str = `Bicicleta` \| `Moto` \| `Taxi` · `placa`: str opcional (obligatoria si es Moto/Taxi) · `disponible`: bool = `True` · `usuario_id`: int opcional (FK → `usuario`, `ON DELETE SET NULL`) — _Métodos:_ `marcar_ocupado()`, `liberar()`                                                                                                                                                                                                                                                                     |
| **UbicacionTracking** (`ubicacion_tracking`) | `tracking`   | `ubicacion_tracking_id` (PK) · `repartidor_id`: int (FK → `repartidor`) · `latitud`: float ∈ [-90, 90] · `longitud`: float ∈ [-180, 180] · `fecha`: date (servidor) · `hora`: time (servidor)                                                                                                                                                                                                                                                                                                                                                          |

### 1.3.1. Relaciones de cardinalidad entre entidades

| Entidad origen  | Cardinalidad | Entidad destino       | Columna / FK                                             | Regla y comportamiento                                                                                                                                                                                                                                   |
| --------------- | ------------ | --------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rol**         | 1 : N        | **Usuario**           | `usuario.rol_id` (NOT NULL)                              | Un rol agrupa muchos usuarios; cada usuario tiene exactamente un rol. Catálogo: `cliente`, `repartidor`, `admin`. Sin `ON DELETE`: el rol no se puede borrar si está en uso.                                                                             |
| **Estado**      | 1 : N        | **Usuario**           | `usuario.estado_id` (NOT NULL)                           | Un estado agrupa muchos usuarios; cada usuario tiene un estado. Catálogo: `activo`, `inactivo`, `suspendido`, `eliminado`. Sin `ON DELETE`.                                                                                                              |
| **Usuario**     | 1 : 1        | **Contacto**          | `contacto.usuario_id` (**UNIQUE**, NOT NULL)             | Cada usuario tiene como máximo un contacto y cada contacto pertenece a un solo usuario. `ON DELETE CASCADE` (si se borra el usuario, se borra su contacto).                                                                                              |
| **Usuario**     | 1 : N        | **Direccion**         | `direccion.usuario_id` (NOT NULL)                        | Un usuario puede registrar muchas direcciones; cada dirección pertenece a un solo usuario. `ON DELETE CASCADE`.                                                                                                                                          |
| **Restaurante** | 1 : N        | **Producto**          | `producto.restaurant_id` (NOT NULL)                      | Un restaurante ofrece muchos productos; cada producto pertenece a un único restaurante. `ON DELETE CASCADE` (borrar el restaurante borra su menú).                                                                                                       |
| **Usuario**     | 1 : N        | **Pedido**            | `pedido.usuario_id` (NOT NULL)                           | Un cliente realiza muchos pedidos; cada pedido pertenece a un solo usuario. Sin `ON DELETE`: no se puede borrar un usuario con pedidos.                                                                                                                  |
| **Restaurante** | 1 : N        | **Pedido**            | `pedido.restaurant_id` (NOT NULL)                        | Un restaurante recibe muchos pedidos; cada pedido va dirigido a un solo restaurante. Sin `ON DELETE`: protege el historial de pedidos.                                                                                                                   |
| **Repartidor**  | 1 : N (0..N) | **Pedido**            | `pedido.repartidor_id` (NULL permitido)                  | Un repartidor puede atender muchos pedidos a lo largo del tiempo; un pedido tiene **0 o 1** repartidor asignado (al inicio es `NULL`). `ON DELETE SET NULL`: si se elimina el repartidor, el pedido queda sin asignar.                                   |
| **Pedido**      | 1 : N        | **DetallePedido**     | `detalle_pedido.pedido_id` (NOT NULL)                    | Un pedido tiene **1 o más** líneas de detalle; cada línea pertenece a un único pedido. `ON DELETE CASCADE` (el detalle no existe sin su pedido).                                                                                                         |
| **Producto**    | 1 : N        | **DetallePedido**     | `detalle_pedido.producto_id` (NOT NULL)                  | Un producto puede aparecer en muchas líneas de muchos pedidos; cada línea referencia un solo producto. Sin `ON DELETE`: el producto no se puede borrar si ya fue vendido (se marca `disponible = False`).                                                |
| **Pedido**      | 1 : 1        | **Pago**              | `pago.pedido_id` (**UNIQUE**, NOT NULL)                  | Cada pedido tiene como máximo un pago y cada pago corresponde a un solo pedido. `ON DELETE CASCADE`. Refuerza la regla de negocio "un solo pago por pedido".                                                                                             |
| **Repartidor**  | 1 : N        | **UbicacionTracking** | `ubicacion_tracking.repartidor_id` (NOT NULL)            | Un repartidor reporta muchas posiciones GPS; cada posición pertenece a un solo repartidor. `ON DELETE CASCADE`.                                                                                                                                          |
| **Usuario**     | 1 : 0..N     | **Repartidor**        | `repartidor.usuario_id` (NULL permitido, **sin UNIQUE**) | A nivel de esquema un usuario puede estar vinculado a varios repartidores y un repartidor puede no tener usuario. La intención de diseño es **1 : 1** (el repartidor es un usuario con rol `repartidor`), pero la BD no lo obliga. `ON DELETE SET NULL`. |
