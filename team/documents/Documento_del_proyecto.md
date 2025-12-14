# Documento del proyecto
# Indicadores del Proyecto

| Miembro del equipo        | Horas | Commits | LoC | Test | Issues | Work Item            | Dificultad |
|---------------------------|-------|---------|-----|------|--------|----------------------|------------|
| Benítez Galván, Mario        | HH    | 66      | 1.293  | 19   | 10     | Creación de comentarios en Datasets     | L      |
| Mantecón Rodríguez, Alejandro        | HH    | 22      | 534  | 9   | II     | Descripción breve     | H/M/L      |
| Moreno Ríos, Juan        | HH    | 82      | 2.781  | 20   | 13     | Seguidores en autores y comunidades     | M     |
| Nuño García, Manuel        | HH    | 44      | 14.696  | ZZ   | 12     | Doble factor de autenticación     | H      |
| Ruíz López, Juan Antonio        | HH    | 37      | 1.072  | ZZ   | 18     | Descripción breve     | H/M/L      |
| Ruíz Martín, Alejandro        | HH    | 28      | 756  | ZZ   | 11     | Descripción breve     | H/M/L      |
| **TOTAL**                  | tHH   | 279     | 21.132 | tZZ  | 73    | Descripción breve     | H (X)/M (Y)/L (Z) |

---

# Resumen Ejecutivo

RubikHub es una plataforma de acceso abierto creada para la gestión, almacenamiento y publicación de datasets relacionados con el cubo de Rubik. Su propósito es proporcionar una herramienta eficiente y accesible para los investigadores, desarrolladores y entusiastas del cubo de Rubik, que puedan beneficiarse del acceso libre a conjuntos de datos valiosos para avanzar en la investigación y el desarrollo de algoritmos relacionados con este enigmático objeto matemático.

El sistema permite a los usuarios cargar, versionar y gestionar datasets de manera sencilla, pero con un fuerte enfoque en la seguridad, la accesibilidad y la interacción comunitaria. Como parte de su funcionalidad, RubikHub integra características avanzadas que mejoran tanto la experiencia de usuario como la integridad del sistema, convirtiéndolo en una plataforma útil para la comunidad científica y académica. A continuación, se detallan las características más destacadas de la plataforma.

Una de las principales mejoras que hemos implementado en RubikHub es la doble factor de autenticación (2FA). Esta medida de seguridad proporciona una capa adicional para proteger las cuentas de usuario frente a accesos no autorizados. A medida que los proyectos de investigación requieren mayor seguridad en los datos, la protección adicional que ofrece la autenticación en dos pasos es crucial para asegurar que solo los usuarios autorizados puedan acceder a sus cuentas y gestionar los datasets. Este sistema de seguridad está diseñado para evitar posibles vulnerabilidades, especialmente en plataformas que manejan información valiosa y sensible.

RubikHub también facilita la interacción social dentro de la plataforma mediante la implementación de un sistema de seguidores para autores y comunidades. Los usuarios pueden seguir a autores específicos para estar al tanto de los nuevos datasets que publiquen o actualicen. Además, pueden unirse a comunidades relacionadas con el cubo de Rubik, ya sea para discutir teorías, compartir resultados o colaborar en proyectos de investigación. Esto fomenta la creación de una comunidad activa y dinámica, que contribuye al intercambio de ideas y la expansión del conocimiento en torno al cubo de Rubik.

Para mejorar la colaboración, RubikHub ha integrado una funcionalidad de comentarios en datasets. Los usuarios pueden dejar comentarios sobre cualquier dataset, lo que permite generar discusiones constructivas sobre la calidad, aplicabilidad y posibles mejoras de los datos. Esta función también es útil para la retroalimentación entre investigadores, quienes pueden compartir sugerencias o advertencias relacionadas con los conjuntos de datos. Los comentarios aumentan la interacción entre los miembros de la plataforma y mejoran el valor del dataset para futuros usuarios.

Una de las características implementadas para ayudar a los usuarios a evaluar la popularidad de un dataset es el contador de descargas. Cada dataset tiene un contador que indica cuántas veces ha sido descargado. Esta información es útil para identificar datasets que son ampliamente utilizados y relevantes para la comunidad. Además, permite a los creadores de los datasets obtener métricas sobre el impacto de su trabajo, lo que puede ser un factor motivador y un indicador de la calidad y utilidad de los datos que han compartido.

