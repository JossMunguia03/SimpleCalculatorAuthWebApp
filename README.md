# Calculadora con Autenticación Google

Esta es una aplicación web sencilla que combina una calculadora con autenticación de Google usando Auth0. La aplicación permite a los usuarios realizar operaciones matemáticas básicas después de autenticarse, y almacena las sesiones en una base de datos local.

## Requisitos

- Python 3.7 o superior
- pip (gestor de paquetes de Python)
- Cuenta de Google para autenticación
- Cuenta de Auth0 para configuración

## Instalación

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:
```
AUTH0_CLIENT_ID=tu_client_id
AUTH0_CLIENT_SECRET=tu_client_secret
AUTH0_DOMAIN=tu_dominio
APP_SECRET_KEY=una_clave_secreta
```

## Configuración de Auth0

1. Crea una cuenta en [Auth0](https://auth0.com)
2. Crea una nueva aplicación
3. Configura las URLs de callback:
   - Allowed Callback URLs: `http://localhost:3000/callback`
   - Allowed Logout URLs: `http://localhost:3000`
   - Allowed Web Origins: `http://localhost:3000`
4. Copia las credenciales (Client ID y Client Secret) al archivo `.env`

## Estructura del Proyecto

```
.
├── server.py              # Archivo principal de la aplicación
├── requirements.txt       # Dependencias del proyecto
├── .env                  # Variables de entorno
├── calculator.db         # Base de datos SQLite
└── templates/
    ├── home.html        # Template de la calculadora
    └── admin.html       # Template del panel de administración
```

## Uso

1. Inicia la aplicación:
```bash
python server.py
```

2. Abre tu navegador y ve a `http://localhost:3000`

3. Inicia sesión con tu cuenta de Google

4. Usa la calculadora:
   - Ingresa los números que desees calcular
   - Usa el botón "Agregar número" para más campos
   - Selecciona la operación deseada
   - El resultado se mostrará en la parte inferior

5. Accede al panel de administración:
   - Ve a `http://localhost:3000/admin`
   - Solo accesible con el email configurado como administrador
   - Gestiona las sesiones activas

## Base de Datos

La aplicación utiliza SQLite para almacenar las sesiones. La estructura de la base de datos es:

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    email TEXT,
    token TEXT,
    created_at TIMESTAMP
)
```

## API Endpoints

- `GET /`: Página principal con la calculadora
- `GET /login`: Inicio de sesión con Google
- `GET /callback`: Callback de autenticación
- `GET /logout`: Cierre de sesión
- `POST /calculate`: Realiza operaciones matemáticas
- `GET /admin`: Panel de administración
- `GET /admin/sessions`: Obtiene lista de sesiones
- `DELETE /admin/sessions/<id>`: Elimina una sesión

## Seguridad

- Autenticación mediante Auth0
- Protección de rutas administrativas
- Validación de datos en operaciones matemáticas
- Almacenamiento seguro de tokens
- Confirmación antes de eliminar sesiones


### Cambiar el Administrador

Para cambiar el email del administrador, modifica la siguiente línea en `server.py`:
```python
if session["user"]["userinfo"]["email"] != "tu_email@ejemplo.com":
```
