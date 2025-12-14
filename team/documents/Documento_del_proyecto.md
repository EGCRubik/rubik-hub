# Documento del proyecto
# Indicadores del Proyecto

| Miembro del equipo        | Horas | Commits | LoC | Test | Issues | Work Item            | Dificultad |
|---------------------------|-------|---------|-----|------|--------|----------------------|------------|
| Benítez Galván, Mario        | HH    | 66      | 1.293  | 19   | 10     | Creación de comentarios en Datasets     | L      |
| Mantecón Rodríguez, Alejandro        | 50    | 22      | 534  | 9   | 10     | Trending Datasets     | M      |
| Moreno Ríos, Juan        | HH    | 82      | 2.781  | 20   | 13     | Seguidores en autores y comunidades     | M     |
| Nuño García, Manuel        | HH    | 44      | 14.696  | ZZ   | 12     | Doble factor de autenticación     | H      |
| Ruíz López, Juan Antonio        | 50    | 37      | 1.072  | 4   | 18     | Gestionar versionado de los datasets     | H      |
| Ruíz Martín, Alejandro        | HH    | 28      | 756  | ZZ   | 11     | Conntabilizar el numero de descargas de un dataset     | L      |
| **TOTAL**                  | tHH   | 279     | 21.132 | tZZ  | 73    | Descripción breve     | H (2)/M (2)/L (5) |

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

RubikHub es la evolución de un sistema previo orientado a datasets de feature models con contenido de ficheros en formato UVL hacia una plataforma centrada en la publicación, consulta y reutilización de datasets tabulares en formato .csv relacionados con cubos de Rubik. A nivel funcional, el sistema permite a usuarios (autenticados o no, según la visibilidad del dataset) explorar datasets, consultar su información, descargar ficheros y, en el caso de autores/creadores, gestionar el ciclo de vida de publicación, versionado y enriquecimiento social del contenido (comentarios y seguimiento). A nivel arquitectónico, la solución mantiene una separación clara entre capas: presentación (UI), lógica de aplicación (servicios y reglas de negocio), persistencia (repositorios y modelos) y módulos transversales como seguridad/autenticación.

En lo que sigue se describen los cambios y componentes del sistema siguiendo exactamente los enunciados indicados, explicando tanto el objetivo funcional como el impacto técnico y su integración con el resto del proyecto.


**Forma de conversión de UVLHub a RubikHub**

La conversión de UVLHub a RubikHub consistió, esencialmente, en eliminar el foco y las dependencias del dominio UVL y reorientar el sistema para almacenar y servir exclusivamente datasets tabulares en formato CSV. Funcionalmente, el cambio principal es que el sistema dejó de tratar los ficheros como artefactos .uvl asociados a un modelo UVL y pasó a tratarlos como ficheros .csv con un esquema y propiedades relevantes para el tipo de datos que RubikHub gestiona.

Técnicamente, el núcleo de esta transición fue una remodelación del modelo de fichero. En el sistema original, la capa de datos y parte de la lógica estaban condicionadas por entidades y campos propios de UVL. Para adaptarlo, se renombró y transformó el modelo central: el antiguo modelo ligado a UVL se sustituyó por un FileModel (modelo de fichero genérico para CSV). Este FileModel elimina atributos específicos de UVL y añade aquellos que aportan valor en un dataset tabular (por ejemplo, información y metadatos coherentes con un CSV). Este cambio no solo afectó al almacenamiento, sino a todo lo que lo rodeaba: validaciones, carga inicial de datos y batería de pruebas.

En la capa de validación, el sistema tenía reglas explícitas que verificaban que los ficheros subidos cumplían el formato .uvl. Tras la conversión, esas validaciones se sustituyeron por comprobaciones de extensión y consistencia orientadas a .csv. Esto implica que, en los puntos de entrada de carga de ficheros (formularios o endpoints), el sistema filtra el tipo de fichero admitido para mantener la coherencia del repositorio, evitando que se suban artefactos que ya no pertenecen al dominio RubikHub. Además, este cambio de validación obliga a revisar cualquier lógica secundaria que asumiera que el contenido era UVL, ya que ahora el flujo de datos y la visualización deben alinearse con la naturaleza tabular de los CSV.

