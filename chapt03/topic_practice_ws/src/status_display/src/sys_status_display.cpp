#include <rclcpp/rclcpp.hpp>
#include <QApplication>
#include <QLabel>
#include <QString>
#include <status_interface/msg/system_status.hpp>

using SystemStatus = status_interface::msg::SystemStatus;


class SysStatusDisplay : public rclcpp::Node
{
public:
    SysStatusDisplay() : Node("sys_status_display")
    {
        // 创建订阅者，订阅系统状态消息
        label_ = new QLabel();
        subscriber = this->create_subscription<SystemStatus>(
            "sys_status", 10,
            [&](const SystemStatus::SharedPtr msg) -> void {
                label_->setText(get_status_text(msg));
            }
        );
            label_->setText(get_status_text(std::make_shared<SystemStatus>()));
            label_->show();
    }

    QString get_status_text(const SystemStatus::SharedPtr msg)
    {
        std::stringstream show_str;
        show_str << "===========状态可视化工具============\n" 
                 << "数据时间：\t " << msg->stamp.sec << "\ts\n" 
                 << "主机名字：\t " << msg->host_name << "\t\n" 
                 << "CPU使用率：\t " << msg->cpu_percent << "\t%\n" 
                 << "内存使用率：\t " << msg->memory_percent << "\t%\n" 
                 << "内存总大小：\t " << msg->memory_total << "\tMB\n" 
                 << "剩余内存大小：\t " << msg->memory_available << "\tMB\n" 
                 << "网络发送速率：\t " << msg->net_sent << "\tMB/s\n" 
                 << "网络接收速率：\t " << msg->net_recv << "\tMB/s\n" 
                 << "====================================\n";
                    
        return QString::fromStdString(show_str.str());
    } 
private:
    rclcpp::Subscription<SystemStatus>::SharedPtr subscriber;
    QLabel* label_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    QApplication app(argc, argv);
    auto node = std::make_shared<SysStatusDisplay>();
    std::thread spin_thread([&]() { rclcpp::spin(node); });
    spin_thread.detach();
    app.exec();  //执行应用，阻塞代码

    return 0;
}