import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class SimpleMove(Node):

    def __init__(self):
        super().__init__('simple_move')

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(LaserScan, '/base_scan', self.scan_cb, 10)

        self.scan = None

        self.timer = self.create_timer(0.2, self.loop)

        self.get_logger().info("Nodo iniciado")

    def scan_cb(self, msg):
        self.scan = msg.ranges

    def loop(self):

        cmd = Twist()

        # SI NO HAY LiDAR → avanzar
        if self.scan is None:
            cmd.linear.x = 0.2
            self.pub.publish(cmd)
            return

        # limpiar inf
        import numpy as np
        scan = np.array(self.scan)
        scan = np.where(np.isinf(scan), 3.5, scan)

        front = np.min(scan[170:190])

        if front < 0.7:
            cmd.angular.z = 0.5
        else:
            cmd.linear.x = 0.2

        self.pub.publish(cmd)


def main():
    rclpy.init()
    node = SimpleMove()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()