También se tuvo que intervenir en los seeders (datos de inicialización). En UVLHub estaban pensados para poblar el sistema con ejemplos .uvl y referencias a entidades del dominio UVL. En RubikHub esos seeders no solo eran irrelevantes, sino que rompían la consistencia del sistema, por lo que se corrigieron para utilizar ficheros .csv y el nuevo modelo FileModel. Del mismo modo, los tests que validaban flujos completos sobre .uvl se reescribieron para cubrir el nuevo comportamiento: subida/validación/descarga sobre .csv, relaciones correctas entre entidades y reglas específicas del nuevo ciclo de vida.

Respecto al “pipeline” de conversión y dónde se ejecuta, la transición se abordó en dos etapas. En un primer momento, para minimizar riesgo y permitir convivencia, se introdujo un modelo BaseDataset del que heredaban variantes: un VLDataset (para UVL) y un TabularDataset (para CSV). Durante ese periodo, el sistema pudo manejar ambos tipos, lo que facilitó migrar lógica por partes y validar que los flujos fundamentales seguían funcionando. Sin embargo, tras una revisión de requisitos, se confirmó que RubikHub debía almacenar datasets de un único tipo, por lo que se decidió eliminar completamente la rama UVL: se quitaron los datasets de tipo UVL del sistema, se retiraron de la UI (headers y navegación) y se simplificó el dominio para quedar exclusivamente con datasets CSV.

Este cambio impactó especialmente en el módulo de datasets, que es donde se centralizan los flujos de alta, detalle, descarga y gestión del dataset. Además, se eliminó el antiguo módulo/estructura ligada a Feature Model (según la nomenclatura original) y se consolidó el nuevo FileModel. Tuvimos que ajustar la entidad de HubFile, que se mantuvo pero se modificó para que su relación principal fuese con FileModel en lugar del modelo UVL anterior.

El resultado final de esta conversión es un sistema más coherente: donde antes se almacenaban ficheros VL con todo el soporte asociado (modelos, validaciones, seeders y tests), ahora el sistema está preparado para gestionar datasets de cubos de Rubik en CSV como primera y única clase ciudadana. Esto simplifica navegación, reduce complejidad del modelo, evita duplicidad de flujos y mejora la mantenibilidad, al eliminar ramificaciones que ya no aportaban valor al dominio objetivo.


**Desacoplamiento de Zenodo e implentación de Fakenodo**

En la versión base, Zenodo se utilizaba como backend externo para la publicación y sincronización de datasets mediante su API. Zenodo aporta identificadores como DOI, gestión de publicación y aspectos de versionado, pero depender de una API externa introduce riesgos y limitaciones: rate limits, latencias, disponibilidad externa y, especialmente en un contexto académico donde múltiples proyectos pueden consumir la API simultáneamente, la posibilidad de saturación y fallos por exceso de llamadas. Esto no solo afecta a la experiencia del usuario, sino también a la estabilidad de los tests y del entorno de integración, porque una prueba automatizada no debería depender de un servicio externo con límites o condiciones variables.

Para resolverlo, se desacopló Zenodo del flujo principal y se diseñó Fakenodo como sustituto interno que replica el comportamiento necesario para que la aplicación funcione sin depender del exterior. Fakenodo no es “un simple mock” aislado, sino un módulo del sistema con modelo(s) y servicios propios, capaz de asignar y almacenar la información que antes se obtenía de Zenodo. Con esto, el sistema conserva el contrato funcional: cuando un dataset “se publica”, pasa de un estado equivalente a borrador/unsynchronized a un estado público y visible, apoyándose en la existencia de un identificador de publicación (por ejemplo, el publication DOI). Dicho de otro modo: un dataset sin DOI de publicación permanece como no publicado, y al publicarse en Fakenodo se le asigna el identificador necesario para habilitar su visibilidad.

La integración se realizó eliminando llamadas directas a la API externa y sustituyéndolas por servicios internos que implementan la misma intención: crear/publicar, consultar metadatos asociados, devolver información de versiones y mantener la coherencia de estados del dataset. Como resultado, Zenodo deja de estar “en medio” del flujo; el sistema no necesita conectividad externa para las operaciones fundamentales de publicación y consulta. Esto permite que la aplicación sea determinista, más estable y menos costosa operativamente: se evitan fallos por red, timeouts, credenciales y límites.

En términos de interfaz (contrato), la idea es que el resto del sistema “siga hablando” con una abstracción de publicación y metadatos: antes esa abstracción se resolvía hacia Zenodo; ahora se resuelve hacia Fakenodo. Así, componentes como el módulo de datasets, el de versionado o las vistas de detalle pueden consumir la misma clase de información (identificadores, versiones, metadatos) sin conocer si el origen es externo o interno. Esto reduce el acoplamiento y facilita evolucionar el sistema a futuro: si se quisiera reintroducir un proveedor externo, podría hacerse con un adaptador sin reescribir la lógica de dominio.

