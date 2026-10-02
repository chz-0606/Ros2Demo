#include "rclcpp/rclcpp.hpp"
#include "chapt04_interfaces/srv/patrol.hpp"
#include <chrono>
#include <ctime>
#include "rcl_interfaces/msg/parameter.hpp"
#include "rcl_interfaces/msg/parameter_value.hpp"
#include "rcl_interfaces/msg/parameter_type.hpp"
#include "rcl_interfaces/srv/set_parameters.hpp"

using SetP = rcl_interfaces::srv::SetParameters;
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
            request->target_x = rand()%11 + 1;  //随机生成目标位置的x坐标(1~11，保证在合法范围内)
            request->target_y = rand()%11 + 1;  //随机生成目标位置的y坐标
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
            });   //async_send_request 收尾
        });       //timer lambda 收尾
    }

    /*
    创建客户端发送参数设置请求，返回结果
    */
    SetP::Response::SharedPtr call_set_parameter(const rcl_interfaces::msg::Parameter &param)
    {
        // 注意：用局部变量，不能覆盖成员 timer_
        auto param_client = this->create_client<SetP>("/turtle_control_node/set_parameters");

        //1.检测参数服务是否上线
        while(param_client->wait_for_service(1s) == false)
        {
            if(!rclcpp::ok())
            {
                RCLCPP_ERROR(this->get_logger(), "等待参数服务超时，客户端退出");
                return nullptr;
            }
            RCLCPP_INFO(this->get_logger(), "等待参数服务上线中...");
        }
        //2.构造请求对象
        auto request = std::make_shared<SetP::Request>();
        request->parameters.push_back(param);
        //3.发送请求并等待结果
        auto future = param_client->async_send_request(request);
        rclcpp::spin_until_future_complete(this->get_node_base_interface(), future);
        return future.get();
    }

    /*
    更新参数k
    */
    void update_server_param_k(double k)
    {
        //1.创建参数对象
        auto param = rcl_interfaces::msg::Parameter();
        param.name = "k";
        //2.创建参数值
        auto param_value = rcl_interfaces::msg::ParameterValue();
        param_value.type = rcl_interfaces::msg::ParameterType::PARAMETER_DOUBLE;
        param_value.double_value = k;
        param.value = param_value;
        //3.请求更新参数并处理结果
        auto response = this->call_set_parameter(param);
        if(response == nullptr)
        {
            RCLCPP_ERROR(this->get_logger(), "参数更新失败（无响应）");
            return;
        }
        for(auto result : response->results)
        {
            if(result.successful == false)
            {
                RCLCPP_ERROR(this->get_logger(), "参数更新失败");
            }
            else
            {
                RCLCPP_INFO(this->get_logger(), "参数更新成功");
            }
        }
    }
};   // ← 类结束的分号


int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<PatrolClient>("patrol_client_control_node");
    node->update_server_param_k(4.0);   // 在 spin 之前先更新参数 k
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}