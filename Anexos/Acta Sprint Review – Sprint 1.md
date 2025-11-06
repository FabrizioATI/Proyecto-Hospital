# 📝 Acta de Sprint Review – Sprint 2

**Proyecto:** Sistema de Gestión de Citas Médicas con Colas Virtuales y Notificaciones SMS  
**Sprint:** 2  
**Periodo:** 10/10/2025 – 25/10/2025  
**Equipo:** 5 participantes  
**Requerimientos trabajados:**
- **RF2:** Cola virtual (check-in remoto y presencial)  
- **RF3:** Gestión de roles y permisos  
- **RF4:** Tipos de cita y modalidad  
- **RF5:** Mantenimiento de disponibilidad (bloqueos/feriados)

---

## ✅ Resultados del Sprint
- Se implementó la **cola virtual**, permitiendo que el paciente realice *check-in* remoto desde su móvil o kiosco y reciba su número de turno.  
- El sistema actualiza en tiempo real la posición en la cola y el tiempo estimado de espera.  
- Se desarrolló la **gestión de roles y permisos**, con autenticación diferenciada para administrador, médico, recepcionista y paciente.  
- Se añadió la funcionalidad de **tipos de cita y modalidad**, validando la compatibilidad (Ej. emergencias solo presenciales).  
- Se incorporó la opción de **bloqueos por feriados**, mostrando mensajes de “No disponible” y sugerencias de fechas alternativas.  

---

## 💡 Lecciones Aprendidas
- La división de tareas por ramas en Git funcionó mejor que en el sprint anterior, reduciendo conflictos al integrar código.  
- Los *dailys* se realizaron de forma presencial en el aula, facilitando la coordinación y revisión rápida de avances.  
- Se evidenció la necesidad de planificar mejor las dependencias entre tareas (por ejemplo, roles y autenticación antes que la cola virtual).  

---

## 🔄 Acuerdos para el Siguiente Sprint
- Mantener el esquema de ramas individuales y un responsable de integración semanal.  
- Reforzar la actualización diaria del tablero en *Jira*.  
- Implementar pruebas unitarias para los módulos completados antes de continuar con nuevas funcionalidades.  
- Avanzar con los requerimientos del Sprint 3:
  - **RF6:** Priorización y triage en la cola.  
  - **RF7:** Integración con historia clínica (EHR).  
  - **RF8:** Reglas de negocio de cupos.  
  - **RF9:** Protección anti-abuso (limitación de agendamientos).  
