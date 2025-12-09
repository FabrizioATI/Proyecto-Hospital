# Manual de Operaciones - Sistema de Gestión de Citas Médicas

## 1. Requisitos Técnicos

### Software Requerido
- **Python 3.8 o superior**
- **Django 5.2.6**
- **SQLite3** (base de datos incluida)
- **Git** (para control de versiones)

### Dependencias de Terceros
- `asgiref==3.9.2` - Gestor de eventos asincronos
- `sqlparse==0.5.3` - Parser SQL
- `tzdata==2025.2` - Datos de zonas horarias
- `holidays` - Librerías de días festivos
- `secure-smtplib==0.1.1` - Envío seguro de correos
- `twilio>=8.0.0` - Servicio de SMS

### Hardware Mínimo Recomendado
- CPU: Dual-core 2.0 GHz
- RAM: 2 GB mínimo
- Almacenamiento: 500 MB libre
- Conexión a Internet: 1 Mbps

---

## 2. Instalación y Configuración Inicial

### 2.1 Clonar el Repositorio
```powershell
git clone https://github.com/FabrizioATI/Proyecto-Hospital.git
cd Proyecto-Hospital
```

### 2.2 Crear Entorno Virtual
```powershell
# En Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2.3 Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 2.4 Configurar Base de Datos
```powershell
# Realizar migraciones
python manage.py migrate

# Crear superusuario para acceso de administración
python manage.py createsuperuser

# Cargar datos de prueba (opcional)
python manage.py loaddata fixtures/datos_base.json
```

---

## 3. Despliegue Local (Desarrollo)

### 3.1 Ejecutar el Servidor
```powershell
python manage.py runserver
```

El sistema estará disponible en: `http://127.0.0.1:8000`

### 3.2 Panel de Administración Django
Acceder a: `http://127.0.0.1:8000/admin`
- Usa el usuario y contraseña del superusuario creado

### 3.3 Variables de Configuración en `settings.py`
```python
DEBUG = True                    # Cambiar a False en producción
ALLOWED_HOSTS = ['127.0.0.1']  # Agregar dominios reales
SECRET_KEY = '...'              # Usar variable de entorno en producción
```

---

## 4. Configuración de Servicios Externos

### 4.1 Servicio de SMS (Twilio)
En `Integrador/settings.py`:
```python
# Configurar credenciales de Twilio
TWILIO_ACCOUNT_SID = "tu_account_sid"
TWILIO_AUTH_TOKEN = "tu_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"
```
### 4.2 Encuestas de satisfacción
En `Integrador/settings.py`:
```python
# Configurar credenciales de Twilio
SURVEY_URL = os.getenv('SURVEY_URL', 'Enlace de encuestas')
```
---

## 5. Estructura del Proyecto

```
Proyecto-Hospital/
├── administrador/         # Gestión administrativa
├── database/             # Modelos y base de datos
├── login/                # Autenticación de usuarios
├── citas/                # Lógica de citas
├── horarios/             # Gestión de horarios
├── medico/               # Panel médico
├── paciente/             # Panel paciente
├── Integrador/           # Configuración principal Django
├── templates/            # Plantillas HTML
├── manage.py             # CLI de Django
└── requirements.txt      # Dependencias
```

### Módulos Principales

| Módulo | Responsabilidad |
|--------|-----------------|
| `database.models` | Define todas las entidades (Entidad, Rol, Especialidad, Cita, etc.) |
| `citas.views` | Vistas para gestión de citas y lista de citas |
| `citas.services` | Lógica de negocio para solicitar y gestionar citas |
| `citas.sms_service` | Integración con Twilio para envío de SMS |
| `horarios.views` | Vistas para gestión de horarios médicos |
| `login.views` | Autenticación y registro de usuarios |
| `administrador.views` | Mantenimiento de roles y especialidades |

---

## 6. Casos de Uso Principales

### Caso 1: Registro de Nuevo Paciente
1. Usuario accede a `/register`
2. Completa formulario: nombre, apellidos, DNI, correo, teléfono, contraseña
3. Sistema valida unicidad de DNI y correo
4. Se crea registro en tabla `Entidad` con rol "Paciente" (002)
5. Se genera entrada en `RolEntidad`

