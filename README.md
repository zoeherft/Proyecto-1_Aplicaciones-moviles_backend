# Sistema Escolar Backend

Backend en Django destinado a cubrir los procesos basicos de un sistema escolar: administracion de usuarios (administradores, Alumnos y maestros), autenticacion por token y utilidades para cifrado, envio de correo y generacion de llaves. El proyecto se encuentra preparado para ejecutarse de manera local con MySQL y para desplegarse en Google App Engine.

## Tabla de contenidos
- [Descripcion general](#descripcion-general)
- [Tecnologias principales](#tecnologias-principales)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos previos](#requisitos-previos)
- [Configuracion del entorno local](#configuracion-del-entorno-local)
- [Variables y secretos](#variables-y-secretos)
- [Modelos y migraciones](#modelos-y-migraciones)
- [Vistas y endpoints](#vistas-y-endpoints)
- [Autenticacion](#autenticacion)
- [Utilidades y servicios internos](#utilidades-y-servicios-internos)
- [Panel de administracion](#panel-de-administracion)
- [Comandos frecuentes](#comandos-frecuentes)
- [Despliegue en Google App Engine](#despliegue-en-google-app-engine)
- [Siguientes pasos sugeridos](#siguientes-pasos-sugeridos)

## Descripcion general
- Persistencia en MySQL mediante `pymysql`, con soporte Unicode (`utf8mb4`) y configuracion centralizada a traves de `my.cnf`.
- API construida con Django REST Framework, orientada a crear perfiles y sesiones para personal administrativo, Alumnos y maestros.
- Seguridad basada en tokens Bearer reutilizando `rest_framework.authtoken`.
- Integracion prevista con Google Cloud Storage (mediante su SDK) y despliegue listo para App Engine.
- Cobertura de tareas auxiliares como cifrado simetrico de datos, generacion de codigos y envio asincrono de correo.

## Tecnologias principales
- Python 3.12 (requerido por el `runtime` de App Engine).
- Django 5.0.2 y Django REST Framework 3.16.
- MySQL consumido via `pymysql`.
- django-cors-headers y django-filter para integraciones web modernas.
- Google Cloud SDK (`gcloud`) para despliegues.
- Librerias adicionales: `cryptography`, `Pillow`, `requests`, `google-cloud-storage`.

## Estructura del proyecto
```
backend/
  app.yaml                 # Configuracion para Google App Engine.
  deploy.sh                # Script de despliegue (gcloud app deploy --project ...).
  main.py                  # Punto de entrada WSGI usado por App Engine.
  manage.py                # Utilidad standard de Django para comandos administrativos.
  my.cnf                   # Archivo de configuracion de cliente MySQL usado por Django.
  requirements.txt         # Dependencias del entorno virtual.
  static/                  # Archivos estaticos ya recolectados (admin y DRF).
  dev_sistema_escolar_api/
    __init__.py            # Registra pymysql como backend MySQL.
    admin.py               # Configuracion del admin de Django (lista Administradores).
    models.py              # Modelos ORM (Administradores + autenticacion Bearer).
    serializers.py         # Serializadores DRF para usuarios y administradores.
    settings.py            # Configuracion de Django (DB, CORS, REST, media, etc.).
    urls.py                # Rutas expuestas actualmente (admin, api-auth, version).
    wsgi.py                # Punto de entrada WSGI para servidores tradicionales.
    utils.py               # Utilidades de archivos y manejo de cadenas aleatorias.
    data_utils.py          # Generacion de llaves y helpers varios para archivos/URLs.
    cypher_utils.py        # Cifrado simetrico con Fernet (requiere CRYPTO_PASSWORD).
    puentes/
      mail.py              # Envio de correo asincrono sobre EmailMessage.
    migrations/            # Definicion de esquemas de base de datos.
    views/                 # Endpoints DRF (auth, bootstrap, administradores, etc.).
```

## Requisitos previos
- Python 3.12 (instalado y disponible en PATH).
- MySQL 8 (o compatible) corriendo localmente.
- `pip` actualizado (por ejemplo `python -m pip install --upgrade pip`).
- (Opcional) Google Cloud SDK (`gcloud`) configurado si se desea desplegar.

## Configuracion del entorno local
1. Crear y activar un entorno virtual (recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # En Windows: .venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Configurar acceso a MySQL editando `my.cnf` (o creando uno nuevo en el mismo directorio) con los datos de tu instancia local:
   ```ini
   [client]
   host = 127.0.0.1
   port = 3306
   database = dev_sistema_escolar_db
   user = root
   password = TU_PASSWORD
   default-character-set = utf8mb4
   ```
4. Crear la base de datos (solo la primera vez):
   ```sql
   CREATE DATABASE dev_sistema_escolar_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
5. Exportar las variables de entorno necesarias (ver seccion [Variables y secretos](#variables-y-secretos)):
   ```bash
   export CRYPTO_PASSWORD="clave-super-secreta"
   export APP_VERSION="1.0.0-local"
   # export SECRET_KEY="..."  # Recomendado en produccion
   ```
6. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```
7. Crear un superusuario para el panel administrativo (opcional pero recomendado):
   ```bash
   python manage.py createsuperuser
   ```
8. Levantar el servidor de desarrollo:
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   El proyecto quedara disponible en `http://localhost:8000/`.

## Variables y secretos
| Variable | Descripcion | Notas |
|----------|-------------|-------|
| `SECRET_KEY` | Clave interna de Django. | Obligatoria en produccion; en desarrollo se usa la definida en `settings.py`. |
| `CRYPTO_PASSWORD` | Password usado por `CypherUtils` para cifrar/descifrar strings. | Debe ser una cadena robusta; es requerida si se usan las utilidades de cifrado. |
| `APP_VERSION` | Valor devuelto por `/api/version/`. | Permite exponer la version de build al frontend. |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, etc. | Variables tipicas de configuracion de correo de Django. | Necesarias para que `puentes/mail.py` pueda enviar emails. |
| `DATABASE_URL` | No se usa. La conexion se define mediante `my.cnf`. | Asegura que el archivo `my.cnf` este presente y con permisos adecuados. |

> Consejo: En ambientes locales puedes colocar estas variables en un script `env.sh` y ejecutarlo con `source env.sh`. Para despliegues en App Engine se configuran en `app.yaml` o desde `gcloud app deploy --set-env-vars`.

## Modelos y migraciones
- `Administradores`: Perfil con campos de identificacion basicos enlazado a la tabla `auth_user`. Soporta datos como clave interna, telefono, RFC, edad y ocupacion.
- `BearerTokenAuthentication`: Subclase de `TokenAuthentication` que ajusta la palabra clave a `Bearer` para alinear la API con estandares modernos.
- Migraciones `0003_Alumnos_maestros.py` agregan modelos `Alumnos` y `Maestros` con estructura detallada (matricula, CURP, RFC, etc.). Estos modelos aun no estan declarados en `models.py`; para evitar errores al importar vistas relacionadas es necesario definirlos en dicho archivo antes de usarlos en produccion.

## Vistas y endpoints
Rutas expuestas actualmente en `dev_sistema_escolar_api/urls.py`:

| Metodo | Ruta | Vista | Descripcion |
|--------|------|-------|-------------|
| `GET` | `/admin/` | Django admin | Panel administrativo estandar. |
| `GET` | `/api-auth/login/` | DRF auth | Autenticacion basada en sesiones (para explorador DRF). |
| `GET` | `/api/version/` | `VersionView` | Devuelve JSON con `{"version": APP_VERSION}`. |

Vistas preparadas pero aun no mapeadas:
- `views.auth.CustomAuthToken`: Login por token (POST) que devuelve `token`, datos del usuario y roles.
- `views.auth.Logout`: Revoca el token actual (GET) para un usuario autenticado.
- `views.admin.AdminView`: Crea usuarios y perfiles de administradores.
- `views.Alumno.AlumnoView`: Crea usuarios y perfiles de Alumnos.
- `views.maestro.MaestroView`: Crea usuarios y perfiles de maestros.
- `views.users.Userme`: Placeholder para obtener datos del usuario autenticado.

Para activarlas, agrega las rutas correspondientes en `dev_sistema_escolar_api/urls.py`, por ejemplo:
```python
from dev_sistema_escolar_api.views.auth import CustomAuthToken, Logout
from dev_sistema_escolar_api.views.admin import AdminView
from dev_sistema_escolar_api.views.Alumno import AlumnoView
from dev_sistema_escolar_api.views.maestro import MaestroView

urlpatterns += [
    path("api/auth/login/", CustomAuthToken.as_view(), name="api-login"),
    path("api/auth/logout/", Logout.as_view(), name="api-logout"),
    path("api/admin/registrar/", AdminView.as_view(), name="api-admin-create"),
    path("api/Alumnos/registrar/", AlumnoView.as_view(), name="api-Alumno-create"),
    path("api/maestros/registrar/", MaestroView.as_view(), name="api-maestro-create"),
]
```

## Autenticacion
- Basada en `rest_framework.authtoken`. Cada usuario obtiene un token persistente almacenado en base de datos.
- Las vistas protegidas por `BearerTokenAuthentication` esperan el header `Authorization: Bearer <token>`.
- Para revocar tokens se usa `Logout`, que elimina el token asociado al usuario autenticado.
- Las vistas de creacion de perfiles (`AdminView`, `AlumnoView`, `MaestroView`) generan usuarios en `auth_user`, asignan roles como `Group` y luego vinculan el perfil especifico.

## Utilidades y servicios internos
- `cypher_utils.CypherUtils`: Cifrado y descifrado utilizando Fernet + PBKDF2. Se requiere `CRYPTO_PASSWORD`.
- `data_utils.DataUtils`: Genera llaves de 4 bloques, strings numericos, detecta mimetypes basicos y valida URLs.
- `utils.Utils`: Conversion de archivos a base64 y generacion de cadenas aleatorias.
- `puentes.mail.MailsBridge`: Envia correos de forma sincrona o asincrona; reemplaza caracteres con acentos por entidades HTML antes de enviar.
- `views.bootstrap.VersionView`: Permite que el frontend obtenga la version actual del backend para diagnostico.

## Panel de administracion
- Accesible en `/admin/`.
- `dev_sistema_escolar_api/admin.py` registra el modelo `Administradores` con lista y filtros basicos.
- Recuerda crear un superusuario (`python manage.py createsuperuser`) para acceder.

## Comandos frecuentes
| Comando | Uso |
|---------|-----|
| `python manage.py runserver` | Levantar el servidor local en `http://127.0.0.1:8000/`. |
| `python manage.py migrate` | Aplicar migraciones pendientes. |
| `python manage.py makemigrations` | Generar migraciones cuando se actualizan modelos. |
| `python manage.py createsuperuser` | Crear un usuario administrador para el panel. |
| `python manage.py shell` | Abrir shell interactiva con contexto de Django. |
| `python manage.py collectstatic` | Copiar archivos estaticos a `STATIC_ROOT` (requerido para despliegues). |

> Por ahora no existen pruebas automatizadas en el repositorio. Para iniciarlas puedes ejecutar `python manage.py test` como base al agregarlas.

## Despliegue en Google App Engine
1. Asegurate de tener `gcloud` instalado y autenticarte:
   ```bash
   gcloud auth login
   gcloud config set project TU_PROYECTO
   ```
2. Verifica que `app.yaml` tenga las rutas estaticas correctas y define variables de entorno adicionales si es necesario (bloque `env_variables`).
3. Ejecuta `python manage.py collectstatic` y confirma que los archivos queden en la carpeta configurada (`static/` o `STATIC_ROOT` segun ajustes).
4. Despliega con:
   ```bash
   ./deploy.sh
   ```
   (Actualiza `--project` en el script o agrega `gcloud app deploy --project TU_PROYECTO` manualmente).
5. Monitorea el despliegue:
   ```bash
   gcloud app logs tail -s default
   ```

## Siguientes pasos sugeridos
1. Declarar en `models.py` las clases `Alumnos` y `Maestros` para alinear el ORM con las migraciones existentes.
2. Registrar las vistas de autenticacion y gestion de perfiles en `urls.py` y protegerlas con permisos adecuados.
3. Configurar variables de correo (`EMAIL_HOST`, etc.) y agregar pruebas automatizadas para validar los flujos de registro y login.
