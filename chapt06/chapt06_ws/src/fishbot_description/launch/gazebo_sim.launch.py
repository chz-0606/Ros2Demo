import launch
import launch_ros
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    #获取默认的urdf路径
    urdf_path = get_package_share_directory('fishbot_description') + '/urdf/qqbot/qqbot.urdf.xacro'
    #default_xacro_path = get_package_share_directory('fishbot_description') + '/config/display_robot_model.rviz'
    default_gazebo_world_path = get_package_share_directory('fishbot_description') + '/world/room/custom_room.world'
    #声明urdf参数，方便修改
    action_declare_urdf_path_cmd = launch.actions.DeclareLaunchArgument(
        name='urdf_path',
        default_value=urdf_path,
        description='加载的模型文件路径'
    )
    #通过文件路径，加载urdf文件内容，并传递给robot_state_publisher节点
    urdf_content = launch.substitutions.Command(['xacro ', launch.substitutions.LaunchConfiguration('urdf_path')])
    urdf_param = launch_ros.parameter_descriptions.ParameterValue(urdf_content, value_type=str)

    action_robot_state_publisher = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': urdf_param}],
    )

    action_launch_gazebo = launch.actions.IncludeLaunchDescription(
    launch.launch_description_sources.PythonLaunchDescriptionSource(
        get_package_share_directory('gazebo_ros')+ '/launch/gazebo.launch.py'
    ),
    launch_arguments={
        'world': default_gazebo_world_path,
        'verbose': 'true',
    }.items()
)
    action_spawn_entity = launch_ros.actions.Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'qqbot'],
        output='screen'
    )
    
    return launch.LaunchDescription([
        action_declare_urdf_path_cmd,
        action_robot_state_publisher,
        action_launch_gazebo,
        action_spawn_entity
    ])

            