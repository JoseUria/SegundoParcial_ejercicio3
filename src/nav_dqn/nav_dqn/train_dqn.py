from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import CheckpointCallback # <-- Para guardar copias cada tanto
from stage_env import StageEnv
import threading
import rclpy
import os

def ros_spin(node):
    try:
        rclpy.spin(node)
    except Exception as e:
        print(f"[ROS] Hilo de spin finalizado: {e}")

if __name__ == "__main__":

    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    carpeta_checkpoints = os.path.join(directorio_actual, "checkpoints")
    ruta_guardado_final = os.path.join(directorio_actual, "dqn_stage")

    env = StageEnv()

    ros_thread = threading.Thread(target=ros_spin, args=(env.node,), daemon=True)
    ros_thread.start()

   
    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path=carpeta_checkpoints,
        name_prefix="dqn_checkpoint"
    )

    model = DQN(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=5e-4,
        buffer_size=100000,
        batch_size=64,
        gamma=0.99,
        train_freq=4,
        gradient_steps=1,
        exploration_fraction=0.30,
        exploration_final_eps=0.05,
        target_update_interval=1000,
    )

    try:
        print(f"Iniciando entrenamiento largo... Copias cada 10k pasos en: {carpeta_checkpoints}")
    
        model.learn(
            total_timesteps=100000, 
            progress_bar=False, 
            callback=checkpoint_callback
        )
        
   
        model.save(ruta_guardado_final)
        print(f"¡CONSEGUIDO! Modelo final guardado en: {ruta_guardado_final}.zip")

    except KeyboardInterrupt:

        ruta_emergencia = os.path.join(directorio_actual, "dqn_stage_interrumpido")
        model.save(ruta_emergencia)
        print(f"\n[!] Entrenamiento cancelado. Guardado de emergencia en: {ruta_emergencia}.zip")

    finally:
        env.close()