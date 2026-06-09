import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty
import math


class OdomResetWrapper(Node):

    def __init__(self):
        super().__init__('odom_reset_wrapper')

        self.sub = self.create_subscription(
            Odometry, '/odom', self.cb, 10)

        self.pub = self.create_publisher(
            Odometry, '/odom/sim', 10)

        self.srv = self.create_service(
            Empty, '/reset_sim', self.reset_cb)

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.offset_yaw = 0.0
        self.reset_flag = False

        self.get_logger().info("Reset node running")

    def reset_cb(self, request, response):
        self.reset_flag = True
        return response

    def cb(self, msg):

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        if self.reset_flag:
            self.offset_x = x
            self.offset_y = y
            self.reset_flag = False

        new_msg = msg
        new_msg.pose.pose.position.x = x - self.offset_x
        new_msg.pose.pose.position.y = y - self.offset_y

        self.pub.publish(new_msg)


def main():
    rclpy.init()
    node = OdomResetWrapper()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()