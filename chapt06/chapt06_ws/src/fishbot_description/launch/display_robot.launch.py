import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    #获取默认的urdf路径
    urdf_path = get_package_share_directory('fishbot_description') + '/urdf/first_robot.urdf'
    default_rviz_config_path = get_package_share_directory('fishbot_description') + '/config/display_robot_model.rviz'
    #声明urdf参数，方便修改
    action_declare_urdf_path_cmd = launch.actions.DeclareLaunchArgument(
        name='urdf_path',
        default_value=urdf_path,
        description='加载的模型文件路径'
    )
    #通过文件路径，加载urdf文件内容，并传递给robot_state_publisher节点
    urdf_content = launch.substitutions.Command(['cat ', launch.substitutions.LaunchConfiguration('urdf_path')])
    urdf_param = launch_ros.parameter_descriptions.ParameterValue(urdf_content, value_type=str)

    action_robot_state_publisher = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': urdf_param}],
    )
    action_joint_state_publisher = launch_ros.actions.Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
    )
    action_rviz2 = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', default_rviz_config_path],
    )
    
    return launch.LaunchDescription([
        action_declare_urdf_path_cmd,
        action_robot_state_publisher,
        action_joint_state_publisher,
        action_rviz2
    ])

            