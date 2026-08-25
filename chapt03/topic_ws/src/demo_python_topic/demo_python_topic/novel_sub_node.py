import espeakng
import rclpy
from rclpy.node import Node
from example_interfaces.msg import String
from queue import Queue
import threading
import time

class NovelSubNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self.get_logger().info(f'{node_name}, 启动')
        self.novel_queue_ = Queue()      #创建队列
        self.novel_subcriber_ = self.create_subscription(String, 'novel_topic', self.novel_callback, 10)
        self.speech_thread_ = threading.Thread(target=self.speake_thread)
        self.speech_thread_.start()  #启动朗读线程

    def novel_callback(self, msg):
        self.novel_queue_.put(msg.data)  #将每行小说放入队列

    def speake_thread(self):
        speaker = espeakng.Speaker()
        speaker.voice = 'zh'

        while rclpy.ok():   #检测ROS2上下文是否正常
            if self.novel_queue_.qsize() > 0:
                text = self.novel_queue_.get()
                self.get_logger().info(f'朗读：{text}')
                speaker.say(text)  #朗读
                speaker.wait()  #等待朗读完成
            else:
                #如果队列为空，休眠一段时间，避免CPU占用过高
                self.get_logger().info('队列为空，休眠1秒')
                time.sleep(1)
                

def main():
    rclpy.init()
    node = NovelSubNode('novel_sub_node')
    rclpy.spin(node)
    rclpy.shutdown()