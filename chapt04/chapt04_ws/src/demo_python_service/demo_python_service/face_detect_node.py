import rclpy
from rclpy.node import Node
from chapt04_interfaces.srv import FaceDetector
import face_recognition
import cv2
from ament_index_python.packages import get_package_share_directory  #获取功能包share的绝对路径
import os
from cv_bridge import CvBridge
import time

class FaceDetectNode(Node):
    def __init__(self):
        super().__init__('face_detect_node')
        self.service = self.create_service(FaceDetector, 'face_detect', self.face_detect_callback)
        self.bridge = CvBridge()
        self.get_logger().info('Face Detect Service is ready.')
        self.number_of_times_to_upsample = 1  # 设置人脸检测的上采样次数
        self.model = 'hog'  # 设置人脸检测的模型
        self.default_image_path = os.path.join(get_package_share_directory('demo_python_service'), 'resource', 'default.jpg')  # 设置默认图像路径


    def face_detect_callback(self, request, response):
        if request.image.data:
            # 将ROS图像消息转换为OpenCV图像
            cv_image = self.bridge.imgmsg_to_cv2(request.image, desired_encoding='bgr8')
        else:
            # 如果没有提供图像数据，则使用默认图像
            self.get_logger().info('没有提供图像数据，使用默认图像进行人脸检测。')
            cv_image = cv2.imread(self.default_image_path)

        start_time = time.time()
        self.get_logger().info('加载完成图像，开始进行人脸检测...')

        # 使用face_recognition来检测人脸位置
        face_locations = face_recognition.face_locations(cv_image, number_of_times_to_upsample=self.number_of_times_to_upsample, model=self.model)  #使用hog模型检测人脸位置
        response.use_time = time.time() - start_time
        response.number = len(face_locations)

        # 绘制人脸框
        for top, right, bottom, left in face_locations:
            response.top.append(top)
            response.right.append(right)
            response.bottom.append(bottom)
            response.left.append(left)  
        self.get_logger().info(f'人脸检测完成，检测到 {response.number} 张人脸，耗时 {response.use_time:.4f} 秒。')
        return response   #必须返回response对象

def main():
    rclpy.init()
    node = FaceDetectNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()