Para hacer la plataforma aún más interactiva y para destacar los recursos más relevantes, hemos introducido un Top 3 de los datasets más populares de las últimas semanas. Este ranking muestra los tres datasets más descargados o más utilizados, permitiendo que los usuarios descubran rápidamente qué datasets están ganando tracción y son más populares dentro de la comunidad. Esta funcionalidad es especialmente útil para aquellos que buscan comenzar con datasets de alta demanda o interés en la comunidad.

Una de las características esenciales de RubikHub es la capacidad de versionado de datasets. Este sistema permite que los usuarios suban nuevas versiones de un mismo dataset, garantizando que los cambios sean gestionados correctamente y que los usuarios puedan acceder tanto a las versiones más recientes como a las anteriores. La gestión de versiones es crucial en proyectos de investigación donde las actualizaciones o correcciones de datos pueden ocurrir regularmente. RubikHub asegura que todas las versiones de un dataset estén bien documentadas y sean fácilmente accesibles, lo que facilita la trazabilidad de los cambios realizados.

RubikHub también incluye una característica innovadora denominada Fakenodo, que permite gestionar datos ficticios o de prueba. Esta funcionalidad es útil en escenarios donde los investigadores necesitan generar datos de prueba sin comprometer la integridad de los datos reales. Los Fakenodos permiten a los usuarios cargar datos simulados para realizar pruebas de carga, experimentos o incluso para generar ejemplos de cómo se utilizarían ciertos tipos de datos en aplicaciones prácticas. Esta característica abre nuevas posibilidades para la exploración y experimentación con datos sin necesidad de utilizar datos reales o sensibles.

Otra funcionalidad destacada de RubikHub es el soporte completo para datasets en formato CSV, lo que facilita la integración con diversas herramientas y plataformas de análisis de datos. El formato CSV es ampliamente utilizado en la comunidad científica debido a su simplicidad y facilidad de uso, por lo que al permitir la carga y el almacenamiento de datasets en este formato, RubikHub asegura que los datos puedan ser fácilmente reutilizados por investigadores utilizando herramientas comunes como Python, R o Matlab. Esta capacidad de importar y exportar datasets en formato CSV facilita la interoperabilidad de RubikHub con otros sistemas y plataformas de análisis de datos.

En resumen, RubikHub es una plataforma completa y avanzada que no solo permite la gestión eficiente de datasets relacionados con el cubo de Rubik, sino que también incorpora características de colaboración, seguridad y usabilidad que mejoran la experiencia del usuario. La implementación de doble factor de autenticación, el sistema de seguidores, los comentarios en datasets, los contadores de descargas, el ranking de los datasets más populares, el versionado y el soporte para formatos CSV hacen de RubikHub una plataforma robusta y adaptable. Además, la inclusión de Fakenodo y otras funcionalidades permite a los usuarios experimentar y gestionar datos de manera más flexible y efectiva.

---

# Descripción del Sistema (1.500 palabras aproximadamente)

Se explicará el sistema desarrollado desde un punto de vista funcional y arquitectónico. Se hará una descripción tanto funcional como técnica de sus componentes y su relación con el resto de subsistemas. Habrá una sección que enumere explícitamente cuáles son los cambios que se han desarrollado para el proyecto.

---

# Visión Global del Proceso de Desarrollo

El desarrollo de software en nuestro proyecto sigue un proceso estructurado y metódico que busca garantizar la calidad del código, la trazabilidad de los cambios y la eficiencia en la integración y despliegue de nuevas funcionalidades. Este proceso se apoya fuertemente en herramientas modernas de control de versiones, gestión de tareas y automatización de integración y despliegue continuo, asegurando que cada cambio se realice de manera controlada y con cobertura de pruebas adecuada.

## Gestión de Tareas y Planificación

El primer paso en nuestro ciclo de desarrollo consiste en la **creación de tareas en GitHub** utilizando una plantilla predefinida que estandariza la información mínima requerida para iniciar el trabajo. Esta plantilla permite registrar de manera clara el objetivo de la tarea, los criterios de aceptación, dependencias y posibles riesgos asociados. Una vez creada la tarea, se identifican y crean **subtareas** si la complejidad de la implementación lo requiere, permitiendo desglosar la funcionalidad en componentes más manejables. Esto asegura que incluso tareas grandes puedan gestionarse de manera incremental, reduciendo el riesgo de errores y facilitando la revisión por pares.

Posteriormente, la tarea es **asignada a un desarrollador**, quien será responsable de su implementación y seguimiento. Este enfoque permite distribuir la carga de trabajo de manera equitativa, además de asignar responsabilidades claras para cada cambio en el sistema.

## Flujo de Desarrollo con Git

