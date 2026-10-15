import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformListener, Buffer  #静态坐标监听器
from tf_transformations import euler_from_quaternion  #四元数转欧拉角
import math

class TFListener(Node):
    def __init__(self):
        super().__init__('tf_listener')
        self.buffer_ = Buffer()
        self.listener = TransformListener(self.buffer_, self)
        self.timer_ = self.create_timer(1.0, self.get_transform)  # 每秒获取一次TF

    def get_transform(self):    
        """
        实时查询坐标关系
        """
        try:
            # 查询坐标关系 
            transform = self.buffer_.lookup_transform('camera_link', 'bottle_link', rclpy.time.Time())
            # 获取平移和旋转
            translation = transform.transform.translation
            rotation = transform.transform.rotation
            # 四元数转欧拉角
            euler = euler_from_quaternion([rotation.x, rotation.y, rotation.z, rotation.w])
            self.get_logger().info(f'获取到TF: 平移: x={translation.x}, y={translation.y}, z={translation.z}, 旋转(欧拉角): roll={math.degrees(euler[0])}, pitch={math.degrees(euler[1])}, yaw={math.degrees(euler[2])}')
        except Exception as e: 
            self.get_logger().error(f'获取TF失败: {e}')

    
def main():
    rclpy.init()
    node = TFListener()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()