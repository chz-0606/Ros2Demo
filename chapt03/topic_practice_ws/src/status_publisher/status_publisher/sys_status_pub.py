import rclpy
from status_interface.msg import SystemStatus
from rclpy.node import Node
import psutil
import platform

class SysStatusPub(Node):
    def __init__(self,node_name):
        super().__init__(node_name)
        self.status_publisher = self.create_publisher(SystemStatus, 'sys_status', 10)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        net_io_counters = psutil.net_io_counters()

        msg = SystemStatus()
        msg.stamp = self.get_clock().now().to_msg()
        msg.host_name = platform.node()
        msg.cpu_percent = cpu_percent
        msg.memory_percent = memory_info.percent
        msg.memory_total = float(memory_info.total)
        msg.memory_available = float(memory_info.available)
        msg.net_sent = net_io_counters.bytes_sent / 1024 /1024  # Convert to MB
        msg.net_recv = net_io_counters.bytes_recv / 1024 /1024  # Convert to MB

        self.get_logger().info(f'发布：{str(msg)}')
        self.status_publisher.publish(msg)



def main():
    rclpy.init()
    node = SysStatusPub('sys_status_pub')
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()