El impacto en despliegue, desde el punto de vista del usuario final, es mínimo: las pantallas y operaciones principales se mantienen. Donde sí hay un impacto claro es en pruebas y calidad: fue necesario crear pruebas específicas del módulo Fakenodo para asegurar que asigna identificadores correctamente, conserva estados, y devuelve la información esperada para la UI y servicios. En definitiva, el sistema gana robustez porque no depende de una API externa para comportamientos esenciales y puede ejecutarse y testearse de forma consistente en cualquier entorno.


**Versionado de datasets**

El versionado se diseñó para que los usuarios puedan evolucionar un dataset sin perder trazabilidad histórica. En RubikHub, una “versión” se entiende como una iteración del mismo dataset conceptual donde los metadatos globales se mantienen, pero el fichero asociado puede cambiar. La plataforma permite al autor crear nuevas versiones cuando lo considere, sin imponer una política rígida de cambios: se contempla una distinción conceptual entre minor updates y major updates, pero la decisión de pasar de 1.0 a 1.1 o a 2.0 queda bajo criterio del usuario. Es decir, RubikHub habilita el versionado, pero no fuerza una semántica de compatibilidad más allá de las reglas de negocio necesarias para mantener coherencia.

Arquitectónicamente, este enfoque se apoya en separar “el dataset como concepto” del “dataset como instancia versionada”. Los metadatos comunes se relacionan con un DatasetConcept, que actúa como ancla de identidad. Cada versión se modela a través de DatasetVersion, y cada DatasetVersion se asocia a un dataset concreto (en este caso, TabularDataset) que contiene toda la información operativa necesaria para existir como dataset independiente (incluyendo su fichero y propiedades), pero a la vez queda vinculado al concepto global. Así, dos versiones son datasets completos por sí mismos, pero comparten el DatasetConcept que los agrupa.

En cuanto a operaciones, el sistema permite listar todas las versiones de un dataset, navegar al detalle de cada una, descargar la versión deseada y, para autores/creadores, crear nuevas versiones. Para mejorar la usabilidad, la versión más actual queda destacada en la interfaz, facilitando que usuarios no expertos identifiquen rápidamente la opción recomendada sin impedir el acceso a versiones anteriores.

Las reglas de negocio garantizan coherencia: no se puede crear una nueva versión si el usuario no es el creador del dataset; no se puede versionar a partir de una versión que no sea la más reciente; no se puede crear una versión nueva si el dataset no está publicado; y, además, la creación de una nueva versión exige aportar un comentario asociado (lo que fuerza una mínima trazabilidad humana del cambio: por qué existe esa versión). Estas restricciones evitan ramificaciones inconsistentes (por ejemplo, múltiples “líneas” de versiones) y mantienen una historia lineal, clara y justificable.


**Registro del número de descargas de cada dataset**

El registro de descargas se definió a nivel de versión, no a nivel global. Esto significa que la versión 1.0, la 1.1 y la 2.0 tienen contadores independientes: cada una acumula su propio histórico de descargas, lo que es coherente con el hecho de que, operativamente, cada versión es un dataset completo y descargable. Este enfoque también habilita análisis más finos (por ejemplo, detectar que una versión antigua sigue siendo muy demandada, o que una versión nueva todavía no se adopta).

La actualización del contador se realiza en el flujo de descarga: cuando el usuario ejecuta la acción de “descargar dataset” (a través del endpoint o ruta correspondiente), el sistema no solo prepara y devuelve el fichero, sino que invoca un servicio adicional responsable de registrar la descarga. En lugar de almacenar un simple entero incremental (que era una idea inicial en BaseDataset), se optó por un enfoque más expresivo y útil: un modelo Download(s) que se asocia al dataset/versión descargada y almacena el instante de descarga.

Este diseño tiene una ventaja clave: permite derivar métricas temporales (como “descargas en la última semana”) sin introducir lógica adicional compleja ni perder información. El número total de descargas se obtiene contando los registros de Download asociados; al crearse uno nuevo por descarga, el total crece automáticamente. En cuanto a auditoría, el sistema guarda exclusivamente la fecha/momento exacto de la descarga, sin almacenar usuario o IP. Esto equilibra trazabilidad mínima para estadísticas con una gestión de datos más simple.


**Pantalla de top datasets basándose en el número de descargas de la última semana**

