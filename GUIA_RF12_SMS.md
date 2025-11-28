# Guía de Ejecución: RF12 - Notificaciones SMS con Twilio

## 1️⃣ INSTALACIÓN DE DEPENDENCIAS

```powershell
# Navegar al directorio del proyecto

# Instalar/actualizar dependencias
pip install -r requirements.txt

En caso de error al instalar twilio ejecutar este comando en consola:
pip install twilio
```

---

## 2️⃣ CONFIGURACIÓN DE TWILIO

### Configurar las claves para twilio:

Editar `Integrador/settings.py` y rellenar las variables en caso tengas cuenta: (Revisar en el archivo)

---
## -------------- (INICIO - NO ES NECESARIO REALIZAR ESTA PARTE) --------------

## 3️⃣ CONFIGURAR VARIABLES DE ENTORNO 

### Opción 1: Archivo `.env` (Recomendado)

Crear archivo `.env` en la raíz del proyecto:

```
TWILIO_ACCOUNT_SID=tu_account_sid_aqui
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_PHONE_NUMBER=+12025551234
```

Luego cargar en `settings.py` con `python-dotenv`:

```powershell
pip install python-dotenv
```

Agregar al inicio de `settings.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Opción 2: Variables de Entorno del Sistema (Windows)

```powershell
# En PowerShell
$env:TWILIO_ACCOUNT_SID = "tu_account_sid"
$env:TWILIO_AUTH_TOKEN = "tu_auth_token"
$env:TWILIO_PHONE_NUMBER = "+12025551234"

# Verificar
Get-ChildItem Env:TWILIO*
```
## -------------- (FIN - NO ES NECESARIO REALIZAR ESTA PARTE) --------------

---

## 4️⃣ CREAR/ACTUALIZAR BASE DE DATOS

```powershell
# Crear migraciones del nuevo modelo SMSNotification
py manage.py makemigrations

# Aplicar migraciones
py manage.py migrate
```

---

## 5️⃣ EJECUTAR SERVIDOR

```powershell
# Iniciar servidor Django
py manage.py runserver

# El servidor estará disponible en:
# http://127.0.0.1:8000/
```

---

## 6️⃣ PRUEBAS EN LA UI

### Flujo para probar RF12:

1. **Acceder a la aplicación**: http://127.0.0.1:8000/

2. **Iniciar sesión como paciente**
   - Usuario: tu usuario de paciente
   - Contraseña: tu contraseña

3. **Solicitar una cita**
   - Ir a "Solicitar Cita"
   - Seleccionar especialidad, doctor y motivo
   - Enviar solicitud

4. **Administrador asigna horario**
   - Iniciar sesión como admin
   - Ir a "Gestionar Citas"
   - Asignar horario disponible a la cita

5. **Paciente hace check-in (RF12 se activa)**
   - Ir a "Mis Citas"
   - Hacer click en "Confirmar/Check-in"
   - **→ Se envía SMS de recordatorio al paciente**

6. **Verificar notificación SMS**
   - En **Admin > SMS Notifications**, se verá:
     - Estado: "enviado" o "entregado"
     - Teléfono destino
     - Mensaje enviado
     - Timestamp y SID de Twilio

---

## 7️⃣ VERIFICAR LOGS

```powershell
# Ver logs en consola mientras se ejecuta el servidor
# Los logs mostrarán:
# - SMS enviado exitosamente
# - Errores de Twilio
# - Números de teléfono sin configurar

# Para logs más detallados, habilitar DEBUG en settings.py:
DEBUG = True  # Ya debe estar en True
```

---

## 8️⃣ MODELO DE DATOS PARA SMS

**Tabla: `database_smsnotification`**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | PK | Identificador único |
| `cita_id` | FK | Referencia a la cita |
| `paciente_id` | FK | Referencia al paciente |
| `telefono` | CharField | Número destino |
| `tipo` | CharField | recordatorio/instrucciones/llamado |
| `mensaje` | TextField | Contenido SMS |
| `estado` | CharField | pendiente/enviado/entregado/fallido |
| `sid` | CharField | ID de Twilio para tracking |
| `intento` | PositiveSmallInteger | Número de reintento |
| `fecha_creacion` | DateTime | Timestamp de creación |
| `fecha_envio` | DateTime | Timestamp de envío |
| `fecha_entrega` | DateTime | Timestamp de entrega |
| `respuesta_twilio` | TextField | JSON con respuesta de Twilio |

---

## 9️⃣ TROUBLESHOOTING

### Error: "TWILIO_ACCOUNT_SID no configurado"
- Verificar variables de entorno
- Ejecutar: `echo $env:TWILIO_ACCOUNT_SID` en PowerShell

### Error: "Credenciales de Twilio inválidas"
- Verificar SID y Token en [console.twilio.com](https://console.twilio.com)
- Asegurarse de no tener espacios extras

### SMS no llega
- Verificar número de teléfono en formato `+<código_país><número>`
- Si es Twilio Sandbox, el número debe estar verificado previamente
- Ver logs en Django para detalles del error

### Error: "ModuleNotFoundError: No module named 'twilio'"
```powershell
pip install twilio>=8.0.0
```

---

## 🔟 ENDPOINTS ÚTILES (ADMIN)

```
http://127.0.0.1:8000/admin/database/smsnotification/
```

Panel admin para:
- Ver todos los SMS enviados
- Filtrar por estado (enviado, entregado, fallido)
- Filtrar por fecha
- Buscar por paciente o teléfono

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Dependencia `twilio` agregada a `requirements.txt`
- [x] Modelo `SMSNotification` creado en `database/models.py`
- [x] Archivo `citas/sms_service.py` con lógica de envío
- [x] Integración en `citas/services.py` (registrar_checkin)
- [x] Configuración de Twilio en `settings.py`
- [x] Variables de entorno configuradas en el sistema
- [x] Migraciones ejecutadas (`makemigrations` + `migrate`)
- [x] Servidor iniciado y funcionando
- [x] Pruebas completadas en la UI

---

**RF12 - Notificaciones SMS implementado correctamente ✅**
