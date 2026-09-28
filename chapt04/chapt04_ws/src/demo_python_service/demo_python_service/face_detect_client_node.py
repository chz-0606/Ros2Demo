import rclpy
from rclpy.node import Node
from chapt04_interfaces.srv import FaceDetector
import face_recognition
import cv2
from ament_index_python.packages import get_package_share_directory  #获取功能包share的绝对路径
import os
from cv_bridge import CvBridge
import time
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter,ParameterValue,ParameterType

class FaceDetectClientNode(Node):
    def __init__(self):
        super().__init__('face_detect_client_node')
        self.bridge = CvBridge()
        self.default_image_path = os.path.join(get_package_share_directory('demo_python_service'), 'resource', 'default.jpg')
        self.get_logger().info('Face Detect Service is ready.')
        self.client = self.create_client(FaceDetector, 'face_detect')
        self.image = cv2.imread(self.default_image_path)

    def call_set_parameters(self, parameters):    
        #1.创建SetParameters服务客户端
        update_param = self.create_client(SetParameters, '/face_detect/set_parameters')
        while update_param.wait_for_service(timeout_sec=1.0) == False:
                    self.get_logger().info('等待参数更新服务端上线...')
        #2.创建请求对象
        request = SetParameters.Request()
        request.parameters = parameters
        #3.调用服务端更新参数
        future = update_param.call_async(request)
        rclpy.spin_until_future_complete(self, future)  #等待服务端返回响应
        response = future.result()
        return response

    def update_detect_model(self, model='hog'):
        """根据传入的model，构造Paramters，然后调用call_set_parameters()方法更新参数"""
        #1.创建参数对象
        param = Parameter()
        param.name = 'model'
        #2.赋值
        param_value = ParameterValue()
        param_value.string_value = model
        param_value.type = ParameterValue.PARAMETER_STRING
        param.value = param_value
        #3.调用call_set_parameters()方法更新参数
        response = self.call_set_parameters([param])
        for result in response.results:
            if result.successful:
                self.get_logger().info(f'参数更新成功: {result.reason}')
            else:
                self.get_logger().info(f'参数更新失败: {result.reason}')

    def send_request(self):
        #1.判断服务端是否在线
        while self.client.wait_for_service(timeout_sec=1.0) == False:
            self.get_logger().info('等待服务端上线...')
        #2.创建请求对象
        request = FaceDetector.Request()
        request.image = self.bridge.cv2_to_imgmsg(self.image, encoding='bgr8')
        #3.发送请求,并等待处理完成
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)  #等待服务端返回响应
        response = future.result()
        self.get_logger().info(f'检测到 {response.number} 张人脸，耗时 {response.use_time:.4f} 秒。')
        self.show_response(response)
        

    def show_response(self, response):
        for i in range(response.number):
            top = response.top[i]
            right = response.right[i]
            bottom = response.bottom[i]
            left = response.left[i]
            cv2.rectangle(self.image, (left, top), (right, bottom), (255, 0, 0), 4)
            cv2.imshow('Face Detection', self.image)
            cv2.waitKey(0)


def main():
    rclpy.init()
    node = FaceDetectClientNode()
    node.send_request()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()