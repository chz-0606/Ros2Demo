import rclpy
from rclpy.node import Node
import requests
from example_interfaces.msg import String
from queue import Queue

class NovelPubNode(Node):
    def __init__(self, node_name):
        super().__init__(node_name)
        self.get_logger().info(f'{node_name}, 启动')
        self.novel_queue_ = Queue()      #创建队列
        self.novel_publiser_ = self.create_publisher(String, 'novel_topic', 10)
        self.create_timer(5, self.timer_callback)

    def timer_callback(self):
             if self.novel_queue_.qsize() > 0:
                lines = self.novel_queue_.get()
                msg = String()    #组装
                msg.data = lines
                self.novel_publiser_.publish(msg)
                self.get_logger().info(f'发布了：{msg}')
    
    

    def download(self, url):
            response = requests.get(url)
            response.encoding = 'utf-8'
            self.get_logger().info(f'下载完成：{url}，字数：{len(response.text)}')
            for lines in response.text.splitlines():
                self.novel_queue_.put(lines)  #将每行小说放入队列
            


def main():
    rclpy.init()
    node = NovelPubNode('novel_pub_node')
    node.download('http://0.0.0.0:8080/novel1.txt')
    rclpy.spin(node)
    rclpy.shutdown()