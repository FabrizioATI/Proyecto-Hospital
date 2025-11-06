# 🧪 Plan de Pruebas – Sistema de Citas Médicas Hospitalarias

---

## 1. Objetivos

Garantizar que las funcionalidades de *agendamiento, atención y gestión de citas* cumplan con los criterios funcionales y no funcionales definidos, verificando:

- Respuesta de *operaciones críticas* (agendar, check-in, recordatorios) ≤ *3 segundos*.  
- *Seguridad, consistencia y trazabilidad* de la información.  
- Cumplimiento de *reglas de negocio* (cupos, feriados, derivaciones, roles).  
- *Disponibilidad* del sistema (≥ *99 % uptime*) durante el horario de atención.  

---

## 2. Alcance

### 2.1 Requerimientos Funcionales

| Sprint | Requerimiento | Funcionalidad |
|:------:|:--------------|:--------------|
| *Sprint 1 (01/10–09/10/2025)* | RF1 | Agendamiento con validación de disponibilidad |
| *Sprint 2 (10/10–25/10/2025)* | RF2, RF3, RF4, RF5 | Cola virtual; Roles y permisos; Tipos y modalidad; Bloqueos/feriados |
| *Sprint 3 (26/10–09/11/2025)* | RF6, RF7, RF8, RF9 | Priorización/triage; Integración EHR; Cupos/capacidad |
| *Sprint 4 (14/11–26/11/2025)* | RF10, RF11, RF12, RF13 | Recordatorios; Derivación; Notificaciones SMS; Idioma/consentimiento |
| *Sprint 5 (30/11–11/12/2025)* | RF14, RF15, RF16, RF17 | Auditoría; Reportes; Encuestas; Exportación CSV |

### 2.2 Requerimientos No Funcionales

- *RNF1:* Disponibilidad (99 % mensual)  
- *RNF2:* Rendimiento (≤ 3 s por solicitud crítica)  
- *RNF3:* Seguridad (TLS, hash seguro, control por roles)  
- *RNF4:* Integridad/consistencia (transacciones atómicas, integridad referencial)  
- *RNF5:* Usabilidad/accesibilidad (≥ 90 % tareas completadas sin asistencia)  
- *RNF6:* Mantenibilidad (cambios menores con < 1 h de inactividad)  
- *RNF7:* Escalabilidad (x2 usuarios con tiempos estables)  

---

## 3. Recursos

### 3.1 Herramientas

| Tipo | Herramienta |
|------|-------------|
| Automatización API | Postman / Newman |
| UI End-to-End | Cypress / Playwright |
| Performance | K6 / JMeter |
| Gestión y CI | GitLab CI/CD, Jira, TestLink |
| Seguridad | OWASP ZAP, SSL Labs |
| Datos de prueba | SQL Scripts / Fixtures JSON |
| Notificaciones | Mock SMS / Twilio Sandbox |

### 3.2 Personal

- QA funcional  
- QA automatización  
- Desarrollador Backend / Frontend  
- DevOps / Infra QA  
- Product Owner  

### 3.3 Entorno

- *Ambiente QA* con base anonimizada y endpoints REST.  
- *EHR simulado* (RF7).  
- *Workers/colas* activos para RF10–RF16.

---

## 4. Estrategia de Pruebas

Se aplicará una metodología de *caja negra*, combinando:

- *Pruebas funcionales* (API/UI)  
- *Pruebas de integración* (agenda, EHR, SMS)  
- *Regresión automatizada* por sprint  
- *Rendimiento*: carga concurrente (200 usuarios)  
- *Seguridad*: autenticación, roles, cifrado  
- *Usabilidad*: flujos principales y mensajes de error  

---

## 5. Plan por Sprint (Casos Clave)

### Sprint 1 – RF1: Agendamiento

