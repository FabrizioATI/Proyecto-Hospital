# 📝 Acta de Sprint Review – Sprint 3

**Proyecto:** Sistema de Gestión de Citas Médicas con Colas Virtuales y Notificaciones SMS  
**Sprint:** 3  
**Periodo:** 26/10/2025 – 09/11/2025  
**Equipo:** 5 participantes  
**Requerimientos trabajados:**
- **RF6:** Priorización y triage en la cola  
- **RF7:** Integración con historia clínica (EHR)  
- **RF8:** Reglas de negocio de cupos (capacidad)  
- **RF9:** Protección anti-abuso (limitación de agendamientos)

---

## ✅ Resultados del Sprint
- Se implementaron parcialmente las reglas de **priorización y triage en la cola**, con ordenamiento dinámico según tipo de atención.  
- Se avanzó el diseño de la **integración con la historia clínica (EHR)**, dejando configurada la estructura de datos y endpoints para sincronización futura.  
- El módulo de **reglas de cupos** fue probado en entorno local, validando correctamente los límites de citas por médico y especialidad.  
- La **protección anti-abuso** se completó a nivel lógico, restringiendo múltiples agendamientos por paciente en la misma especialidad.  

---

## 💡 Lecciones Aprendidas
- Hubo **muy poca comunicación entre los integrantes**, lo que afectó la coordinación general del sprint.  
- Solo algunos miembros del equipo **reportaron avances o subieron sus cambios** al repositorio.  
- La ausencia de reuniones frecuentes generó **duplicidad de tareas y falta de integración** entre los módulos desarrollados.  
- Se identificó la necesidad de establecer un **canal de seguimiento constante (Trello o GitHub Issues)** para mantener visibilidad de los avances, incluso cuando no se realizan reuniones.  
- El equipo reconoció la importancia de definir **responsables técnicos por requerimiento** antes de iniciar el sprint.  

---

## 🔄 Acuerdos para el Siguiente Sprint
- Establecer un cronograma mínimo de **2 reuniones semanales** (presencial o virtual) para evitar descoordinaciones.  
- Reforzar el uso de **GitHub y Jira** para registrar avances individuales y comentarios técnicos.  
- Designar a un **miembro responsable por cada módulo** (cola, EHR, reglas, notificaciones) para centralizar decisiones técnicas.  
- Priorizar el cierre completo de las funcionalidades iniciadas antes de avanzar con nuevas tareas.  
- Iniciar los desarrollos del **Sprint 4**, enfocados en:
  - **RF10:** Recordatorios escalonados (48h y 2h)  
  - **RF11:** Reglas de elegibilidad por especialidad  
  - **RF12:** Notificaciones por SMS  
  - **RF13:** Consentimiento e idioma para SMS  

---

**Fecha de revisión:** 09/11/2025  
**Aprobado por:** Equipo de desarrollo del proyecto
