# Aplicacion de administracion de servicios de mantenimiento de vehiculos
Es una aplicacion de escritorio desarrollada en Python que permite gestionar y llevar un control detallado de los servicios de mantenimiento realizados a vehiculos. La aplicacion ofrece una interfaz amigable y funcional para registrar, actualizar y visualizar informacion relevante sobre los vehiculos, compra y venta de partes, y los servicios de mantenimiento realizados.
## Caracteristicas principales
- Registro de reparaciones: Permite ingresar y almacenar informacion detallada sobre cada servicio de mantenimiento realizado, incluyendo fecha, tipo de servicio, costo y observaciones.+
- Gestion de vehiculos: Facilita el seguimiento de los vehiculos, incluyendo datos como marca, modelo, año, kilometraje y estado general.
- Inventario de partes: Permite llevar un control del inventario de partes y repuestos, incluyendo cantidades disponibles, ubicacion y proveedores.
- Reportes y estadisticas: Genera reportes detallados sobre los servicios realizados, costos asociados y tendencias de mantenimiento.
- Interfaz de usuario intuitiva: Utiliza una interfaz grafica amigable que facilita la navegacion y el uso de la aplicacion.
## Requisitos
- Python 3.10 o superior
- Librerias necesarias: customtkinter, Pillow
## Instalacion
1. Clona este repositorio en tu maquina local.
   ```bash
   git clone <URL_DEL_REPOSITORIO>
    ```
2. Navega al directorio del proyecto.
   ```bash
   cd InventarioMecanico
   ```
3. Instala las dependencias necesarias.
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la aplicacion.
   ```bash
   python main.py
   ```
## Uso
- Al iniciar la aplicacion, se mostrara la interfaz principal donde podras acceder a las diferentes secciones como registro de reparaciones, gestion de vehiculos e inventario de partes.
- Utiliza los formularios proporcionados para ingresar nueva informacion o actualizar la existente.
- Navega a traves de los menus para generar reportes y visualizar estadisticas.
## Estructura del proyecto
```bash
taller_mecanico/
│
├── main.py                            # Ejecuta la app (usa TallerApp)
│
├── data/
│   ├── database.sql                   # Tu script SQL original
│   └── db_manager.py                  # Conexión y creación automática de tablas
│
├── domain/                            # Capa de negocio (entidades, lógica)
│   └── cliente_entity.py
│
├── repositories/                      # Capa de datos (consultas SQL)
│   └── cliente_repository.py
│
├── services/                          # Capa de aplicación (coordinación entre repo y vista)
│   └── cliente_service.py
│
├── ui/                                # Capa de presentación
│   ├── app_main.py                    # Tu clase TallerApp adaptada
│   ├── views/
│   │   └── cliente_view.py            # Pantalla de gestión de clientes
│   └── assets/icons/                  # Íconos
│
└── config/
    └── colors.py
```

## Contribuciones
Las contribuciones son bienvenidas! Si deseas mejorar esta aplicacion, por favor sigue estos pasos:
1. Haz un fork de este repositorio.
2. Crea una nueva rama para tu caracteristica o correccion de errores.
3. Realiza tus cambios y haz commit de los mismos.
4. Envía un pull request describiendo tus cambios.
## Licencia
Este proyecto esta licenciado bajo la Licencia MIT. Consulta el archivo LICENSE para mas detalles.  