Una vez asignada la tarea, el desarrollador procede a crear una **rama específica para la implementación**, siguiendo la convención de nomenclatura `"Issue" + nº de la Issue`, a partir de la rama `trunk`. Este enfoque asegura que cada cambio se aísle del código principal, evitando que errores en desarrollo afecten la estabilidad de la versión en producción. El uso de ramas dedicadas permite además un historial limpio y ordenado de los commits relacionados con cada tarea específica.

Con la rama creada, la **issue se mueve del estado "DONE" a "IN PROGRESS"**, reflejando visualmente en GitHub que el trabajo ha comenzado. Durante esta fase, el desarrollador realiza la implementación siguiendo las especificaciones de la tarea. Los **commits se realizan de manera unitarias y siguiendo la convención de Conventional Commits**, garantizando que cada cambio quede documentado y pueda rastrearse fácilmente. Esto no solo mejora la trazabilidad, sino que también facilita la generación automática de changelogs y la identificación de errores en revisiones futuras.

## Pruebas y Cobertura

El desarrollo incluye de manera obligatoria la creación de **tests que validen la funcionalidad implementada**. Estos tests permiten detectar errores antes de que los cambios se integren a la rama principal, minimizando riesgos y asegurando que la nueva funcionalidad cumpla con los criterios de aceptación definidos inicialmente. Además, se verifica que la **cobertura de tests** se mantenga o mejore, promoviendo una base de código más robusta y confiable.

Una vez que se han completado avances parciales significativos (incluyendo los tests), se realiza un **merge a la rama trunk**, integrando los cambios de manera incremental. Finalmente, al terminar la tarea por completo, se efectúa un **merge final a trunk**, consolidando la implementación.

## Integración y Despliegue Continuo

Tras la integración de los cambios, se verifica que los **workflows de GitHub Actions** funcionen correctamente, asegurando que los pipelines de CI (Integración Continua) validen la compilación, ejecución de tests y demás pasos automatizados. Esto se complementa con la comprobación del **despliegue en Render**, confirmando que la nueva versión del software se despliegue correctamente en un entorno controlado de pruebas o preproducción.

Una vez validados estos pasos, la **issue se marca como DONE** y la **rama temporal se elimina**, manteniendo el repositorio limpio y organizado. Posteriormente, se realiza un **merge de trunk a main localmente**, asegurando que la rama principal refleje todos los cambios recientes. Todos los tests se ejecutan nuevamente para confirmar la estabilidad antes de generar una **nueva versión del software**.

Finalmente, se sube el merge asociado a esta nueva versión al repositorio remoto y se verifica que los **workflows de CD (Despliegue Continuo)** se ejecuten correctamente. Como parte de este proceso, existe un **workflow de notificación en Discord** que informa del **estado del despliegue en Render**, indicando cuándo el servicio ha terminado de cargarse y se encuentra accesible. Esta notificación permite al desarrollador conocer el momento exacto en el que puede acceder a la aplicación desplegada para realizar las comprobaciones manuales necesarias, sin necesidad de supervisar continuamente el proceso de despliegue.

Adicionalmente, junto con el mensaje de despliegue, se ejecuta **otro workflow que genera y publica un artifact en GitHub**, el cual incluye información detallada sobre la **cobertura de tests** del proyecto. Este artifact proporciona un acceso rápido y centralizado a los resultados de cobertura, permitiendo comprobar que los estándares de calidad se mantienen tras cada despliegue y facilitando el seguimiento de la evolución del proyecto a lo largo del tiempo.

Más allá de los pipelines principales de integración y despliegue, el proyecto cuenta con varios **workflows de CI adicionales**, los cuales pueden **consultarse en cualquier momento para evaluar tanto el estado del proyecto como la progresión del equipo de desarrollo**. Entre ellos se incluyen:
- Un workflow encargado de generar un **informe de seguridad mediante Bandit**, permitiendo detectar posibles vulnerabilidades o malas prácticas en el código.
- Un workflow integrado con **Codacy**, que analiza la calidad del código, el cumplimiento de estándares y la presencia de problemas técnicos.
- Un workflow que **mide diferentes estadísticas relacionadas con la actividad de los miembros del equipo**, proporcionando una visión objetiva sobre la participación y evolución del desarrollo.
- Un workflow dedicado exclusivamente a **comprobar de forma continua que todos los tests del proyecto funcionan correctamente**, actuando como una salvaguarda constante frente a regresiones.

Estos workflows refuerzan la transparencia, la calidad y la trazabilidad del desarrollo, permitiendo realizar un seguimiento continuo del estado del proyecto y facilitando la toma de decisiones basadas en métricas objetivas.

