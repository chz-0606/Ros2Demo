#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "turtlesim/msg/pose.hpp"
#include <chrono>

using namespace std::chrono_literals;


class TurtleControlNode : public rclcpp::Node
{
private:
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;  //发布者的智能指针
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscriber_;  //姿态订阅者的智能指针
    double target_x_{1.0};  //目标位置的x坐标
    double target_y_{1.0};  //目标位置的y坐标  
    double k_{1.0};  //比例系数
    double max_speed_{3.0};  //最大速度
public:
    explicit TurtleControlNode(const std::string & node_name)
    : Node(node_name)
    {
        publisher_ = this->create_publisher<geometry_msgs::msg::Twist>("turtle1/cmd_vel", 10);
        subscriber_ = this->create_subscription<turtlesim::msg::Pose>(
            "turtle1/pose",
            10,
            std::bind(&TurtleControlNode::on_pose_received_, this, std::placeholders::_1)
        );
        //timer_ = this->create_wall_timer(
        //    1000ms,
        //    std::bind(&TurtleControlNode::timer_callback, this)
        //);
    }

    void on_pose_received_(const turtlesim::msg::Pose::SharedPtr pose)  //参数：收到数据的共享指针
    {
        //1.获取当前的位置信息
        auto current_x = pose->x;
        auto current_y = pose->y;
        RCLCPP_INFO(this->get_logger(), "当前位置: x=%.2f, y=%.2f", current_x, current_y);

        //2.计算当前位置与目标位置之间的距离和角度差
        auto dx = target_x_ - current_x;
        auto dy = target_y_ - current_y;
        auto distance = std::sqrt(dx * dx + dy * dy);
        auto angle = std::atan2(dy, dx) - pose->theta;

        //3.根据距离和角度差计算控制指令
        auto message = geometry_msgs::msg::Twist();
        if (distance > 0.1)  //如果距离大于0.1，则继续移动
        {
            if(fabs(angle) > 0.2)  //如果角度差大于0.1，则先转向
            {
                message.angular.z = fabs(angle);
            }
            else  //如果角度差小于等于0.1，则前进
            {
               message.linear.x = k_ * distance;
            }
        }
        //4.限制最大速度
        if (message.linear.x > max_speed_)
        {
            message.linear.x = max_speed_;
        }
        publisher_->publish(message);
    }

    //void timer_callback()
    //{
    //   auto message = geometry_msgs::msg::Twist();
    //    message.linear.x = 1.0;
    //   message.angular.z = 0.5;
    //   publisher_->publish(message);
    //}
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<TurtleControlNode>("turtle_control_node");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}