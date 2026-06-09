import gymnasium as gym
import numpy as np
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty

import time
from math import atan2, sqrt


class StageEnv(gym.Env):

    def __init__(self):
        super().__init__()

        if not rclpy.ok():
            rclpy.init()

        self.node = Node("stage_dqn_env")

        # ---------------- ROS ----------------

        self.pub = self.node.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )

        self.node.create_subscription(
            LaserScan,
            "/base_scan",
            self.scan_cb,
            10
        )

        self.node.create_subscription(
            Odometry,
            "/ground_truth",
            self.odom_cb,
            10
        )

        self.reset_client = self.node.create_client(
            Empty,
            "/reset_positions"
        )

        # ---------------- Estado robot ----------------

        self.scan = None

        self.robot_x = -7.0
        self.robot_y = -7.0

        self.prev_x = -7.0
        self.prev_y = -7.0

        self.vel = 0.0
        self.yaw = 0.0

        # ---------------- Meta ----------------

        self.goal_x = 7.0
        self.goal_y = -4.0

        self.prev_distance = None
        self.stuck_counter = 0

        # ---------------- Gym ----------------

        # 3 Acciones discretas: 0=Avanzar, 1=Izquierda, 2=Derecha
        self.action_space = gym.spaces.Discrete(3)

        # Vector de estado de tamaño 13: 10 rayos de LiDAR + 1 vel + 1 dist_meta + 1 angulo_meta
        self.observation_space = gym.spaces.Box(
            low=-100.0,
            high=100.0,
            shape=(13,),
            dtype=np.float32
        )

    # =================================================
    # CALLBACKS
    # =================================================

    def scan_cb(self, msg):
        scan = np.array(msg.ranges)
        scan = np.where(np.isinf(scan), 10.0, scan)


        mitad = len(scan) // 2
        rango_vision = len(scan) // 3  
        
        indices = np.linspace(mitad - rango_vision, mitad + rango_vision, 10).astype(int)
        self.scan = scan[indices]

    def odom_cb(self, msg):
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y
        self.vel = msg.twist.twist.linear.x

        q = msg.pose.pose.orientation
        self.yaw = np.arctan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        )

    # =================================================
    # AUXILIARES
    # =================================================

    def goal_distance(self):
        return sqrt(
            (self.goal_x - self.robot_x) ** 2 +
            (self.goal_y - self.robot_y) ** 2
        )

    def goal_angle(self):
        angle_to_goal = atan2(
            self.goal_y - self.robot_y,
            self.goal_x - self.robot_x
        )

        angle = angle_to_goal - self.yaw

        while angle > np.pi:
            angle -= 2 * np.pi
        while angle < -np.pi:
            angle += 2 * np.pi

        return angle

    # =================================================
    # RESET
    # =================================================

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.pub.publish(Twist())
        self.stuck_counter = 0

        if self.reset_client.wait_for_service(timeout_sec=2.0):
            future = self.reset_client.call_async(Empty.Request())
            while not future.done():
                time.sleep(0.01)

        time.sleep(1.0)

        self.prev_distance = self.goal_distance()
        self.prev_x = self.robot_x
        self.prev_y = self.robot_y

        print(
            f"RESET -> "
            f"x={self.robot_x:.2f} "
            f"y={self.robot_y:.2f} "
            f"dist={self.prev_distance:.2f}"
        )

        return self.get_obs(), {}

    # =================================================
    # OBS
    # =================================================

    def get_obs(self):
        if self.scan is None or len(self.scan) < 10:
            scan = np.ones(10) * 10.0
        else:
            scan = np.array(self.scan[:10])

        obs = np.concatenate([
            scan,
            [self.vel],
            [self.goal_distance()],
            [self.goal_angle()]
        ])

        return obs.astype(np.float32)


    def step(self, action):
        cmd = Twist()

        if action == 0:     
            cmd.linear.x = 0.70
            cmd.angular.z = 0.0
        elif action == 1:   
            cmd.linear.x = 0.0
            cmd.angular.z = 0.80
        elif action == 2:   
            cmd.linear.x = 0.0
            cmd.angular.z = -0.80

        self.pub.publish(cmd)
        time.sleep(0.05)

    
        movement = np.sqrt(
            (self.robot_x - self.prev_x) ** 2 +
            (self.robot_y - self.prev_y) ** 2
        )
        self.prev_x = self.robot_x
        self.prev_y = self.robot_y

        if movement < 0.01:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0

        obs = self.get_obs()
        done = self.is_done()
        reward = self.compute_reward(action)

        return obs, reward, done, False, {}

    # =================================================
    # REWARD
    # =================================================

    def compute_reward(self, action):
        current_distance = self.goal_distance()

    
        reward = (self.prev_distance - current_distance) * 30.0
        self.prev_distance = current_distance

        reward -= 0.05
        if action != 0:
            reward -= 0.02

        if self.scan is not None:
            min_dist = np.min(self.scan)
            if min_dist < 0.40:
                reward -= 1.0

        if current_distance < 0.8:
            reward += 500.0  
            
        elif self.scan is not None and np.min(self.scan) < 0.20:
            reward -= 150.0  
            
        elif self.stuck_counter > 40:
            reward -= 100.0  

        return reward

    # =================================================
    # DONE
    # =================================================

    def is_done(self):
        # Éxito
        if self.goal_distance() < 0.8:
            print("META ALCANZADA")
            return True

        # Colisión
        if self.scan is not None:
            min_dist = np.min(self.scan)
            if min_dist < 0.20:
                print(f"COLISION dist={min_dist:.2f}")
                return True

        # Atascado
        if self.stuck_counter > 50:
            print("ROBOT ATASCADO")
            return True

        return False

    # =================================================
    # CLOSE
    # =================================================

    def close(self):
        self.pub.publish(Twist())
        self.node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()