Para explotar el histórico temporal de descargas, se implementó una vista de “Top Datasets” basada en las descargas de los últimos 7 días naturales (ventana móvil). El criterio es sencillo: se consideran las descargas cuyo timestamp cae dentro de la ventana de siete días hacia atrás desde la fecha actual, y se seleccionan los datasets con mayor número de descargas en ese intervalo.

El cálculo se implementa mediante un servicio que, apoyándose en consultas del repositorio, recupera las descargas filtradas por fecha para cada dataset y determina el ranking. El resultado que se muestra son los tres datasets más descargados dentro de esa ventana temporal. Al estar basado en registros Download con fecha, el sistema puede responder a esta pregunta sin necesidad de mantener contadores secundarios ni jobs nocturnos: la información está disponible y es consistente con el historial real.

En la UI, el acceso aparece en la navegación principal (junto a secciones como Home o Explore) mediante una entrada “Top Datasets”. Al entrar, se listan los “Top 3 Most Downloaded Datasets” y, para cada dataset, se muestran campos relevantes: título, descripción, tipo de publicación, número de descargas, el dataset DOI y acciones rápidas para ver o descargar. Además, se marca con una “estrellita” cuando el dataset mostrado corresponde a la versión más actual de su concepto, lo que añade una capa de recomendación sin ocultar que podría existir interés por versiones anteriores.

En rendimiento, no se añadieron índices específicos, pero sí se cuidó que la consulta se realice en el repositorio, de forma que el filtrado por fecha y el conjunto de datos devuelto se ajuste a lo estrictamente necesario (solo última semana), reduciendo transferencia y procesamiento innecesario en la capa de servicio.


**Comentarios en cada dataset**

RubikHub incorpora comentarios como mecanismo social de discusión y feedback, con especial atención a que el debate sea trazable y coherente con el versionado. El modelo de comentario almacena el autor (relación y su ID), la versión concreta del dataset a la que se refiere (relación con dataset y su ID), la fecha (datePosted) y el contenido textual del comentario. No se contempla edición del comentario una vez publicado, lo cual favorece integridad histórica y evita ambigüedad sobre qué se dijo y cuándo.

Funcionalmente, un usuario puede crear y eliminar comentarios, y cualquier usuario puede ver el conjunto de comentarios del dataset. Sin embargo, el sistema define que los comentarios son por versión: los comentarios realizados sobre la versión 1.0 no se muestran en la 1.1. Esto tiene sentido en un sistema versionado, porque un comentario puede quedar obsoleto o descontextualizado cuando el fichero cambia; así, cada versión conserva su conversación relevante.

A nivel de permisos y validaciones, no se permiten comentarios vacíos, y la eliminación está restringida: solo puede borrar un comentario quien lo creó o quien es creador del dataset/versión. Con esto se evita moderación indiscriminada, pero se permite al creador mantener el orden en el espacio asociado a su contenido.


**Seguimiento de comunidades y autores**

El sistema incluye el concepto de “seguir” comunidades y autores como base para un uso más personalizado. Seguir implica que un usuario se suscribe a la actividad de determinadas entidades para recibir un acceso más directo a contenidos relevantes: nuevos datasets, nuevas versiones, publicaciones o actualizaciones asociadas a una comunidad o un autor. Desde el punto de vista de producto, esto suele materializarse en una lista de seguidos (comunidades seguidas y autores seguidos) y, cuando procede, en experiencias derivadas como feed o notificaciones.

A nivel de dominio, este comportamiento se implementa como relaciones Many-to-Many: User–Community y User–Author, normalmente mediante entidades intermedias de seguimiento que almacenan al menos el par de identificadores y una fecha de alta (createdAt). Este diseño permite garantizar unicidad (un usuario no sigue dos veces lo mismo) y mantener integridad referencial (no seguir entidades inexistentes). Además, posibilita futuras extensiones sin rediseño (por ejemplo, preferencias del seguimiento, silenciar, activar/desactivar avisos o soft delete).

En cuanto a operaciones, el sistema necesita permitir seguir/dejar de seguir y listar seguidos. También se contemplan casos límite típicos: dejar de seguir algo que no se sigue debería ser una operación idempotente (no romper al cliente); seguir dos veces debería resolverse evitando duplicados; y, si existe privacidad o restricciones (por ejemplo, comunidades privadas), el seguimiento debería respetar dichas condiciones. Aunque la implementación concreta puede variar, el objetivo es mantener consistencia funcional y que el seguimiento se integre con la navegación y descubrimiento de contenido.


