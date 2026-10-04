import launch
import launch_ros

def generate_launch_description():
    #1.声明一个launch参数
    action_declare_arg_background_g = launch.actions.DeclareLaunchArgument(
        name='launch_bg',
        default_value='128',
        description='Green value for the background color'
    )
    #2.把launch的参数手动传递给某个节点

    action_node_turtlesim_node = launch_ros.actions.Node(
        package='turtlesim',
        executable='turtlesim_node',
        output='screen',
        parameters=[{'background_g': launch.substitutions.LaunchConfiguration('launch_bg')}]
    )
    action_node_patrol_client = launch_ros.actions.Node(
        package='demo_cpp_service',
        executable='patrol_client',
        output='log',
    )
    action_node_turtle_control = launch_ros.actions.Node(
        package='demo_cpp_service',
        executable='turtle_control',
        output='both',
    )

    return launch.LaunchDescription(
            [action_declare_arg_background_g,
             action_node_turtlesim_node, 
             action_node_patrol_client, 
             action_node_turtle_control]
    )