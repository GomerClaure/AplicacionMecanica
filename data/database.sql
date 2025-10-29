-- ==================================================
-- TALLER MECÁNICO - MODELO ESCALABLE
-- Autor: Rafael
-- Fecha: 2025-10-28
-- ==================================================

-- ==================================================
-- 1. CLIENTES Y VEHÍCULOS
-- ==================================================

CREATE TABLE Clientes (
    cliente_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(30),
    email VARCHAR(100) UNIQUE,
    direccion VARCHAR(255)
);

CREATE TABLE Vehiculos (
    vehiculo_id SERIAL PRIMARY KEY,
    cliente_id INT NOT NULL REFERENCES Clientes(cliente_id) ON DELETE CASCADE,
    placa VARCHAR(20) UNIQUE NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    anio INT,
    kilometraje_actual INT
);

-- ==================================================
-- 2. PERSONAL Y USUARIOS (Escalable)
-- ==================================================

CREATE TABLE Personal (
    personal_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(50), -- Ej: Mecanico, Administrador, Recepcionista
    telefono VARCHAR(30)
);

CREATE TABLE Usuarios (
    usuario_id SERIAL PRIMARY KEY,
    personal_id INT REFERENCES Personal(personal_id) ON DELETE CASCADE,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol_sistema VARCHAR(50) DEFAULT 'Admin', -- Admin, Mecanico, Cajero, Recepcionista
    activo BOOLEAN DEFAULT TRUE
);

-- ==================================================
-- 3. REPARACIONES
-- ==================================================

CREATE TABLE Reparaciones (
    reparacion_id SERIAL PRIMARY KEY,
    vehiculo_id INT NOT NULL REFERENCES Vehiculos(vehiculo_id) ON DELETE CASCADE,
    tecnico_asignado_id INT REFERENCES Personal(personal_id),
    fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_salida_estimada DATE,
    descripcion_problema TEXT,
    descripcion_servicio_realizado TEXT,
    costo_mano_obra DECIMAL(10,2) DEFAULT 0,
    estado VARCHAR(30) DEFAULT 'Pendiente' -- Pendiente, En Curso, Finalizada, Entregada
);

-- ==================================================
-- 4. INVENTARIO Y MOVIMIENTOS
-- ==================================================

CREATE TABLE Inventario (
    repuesto_id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    stock_actual INT DEFAULT 0,
    stock_minimo INT DEFAULT 5,
    precio_venta_estandar DECIMAL(10,2)
);

CREATE TABLE MovimientosInventario (
    movimiento_id SERIAL PRIMARY KEY,
    repuesto_id INT NOT NULL REFERENCES Inventario(repuesto_id) ON DELETE CASCADE,
    reparacion_id INT REFERENCES Reparaciones(reparacion_id),
    usuario_id INT REFERENCES Usuarios(usuario_id),
    tipo_movimiento VARCHAR(20) NOT NULL, -- Ingreso, Salida
    cantidad INT NOT NULL,
    costo_unitario_kardex DECIMAL(10,2) NOT NULL,
    fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================================================
-- 5. TRANSACCIONES FINANCIERAS
-- ==================================================

CREATE TABLE Ventas (
    venta_id SERIAL PRIMARY KEY,
    cliente_id INT REFERENCES Clientes(cliente_id),
    reparacion_id INT UNIQUE REFERENCES Reparaciones(reparacion_id),
    usuario_id INT REFERENCES Usuarios(usuario_id),
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo_venta VARCHAR(20) DEFAULT 'Menor', -- Mayor (Reparación), Menor (Repuesto Directo)
    total_descuento_general DECIMAL(10,2) DEFAULT 0,
    importe_total_neto DECIMAL(10,2) NOT NULL,
    estado_pago VARCHAR(20) DEFAULT 'Pendiente', -- Pagada, Pendiente
    metodo_pago VARCHAR(30)
);

CREATE TABLE VentaDetalle (
    detalle_id SERIAL PRIMARY KEY,
    venta_id INT NOT NULL REFERENCES Ventas(venta_id) ON DELETE CASCADE,
    repuesto_id INT REFERENCES Inventario(repuesto_id),
    descripcion_item VARCHAR(255) NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario_aplicado DECIMAL(10,2) NOT NULL,
    descuento_porcentual DECIMAL(5,2) DEFAULT 0,
    subtotal_linea DECIMAL(10,2) NOT NULL,
    costo_unitario_inventario DECIMAL(10,2)
);

-- ==================================================
-- 6. COMPRAS Y PROVEEDORES
-- ==================================================

CREATE TABLE Proveedores (
    proveedor_id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(30),
    email VARCHAR(100),
    direccion VARCHAR(255)
);

CREATE TABLE Compras (
    compra_id SERIAL PRIMARY KEY,
    proveedor_id INT REFERENCES Proveedores(proveedor_id),
    usuario_id INT REFERENCES Usuarios(usuario_id),
    fecha_factura DATE,
    tipo_compra VARCHAR(20) DEFAULT 'Menor', -- Mayor (Maquinaria), Menor (Repuestos)
    importe_total DECIMAL(10,2),
    fecha_vencimiento DATE,
    estado_pago VARCHAR(20) DEFAULT 'Pendiente' -- Pagada, Pendiente
);

ALTER TABLE MovimientosInventario
ADD COLUMN compra_id INT REFERENCES Compras(compra_id);

-- ==================================================
-- 7. DATOS INICIALES (Opcionales)
-- ==================================================

-- Insertar al dueño como único usuario inicial
INSERT INTO Personal (nombre, rol, telefono)
VALUES ('Dueño del Taller', 'Administrador', '70000000');

INSERT INTO Usuarios (personal_id, username, password_hash, rol_sistema)
VALUES (1, 'admin', 'hash_temporal', 'Admin');

-- ==================================================
-- FIN DEL MODELO
-- ==================================================