### Caso 2: Agendar Cita (Paciente)
1. Paciente accede a vista de citas
2. Selecciona especialidad deseada
3. Sistema valida si requiere derivación (`Especialidad.requiere_derivacion`)
4. Si requiere: verifica existencia de `Derivacion` válida
5. Muestra doctores disponibles con sus horarios
6. Paciente selecciona fecha/hora disponible
7. Sistema crea registro en `Cita` (estado: pendiente)
8. Se envía notificación por SMS/email según preferencias

### Caso 3: Confirmar Cita (Médico)
1. Médico accede a su lista de citas
2. Revisa detalles de la cita programada
3. Puede confirmar, reprogramar o cancelar
4. Sistema actualiza `Cita.estado` y notifica al paciente

### Caso 4: Crear Derivación (Médico a Especialista)
1. Durante la consulta, médico genera derivación
2. Especifica especialidad destino
3. Sistema crea registro en `Derivacion`
4. Define fecha de expiración (ej: 6 meses)
5. Paciente recibe notificación y puede usar derivación

---

## 7. Gestión de Base de Datos

### 7.1 Esquema Principal
```
Entidad (usuarios)
├── id, nombre, apellidos, DNI, correo, teléfono
└── RolEntidad (relación con roles)

Rol
├── codigo_rol (001=Doctor, 002=Paciente, 003=Admin)
└── nombre_rol

Especialidad
├── nombre
├── capacidad_por_hora
└── requiere_derivacion

DoctorDetalle
├── entidad → Entidad
├── especialidad → Especialidad
├── nro_colegiatura
├── cupos_diarios, cupos_semanales

DoctorHorario
├── doctor → DoctorDetalle
├── dia_semana
├── hora_inicio, hora_fin

Cita
├── paciente → Entidad
├── doctor_horario → DoctorHorario
├── fecha, estado, recordatorio_2h_enviado

Derivacion
├── paciente → Entidad
├── especialidad → Especialidad
├── fecha_emision, fecha_expiracion
└── valido (boolean)
```

### 7.2 Comandos Útiles
```powershell
# Crear migrations de cambios en modelos
python manage.py makemigrations

# Ver estado de migraciones
python manage.py showmigrations

# Backup de base de datos
Copy-Item db.sqlite3 db.sqlite3.backup

# Limpiar cache de migraciones
python manage.py migrate --fake database zero
```

---

## 8. Monitoreo y Mantenimiento

### 8.1 Logs
Revisar archivo de logs (si está configurado):
```powershell
Get-Content logs/application.log -Tail 50
```

### 8.2 Tareas Periódicas
- **Diarias:** Verificar citas de las próximas 2 horas para recordatorios
- **Semanales:** Revisar derivaciones próximas a expirar
- **Mensuales:** Limpiar sesiones expiradas

### 8.3 Rendimiento
```powershell
# Ver uso de recursos
Get-Process python

# Verificar tamaño de base de datos
(Get-Item db.sqlite3).Length / 1MB
```

---

## 9. Despliegue en Producción

### 9.1 Preparación
1. Cambiar `DEBUG = False` en `settings.py`
2. Usar SECRET_KEY desde variable de entorno
3. Configurar HTTPS y certificados SSL
4. Cambiar base de datos a PostgreSQL (recomendado)
5. Configurar ALLOWED_HOSTS con dominios reales

### 9.2 Usar Gunicorn (servidor WSGI)
```powershell
pip install gunicorn
gunicorn Integrador.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 9.3 Configurar Nginx como Reverse Proxy
```nginx
server {
    listen 80;
    server_name tudominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }
}
```

---

## 10. Troubleshooting

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError: No module named 'django'` | Dependencias no instaladas | Ejecutar `pip install -r requirements.txt` |
| `django.core.exceptions.ImproperlyConfigured` | Base de datos no configurada | Ejecutar `python manage.py migrate` |
| `PermissionError: db.sqlite3` | Problemas de permisos | Revisar permisos de archivo en `db.sqlite3` |
| `ConnectionRefusedError` para SMS | Credenciales Twilio inválidas | Verificar `TWILIO_ACCOUNT_SID` y `AUTH_TOKEN` |
| Citas no se notifican | Email/SMS no configurados | Revisar configuración en `settings.py` |

---

## 11. Contacto y Soporte

Para soporte técnico o preguntas de despliegue:
- **Email:** soporte@hospital.local
- **Repositorio:** https://github.com/FabrizioATI/Proyecto-Hospital
- **Documentación API:** Disponible en `/admin/`

**Última actualización:** Diciembre 2025
