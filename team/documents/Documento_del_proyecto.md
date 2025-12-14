# Documento del proyecto
# Indicadores del Proyecto

| Miembro del equipo        | Horas | Commits | LoC | Test | Issues | Work Item            | Dificultad |
|---------------------------|-------|---------|-----|------|--------|----------------------|------------|
| Benítez Galván, Mario        | HH    | 66      | 1.293  | ZZ   | 10     | Creación de comentarios en Datasets     | L      |
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

# Visión Global del Proceso de Desarrollo (1.500 palabras aproximadamente)

Debe dar una visión general del proceso que ha seguido enlazándolo con las herramientas que ha utilizado. Ponga un ejemplo de un cambio que se proponga al sistema y cómo abordaría todo el ciclo hasta tener ese cambio en producción. Los detalles de cómo hacer el cambio vendrán en el apartado correspondiente.

---

# Entorno de Desarrollo (800 palabras aproximadamente)

Debe explicar cuál es el entorno de desarrollo que ha usado, cuáles son las versiones usadas y qué pasos hay que seguir para instalar tanto su sistema como los subsistemas relacionados para hacer funcionar el sistema al completo. Si se han usado distintos entornos de desarrollo por parte de distintos miembros del grupo, también debe referenciarlo aquí.

---

# Ejercicio de Propuesta de Cambio

Se presentará un ejercicio con una propuesta concreta de cambio en la que a partir de un cambio que se requiera, se expliquen paso por paso (incluyendo comandos y uso de herramientas) lo que hay que hacer para realizar dicho cambio. Debe ser un ejercicio ilustrativo de todo el proceso de evolución y gestión de la configuración del proyecto.

---

# Conclusiones y Trabajo Futuro

Se enunciarán algunas conclusiones y se presentará un apartado sobre las mejoras que se proponen para el futuro (curso siguiente) y que no han sido desarrolladas en el sistema que se entrega.