**Doble factor**

Para reforzar la seguridad de acceso, RubikHub incorpora autenticación de doble factor (2FA) basada en TOTP (códigos temporales). Funcionalmente, el usuario activa el doble factor desde la sección de editar perfil: durante la activación, vincula su cuenta con una aplicación autenticadora, y confirma la activación introduciendo el código generado por dicha aplicación. Una vez activado, cada inicio de sesión requiere, además de las credenciales habituales, el código TOTP.

El comportamiento temporal del TOTP se ajusta a lo estándar: el código tiene una ventana aproximada de 30 segundos, tras la cual se invalida y se genera uno nuevo en la app autenticadora. Para desactivar el 2FA, el usuario vuelve a la edición de perfil y desactiva la opción, recuperando el login de un solo paso. A nivel de impacto, la autorización del sistema no cambia en roles o permisos, pero sí aumenta significativamente la protección frente a accesos no autorizados por robo de contraseña, al añadir un factor que el atacante no tiene de forma trivial.


**Cambios desarrollados en el proyecto**

A partir del sistema base, el proyecto ha experimentado una transformación completa para alinearse con el nuevo dominio RubikHub. En primer lugar, se realizó la conversión de UVLHub eliminando los elementos específicos de UVL y trasladando el núcleo del almacenamiento a ficheros CSV: esto implicó redefinir el modelo principal asociado a ficheros, reemplazar FeatureModel por FileModel, adaptar HubFile para apuntar a la nueva entidad, y rehacer validaciones que antes asumían .uvl para que ahora verifiquen .csv. Del mismo modo, se revisaron y corrigieron seeders y tests preexistentes, ya que estaban construidos alrededor del dominio UVL y debían alinearse con los nuevos flujos tabulares.

En segundo lugar, se eliminó la dependencia operativa de Zenodo introduciendo Fakenodo como módulo interno que replica las asignaciones y datos necesarios para el ciclo de publicación, evitando rate limits y problemas derivados de un servicio externo. Esta sustitución mantuvo el comportamiento funcional de “publicar para hacer visible”, pero trasladó la asignación de identificadores y la consulta de información a servicios internos, obligando a crear nuevas pruebas y a integrar un nuevo subsistema coherente con el resto de módulos del proyecto.

En paralelo, se incorporó un sistema de versionado real: se introdujeron DatasetConcept y DatasetVersion para relacionar varias instancias TabularDataset bajo una identidad común, imponiendo reglas de negocio claras sobre quién puede versionar, desde qué versión se puede crear una nueva, y en qué condiciones (solo desde la última versión, solo si está publicado y exigiendo comentario de versión). Sobre esta base, se añadió el registro de descargas por versión mediante un modelo Download con timestamp, descartando el contador simple por su falta de valor analítico y por la necesidad de soportar métricas temporales.

Finalmente, se construyeron funcionalidades orientadas a uso y comunidad: la pantalla de Top Datasets basada en descargas de los últimos siete días naturales; el sistema de comentarios por versión con permisos de creación y borrado bien definidos y sin edición posterior; el seguimiento de comunidades y autores como mecanismo de suscripción a actividad; y la activación de doble factor TOTP desde el perfil para endurecer el proceso de autenticación. En conjunto, estos cambios convierten la base inicial en una plataforma enfocada, consistente y mantenible, con un dominio único (CSV), métricas derivables y componentes sociales y de seguridad integrados.

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

RubikHub ha propiciado la elaboración de una plataforma robusta y funcional en la gestión, versionado y publicación de datasets asociados al cubo de Rubik, en la que se ha ido dotando de seguridad, mecanismo de colaboración y seguimiento respecto de las formas de uso de los datos. El sistema representa, pues, algo más un repositorio que un entorno colaborativo que ayuda a aumentar la interacción por parte de los usuarios mediante comentarios, seguidores y comunidades, de modo que se aumenta la reusabilidad y el valor que pudieran tener los datasets.

La incorporación de autenticación de doble factor permite tener un sistema más seguro que si solo se hubiera utilizado usuario y contraseña, y en cuanto al proceso de desarrollo estructurado, mediante control de versiones, pruebas automatizadas y un entorno de pipelines CI/CD, ha hecho posible garantizar la calidad y la trazabilidad, así como la estabilidad del software. Por tanto, el proyecto en conjunto responde a los objetivos que se había planteado, y demuestra las ventajas de aplicar buenas prácticas de ingeniería del software en el desarrollo de sistemas reales.