| ID | Caso | Precondición | Pasos | Resultado Esperado |
|----|------|--------------|-------|--------------------|
| RF1-01 | Agendar con cupo libre | Usuario autenticado, slot libre | Seleccionar especialidad/médico/fecha/hora y confirmar | Cita creada “Programada” |
| RF1-02 | Agendar con cupo ocupado | Slot ocupado | Confirmar cita | “Horario no disponible” + sugerencias |
| RF1-03 | Evitar colisión | Cita misma franja | Intentar reservar | Bloqueo doble reserva |

---

### Sprint 2 – RF2 a RF5

| ID | Caso | Precondición | Pasos | Resultado Esperado |
|----|------|--------------|-------|--------------------|
| RF2-01 | Check-in remoto | Cita programada, SMS enviado | Hacer clic en enlace y confirmar | Inserta en cola; muestra posición y ETA |
| RF2-02 | Check-in presencial | Cita programada | Autenticarse en kiosco | Sincroniza cola; estado “En espera (presencial)” |
| RF3-01 | Acceso administrador | Credenciales admin | Iniciar sesión | Acceso completo; restricciones válidas |
| RF3-02 | Acceso médico | Credenciales médico | Abrir agenda | Solo ve su propia agenda |
| RF4-01 | Modalidad teleconsulta | Permite virtual | Seleccionar tipo y modalidad | Enlace videollamada generado |
| RF5-01 | Feriado 08/12/2025 | Feriado configurado | Intentar agendar ese día | “No disponible por feriado” + alternativas |

---

### Sprint 3 – RF6 a RF9

| ID | Caso | Precondición | Pasos | Resultado Esperado |
|----|------|--------------|-------|--------------------|
| RF6-01 | Reorden por triage | Cola activa | Aplicar reglas de prioridad | Reorden con trazabilidad |
| RF7-01 | Sincronizar EHR | Cita atendida | Registrar diagnóstico | Datos sincronizados con historia clínica |
| RF8-01 | Cupos agotados | Límite diario | Intentar reservar | Rechazo + horarios alternos |
| RF9-01 | Límite horario odontología | 10 cupos/h | Agotar cupos e intentar más | Lista de espera activada |

---

### Sprint 4 – RF10 a RF13

| ID | Caso | Precondición | Pasos | Resultado Esperado |
|----|------|--------------|-------|--------------------|
| RF10-01 | Recordatorios 48h/2h | Cita confirmada | Simular T-48h y T-2h | Dos SMS enviados |
| RF11-01 | Derivación requerida | Oftalmología requiere derivación | Intentar agendar sin derivación | Bloqueo y mensaje de requisito |
| RF12-01 | Notificación SMS | Cita confirmada | Se aproxima cita o llamado | SMS enviado; log registrado |
| RF13-01 | Consentimiento e idioma | Paciente registrado | Seleccionar idioma y aceptar SMS | SMS en idioma elegido |

---

### Sprint 5 – RF14 a RF17

| ID | Caso | Precondición | Pasos | Resultado Esperado |
|----|------|--------------|-------|--------------------|
| RF14-01 | Auditoría reprogramación | Operador autenticado | Reprogramar cita y guardar | Registro usuario/fecha/motivo |
| RF15-01 | Reporte diario | Fin de jornada | Solicitar reporte | Resumen con KPIs operativos |
| RF16-01 | Encuesta post atención | Cita “Atendida” | Esperar 2 horas | SMS con enlace encuesta |
| RF17-01 | Exportación CSV | Admin autenticado | Confirmar rango “hoy” | CSV generado + auditoría exportador |

---

## 6. Matriz de Trazabilidad (Resumen)

