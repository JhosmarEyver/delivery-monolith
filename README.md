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
