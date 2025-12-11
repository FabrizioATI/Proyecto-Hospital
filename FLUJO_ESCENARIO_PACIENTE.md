# Flujo del Paciente en el Hospital

## 1. Paciente Nuevo - Primeros Pasos

**Vista**: `login/templates/accounts/registrar.html`

El paciente ingresa al sistema y se registra con sus datos:
- DNI
- Nombre completo
- Teléfono y email
- Antecedentes médicos básicos

Se crea automáticamente su **Historia Clínica**.

## 1.5 Seguridad: Contraseña y Verificación

**Vista**: `login/templates/accounts/registrar.html`

Durante el registro, el sistema debe:

1. **Generar contraseña temporal segura** (ej: `Hosp2024#Temporal`)
   - El paciente la recibe vía **SMS o Email**
   - Debe cambiarla en el primer login

2. **En el primer login**:
   - El paciente ingresa DNI + contraseña temporal
   - El sistema lo obliga a crear **nueva contraseña personal**
   - Requisitos: Mínimo 8 caracteres, mayúsculas, números y símbolos

3. **Alternativa: Sin contraseña inicial**
   - El sistema envía **link de activación** al email
   - El paciente hace click → Establece su propia contraseña
   - Válido por 24 horas

**Recomendación**: Usar la opción 2 (link de activación) es más segura y amigable.

## 2. Agendar una Cita

**Vista**: `citas/templates/citas/registrar_cita.html`

El paciente selecciona:
- **Especialidad** (Cardiología, Dermatología, etc.)
- **Médico** disponible
- **Tipo**: Presencial o Virtual
- **Motivo** de la consulta
- **Clasificación**: Emergencia, Adulto Mayor, Regular

## 3. Sistema Genera Oferta de Cupo

**Función**: `citas/views.py:registrar_cita_paciente()`

El sistema automáticamente:
- Ordena por prioridad (emergencia primero)
- Busca un horario disponible
- **Notifica al paciente** vía SMS/Email con la oferta
- El paciente tiene **15 minutos** para aceptar

### Si el paciente acepta:
✅ Cita confirmada → Entra en la cola del médico

### Si rechaza o no responde:
↻ Vuelve a la cola → Se intenta otra oferta después

## 4. Recordatorios Automáticos

El paciente recibe notificaciones:
- **48 horas antes**: "Tu cita es en 2 días"
- **2 horas antes**: "Tu cita es hoy en 2 horas"

## 5. Día de la Cita - Llegada al Hospital

**Vista**: `citas/views.py:checkin_view()`

El paciente llega y se registra en **recepción**:
- El sistema lo busca por DNI
- Confirmación de datos
- **Check-in**: Se marca como presente

## 6. En la Sala de Espera

**Vista**: `citas/templates/citas/lista_citas.html`

El paciente ve una **pantalla** que muestra:
- Su turno actual
- Posición en la cola
- Próximo turno a atender

## 7. Consultorio del Médico

**Función**: `citas/views.py:marcar_cita_atendida()`

El médico:
- **Examina** al paciente
- Toma **signos vitales** (presión, temperatura, etc.)
- Hace el **diagnóstico**
- Crea **plan de tratamiento**
- Genera **notas en la Historia Clínica**

Todo se registra automáticamente en `citas/templates/ehr/`

## 8. Después de la Consulta

- La cita se marca como **ATENDIDA**
- El paciente recibe **email** con resumen de la consulta
- Puede ver su **Historia Clínica actualizada**

---

## 🏥 Paciente que Llega sin Cita Previa

**Vistas**: `paciente/templates/paciente/registrar_pacientes.html` + `citas/templates/citas/registrar_cita.html`

### Paso a Paso:

1. **Recepcionista lo atiende** → Busca si es paciente existente
2. **Si NO existe**: Lo registra rápidamente con datos básicos
3. **Triage**: Evalúa urgencia (emergencia, adulto mayor, regular)
4. **El sistema ordena la cola** según urgencia (`citas/views.py:procesar_cola_doctor()`)
5. **Se asigna médico** disponible
6. **Espera en sala** con número de turno visible
7. **Lo llama el médico** → Misma consulta que agendado
8. **Se actualiza Historia Clínica**

---

## 📊 Diferencias Principales

| Aspecto | Agendado | Sin Cita |
|---------|----------|---------|
| **Registro** | Por plataforma | En recepción |
| **Espera** | Conocida | Estimada |
| **Prioridad** | Según clasificación | Según urgencia |
| **Notificaciones** | Automáticas | En mostrador |

---

## ✅ Puntos Clave

✓ **Todo es automático**: El sistema gestiona colas, prioridades y notificaciones

✓ **Paciente siempre informado**: Recibe SMS/email en cada paso

✓ **Historia Clínica integrada**: Todos los doctores ven el historial completo

✓ **Flexible**: Puede aceptar/rechazar ofertas de cupo

✓ **Seguro**: Datos protegidos y auditoría completa
