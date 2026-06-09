# Navegación Autónoma de un Robot Móvil mediante DQN en ROS 2

Este repositorio contiene el desarrollo del **Ejercicio 3** para el Segundo Parcial de la materia **Robótica IMT-342**. Se implementa un agente de aprendizaje por refuerzo profundo basado en el algoritmo **DQN (Deep Q-Network)** integrado con **Gymnasium** y el middleware **ROS 2 Jazzy Jalisco** para navegar de forma autónoma en entornos con alta oclusión espacial.

El reporte generado se encuentra en la rama main con el nombre de "Reporte Tecnico_ Navegacion Autonoma DQN en ROS 2"
---

## 📋 Requisitos del Sistema

Antes de ejecutar el proyecto, asegúrate de contar con las siguientes herramientas instaladas:

- Ubuntu (Distribución nativa con soporte para ROS 2)
- ROS 2 Jazzy Jalisco
- Simulador Stage (`stage_ros2`)
- Python 3 junto con las librerías: `stable-baselines3`, `gymnasium`, `torch` y `numpy`

---

## 🛠️ Compilación del Espacio de Trabajo

Para asegurar que ROS 2 reconozca los paquetes de navegación (`nav_dqn`), el de reinicio del entorno (`reset_stage`) y el propio simulador (`stage_ros2`), es necesario limpiar, compilar y mapear el espacio de trabajo.

Sigue este procedimiento en tu terminal principal:

```bash
# 1. Navegar a la raíz del espacio de trabajo (Workspace)
cd ~/stage_ws

# 2. Compilar los paquetes utilizando el constructor de ROS 2 (Colcon)
colcon build

# 3. Cargar las variables de entorno del espacio de trabajo en la terminal
source install/setup.bash
```

> **Nota técnica:** Estos comandos ubican la terminal en la carpeta raíz del entorno de desarrollo, analizan recursivamente todo el código fuente dentro de `/src`, resuelven las dependencias internas, compilan los scripts y registran las rutas de los paquetes dentro del entorno de ejecución de ROS 2. Es **obligatorio** ejecutar el `source`; de lo contrario, el sistema devolverá un error de *"paquete no encontrado"* al intentar lanzar los nodos.

---

## 🚀 Instrucciones de Ejecución

El sistema requiere la ejecución en paralelo del simulador físico y el nodo de inferencia/control de la red neuronal. Sigue el **orden estricto** detallado a continuación utilizando **dos terminales distintas**.

### Paso 1: Lanzar el Entorno de Simulación (Stage)

En tu primera terminal (donde acabas de compilar), inicializa el simulador cargando el escenario estructurado `cave.world`:

```bash
# Ejecutar el simulador Stage
ros2 launch stage_ros2 stage.launch.py world:=cave
```

> **Explicación:** Este comando invoca el archivo de lanzamiento de ROS 2 para levantar la interfaz gráfica del simulador Stage. Carga un entorno de pasillos estrechos altamente ocluidos (`cave.world`) y posiciona al robot en sus coordenadas iniciales de origen, dejándolo a la escucha de comandos de velocidad en el tópico correspondiente.

### Paso 2: Ejecutar el Agente en Modo Evaluación (Test)

Abre una **segunda terminal completamente nueva**. Es obligatorio navegar hasta la ruta interna del paquete y cargar las variables de entorno antes de ejecutar la IA:

```bash
# 1. Navegar a la ruta exacta del paquete nav_dqn
cd ~/stage_ws/src/nav_dqn/nav_dqn

# 2. Cargar el entorno de ROS 2 en esta nueva terminal
source ~/stage_ws/install/setup.bash

# 3. Ejecutar el nodo de prueba de la red neuronal DQN
ros2 run nav_dqn test_dqn
```

> **Explicación:** Al abrir una terminal independiente, se requiere volver a mapear el entorno con `source`. El comando `ros2 run` ejecuta el script de evaluación que conecta el entorno de Gymnasium con los nodos vivos de ROS 2. A partir de este momento, el agente de IA empieza a recibir los rangos del LiDAR en tiempo real, calcula la acción óptima a través de la red de pesos guardada y publica las velocidades de forma síncrona para que el robot navegue de forma autónoma hacia la meta sin colisionar.



## 👥 Autores

| Nombre |
|---|
| Pomier Sevilla Ignacio Eduardo |
| Salgueiro Vargas Jorge Fernando |
| Sanabria Vidaurre Pablo Angel |
| Uría Fernandez José Manuel |

**Asignatura:** Robótica IMT-342  
**Institución:** Universidad Católica Boliviana "San Pablo"
