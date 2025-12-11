# Flujo de Escenario: Desde que el Paciente Ingresa hasta que es Atendido

## 📋 Documento Narrativo del Proceso

**Sistema:** Sistema de Gestión de Citas Médicas del Hospital  
**Versión:** 1.0  
**Fecha:** Diciembre 2025  
**Proyecto:** Proyecto-Hospital

---

## 📑 Tabla de Contenidos

1. [El Inicio del Viaje del Paciente](#el-inicio-del-viaje-del-paciente)
2. [Primera Vez: Registro](#primera-vez-registro)
3. [Agendar una Cita](#agendar-una-cita)
4. [Esperar la Confirmación](#esperar-la-confirmación)
5. [El Día de la Cita](#el-día-de-la-cita)
6. [Llegada al Hospital](#llegada-al-hospital)
7. [En la Sala de Espera](#en-la-sala-de-espera)
8. [El Consultorio](#el-consultorio)
9. [Después de la Cita](#después-de-la-cita)
10. [Flujos Presenciales Especiales](#flujos-presenciales-especiales)
11. [Notificaciones Especiales](#notificaciones-especiales)
12. [Protocolo de Emergencias](#protocolo-de-emergencias)
13. [Situaciones Especiales en Recepción](#situaciones-especiales-en-recepción)
14. [Casos de Uso Específicos](#casos-de-uso-específicos)

---

## 🌟 El Inicio del Viaje del Paciente

El flujo del sistema está diseñado para que un paciente pueda acceder a atención médica de dos formas:

**Opción 1: Agendar por la Plataforma** (Planificado)
- El paciente elige especialidad, médico y horario
- Recibe notificaciones automáticas
- Llega a la hora exacta

**Opción 2: Llegar Presencialmente** (Inmediato)
- El paciente llega sin cita previa
- Se registra en recepción
- Entra a una cola según su urgencia
- Espera su turno

El sistema maneja ambos flujos automáticamente, priorizando por urgencia. Un paciente con **EMERGENCIA** (haya agendado o no) siempre será atendido primero.

El proceso completo se puede resumir en estos pasos:

```
FLUJO AGENDADO:                    FLUJO PRESENCIAL:
└─ SE REGISTRA O INICIA SESIÓN     └─ LLEGA AL HOSPITAL SIN CITA
   └─ SOLICITA UNA CITA              └─ SE REGISTRA EN RECEPCIÓN
      └─ ENTRA EN COLA                  └─ SE EVALÚA URGENCIA (TRIAGE)
         └─ RECIBE OFERTA               └─ ENTRA EN COLA
            └─ ACEPTA O RECHAZA         └─ ESPERA SU TURNO
               └─ CONFIRMA CITA
                  └─ RECIBE RECORDATORIOS ← AMBOS FLUJOS CONVERGEN
                     └─ LLEGA AL HOSPITAL
                        └─ SE PRESENTA EN RECEPCIÓN
                           └─ ESPERA EN SALA DE ESPERA
                              └─ ES ATENDIDO
                                 └─ HISTORIAL SE ACTUALIZA
```
        ↓
    ESPERA SU TURNO EN LA SALA DE ESPERA
        ↓
    ES LLAMADO AL CONSULTORIO
        ↓
    ES ATENDIDO POR EL MÉDICO
        ↓
    SE REGISTRA TODO EN SU HISTORIA CLÍNICA
```

---

## 🎯 Primera Vez: Registro

### Escena 1: El Paciente se Registra por Primera Vez

**Hora:** Una noche cualquiera, en casa  
**Lugar:** Navegador web del paciente

**Lo que pasa:**

Juan es un paciente nuevo que necesita una consulta cardíaca. Por primera vez, accede a la plataforma web del hospital desde su casa.

1. **Juan abre el navegador y va a la página del hospital**
   - Ve un botón que dice "Registrarse" o "Crear una cuenta"
   - Hace clic allí

2. **Se abre un formulario de registro con los siguientes campos:**
   - Nombre
   - Apellido Paterno
   - Apellido Materno
   - Número de DNI (documento de identidad)
   - Correo electrónico
   - Número de teléfono (importante para recibir recordatorios por SMS)
   - Una contraseña que elige

3. **Juan completa los datos cuidadosamente:**
   - "Juan"
   - "García"
   - "Pérez"
   - "12345678"
   - "juan.garcia@correo.com"
   - "+56987654321"
   - Contraseña: "MiContraseña123!"

4. **Juan hace clic en "Crear Cuenta"**
   - El sistema verifica que:
     - El DNI no esté ya registrado
     - El correo no esté ya registrado
     - Los datos sean válidos
   
5. **Si todo está bien:**
   - La cuenta se crea automáticamente
   - Se crea su **Historia Clínica** (un archivo digital único para él)
   - El sistema lo redirige a la página de **Iniciar Sesión**
   - Se envía un correo de bienvenida a su email

6. **Juan recibe el correo de bienvenida**
   - Dice algo como: "¡Bienvenido al Sistema de Citas del Hospital!"
   - Le explica cómo usar la plataforma
   - Lo invita a agendar su primera cita

---

### Escena 2: Juan Inicia Sesión

**Hora:** Al día siguiente, por la mañana  
**Lugar:** Nuevamente en su casa, en la computadora

**Lo que pasa:**

1. **Juan regresa a la página del hospital**
   - Hace clic en **"Iniciar Sesión"**

2. **Se abre la pantalla de login**
   - Un campo para DNI (o email)
   - Un campo para contraseña

3. **Juan ingresa sus credenciales:**
   - DNI: "12345678"
   - Contraseña: "MiContraseña123!"

4. **Hace clic en "Entrar"**
   - El sistema verifica que existe esa cuenta
   - Verifica que la contraseña sea correcta
   - Lo autentifica

5. **Juan entra al sistema**
   - Ve su **Dashboard** o panel personal
   - Ve opciones como:
     - "Agendar una Cita"
     - "Mis Citas"
     - "Configuración"
     - "Ver mi Historial Médico"

---

---

## 📅 Agendar una Cita

### Escena 3: Juan Entra al Formulario de Agendar Cita

**Hora:** Mismo día, 10 de la mañana  
**Lugar:** Panel de Juan en la plataforma

**Lo que pasa:**

1. **Juan hace clic en "Agendar una Cita"**
   - Ve un asistente paso a paso
   - Cada paso le pide información diferente

### Paso 1: Elegir la Especialidad

2. **Se abre una pantalla con todas las especialidades disponibles**
   - Cardiología
   - Endocrinología
   - Dermatología
   - Neurología
   - Pediatría
   - Y muchas más...

3. **Juan selecciona "Cardiología"**
   - Porque necesita control cardiaco

4. **El sistema verifica automáticamente:**
   - ¿Cardiología requiere derivación médica previa?
   - En este caso NO
   - Por lo tanto, permite continuar

**Nota Importante:** Algunas especialidades sí requieren derivación de otro médico. Si fuera así, el sistema diría: "Necesita una derivación médica de su doctor de cabecera para poder agendar con un cardiólogo."

### Paso 2: Elegir el Médico

5. **Se abre una lista de cardiólogos disponibles**
   - Dr. García (Cardiología) - Disponible
   - Dra. López (Cardiología) - Disponible
   - Dr. Martínez (Cardiología) - Disponible

6. **Juan elige al Dr. García**
   - Lo ve como una opción recomendada
   - Hace clic

### Paso 3: Clasificar la Consulta

7. **Se le pide seleccionar el tipo de consulta que necesita:**
   - ⚠️ **EMERGENCIA** - Necesita atención urgente ahora
   - 👴 **ADULTO MAYOR** - Soy mayor de 65 años
   - ✅ **REGULAR** - Es una consulta de rutina

8. **Juan selecciona "REGULAR"**
   - Porque es un control de rutina, no es urgente

**Esto es importante:** Si hubiera seleccionado EMERGENCIA, el sistema habría intentado asignarle un cupo mucho más rápido, incluso desplazando otros pacientes a posiciones posteriores en la cola.

### Paso 4: Elegir Modalidad

9. **Se le pregunta cómo prefiere la consulta:**
   - 🏥 **PRESENCIAL** - En el consultorio del hospital
   - 💻 **VIRTUAL** - Por videollamada

10. **Juan elige "PRESENCIAL"**
    - Porque quiere que le hagan electrocardiograma

### Paso 5: Describir el Motivo

11. **Se abre un campo de texto para el motivo:**
    - "¿Por qué quiere ver al cardiólogo?"

12. **Juan escribe:**
    - "Control cardiaco de rutina. Tengo algunos mareos ocasionales"

### Paso 6: Confirmar y Enviar

13. **Juan ve un resumen de su solicitud:**
    ```
    Especialidad: Cardiología
    Médico: Dr. García
    Clasificación: Regular
    Modalidad: Presencial
    Motivo: Control cardiaco de rutina. Tengo algunos mareos ocasionales
    ```

14. **Juan hace clic en "Confirmar Solicitud de Cita"**
    - Su solicitud se envía al sistema
    - El sistema lo pone en una **cola de espera**
    - Juan ve un mensaje: "¡Tu solicitud ha sido registrada! Te avisaremos cuando se libere un cupo."

---

### Fase 3: Gestión Automática de Cola de Espera

---

## ⏳ Esperar la Confirmación

### Escena 4: Juan Recibe la Oferta de Cupo

**Hora:** 30 minutos después de solicitar la cita  
**Medio:** Correo electrónico y SMS

**Lo que pasa:**

El sistema **automáticamente** (sin intervención de humanos) hace lo siguiente:

1. **El sistema evalúa la cola de espera del Dr. García**
   - Busca todas las solicitudes pendientes para cardiólogos
   - Las ordena por:
     - 🔴 EMERGENCIA (primero)
     - 🟡 ADULTO MAYOR (segundo)
     - 🟢 REGULAR (tercero)
     - Dentro de cada grupo, por orden de llegada (primero en llegar, primero atendido)

2. **El sistema busca horarios disponibles del Dr. García**
   - Ve cuándo está disponible: martes, jueves, viernes
   - Verifica cuántos cupos quedan en cada horario
   - Una especialidad puede tener máximo 10 pacientes por hora

3. **El sistema asigna a Juan un horario**
   - Encuentra que el **martes a las 10:00 AM** hay un cupo disponible
   - Asigna a Juan a ese horario
   - Estado de Juan en la cola: "OFERTA ENVIADA"

4. **Juan recibe una notificación (Correo Electrónico)**
   ```
   ¡BUEN DÍA JUAN!
   
   Se ha liberado un cupo para ti con el Dr. García.
   
   📅 Fecha: Martes, 14 de Diciembre de 2025
   🕙 Hora: 10:00 AM
   🏥 Especialidad: Cardiología
   👨‍⚕️ Médico: Dr. García
   
   ⏰ IMPORTANTE: Tienes 15 MINUTOS para confirmar si aceptas este cupo.
   Si no confirmas en ese tiempo, volverá a la cola y será ofrecido a otro paciente.
   
   [ACEPTAR CUPO] [RECHAZAR CUPO]
   ```

5. **Juan recibe también un SMS**
   ```
   Cupo disponible con Dr. García - Martes 10:00 AM.
   Confirma en: www.hospital.com/citas (15 min)
   ```

### Escena 5: Juan Acepta o Rechaza el Cupo

**Hora:** Mientras recibe la notificación  
**Lugar:** En su teléfono o computadora

**Opción A - Juan Acepta:**

6. **Juan lee el correo**
   - Ve que el horario le viene bien
   - Hace clic en "ACEPTAR CUPO"

7. **El sistema confirma la aceptación**
   - Cambia el estado de Juan de "OFERTA" a "CONFIRMADA"
   - Crea una **CITA** oficial en su calendario
   - Envía confirmación por correo:
   ```
   ¡CITA CONFIRMADA!
   
   Tu cita ha sido agendada exitosamente:
   
   📅 Martes, 14 de Diciembre de 2025
   🕙 10:00 AM
   👨‍⚕️ Dr. García - Cardiología
   🏥 Consultorio 205
   
   Por favor, llega 10 minutos antes.
   ```

**Opción B - Juan Rechaza:**

6. **Juan ve el correo pero tiene un compromiso**
   - Hace clic en "RECHAZAR CUPO"
   - Se abre una opción para explicar por qué rechaza (opcional)

7. **El sistema lo vuelve a poner en la cola**
   - El cupo del martes 10 AM se libera
   - Juan vuelve a esperar por una nueva oferta
   - El siguiente paciente en la cola recibe la oferta

**Opción C - Juan no responde en 15 minutos:**

6. **Pasan los 15 minutos**
   - Juan estaba ocupado y no vio el correo
   - El cupo automáticamente expira
   - Vuelve a la cola de espera
   - Se le ofrecerá otro horario después

---

---

## 📅 El Día de la Cita

### Escena 6: Recordatorios Automáticos

**Hora:** Lunes, 13 de Diciembre (un día antes)  
**Medio:** SMS a las 2:00 PM

**Lo que pasa:**

1. **Juan recibe un SMS recordatorio:**
   ```
   RECORDATORIO: Tu cita es MAÑANA martes a las 10:00 AM
   con el Dr. García - Cardiología.
   Por favor, confirma que asistirás.
   ```

**Hora:** Martes, 14 de Diciembre, 8:00 AM (2 horas antes)  
**Medio:** SMS

2. **Juan recibe otro SMS 2 horas antes:**
   ```
   ¡IMPORTANTE! Tu cita es en 2 HORAS.
   Dr. García - Cardiología - 10:00 AM - Consultorio 205.
   Si NO PUEDES ASISTIR, cancela ahora en www.hospital.com
   ```

**¿Por qué estos recordatorios?**
- El primer recordatorio (48 horas) le avisa con tiempo
- El segundo (2 horas) es el último aviso
- Si Juan no puede ir, tiene tiempo para cancelar y liberar el cupo para otro paciente

---

## 🏥 Llegada al Hospital

### Escena 7: Juan Llega a la Recepción

**Hora:** Martes, 14 de Diciembre, 9:50 AM  
**Lugar:** Entrada principal del hospital, mostrador de recepción

**Lo que pasa:**

1. **Juan entra al hospital**
   - Ve un letrero: "RECEPCIÓN"
   - Se forma en la cola de pacientes

2. **Le toca el turno a Juan**
   - Se acerca al mostrador
   - La recepcionista lo saluda: "¡Buenos días! ¿Cómo le puedo ayudar?"

3. **Juan dice:**
   - "Buenos días. Tengo una cita con el Dr. García a las 10:00 AM"
   - "Mi nombre es Juan García Pérez"

4. **La recepcionista busca en el sistema**
   - Ingresa el DNI de Juan: 12345678
   - El sistema muestra la cita:
     ```
     PACIENTE: Juan García Pérez
     MÉDICO: Dr. García
     ESPECIALIDAD: Cardiología
     HORA: 10:00 AM
     CONSULTORIO: 205
     ESTADO: Confirmada
     MOTIVO: Control cardiaco de rutina
     ```

5. **La recepcionista le da instrucciones:**
   - "Perfecto, todo está en orden"
   - "El Dr. García está en el Consultorio 205, segundo piso"
   - "Por favor, espera en la sala de espera"
   - Le entrega un papelito con el número de consultorio

6. **El sistema actualiza el estado en la plataforma**
   - La cita de Juan cambia de "Pendiente" a "Confirmada"
   - Se registra la hora de llegada
   - Se le avisa al Dr. García que Juan está en la sala de espera

---

## ⏱️ En la Sala de Espera

### Escena 8: Juan Espera su Turno

**Hora:** Martes, 14 de Diciembre, 9:55 AM  
**Lugar:** Sala de espera del segundo piso, Cardiología

**Lo que pasa:**

1. **Juan sube al segundo piso**
   - Ve varias puertas con números: 201, 202, 203...
   - Llega a una sala grande con sillas
   - Un cartel dice: "SALA DE ESPERA - CARDIOLOGÍA"

2. **En una pantalla digital se ve el orden de atención:**
   ```
   PRÓXIMOS A SER ATENDIDOS:
   ────────────────────────────
   1. Paciente: María López     → Consultorio 203 (Dr. Martínez)
   2. Paciente: Juan García     → Consultorio 205 (Dr. García) ← JUAN
   3. Paciente: Pedro Sánchez   → Consultorio 207 (Dra. López)
   
   CONSULTORIO 205: En atención
   ```

3. **Juan se sienta**
   - Mira su papelito: "Consultorio 205"
   - Ve que María López está siendo atendida en 203
   - Sabe que él será el siguiente

4. **Mientras espera:**
   - Lee revistas en la sala
   - Se relaja
   - Piensa en las preguntas que quiere hacerle al doctor
   - Espera aproximadamente 5-10 minutos

5. **El sistema (en tiempo real) muestra al Dr. García:**
   - "Juan García está esperando en la sala"
   - "Es el siguiente en tu lista"
   - El doctor ve su información: motivo, historial, etc.

---

## 🩺 El Consultorio

### Escena 9: El Dr. García Llama a Juan

**Hora:** Martes, 14 de Diciembre, 10:00 AM  
**Lugar:** Consultorio 205

**Lo que pasa:**

1. **El Dr. García sale del Consultorio 203**
   - Dice: "¡Próximo!"
   - O grita: "¡Juan García!"

2. **Juan se levanta y entra al Consultorio 205**
   - Saluda al doctor
   - Se sientan

3. **El Dr. García abre el sistema en su computadora**
   - Ve la información de Juan:
     ```
     PACIENTE: Juan García Pérez
     DNI: 12345678
     EDAD: 45 años
     MOTIVO: Control cardiaco de rutina. Tengo algunos mareos ocasionales
     HISTORIAL PREVIO: Hace 2 años fue atendido por hipertensión leve
     MEDICAMENTOS: Losartán 50mg diarios
     ALERGIAS: Ninguna registrada
     ```

4. **El doctor comienza la consulta**
   - "Buenos días Juan, ¿cómo se ha sentido?"
   - Escucha al paciente
   - Toma nota mentalmente

5. **El Dr. García realiza el examen físico**
   - Le pide que se suba a la camilla
   - Ausculta con estetoscopio el corazón y pulmones
   - Mide presión arterial: 130/85
   - Verifica frecuencia cardíaca
   - Pide que se acueste
   - Palpita el abdomen
   - Revisa reflejos

6. **Toma los signos vitales:**
   - Temperatura: 36.8°C
   - Frecuencia cardíaca: 72 latidos/min
   - Presión arterial: 130/85 mmHg
   - Saturación de oxígeno: 98%
   - Frecuencia respiratoria: 16

7. **El Dr. García decide hacer un electrocardiograma (EKG)**
   - Le coloca electrodos en el pecho
   - El aparato registra la actividad cardíaca
   - El resultado se genera en papel o digitalmente

8. **Mientras realiza esto:**
   - El doctor abre el sistema en la computadora
   - Crea una **Nota de Evolución** en la Historia Clínica de Juan
   - Comienza a escribir todo lo que observa:
   
   ```
   NOTA DE EVOLUCIÓN - CARDIOLOGÍA
   Paciente: Juan García Pérez
   Fecha: 14 Diciembre 2025, 10:00 AM
   Doctor: Dr. García
   
   ANAMNESIS (Historia):
   - Paciente refiere mareos ocasionales desde hace 1 mes
   - Niega dolor pectoral
   - Niega disnea (falta de aire)
   - Presión arterial controlada con Losartán
   
   EXAMEN FÍSICO:
   - Paciente lúcido y orientado
   - Sin signos de angustia
   - Corazón: ritmo regular, sin soplos
   - Pulmones: ventilación simétrica
   
   SIGNOS VITALES:
   - Temperatura: 36.8°C
   - FC: 72 lpm
   - PA: 130/85 mmHg
   - SatO2: 98%
   - FR: 16
   
   EXÁMENES:
   - EKG: Normal, sin alteraciones
   
   IMPRESIÓN:
   - Mareos probablemente de etiología neurogénica
   - Sin evidencia de patología cardíaca aguda
   - Mantener Losartán actual
   
   PLAN:
   - Reposo relativo
   - Aumentar ingesta de agua
   - Evitar cambios bruscos de posición
   - Control en 3 meses o antes si síntomas empeoran
   - Si mareos persisten, solicitar resonancia magnética cerebral
   ```

9. **El Dr. García termina el examen**
   - "Todo está bien, Juan"
   - "Tu corazón está funcionando correctamente"
   - "Esos mareos pueden ser por baja presión postural"
   - "Te recomiendo descansar más y beber más agua"

10. **El doctor finalmente:**
    - Presiona el botón "Finalizar Atención" en el sistema
    - El estado de la cita cambia a "ATENDIDA"
    - El episodio clínico se marca como "CERRADO"
    - La Historia Clínica de Juan se actualiza automáticamente

---

## 📝 Después de la Cita

### Escena 10: Juan Sale del Consultorio

**Hora:** Martes, 14 de Diciembre, 10:25 AM  
**Lugar:** Puerta del Consultorio 205

**Lo que pasa:**

1. **Juan sale con sus resultados**
   - El doctor le entrega un papel con:
     - Diagnóstico
     - Medicamentos recomendados
     - Próxima cita (si es necesaria)
     - Instrucciones de cuidado

2. **Juan va a recepción para pagar o gestionar trámites**
   - La recepcionista ve en el sistema: "CITA COMPLETADA"
   - Genera un comprobante si lo necesita
   - Le dice: "Gracias por visitarnos, que se mejore"

3. **Juan se va a casa**
   - Su cita está registrada en el sistema
   - Su Historia Clínica tiene todas las notas

### Escena 11: Juan Recibe Confirmación por Email

**Hora:** Martes, 14 de Diciembre, 10:30 AM  
**Medio:** Correo electrónico automático

**Lo que pasa:**

1. **El sistema envía automáticamente un email:**
   ```
   ¡GRACIAS POR VISITARNOS, JUAN!
   
   Tu cita ha sido completada exitosamente.
   
   📋 RESUMEN DE LA CONSULTA:
   Médico: Dr. García
   Especialidad: Cardiología
   Fecha: Martes, 14 de Diciembre de 2025
   Hora: 10:00 AM
   
   DIAGNÓSTICO: Mareos posturales
   
   PLAN DE SEGUIMIENTO:
   - Reposo relativo
   - Aumentar ingesta de agua
   - Evitar cambios bruscos de posición
   - Próxima cita en 3 meses (si es necesaria)
   
   Para ver el detalle completo de tu consulta:
   [ACCEDER A MI HISTORIA CLÍNICA]
   ```

### Escena 12: Juan Recibe Encuesta de Satisfacción

**Hora:** Martes, 14 de Diciembre, 4:00 PM (6 horas después)  
**Medio:** SMS

**Lo que pasa:**

1. **Juan recibe un SMS:**
   ```
   ¡Ayúdanos a mejorar! ¿Cómo fue tu experiencia hoy?
   
   ¿Fue el doctor puntual? (Sí/No)
   ¿Califica la atención? (1-5 estrellas)
   ¿Recomendarías este médico? (Sí/No)
   
   Responde: www.hospital.com/encuesta
   ```

2. **Juan responde:**
   - Fue puntual: Sí ✓
   - Calificación: 5 estrellas ⭐⭐⭐⭐⭐
   - ¿Lo recomendaría? Sí ✓

3. **El sistema registra las respuestas:**
   - Se guardan en una tabla de encuestas
   - Se usan para mejorar la calidad del servicio
   - Los resultados se pueden ver en reportes

---

## 🏥 Flujos Presenciales Especiales

### Flujo A: Triage en Recepción

**Cuando llega un paciente presencial sin cita:**

1. **En Recepción:**
   ```
   PACIENTE LLEGA → RECEPCIONISTA LO REGISTRA
        ↓
   ¿Es paciente nuevo?
   ├─ SÍ → Crear cuenta rápida
   └─ NO → Buscar en sistema por DNI
        ↓
   ¿Cuál es la urgencia?
   ├─ EMERGENCIA → Enfermero de triage hace evaluación rápida
   │  └─ Signos vitales críticos? → Lo llevan a emergencias
   │
   ├─ ADULTO MAYOR → Se le da prioridad
   │  └─ Se asigna a especialidad requerida
   │
   └─ REGULAR → Entra a cola normal
      └─ Se estima tiempo de espera
        ↓
   Se le asigna número de turno
   Se le dice especialista y tiempo aproximado
   Se sienta en sala de espera
   ```

2. **Evaluación Rápida de Enfermero (si es necesario):**
   - Temperatura
   - Presión arterial
   - Frecuencia cardíaca
   - Saturación de oxígeno
   - Preguntas sobre síntomas graves

3. **Asignación de Especialidad:**
   - Recepcionista pregunta: "¿Qué especialidad necesita?"
   - Si dice: "Dolor en el pecho" → Cardiología/Emergencias
   - Si dice: "Erupción en la piel" → Dermatología
   - Si dice: "Mareos" → Neurología o Medicina General

4. **Colocación en Cola:**
   - Se crea registro en `WaitlistItem`
   - Se ordena por prioridad
   - Se asigna número de turno visible

---

### Flujo B: Cambios de Turno en la Sala de Espera

**Si el médico se atrasa o hay cambios:**

1. **Sistema detecta retrasos:**
   - Monitor muestra: "Consultorio 205 con 15 min de atraso"
   - Se actualizan tiempos estimados para otros pacientes
   - Se notifica a pacientes (si tienen SMS): "Tu turno se ha reprogramado a las X:XX"

2. **Si un médico se enferma o no llega:**
   - Administrador marca: "Dr. García NO DISPONIBLE"
   - Sistema automáticamente reasigna pacientes a otro médico
   - Se notifica a pacientes por SMS

3. **Si llega una emergencia (No-Show de prior):**
   - Cupo se libera
   - Sistema busca siguiente en cola
   - Lo llama inmediatamente (si está en espera)

---

### Flujo C: Paciente se Arrepiente o Quiere Irse

**Durante la espera:**

1. **Si el paciente quiere IRSE:**
   - Avisa a recepción
   - Recepcionista anota: "Cita cancelada por paciente"
   - Se libera el cupo
   - Se registra en sistema

2. **Si el paciente DESERTA (se va sin avisar):**
   - Pasados 15 minutos de no aparecer
   - Médico marca: "Paciente no presente"
   - Se registra como abandono
   - Se libera el cupo para siguiente

3. **Pueden **regresar después:**
   - Pueden reagendar
   - Se registra el abandono anterior (auditoría)
   - Si es reincidente, puede alertarse al personal

---

## 📱 Notificaciones Especiales

### Para Pacientes Presenciales en Espera

**Sistema envía SMS en tiempo real:**

```
Ejemplo 1: Faltan 3 pacientes antes de ti
"Te faltan 3 pacientes para ser atendido. 
Tiempo estimado: 20 minutos. Permanece en la sala."

Ejemplo 2: Ya es tu turno
"¡Es tu turno! Dirígete al Consultorio 205"

Ejemplo 3: Hay retraso
"Tu médico se está demorando. 
Tiempo estimado: 30 minutos más."

Ejemplo 4: Cambio de turno
"Tu cita ha sido trasladada al Dr. López 
en el Consultorio 208"
```

---

### Para Pacientes Agendados Previamente

**Si hay cambios o cancelaciones:**

```
"El Dr. García ha cancelado sus horarios hoy. 
Tu cita ha sido reprogramada para mañana a las 10:00 AM 
con la Dra. López (mismo especialista).
¿Confirmas el cambio?"
```

---

## 🚑 Protocolo de Emergencias

### Si llega Paciente en Estado Crítico

**Flujo de Emergencias (diferente al normal):**

1. **Paciente llega sin cita o con síntomas graves:**
   - "Tengo un infarto" o "Me cortaron la mano"
   - Recepcionista grita: "¡EMERGENCIA!"

2. **Protocolo Inmediato:**
   - Se para todo en recepción
   - Lo llevan de inmediato a sala de estabilización
   - Se avisa a médico de emergencias
   - Se llama ambulancia si es necesario
   - Se toman signos vitales critales
   - Se hace procedimiento de reanimación si es necesario

3. **Sistema Registra:**
   - Cita de emergencia se crea automáticamente
   - Clasificación: EMERGENCIA (máxima prioridad)
   - Episodio clínico tipo: "EMERGENCIA"
   - Se notifica a jefe de enfermería

4. **Después de Estabilizar:**
   - Se registra todo en historia clínica
   - Si necesita internamiento, se trasladaa piso de hospitalizació
   - Si es manejable, se atiende en consultorio

---

## 📊 Situaciones Especiales en Recepción

### Paciente Llega Acompañado (Menor o Incapaz)

1. **Puede venir acompañado por:**
   - Padres/Tutores (si es menor)
   - Cuidador (si es incapaz de entender)
   - Familiar (apoyo)

2. **Autorización:**
   - Se requiere consentimiento informado
   - Acompañante firma documentos si es necesario
   - Se registra relación con paciente

3. **Acceso a Información:**
   - Acompañante puede estar en consultorio si paciente lo desea
   - Se respeta privacidad del paciente
   - Datos sensibles no se comparten sin consentimiento

---

### Paciente Llega sin Documentos

1. **Si no trae DNI/Cédula:**
   - Recepcionista lo busca por nombre
   - Si no está registrado, solicita identificación alternativa
   - Teléfono, Cédula de otra región, Pasaporte

2. **Si absolutamente no hay ID:**
   - Se registra como "PACIENTE SIN IDENTIFICAR"
   - Se le asigna un número temporal
   - Se le pide que traiga documento en próxima cita
   - Se crea nota en historia: "Paciente sin identificación verificada"

3. **Implicaciones:**
   - No puede agendar por plataforma
   - Debe venir presencialmente
   - Es más lento de procesar

---

### Paciente que no Habla Español

1. **Si no habla idioma del hospital:**
   - Se busca intérprete disponible
   - Si no hay, se intenta con gestos
   - Se documenta idioma en sistema
   - Para próximas citas, se avisa al médico

2. **Registro Especial:**
   - Se anota idioma preferido
   - Se guarda información en:
     ```
     Datos del Paciente:
     - Idioma: Inglés
     - Requiere intérprete: Sí
     ```

3. **Futuras Citas:**
   - Se intenta asignar médico que hable el idioma
   - O se reserva intérprete con anticipación

---

## ✅ Resumen: Diferencias Presencial vs Agendado

| Aspecto | AGENDADO PREVIAMENTE | PRESENCIAL SIN CITA |
|--------|----------------------|-------------------|
| **Registro** | Por plataforma | En recepción |
| **Tiempo de espera** | Conocido | Estimado |
| **Prioridad** | Según clasificación | Según urgencia + triage |
| **Notificaciones** | Automáticas | In situ |
| **Cambios** | Por SMS/Email | Comunicado en recepción |
| **Emergencia** | Rara vez | Común |
| **Derivación previa** | Se verifica | Se crea si es necesario |
| **Historia clínica** | Se consulta | Se actualiza |
| **Flexibilidad** | Menos | Más (pueden irse) |
| **Cobro** | Puede pre-pagarse | Se realiza después |

### CASO 0: Paciente Llega Presencial sin Cita Previa

**Escenario:** Pedro llega al hospital sin haber agendado por la plataforma

**¿Qué sucede?**

#### Paso 1: Pedro Llega a Recepción

**Lugar:** Mostrador de Recepción  
**Pantalla Visible:** **PANTALLA DE RECEPCIÓN** (aplicación en tablet o PC)

1. **Pedro entra al hospital sin cita previa**
   - Se acerca al mostrador de recepción
   - Ve un aviso: "¿Paciente nuevo? Registrarse aquí"

2. **La recepcionista lo recibe:**
   - "¡Bienvenido! ¿Es su primera vez aquí?"
   - "¿Cuál es su DNI?"

#### Paso 2: Búsqueda en el Sistema

3. **La recepcionista abre la PANTALLA DE RECEPCIÓN:**
   - Interfaz especial para personal administrativo
   - Opciones principales:
     - Buscar paciente existente
     - Registrar paciente nuevo
     - Crear cita presencial
     - Ver cola de espera actual

4. **Búsqueda en la Base de Datos:**
   - Si Pedro dice su DNI: "12345678"
   - La recepcionista lo busca en el sistema
   - El sistema busca en tabla `Entidad` donde `dni = 12345678`

#### Paso 3: ¿Paciente Nuevo o Existente?

**Caso A - Paciente Existente:**

5. **El sistema encuentra a Pedro**
   - Muestra sus datos:
     ```
     DATOS DEL PACIENTE:
     ━━━━━━━━━━━━━━━━━━━━━━
     Nombre: Pedro García Sánchez
     DNI: 12345678
     Edad: 52 años
     Correo: pedro@email.com
     Teléfono: +56987654321
     
     HISTORIAL:
     - Última cita: 15/Nov/2025 (Cardiología)
     - Citas totales: 5
     - Estado: Activo
     ```
   - La recepcionista continúa al Paso 4

**Caso B - Paciente Nuevo:**

5. **El sistema NO encuentra a Pedro**
   - Muestra: "Paciente no registrado"
   - La recepcionista hace clic: **"Registrar Nuevo Paciente"**
   
6. **Se abre FORMULARIO DE REGISTRO RÁPIDO:**
   - Pantalla: `paciente/registrar_pacientes.html`
   - Campos requeridos:
     ```
     [ ] Nombre                    [Pedro          ]
     [ ] Apellido Paterno          [García         ]
     [ ] Apellido Materno          [Sánchez        ]
     [ ] DNI                       [12345678       ]
     [ ] Correo Electrónico        [pedro@email.com]
     [ ] Teléfono                  [+56987654321   ]
     [ ] Contraseña                [****password***]
     
                    [REGISTRAR]  [CANCELAR]
     ```
   
7. **La recepcionista completa los datos:**
   - Escucha a Pedro o lee su documento
   - Llena el formulario
   - Hace clic en **"REGISTRAR"**

8. **Sistema crea la cuenta:**
   - Se crea registro en tabla `Entidad`
   - Se crea automáticamente `HistoriaClinica` (HCL-12345678)
   - Se asigna rol "Paciente" (código "002")
   - Se asigna `NotificationPreference` para notificaciones

#### Paso 4: Evaluación de Urgencia (Triage)

**Ubicación:** Mostrador o Sala de Espera

9. **La recepcionista (o enfermero) hace TRIAGE:**
   - Pregunta a Pedro: "¿Qué síntomas tiene?"
   - "¿Tiene dolor?"
   - "¿Cuál es la gravedad?"

10. **Opciones de Clasificación:**
    ```
    ¿CUÁL ES LA URGENCIA?
    
    ⚠️ EMERGENCIA - "Tengo dolor severo en el pecho"
       └─ Se atiende de inmediato
    
    👴 ADULTO MAYOR - "Tengo 72 años"
       └─ Prioridad alta
    
    ✅ REGULAR - "Chequeo de rutina"
       └─ Cola normal
    ```

11. **Pedro dice:** "Tengo algunos mareos ocasionales, quiero control"
    - Se clasifica como: **REGULAR**
    - El sistema asigna: **prioridad = 3**

#### Paso 5: Selección de Especialidad

12. **La recepcionista pregunta:**
    - "¿Qué especialidad necesita?"
    
13. **Se abre pantalla:** `citas/registrar_cita.html`
    - Muestra lista de especialidades:
      ```
      ESPECIALIDADES DISPONIBLES:
      ├─ Cardiología
      ├─ Dermatología
      ├─ Endocrinología
      ├─ Neurología
      ├─ Pediatría
      ├─ Medicina General
      └─ [Ver más...]
      ```

14. **Pedro necesita:**
    - "Cardiología, por los mareos"
    - La recepcionista selecciona: **Cardiología**

#### Paso 6: Selección de Médico

15. **El sistema carga médicos disponibles:**
    - Query: `get_doctores_con_horario(especialidad_id=Cardiología)`
    - Muestra:
      ```
      CARDIÓLOGOS DISPONIBLES:
      
      ○ Dr. García Pérez
        Colegiatura: CC-001
        Próximo disponible: Hoy 2:00 PM
      
      ○ Dra. López Martínez
        Colegiatura: CC-002
        Próximo disponible: Mañana 10:00 AM
      
      ○ Dr. Martínez Rodríguez
        Colegiatura: CC-003
        Próximo disponible: Mañana 3:00 PM
      ```

16. **La recepcionista selecciona:**
    - "Dr. García" - porque tiene disponibilidad hoy

#### Paso 7: Motivo y Tipo de Cita

17. **La recepcionista completa:**
    - **Motivo:** "Mareos ocasionales, solicita control cardiaco"
    - **Tipo de Cita:** 
      - ○ PRESENCIAL (seleccionado por defecto para casos sin cita)
      - ○ VIRTUAL

#### Paso 8: Crear Cita Presencial

18. **La recepcionista hace clic:** **"CREAR CITA"**

19. **El sistema ejecuta:**
    ```
    // CREAR REGISTRO EN BASE DE DATOS
    Cita.objects.create(
        paciente=Pedro,
        doctor=García,
        doctor_horario=Dr_García_HOY_2PM,
        motivo="Mareos ocasionales, solicita control cardiaco",
        clasificacion="REGULAR",
        tipo_cita="PRESENCIAL",
        estado="EN_ESPERA",
        prioridad=3,
        fecha_creacion=now()
    )
    
    // CREAR EPISODIO CLÍNICO
    EpisodioClinico.objects.create(
        historia=Pedro.historia_clinica,
        cita=cita_creada,
        tipo="consulta",
        motivo="Mareos ocasionales",
        estado="abierto"
    )
    ```

20. **Confirmación en Pantalla:**
    - Se muestra:
      ```
      ✅ CITA REGISTRADA EXITOSAMENTE
      
      Paciente: Pedro García Sánchez
      Médico: Dr. García
      Especialidad: Cardiología
      Fecha: Hoy
      Hora: 2:00 PM
      Consultorio: 205 (2do piso)
      Tipo: Presencial
      
      Número de Turno: 047
      
      ¡Por favor, dirígete a la sala de espera!
      ```

#### Paso 9: Asignación en Cola de Espera

21. **El sistema ejecuta:** `procesar_cola_doctor(Doctor_García)`
    - Busca otros pacientes en espera para el Dr. García
    - Ordena por prioridad:
      - EMERGENCIA (si las hay)
      - ADULTO_MAYOR (si las hay)
      - REGULAR (como Pedro)
    - Dentro de REGULAR: por orden de llegada

22. **La pantalla de la sala de espera se ACTUALIZA:**
    - Muestra nueva cola:
      ```
      PRÓXIMOS A SER ATENDIDOS - DR. GARCÍA
      ════════════════════════════════════════
      
      1. María López (Emergencia)      → Consultorio 205
      2. Rosa Martínez (Adulto Mayor)  → Próximo
      3. Pedro García (Regular)        → Será en ~30 min
      4. Juan Pérez (Regular)          → Será en ~50 min
      ```

#### Paso 10: Entrega de Ticket

23. **La recepcionista le entrega a Pedro:**
    - Papelito con:
      ```
      ═══════════════════════════════════════
      COMPROBANTE DE CITA PRESENCIAL
      
      Paciente: Pedro García Sánchez
      Turno: 047
      Médico: Dr. García
      Especialidad: Cardiología
      Consultorio: 205 (2do piso)
      Hora aproximada: 2:00 PM
      Tiempo estimado de espera: 30 minutos
      
      ¡Dirigirse a Sala de Espera - Cardiología!
      ═══════════════════════════════════════
      ```

24. **La recepcionista le dice:**
    - "Toma asiento en la sala de espera del segundo piso"
    - "Un enfermero te llamará cuando sea tu turno"
    - "Si tienes tu teléfono, te enviaremos SMS cuando falten 5 minutos"

#### Paso 11: SMS Opcional en Espera

25. **Si Pedro está registrado con teléfono:**
    - Pueden enviarle SMS en tiempo real:
      ```
      Turno 047: Te faltan 2 pacientes antes de ti.
      Tiempo estimado: 10 minutos. Permanece en la sala.
      ```

#### Paso 12: En la Sala de Espera

26. **Pedro ve una PANTALLA GRANDE:**
    ```
    ╔═══════════════════════════════════════╗
    ║  CARDIOLOGÍA - SALA DE ESPERA         ║
    ║                                       ║
    ║  SIENDO ATENDIDOS:                    ║
    ║  ┌─ Consultorio 205: María López     ║
    ║  └─ Consultorio 207: Rosa Martínez   ║
    ║                                       ║
    ║  PRÓXIMOS:                            ║
    ║  1. Pedro García (Turno 047) ← AQUÍ  ║
    ║  2. Juan Pérez (Turno 048)           ║
    ║                                       ║
    ║  Tiempo estimado: 10 minutos         ║
    ╚═══════════════════════════════════════╝
    ```

#### Paso 13: Lo Llaman al Consultorio

27. **El Dr. García termina con María López**
    - Marca en el sistema: **"Próximo"**
    - Sistema muestra: "**PEDRO GARCÍA - CONSULTORIO 205**"
    - Una voz (o anuncio) dice: "¡Turno 047! ¡Consultorio 205!"

#### Paso 14: Atención Médica

28. **Pedro entra al Consultorio 205**
    - Saluda al Dr. García
    - El Dr. abre el sistema:
      ```
      HISTORIA CLÍNICA - CONSULTORIO 205
      
      PACIENTE: Pedro García Sánchez
      DNI: 12345678
      EDAD: 52 años
      
      MOTIVO DE CONSULTA: 
      Mareos ocasionales, solicita control cardiaco
      
      CLASIFICACIÓN: Regular
      TIPO DE CITA: Presencial
      CREADO: HOY a las 1:30 PM
      
      [ABRIR HISTORIAL] [CREAR NOTA] [EXÁMENES]
      ```

29. **Dr. García realiza examen:**
    - Escucha síntomas
    - Toma signos vitales
    - Examina físicamente
    - Crea notas en sistema
    - Hace diagnóstico

#### Paso 15: Finalización

30. **Dr. García hace clic:** **"FINALIZAR ATENCIÓN"**
    - El estado cambia a: **"ATENDIDA"**
    - `EpisodioClinico` se marca como: **"cerrado"**
    - Se registra la hora de finalización

#### Paso 16: Post-Consulta

31. **Pedro sale del consultorio con:**
    - Diagnóstico verbal
    - Recomendaciones
    - Papelito con indicaciones (si lo requiere)

32. **Recibe confirmación por:**
    - Email automático (si tiene)
    - SMS (si está registrado)
    - Opcionalmente: resumen en papel de recepción

---

## 📊 Diagrama del Flujo Presencial Completo

```
┌─────────────────────────────────────┐
│ PEDRO LLEGA AL HOSPITAL             │
│ Sin cita previa                     │
└────────────┬────────────────────────┘
             ↓
┌─────────────────────────────────────┐
│ RECEPCIONISTA LO ATIENDE            │
│ Busca: ¿Paciente existente?         │
└────────────┬────────────────────────┘
             │
     ┌───────┴────────┐
     ↓                ↓
 EXISTE        NO EXISTE
     │                │
     │                └─→ REGISTRAR NUEVO
     │                    Formulario rápido
     │                    ↓
     └───────────┬────────┘
                 ↓
    ┌────────────────────────────┐
    │ TRIAGE (EVALUACIÓN RÁPIDA) │
    │ ¿Qué urgencia tiene?       │
    └────────────┬───────────────┘
                 ↓
        ┌────────────────┐
        │ CLASIFICACIÓN  │
        ├─ EMERGENCIA   │ → Atendido inmediato
        ├─ ADULTO_MAYOR │ → Prioridad alta
        └─ REGULAR      │ → Cola normal (Pedro)
                 ↓
    ┌────────────────────────────┐
    │ SELECCIONAR ESPECIALIDAD   │
    │ (Cardiología)              │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ SELECCIONAR MÉDICO         │
    │ (Dr. García)               │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ CREAR CITA en BASE de DATOS│
    │ - WaitlistItem             │
    │ - Cita                     │
    │ - EpisodioClinico          │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ PROCESAR COLA              │
    │ Ordenar por prioridad      │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ ENTREGAR TICKET            │
    │ Turno: 047                 │
    │ Consultorio: 205           │
    │ Tiempo est.: 30 minutos    │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ ESPERAR EN SALA            │
    │ Ver pantalla de colas      │
    │ Recibir SMS si disponible  │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ SER LLAMADO AL CONSULTORIO │
    │ Turno 047 - Consultorio 205│
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ ATENCIÓN DEL MÉDICO        │
    │ - Examen                   │
    │ - Notas en historia        │
    │ - Diagnóstico              │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ FINALIZAR ATENCIÓN         │
    │ Cita → ATENDIDA            │
    │ Episodio → CERRADO         │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ SALIR CON RESULTADOS       │
    │ Recibir email/SMS          │
    │ Historia clínica actualizada
    └────────────────────────────┘
```

---

## 🖥️ Pantallas/Vistas Utilizadas en Flujo Presencial

| Módulo | Pantalla | Archivo | Función |
|--------|----------|---------|---------|
| **Login** | Pantalla de Recepción | `login/templates/accounts/login.html` | Personal ingresa con credenciales especiales |
| **Paciente** | Registrar Paciente | `paciente/templates/paciente/registrar_pacientes.html` | Registro rápido de pacientes nuevos |
| **Citas** | Registrar Cita | `citas/templates/citas/registrar_cita.html` | Crear cita presencial |
| **Citas** | Lista de Citas | `citas/templates/citas/lista_citas.html` | Ver cola actual |
| **Citas** | Check-in | `citas/views.py:checkin_view()` | Marcar llegada |
| **Citas** | Marcar Atendida | `citas/views.py:marcar_cita_atendida()` | Finalizar atención |
| **EHR** | Historia Clínica | `citas/templates/ehr/` | Ver/editar notas |

---

## 🔑 Diferencias Clave: Presencial vs Agendado

| Aspecto | AGENDADO | PRESENCIAL |
|--------|----------|-----------|
| **Iniciador** | Paciente por plataforma | Recepcionista en mostrador |
| **Registro** | Automático online | Formulario rápido |
| **Búsqueda DNI** | No necesaria | Obligatoria |
| **Derivación** | Se valida | No se valida (presencial) |
| **Espera** | Notificación previa | Espera física |
| **Cola** | Virtual (planificada) | Física (por llegada) |
| **Cambios** | SMS/Email | Comunicado en recepción |
| **Pantalla Visible** | Del paciente (móvil) | Del personal (mostrador) |

---

### CASO 1: Paciente con Emergencia

**Escenario:** Carlos llega a emergencias con dolor agudo

**Flujo Diferente:**

1. **Carlos no agenda por la plataforma**
   - Se presenta directamente en emergencias
   - Personal lo recibe de inmediato

2. **Se le asigna clasificación EMERGENCIA**
   - Prioridad = 1 (máxima)
   - Se pone primero en la cola, desplazando otros

3. **Es atendido casi inmediatamente**
   - No espera el turno normal
   - El doctor disponible lo ve de urgencia

4. **Se registra igual en Historia Clínica**
   - Pero con tipo de episodio = "Emergencia"
   - Se pueden tomar decisiones urgentes
   - Puede generar derivaciones inmediatas

---

### CASO 2: Paciente que Cancela (No-Show)

**Escenario:** Roberto agendó pero no puede ir

**Opción A - Cancela antes:**

1. **Roberto ve en su celular la cita confirmada**
   - Se da cuenta de que no puede ir
   - Abre la plataforma
   - Busca "Mis Citas"
   - Selecciona su cita
   - Hace clic en "Cancelar Cita"

2. **El sistema lo deja cancelar**
   - Pide un motivo (opcional): "Tengo un compromiso de trabajo"
   - Se genera una nota: "Cancelada por paciente - motivo: compromiso laboral"

3. **Se libera el cupo**
   - El siguiente paciente en la cola es notificado
   - Recibe una oferta para ese horario
   - La cita de Roberto desaparece de su calendario

**Opción B - No asiste sin avisar (No-Show):**

1. **Llega la hora de la cita**
   - El Dr. García mira su lista: "Próximo: Roberto"
   - Grita el nombre pero nadie aparece
   - Espera 15 minutos

2. **Marca "No-Show" en el sistema**
   - La cita cambia a estado "NO ASISTIÓ"
   - Se registra la ausencia
   - El cupo se libera inmediatamente

3. **Roberto ve en su app:**
   - "Cita no realizada por no asistencia"
   - Se marca en su historial
   - Si tiene muchas ausencias, puede ser penalizado

---

### CASO 3: Especialidad que Requiere Derivación

**Escenario:** María necesita endocrinólogo

**Flujo Diferente:**

1. **María intenta agendar con endocrinólogo**
   - El sistema verifica: "¿Tiene derivación válida?"
   - María nunca ha visto endocrinólogo
   - Respuesta: NO

2. **El sistema bloquea el agendamiento**
   - Mensaje: "Esta especialidad requiere derivación médica previa"
   - "Por favor, solicita una derivación a tu doctor de cabecera"
   - No puede continuar

3. **María va con su médico general**
   - Le dice: "Necesito ver un endocrinólogo"
   - El médico lo anota y crea la derivación en el sistema:
     ```
     DERIVACIÓN
     Paciente: María
     Para especialidad: Endocrinología
     Válida desde: Hoy
     Válida hasta: 6 meses
     ```

4. **Al día siguiente, María puede agendar**
   - El sistema ve: "¿Tiene derivación?" → SÍ ✓
   - Permite que continúe con el agendamiento
   - Elige endocrinólogo, hora, etc.
   - Completa todo normalmente

---

## 📊 Casos de Uso Específicos

### CASO 5: Consulta Virtual (Telemedicina)

**Escenario:** Ana agendó una consulta VIRTUAL con el Dr. López

**¿Qué sucede diferente?**

1. **Ana agendó presencialmente:**
   - Especialidad: Dermatología
   - Tipo: VIRTUAL
   - Horario: Viernes 3:00 PM
   - Se confirma exactamente igual que presencial

2. **Ana recibe notificaciones iguales:**
   - Email de confirmación
   - SMS de recordatorio 48h antes
   - SMS de recordatorio 2h antes

3. **30 minutos antes (Viernes 2:30 PM):**
   - Ana recibe un email con un **link de videoconferencia**
     ```
     ENLACE A TU CONSULTA VIRTUAL:
     
     Haz clic aquí para entrar:
     www.hospital.com/videollamada/12345
     
     Médico: Dr. López
     Horario: 3:00 PM
     Duración estimada: 20-30 minutos
     
     ⚠️ Importante:
     - Asegúrate de tener buena iluminación
     - Cámara y micrófono funcionando
     - Conexión estable de internet
     - Espacio privado sin ruidos
     ```

4. **A la hora exacta (3:00 PM):**
   - Ana hace clic en el enlace
   - Se abre una ventana de videoconferencia
   - El Dr. López está esperando
   - Se saludan y comienza la consulta

5. **Durante la Consulta Virtual:**
   - Dr. López puede:
     - Ver al paciente y sus síntomas
     - Hacer preguntas detalladas
     - Anotar observaciones
     - Hacer diagnóstico (si es posible)
     - Recetar medicamentos
     - Derivar si es necesario
   
   - Limitaciones vs presencial:
     - No puede auscultar con estetoscopio
     - No puede hacer examen físico completo
     - Depende de que el paciente le muestre áreas

6. **Registro en Historia Clínica:**
   - Dr. López abre el sistema en otra ventana
   - Mientras consulta, anota:
     - Síntomas reportados
     - Observaciones visuales
     - Diagnóstico
     - Plan de tratamiento
   - Todo se registra igual que presencial

7. **Finalización:**
   - Dr. López dice: "De acuerdo, te enviaré la receta por email"
   - Cierra la videollamada
   - Ana ve: "Consulta completada"
   - Recibe resumen por email

8. **Diferencias Respecto a Presencial:**
   - ✅ NO necesita ir al hospital
   - ✅ Ahorra tiempo de transporte
   - ✅ Puede consultar desde casa
   - ✅ Útil para seguimientos
   - ❌ No permite examen físico completo
   - ❌ Requiere tecnología y conexión

---

### CASO 6: Derivación Urgente durante Consulta

**Escenario:** El Dr. García ve a Juan y descubre algo que necesita especialista

**¿Qué sucede?**

1. **Durante la consulta:**
   - Dr. García examina a Juan
   - Nota algo anormal en el EKG
   - Decide que necesita Ver a un cardiólogo especializado

2. **Dr. García crea la Derivación en el Sistema:**
   - Abre la opción "Crear Derivación"
   - Selecciona:
     - Especialidad: Cardiología (especializada)
     - Urgencia: NORMAL o URGENTE
     - Notas: "Se observa arritmia en EKG, requiere evaluación urgente"
   - Presiona "Enviar Derivación"

3. **Sistema crea la Derivación:**
   - Se registra automáticamente en la Historia Clínica
   - Se notifica a Juan:
     ```
     DERIVACIÓN RECIBIDA:
     
     El Dr. García te ha derivado a:
     Cardiología Especializada
     
     Esta derivación es VÁLIDA por 6 MESES
     Puedes agendar con cualquier cardiólogo especializado
     
     [AGENDAR CITA AHORA]
     ```

4. **Juan puede agendar inmediatamente:**
   - Hace clic en "Agendar Cita"
   - Elige cardiología especializada
   - El sistema la reconoce como válida
   - Permite continuar sin bloqueos

5. **Prioridad:**
   - Si la derivación es URGENTE:
     - Se coloca de prioridad ALTA
     - Se busca primer horario disponible
     - Se intenta agendar para ese mismo día o próximo día
   - Si es NORMAL:
     - Se sigue el flujo regular de agendar

---

**Escenario:** Doña Rosa tiene 78 años y necesita cita

**Lo que pasa diferente:**

1. **Rosa agenda cita normalmente**
   - Pero selecciona: "ADULTO MAYOR"
   - En la clasificación

2. **Sistema le da PRIORIDAD ALTA**
   - Prioridad 2 (después de emergencias solamente)
   - Se le ofrece cupo antes que pacientes regulares

3. **Rosa espera MENOS tiempo**
   - Si hay 5 pacientes regulares esperando
   - Rosa se coloca delante de ellos
   - Solo se mantiene detrás de emergencias

4. **En la sala de espera:**
   - El personal la trata con atención especial
   - Le ofrecen asiento cómodo
   - La llaman antes si hay oportunidad

---

## ✅ Resumen del Flujo Completo

**Paso a Paso, lo que ve el paciente:**

1. **Se registra o inicia sesión**
   - Crea su cuenta con datos personales
   - O entra con DNI y contraseña

2. **Elige especialidad y médico**
   - Ve opciones disponibles
   - Selecciona lo que necesita

3. **Completa formulario**
   - Dice si es emergencia, adulto mayor, o regular
   - Elige presencial o virtual
   - Explica por qué va al doctor

4. **Envía solicitud**
   - Sistema lo pone en una cola de espera
   - "Te avisaremos cuando se libere un cupo"

5. **Recibe oferta de cupo**
   - Email: "Se liberó un cupo para ti el martes a las 10:00 AM"
   - SMS: Recordatorio con los detalles
   - Tiene 15 minutos para decir que sí

6. **Acepta o rechaza**
   - Si dice SÍ: Cita confirmada
   - Si dice NO: Vuelve a esperar otro cupo
   - Si no responde: Automaticamente rechazada

7. **Recibe recordatorios**
   - Un día antes: SMS "Tu cita es mañana a las 10:00 AM"
   - 2 horas antes: SMS "Tu cita es en 2 horas"

8. **Llega al hospital**
   - Va a recepción
   - "Tengo cita con el Dr. García"
   - Recepcionista lo registra
   - Le dice dónde esperar

9. **Espera en la sala**
   - Ve pantalla con orden de atención
   - Espera su turno

10. **Es llamado al consultorio**
    - Doctor lo atiende
    - Hace examen
    - Toma signos vitales
    - Crea diagnóstico y plan

11. **Se va con sus resultados**
    - Doctor le entrega plan de tratamiento
    - Va a recepción
    - Se va a casa

12. **Recibe confirmación por email**
    - "Tu cita fue completada"
    - "Aquí está el resumen de tu consulta"
    - Puede ver su historia clínica online

13. **Recibe encuesta**
    - SMS preguntando: "¿Cómo fue tu experiencia?"
    - Responde según su satisfacción

---

## 🔄 El Flujo en Diagrama Simple

```
┌─────────────────────────────────────────────────────────┐
│  PACIENTE SE REGISTRA / INICIA SESIÓN                  │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  SELECCIONA ESPECIALIDAD Y MÉDICO                      │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  COMPLETA FORMULARIO CON MOTIVO Y CLASIFICACIÓN        │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  ENTRA EN COLA DE ESPERA                               │
└────────────────┬────────────────────────────────────────┘
                 ↓
         (Sistema automático ordena por prioridad)
         (Emergencia → Adulto Mayor → Regular)
                 ↓
┌─────────────────────────────────────────────────────────┐
│  RECIBE OFERTA DE CUPO (Email + SMS)                   │
│  "Tienes 15 minutos para aceptar"                      │
└────────────────┬────────────────────────────────────────┘
                 ↓
        ┌────────┴────────┐
        ↓                 ↓
    ACEPTA          RECHAZA o NO RESPONDE
        │                 │
        ↓                 ↓
    Cita Confirmada    Vuelve a la cola
        │
        ↓
┌─────────────────────────────────────────────────────────┐
│  RECIBE RECORDATORIOS (48h, 2h antes)                  │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  LLEGA AL HOSPITAL Y SE REGISTRA EN RECEPCIÓN          │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  ESPERA EN SALA DE ESPERA (VE PANTALLA CON SU TURNO)   │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  MÉDICO LO LLAMA AL CONSULTORIO                        │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  EXAMEN Y CONSULTA                                      │
│  - Doctor examina                                       │
│  - Toma signos vitales                                  │
│  - Hace diagnóstico                                     │
│  - Crea plan de tratamiento                             │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  HISTORIA CLÍNICA SE ACTUALIZA AUTOMÁTICAMENTE         │
│  - Todas las notas quedan registradas                   │
│  - Disponible para futuros doctores                     │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  PACIENTE SE VA CON RESULTADOS                         │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  RECIBE EMAIL CON RESUMEN DE CONSULTA                  │
│  Puede ver su historial clínico completo               │
└────────────────┬────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────┐
│  RECIBE ENCUESTA DE SATISFACCIÓN (SMS)                 │
│  Responde: ¿Cómo fue tu experiencia?                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🎭 Ejemplos de Mensajes que Recibe el Paciente

### Email 1: Oferta de Cupo
```
DE: Sistema Hospital
ASUNTO: ¡Se liberó un cupo para ti!

¡Hola Juan!

Se ha liberado un cupo para ti con el Dr. García en CARDIOLOGÍA.

📅 Fecha: Martes, 14 de Diciembre de 2025
🕙 Hora: 10:00 AM
🏥 Lugar: Consultorio 205, 2do piso

⏰ IMPORTANTE: Tienes 15 MINUTOS para confirmar.

[ACEPTAR CUPO] [RECHAZAR]
```

### SMS 1: Recordatorio 48 horas
```
RECORDATORIO: Tu cita es MAÑANA martes a las 10:00 AM
con el Dr. García - Cardiología.
Consultorio 205. Llega 10 minutos antes.
```

### SMS 2: Recordatorio 2 horas
```
¡ÚLTIMA NOTIFICACIÓN!
Tu cita es en 2 HORAS con Dr. García - Cardiología.
10:00 AM - Consultorio 205.
Si no puedes ir, cancela en: www.hospital.com
```

### Email 2: Confirmación de Atención
```
DE: Sistema Hospital
ASUNTO: Tu cita ha sido completada ✓

¡Gracias por visitarnos, Juan!

Tu consulta con el Dr. García ha sido registrada.

RESUMEN:
- Médico: Dr. García
- Especialidad: Cardiología
- Diagnóstico: Mareos posturales benignos
- Plan: Reposo, hidratación, evitar cambios de posición
- Próxima cita: En 3 meses

[VER MI HISTORIAL COMPLETO]
```

### SMS 3: Encuesta de Satisfacción
```
¿Cómo fue tu experiencia hoy?

¿Fue puntual? (Sí/No)
Calificación: ⭐⭐⭐⭐⭐
¿Lo recomendarías? (Sí/No)

Responde: www.hospital.com/encuesta
```

---

## 📌 Puntos Clave del Sistema

✅ **Automatización:** El sistema automáticamente ordena pacientes por prioridad

✅ **Notificaciones:** El paciente siempre sabe dónde está en el proceso

✅ **Prioridades:** Emergencias y adultos mayores se atienden primero

✅ **Derivaciones:** Algunas especialidades requieren que otro doctor lo derive primero

✅ **Historia Clínica Digital:** Todo queda registrado para futuras consultas

✅ **Recordatorios:** SMS/Email automáticos para no olvidar la cita

✅ **Flexibilidad:** Puede aceptar, rechazar o cancelar citas fácilmente

✅ **Retroalimentación:** Se pide evaluación de satisfacción para mejorar

---

## 🎯 Lo Más Importante

El paciente **nunca tiene que preocuparse** por:
- Llamar para agendar
- Anotar fechas y horas
- Acordarse de la cita
- Perder su papelito con la cita

**El sistema lo hace todo:**
- Lo notifica por email y SMS
- Le recuerda con tiempo
- Guarda toda su información médica
- Ordena la cola automáticamente por prioridad

**El paciente solo tiene que:**
1. Hacer clic en "Agendar Cita"
2. Seleccionar especialidad y médico
3. Llegar al hospital a la hora indicada
4. Esperar su turno
5. Ser atendido