Esto garantiza que la versión lista para producción cumpla con todos los estándares de calidad y que la transición a los usuarios finales se realice de manera controlada, eficiente y verificable.



## Ejemplo de Ciclo de Desarrollo de un Cambio

Para ilustrar cómo este proceso se aplica en la práctica, consideremos un ejemplo en el que se propone agregar una **funcionalidad de notificación por correo electrónico** cuando un usuario completa una tarea.

1. **Creación de la tarea**: Se genera un Issue en GitHub titulado "Notificación por correo al completar tareas", incluyendo la descripción, criterios de aceptación, posibles dependencias (por ejemplo, integración con un servicio de correo externo) y subtareas relacionadas: 
   - Configuración del servicio de correo
   - Implementación de la lógica de envío
   - Creación de tests unitarios y de integración

2. **Asignación y rama**: La tarea se asigna a un desarrollador y se crea la rama `Issue-42` a partir de `trunk`. La issue se marca como `IN PROGRESS`.

3. **Implementación y commits**: El desarrollador implementa la funcionalidad paso a paso, realizando commits unitarios siguiendo la convención de Conventional Commits. Por ejemplo:
   - `feat: add email service configuration`
   - `test: add unit test for email sending`

4. **Pruebas y cobertura**: Se crean y ejecutan tests que comprueban que la notificación se envía correctamente, que los mensajes se formatean adecuadamente y que no se envían correos en condiciones no permitidas. Se verifica que la cobertura no disminuya y se corrigen posibles fallos.

5. **Merge a trunk y validación**: Una vez completadas todas las subtareas, se realiza un merge a `trunk`. Se ejecutan los workflows de CI y se comprueba que el despliegue en Render de preproducción funciona correctamente.

6. **Finalización y despliegue**: La issue se marca como `DONE`, la rama temporal se elimina, y se mergea `trunk` a `main` localmente. Se crean los tags de versión correspondientes y se confirma que los pipelines de CD desplieguen correctamente la nueva versión a producción.

Este ejemplo demuestra cómo el flujo de trabajo asegura **control, calidad y trazabilidad** en cada etapa, desde la concepción de la tarea hasta la entrega en producción.

## Herramientas Clave Utilizadas

En nuestro proceso se utilizan varias herramientas que facilitan y aseguran cada etapa del desarrollo:

- **GitHub**: Para gestión de tareas, creación de issues, control de versiones y seguimiento del progreso.
- **Ramas Git**: Para aislar cambios y mantener un historial organizado.
- **GitHub Actions**: Para automatizar la Integración y el Despliegue Continuo (CI/CD).
- **Render**: Como plataforma de despliegue, asegurando que las versiones generadas sean consistentes y estables.
- **Pruebas automatizadas**: Para garantizar la calidad y estabilidad del software en cada cambio.

## Conclusión

El proceso de desarrollo adoptado proporciona una **visión global integral**, cubriendo desde la planificación inicial hasta la entrega de la funcionalidad en producción. Cada cambio sigue un ciclo estructurado que incluye: planificación, desarrollo aislado, pruebas rigurosas, integración controlada y despliegue seguro. La combinación de herramientas modernas, buenas prácticas de control de versiones y cobertura de tests asegura que el software se mantenga robusto, confiable y fácil de mantener.

Al seguir este proceso, el equipo puede introducir cambios de manera incremental y segura, minimizando riesgos, optimizando la colaboración y garantizando la trazabilidad de cada modificación realizada en el sistema.



# Entorno de Desarrollo (800 palabras aproximadamente)

Debe explicar cuál es el entorno de desarrollo que ha usado, cuáles son las versiones usadas y qué pasos hay que seguir para instalar tanto su sistema como los subsistemas relacionados para hacer funcionar el sistema al completo. Si se han usado distintos entornos de desarrollo por parte de distintos miembros del grupo, también debe referenciarlo aquí.

---

# Ejercicio de Propuesta de Cambio

Se presentará un ejercicio con una propuesta concreta de cambio en la que a partir de un cambio que se requiera, se expliquen paso por paso (incluyendo comandos y uso de herramientas) lo que hay que hacer para realizar dicho cambio. Debe ser un ejercicio ilustrativo de todo el proceso de evolución y gestión de la configuración del proyecto.

---

# Conclusiones y Trabajo Futuro

Se enunciarán algunas conclusiones y se presentará un apartado sobre las mejoras que se proponen para el futuro (curso siguiente) y que no han sido desarrolladas en el sistema que se entrega.
