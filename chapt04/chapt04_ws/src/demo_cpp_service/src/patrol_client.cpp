#include "rclcpp/rclcpp.hpp"
#include "chapt04_interfaces/srv/patrol.hpp"
#include <chrono>
#include <ctime>

using Patrol = chapt04_interfaces::srv::Patrol;
using namespace std::chrono_literals; //使用命名空间std::chrono_literals，允许使用时间字面量（如100ms、1s等）来表示时间间隔




class PatrolClient : public rclcpp::Node
{
private:
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Client<Patrol>::SharedPtr patrol_client_;
public:
    explicit PatrolClient(const std::string & node_name)
    : Node(node_name)
    {
        srand((unsigned)time(NULL));  //设置随机数种子
        patrol_client_ = this->create_client<Patrol>("patrol_service");
        timer_ = this->create_wall_timer(10s,[&]()->void{
            //1.检测服务端是否上线
            while(this->patrol_client_->wait_for_service(1s) == false)
            {
                if(!rclcpp::ok())
                {
                    RCLCPP_ERROR(this->get_logger(), "等待服务端超时，客户端退出");
                    return;
                }
                RCLCPP_INFO(this->get_logger(), "等待服务上线中...");
                
            }
            //2.构造请求对象
            auto request = std::make_shared<Patrol::Request>();
            request->target_x = rand()%15;  //随机生成目标位置的x坐标
            request->target_y = rand()%15;  //随机生成目标位置的y坐标
            RCLCPP_INFO(this->get_logger(), "准备好目标点:%f,%f", request->target_x, request->target_y);
            //3.发送请求
            patrol_client_->async_send_request(request,[&](rclcpp::Client<Patrol>::SharedFuture result_future)->void{
                auto response = result_future.get();
                if(response->result == Patrol::Response::SUCESS)
                {
                    RCLCPP_INFO(this->get_logger(), "巡逻请求成功，目标点:%f,%f", request->target_x, request->target_y);
                }
                else
                {
                    RCLCPP_ERROR(this->get_logger(), "巡逻请求失败，目标点:%f,%f", request->target_x, request->target_y);
                }
            });
        }); 
    }

};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<PatrolClient>("patrol_client_control_node");
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}