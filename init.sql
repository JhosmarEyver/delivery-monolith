-- =========================================================================
-- CONFIGURACIÓN DEL ESQUEMA Y EXTENSIONES (PostgreSQL)
-- =========================================================================
CREATE SCHEMA IF NOT EXISTS delivery;
SET search_path TO delivery, public;

-- =========================================================================
-- ORDEN 1: CATÁLOGOS BASE (Sin dependencias de llaves foráneas)
-- =========================================================================

-- Tabla de Roles (Catálogo)
CREATE TABLE IF NOT EXISTS rol (
    rol_id SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla de Estados (Catálogo)
CREATE TABLE IF NOT EXISTS estado (
    estado_id SERIAL PRIMARY KEY,
    nombre_estado VARCHAR(50) NOT NULL UNIQUE
);

-- Insertar los roles fijos del sistema
INSERT INTO rol (nombre_rol) VALUES 
('cliente'), 
('repartidor'), 
('admin') 
ON CONFLICT (nombre_rol) DO NOTHING;

-- Insertar los estados iniciales de las cuentas de usuario
INSERT INTO estado (nombre_estado) VALUES 
('activo'), 
('inactivo'), 
('suspendido'), 
('eliminado') 
ON CONFLICT (nombre_estado) DO NOTHING;


-- =========================================================================
-- ORDEN 2: MÓDULO AUTH & USERS (Depende de rol y estado)
-- =========================================================================

CREATE TABLE IF NOT EXISTS usuario (
    usuario_id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(64) NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    email VARCHAR(128) NOT NULL UNIQUE,
    rol_id INT NOT NULL,
    estado_id INT NOT NULL,
    CONSTRAINT fk_usuario_rol FOREIGN KEY (rol_id) REFERENCES rol(rol_id),
    CONSTRAINT fk_usuario_estado FOREIGN KEY (estado_id) REFERENCES estado(estado_id)
);

CREATE TABLE IF NOT EXISTS contacto (
    contacto_id SERIAL PRIMARY KEY,
    phone_personal VARCHAR(20),
    phone_trabajo VARCHAR(20),
    domicilio VARCHAR(255),
    usuario_id INT NOT NULL UNIQUE,
    CONSTRAINT fk_contacto_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS direccion (
    direccion_id SERIAL PRIMARY KEY,
    direccion_texto VARCHAR(255) NOT NULL,
    latitud NUMERIC(10, 8),
    longitud NUMERIC(11, 8),
    referencia VARCHAR(255),
    etiqueta VARCHAR(50), 
    es_temporal BOOLEAN DEFAULT FALSE,
    usuario_id INT NOT NULL,
    CONSTRAINT fk_direccion_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id) ON DELETE CASCADE
);


-- =========================================================================
-- ORDEN 3: MÓDULO RESTAURANTS (Independiente al inicio)
-- =========================================================================

CREATE TABLE IF NOT EXISTS restaurante (
    restaurant_id SERIAL PRIMARY KEY,
    nombre VARCHAR(128) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    contacto VARCHAR(50),
    horario_apertura TIME,
    horario_cierre TIME,
    estado VARCHAR(20) DEFAULT 'Abierto' CHECK (estado IN ('Abierto', 'Cerrado'))
);

CREATE TABLE IF NOT EXISTS producto (
    producto_id SERIAL PRIMARY KEY,
    nombre VARCHAR(128) NOT NULL,
    descripcion TEXT,
    precio NUMERIC(10, 2) NOT NULL CHECK (precio >= 0),
    disponible BOOLEAN DEFAULT TRUE,
    categoria VARCHAR(64) NOT NULL,
    restaurant_id INT NOT NULL,
    CONSTRAINT fk_producto_restaurante FOREIGN KEY (restaurant_id) REFERENCES restaurante(restaurant_id) ON DELETE CASCADE
);


-- =========================================================================
-- ORDEN 4: MÓDULO DELIVERY / TRACKING (Depende de usuario)
-- =========================================================================

CREATE TABLE IF NOT EXISTS repartidor (
    repartidor_id SERIAL PRIMARY KEY,
    tipo_vehiculo VARCHAR(20) NOT NULL CHECK (tipo_vehiculo IN ('Bicicleta', 'Moto', 'Taxi')),
    placa VARCHAR(20),
    disponible BOOLEAN DEFAULT TRUE,
    usuario_id INT DEFAULT NULL,
    CONSTRAINT fk_repartidor_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ubicacion_tracking (
    ubicacion_tracking_id SERIAL PRIMARY KEY,
    latitud NUMERIC(10, 8) NOT NULL,
    longitud NUMERIC(11, 8) NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    repartidor_id INT NOT NULL,
    CONSTRAINT fk_tracking_repartidor FOREIGN KEY (repartidor_id) REFERENCES repartidor(repartidor_id) ON DELETE CASCADE
);


-- =========================================================================
-- ORDEN 5: MÓDULO ORDERS & PAYMENTS (Depende de usuario, restaurante, repartidor y producto)
-- =========================================================================

CREATE TABLE IF NOT EXISTS pedido (
    pedido_id SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sum_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    notas_cliente TEXT,
    estado VARCHAR(30) DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'En_Preparacion', 'En_Camino', 'Entregado', 'Cancelado')),
    tiempo_estimado_min INT DEFAULT 30,
    permite_cancelacion BOOLEAN DEFAULT TRUE,
    usuario_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    repartidor_id INT DEFAULT NULL,
    CONSTRAINT fk_pedido_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id),
    CONSTRAINT fk_pedido_restaurante FOREIGN KEY (restaurant_id) REFERENCES restaurante(restaurant_id),
    CONSTRAINT fk_pedido_repartidor FOREIGN KEY (repartidor_id) REFERENCES repartidor(repartidor_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS detalle_pedido (
    detalle_pedido_id SERIAL PRIMARY KEY,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    CONSTRAINT fk_detalle_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(pedido_id) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_producto FOREIGN KEY (producto_id) REFERENCES producto(producto_id)
);

CREATE TABLE IF NOT EXISTS pago (
    pago_id SERIAL PRIMARY KEY,
    monto NUMERIC(10, 2) NOT NULL CHECK (monto > 0),
    metodo_pago VARCHAR(20) NOT NULL CHECK (metodo_pago IN ('Efectivo', 'Tarjeta', 'QR')),
    estado_pago VARCHAR(20) DEFAULT 'Pendiente' CHECK (estado_pago IN ('Completado', 'Fallido', 'Pendiente')),
    transaccion_id VARCHAR(128) UNIQUE,
    fecha DATE NOT NULL,
    pedido_id INT NOT NULL UNIQUE,
    CONSTRAINT fk_pago_pedido FOREIGN KEY (pedido_id) REFERENCES pedido(pedido_id) ON DELETE CASCADE
);