| RF | Caso Clave | Tipo | Dato Principal | Resultado Esperado |
|----|-------------|------|----------------|--------------------|
| RF1 | RF1-01/02/03 | API/UI | Disponibilidad en tiempo real | Cita creada o sugerencias |
| RF2 | RF2-01/02 | UI | Link SMS / kiosco | Turno y posición |
| RF3 | RF3-01/02 | API/UI | Roles | Permisos correctos |
| RF4 | RF4-01 | UI | Modalidad | Videollamada creada |
| RF5 | RF5-01 | UI | Feriado | No disponible + sugerencias |
| RF6 | RF6-01 | Lógica | Triage | Reordenado con trazabilidad |
| RF7 | RF7-01 | Integración | EHR | Sincronización correcta |
| RF8 | RF8-01 | API/UI | Límite diario | Rechazo + alternativas |
| RF9 | RF9-01 | API/UI | 10 cupos/h | Lista de espera |
| RF10 | RF10-01 | Job | T-48h / T-2h | SMS enviados |
| RF11 | RF11-01 | Validación | Derivación | Bloqueo + mensaje |
| RF12 | RF12-01 | Notificación | Datos válidos | SMS log correcto |
| RF13 | RF13-01 | Preferencias | Idioma/consentimiento | SMS idioma elegido |
| RF14 | RF14-01 | Auditoría | Reprogramación | Registro correcto |
| RF15 | RF15-01 | Reporte | Fin jornada | KPIs generados |
| RF16 | RF16-01 | Encuesta | 2h post “Atendida” | SMS enviado |
| RF17 | RF17-01 | Exportación | Rango “hoy” | CSV + auditoría |

---

## 7. Procedimiento de Ejecución

1. Validar ambiente QA y Swagger.  
2. Cargar fixtures: usuarios, roles, cupos, feriados, consentimientos.  
3. Ejecutar *Postman/Newman* por RF y guardar reportes.  
4. Ejecutar *Cypress/Playwright* y capturar evidencias.  
5. Simular *jobs* para recordatorios y encuestas.  
6. Ejecutar *K6/JMeter* en endpoints críticos.  
7. Documentar hallazgos y generar informe final.

---

## 8. Pruebas de Rendimiento (RNF2)

| Endpoint | Escenario | Límite | Métrica |
|----------|------------|---------|---------|
| POST /api/citas | Crear cita | p95 ≤ 3 s | Latencia |
| POST /api/checkin | Insertar a cola | p95 ≤ 2.5 s | Latencia |
| GET /api/reportes/diarios | Generar reporte | p95 ≤ 4 s | Latencia |
| GET /api/agenda/disponibilidad | Buscar slots | p95 ≤ 1.5 s | Latencia |

---

## 9. Pruebas de Seguridad (RNF3)

- Validar *HTTPS/TLS* en todos los endpoints.  
- Acceso sin token → *401 Unauthorized*.  
- Acceso sin rol → *403 Forbidden*.  
- Cifrado de datos personales y médicos.  
- *OWASP ZAP:* sin vulnerabilidades críticas.  

---

## 10. Criterios de Aceptación

| Tipo | Criterio |
|------|-----------|
| Funcional | ≥ 95 % casos PASSED |
| Rendimiento | p95 dentro de límites |
| Seguridad | 0 vulnerabilidades críticas |
| Disponibilidad | ≥ 99 % uptime |
| Usabilidad | ≥ 90 % tareas exitosas |
| Auditoría | 100 % eventos críticos registrados |

---

## 11. Cronograma General

| Fase | Inicio | Fin |
|------|--------|-----|
| Preparación | 01/10/2025 | 03/10/2025 |
| Sprints 1–2 | 04/10/2025 | 25/10/2025 |
| Sprints 3–4 | 26/10/2025 | 26/11/2025 |
| Sprint 5 | 27/11/2025 | 11/12/2025 |
| Performance y seguridad | 12/12/2025 | 15/12/2025 |
| Informe final QA | 16/12/2025 | 17/12/2025 |

---

## 12. Riesgos y Mitigación

| Riesgo | Mitigación |
|--------|-------------|
| Cambios en API | Congelar contratos antes de ejecución |
| Feriados o cupos mal cargados | Scripts idempotentes |
| Falla SMS gateway | Mock SMS |
| Desfase horario | Validar timezone servidor |
| Caída de QA | Monitoreo y reinicio automático |

---

## 13. Entregables

- Colecciones *Postman/Newman* con reportes HTML/JUnit.  
- Suites *Cypress/Playwright* con evidencias.  
- Scripts/reportes *K6/JMeter*.  
- Dataset de *fixtures* reproducibles.  
- *Informe final QA* con resultados y conclusiones.
