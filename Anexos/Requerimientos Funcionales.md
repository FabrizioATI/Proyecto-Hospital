# 📋 Requerimientos Funcionales – Sistema de Gestión de Citas Médicas

**Proyecto:** Sistema de Gestión de Citas Médicas con Colas Virtuales y Notificaciones SMS  
**Equipo:** 5 participantes  
**Ciclo:** 2025 - 2  
**Framework:** Django (MTV)

---

## 🟦 SPRINT 1 – Del 10/09/2025 al 27/09/2025

### **RF1: Agendamiento de citas con validación de disponibilidad**

**GIVEN** que un paciente ingresa al portal para agendar una cita y selecciona especialidad, médico, fecha y hora  
**WHEN** confirma su selección  
**THEN** el sistema valida la disponibilidad en tiempo real contra la agenda del médico y permite reservar solo si el cupo está libre; de lo contrario, muestra alternativas disponibles.

---

## 🟩 SPRINT 2 – Del 10/10/2025 al 25/10/2025

### **RF2: Cola virtual (check-in remoto y presencial)**  
**GIVEN** que un paciente tiene una cita programada  
**WHEN** realiza check-in desde su móvil antes de llegar o en el kiosco presencial  
**THEN** el sistema lo inserta en la cola virtual, asigna número de turno y actualiza en pantalla su posición y tiempo estimado de espera.

### **RF3: Gestión de roles y permisos**  
**GIVEN** que un usuario accede con credenciales válidas  
**WHEN** inicia sesión en la plataforma  
**THEN** el sistema habilita solo las funciones correspondientes a su rol (administrador, médico, recepcionista o paciente) y restringe accesos no autorizados.

### **RF4: Tipos de cita y modalidad**  
**GIVEN** que un paciente inicia el proceso de agendamiento  
**WHEN** selecciona tipo de cita (primera vez, control, emergencia) y modalidad (presencial o virtual)  
**THEN** el sistema valida compatibilidad (ej. emergencias solo presenciales) y registra la modalidad elegida.

### **RF5: Mantenimiento de disponibilidad (bloqueos/feriados)**  
**GIVEN** que un administrador registra como feriado el 08/12/2025 en el calendario de disponibilidad  
**WHEN** un ciudadano intenta agendar una cita en esa fecha  
**THEN** el sistema bloquea el agendamiento, muestra “No disponible por feriado” y sugiere fechas alternativas disponibles.

---

## 🟨 SPRINT 3 – Del 26/10/2025 al 09/11/2025

### **RF6: Priorización y triage en la cola**  
**GIVEN** que varios pacientes están en cola  
**WHEN** el sistema aplica reglas de triage basadas en gravedad, tipo de atención o prioridad médica  
**THEN** reordena dinámicamente la cola asignando prioridad sin perder trazabilidad del orden original.

### **RF7: Integración con historia clínica (EHR)**  
**GIVEN** que un paciente ha sido atendido en una cita  
**WHEN** el médico registra observaciones o diagnósticos  
**THEN** el sistema sincroniza automáticamente los datos de la cita con la historia clínica electrónica, garantizando interoperabilidad.

### **RF8: Reglas de negocio de cupos (capacidad)**  
**GIVEN** que un paciente intenta reservar una cita en determinada especialidad  
**WHEN** los cupos diarios o semanales de ese médico están agotados  
**THEN** el sistema rechaza la reserva y muestra opciones alternativas de horarios o profesionales.

### **RF9: Protección anti-abuso (limitación de agendamientos)**  
**GIVEN** que un ciudadano ya tiene dos citas activas en la misma especialidad  
**WHEN** intenta crear una tercera cita  
**THEN** el sistema rechaza la solicitud y muestra el mensaje “Límite de citas activas alcanzado para esta especialidad”.

---

## 🟧 SPRINT 4 – Del 14/11/2025 al 26/11/2025

### **RF10: Recordatorios escalonados (48h y 2h)**  
**GIVEN** que el ciudadano tiene una cita confirmada  
**WHEN** faltan 48 horas y, posteriormente, 2 horas para la cita  
**THEN** el sistema envía dos SMS de recordatorio (manteniendo el mismo código de cita en ambos).

### **RF11: Reglas de elegibilidad por especialidad (derivación previa)**  
**GIVEN** que la especialidad "Oftalmología" requiere derivación previa  
**WHEN** el ciudadano intenta agendar sin contar con dicha derivación  
**THEN** el sistema bloquea el agendamiento y muestra el requisito pendiente (solicitar o adjuntar derivación).

### **RF12: Notificaciones por SMS (recordatorios y llamados)**  
**GIVEN** que un paciente tiene cita confirmada con datos de contacto válidos  
**WHEN** se aproxima la fecha/hora o el sistema lo llama para ingresar  
**THEN** se envía un SMS con recordatorio, instrucciones o llamado, registrando el intento y estado de entrega.

### **RF13: Consentimiento e idioma para SMS**  
**GIVEN** que un paciente completa su registro  
**WHEN** define idioma preferido y otorga consentimiento para recibir mensajes  
**THEN** el sistema guarda la configuración y envía SMS únicamente en el idioma elegido, respetando la Ley de Protección de Datos Personales.

---

## 🟥 SPRINT 5 – Del 30/11/2025 al 11/12/2025

### **RF14: Auditoría y trazabilidad (bitácora de eventos)**  
**GIVEN** que un operador reprograma una cita  
**WHEN** guarda los cambios  
**THEN** el sistema registra en auditoría usuario, fecha/hora y motivo, y deja el registro accesible para supervisión.

### **RF15: Reportes operativos (reporte diario de atención)**  
**GIVEN** que terminó la jornada en el Hospital Provincial  
**WHEN** el administrador solicita el reporte diario  
**THEN** el sistema genera un resumen con citas programadas, atendidas, canceladas, no-show y tiempos promedio de espera.

### **RF16: Encuestas posteriores a la atención (NPS/Satisfacción)**  
**GIVEN** que una cita cambió a estado “Atendida”  
**WHEN** han transcurrido 2 horas  
**THEN** el sistema envía un SMS con enlace breve a la encuesta de satisfacción.

### **RF17: Exportación / Interoperabilidad (CSV agenda del día)**  
**GIVEN** que el administrador solicita la exportación de la agenda de hoy  
**WHEN** confirma el rango “hoy”  
**THEN** el sistema genera un archivo CSV con columnas estándar y registra en auditoría quién realizó la exportación.

---

**📅 Fecha de última actualización:** 05/11/2025  
**Autor:** Equipo de desarrollo del proyecto
