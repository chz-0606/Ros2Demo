import rclpy
from rclpy.node import Node

def main():
  rclpy.init() #初始化工作，分配资源
  node = Node('python_node')
  node.get_logger().info('节点已运行!')  #export RCUTILS_CONSOLE_OUTPUT_FORMAT=[{function_name}:{line_number}]:{message}
  rclpy.spin(node)
  rclpy.shutdown()