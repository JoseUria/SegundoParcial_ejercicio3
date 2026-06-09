import gymnasium as gym
import time
import sys
import rclpy
import threading
from stable_baselines3 import DQN
from .stage_env import StageEnv

def main(args=None):
    if args is None:
        args = sys.argv
    ros_args = args + ['--ros-args', '-p', 'use_sim_time:=true']
    rclpy.init(args=ros_args)
    
    print("Iniciando entorno de pruebas para Stage...")
    env = StageEnv()
    
 
    def ros_spin_thread():
        while rclpy.ok():
            try:
                rclpy.spin_once(env.node, timeout_sec=0.01)
            except Exception:
                break

    spin_thread = threading.Thread(target=ros_spin_thread, daemon=True)
    spin_thread.start()

    
    model_path = "/home/joseuf18/stage_ws/src/nav_dqn/nav_dqn/dqn_stage"
    print(f"Cargando el modelo desde: {model_path}.zip")
    
    try:
        model = DQN.load(model_path, env=env)
        print("¡Modelo cargado con éxito!")
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")
        rclpy.shutdown()
        return

    try:
        print("⏳ Ejecutando Reset en Stage (esperando respuesta...)")
        obs, info = env.reset()
        print("\n¡Cerebro DQN conectado! El robot debería empezar a moverse...")
        
        while rclpy.ok():
 
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, truncated, info = env.step(int(action))
            
            if done or truncated:
                print("🏁 Fin del intento. Reiniciando posiciones...")
                obs, info = env.reset()
            
            time.sleep(0.02)
            
    except KeyboardInterrupt:
        print("\nPrueba detenida por el usuario.")
    finally:
        env.close()

if __name__ == "__main__":
    main()