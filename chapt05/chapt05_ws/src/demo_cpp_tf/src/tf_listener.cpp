#include "geometry_msgs/msg/transform_stamped.hpp"  //提供消息接口
#include "rclcpp/rclcpp.hpp"
#include "tf2/LinearMath/Quaternion.h"   //提供四元数接口
#include "tf2_ros/transform_listener.h"  //提供tf监听器接口
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"  //提供tf与geometry_msgs之间的转换接口
#include "tf2_ros/buffer.h"  //提供tf缓存接口
#include "tf2/utils.h"  //提供四元数与欧拉角之间的转换接口
#include <chrono>

class TfListener : public rclcpp::Node
{
public:
  TfListener() : Node("tf_listener")
  {
    buffer_ = std::make_shared<tf2_ros::Buffer>(this->get_clock());
    listener_ = std::make_shared<tf2_ros::TransformListener>(*buffer_,this);
    timer_ = this->create_wall_timer(
      std::chrono::seconds(6),
      std::bind(&TfListener::getTransform, this));
  };

  void getTransform()
  {
    //到buffer里查询坐标关系
    try
    {
        //查询坐标关系
        const auto transform = buffer_->lookupTransform("base_link", "target_point", this->get_clock()->now(), rclcpp::Duration::from_seconds(1.0));
        //获取查询结果
        auto translation = transform.transform.translation;
        auto rotation = transform.transform.rotation;
        //将四元数转换为欧拉角
        double roll, pitch, yaw;
        tf2::getEulerYPR(rotation, yaw, pitch, roll);
        RCLCPP_INFO(this->get_logger(), "Translation: x=%f, y=%f, z=%f", translation.x, translation.y, translation.z);
        RCLCPP_INFO(this->get_logger(), "Rotation: roll=%f, pitch=%f, yaw=%f", roll, pitch, yaw);
    }
    catch(const std::exception& e)  
    {
        RCLCPP_WARN(this->get_logger(), "Could not get transform: %s", e.what());
    }
    
  }

  private:
    std::shared_ptr<tf2_ros::TransformListener> listener_;
    rclcpp::TimerBase::SharedPtr timer_;
    std::shared_ptr<tf2_ros::Buffer> buffer_;
};

int main(int argc, char *argv[])
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<TfListener>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}