import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster     #静态坐标发布器
from tf_transformations import quaternion_from_euler  #欧拉角转四元数
import math

class StaticTFBroadcaster(Node):
    def __init__(self):
        super().__init__('static_tf_broadcaster')
        self.static_broadcaster = StaticTransformBroadcaster(self)
        self.publish_static_tf()

    def publish_static_tf(self):    
        """
        发布静态坐标变换
        """
        transform = TransformStamped()
        transform.header.frame_id = 'base_link'
        transform.child_frame_id = 'camera_link'
        transform.header.stamp = self.get_clock().now().to_msg()
        # 设置平移和旋转
        transform.transform.translation.x = 0.5  # 平移x
        transform.transform.translation.y = 0.3  # 平移y
        transform.transform.translation.z = 0.6  # 平移z
        #欧拉角转四元数q=x,y,z,w
        quaternion = quaternion_from_euler(math.radians(180),0, 0)  # 将角度转换为弧度
        # 设置旋转
        transform.transform.rotation.x = quaternion[0]
        transform.transform.rotation.y = quaternion[1]
        transform.transform.rotation.z = quaternion[2]
        transform.transform.rotation.w = quaternion[3]
        #静态坐标发布出去
        self.static_broadcaster.sendTransform(transform)
        self.get_logger().info(f'发布静态TF:{transform}')


def main():
    rclpy.init()
    node = StaticTFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()