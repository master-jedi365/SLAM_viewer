import bpy
import os
import sys
import glob
import numpy as np
from scipy.spatial.transform import Rotation

# 入力データ
RT_TXT_DIR = os.path.join("data", "aist_living_lab_1", "RTs")
RT_LIST_TXT_PATH = os.path.join("data", "aist_living_lab_1", "RT_txt_list.txt")
MAP_PLY_PATH = os.path.join("data", "aist_living_lab_1", "map.ply")

# 実行パラメータ
WORKDIR_PATH = "workdir"
SKIP_FRAME = 5
# 参考文献
# https://tamaki-py.hatenablog.com/entry/2019/05/26/190022
# https://kamino.hatenablog.com/entry/blender_viz_coordinates
# https://3dcg-school.pro/blender-freestyle/
# https://bluebirdofoz.hatenablog.com/entry/2020/07/19/212559


def make_trajectory_points_ply(txt_path_list, txt_dir_path, output_path):
    points_list = make_points_list(txt_path_list, txt_dir_path)
    length = len(points_list)
    data_list = [
        "ply\n",
        "format ascii 1.0\n",
        f"element vertex {length}\n",
        "property float x\n",
        "property float y\n",
        "property float z\n",
        "end_header\n",
    ]
    points_str_list = [f"{point[0]} {point[1]} {point[2]}\n" for point in points_list]
    data_list += points_str_list
    with open(output_path, "w") as f_out:
        f_out.writelines(data_list)

def make_points_list(txt_path_list, txt_dir_path):
    points_list = []
    for txt_path in txt_path_list:
        local_origin = np.array([0, 0, 0, 1]).reshape(4, 1)
        RT = np.loadtxt(os.path.join(txt_dir_path, txt_path))
        world_xyz = np.linalg.inv(RT)@local_origin
        points_list.append(world_xyz.ravel())
    return points_list

def make_RT_txt_list(RT_dir_path):
    rt_list = glob.glob(RT_dir_path)
    rt_list = [os.path.basename(txt) for txt in rt_list]

    with open("RT_txt_list.txt", "w")as f:
        for txt in rt_list:
            print(txt, file=f)

def set_campose(camera_pose_obj, RT, RT_orient="left_hand"):
    # blender = 右手系, opnvslam = 左手系
    if RT_orient == "left_hand":
        sp_rot = Rotation.from_matrix(RT[:3, :3].transpose())
    elif RT_orient == "right_hand":
        pass
    else:
        raise ValueError("RT_orient flag must be `left_hand` or `right_hand`!!")

    camera_pose_obj.rotation_mode = 'XYZ'
    camera_pose_obj.rotation_euler = [
        sp_rot.as_euler('xyz')[0],
        sp_rot.as_euler('xyz')[1],
        sp_rot.as_euler('xyz')[2],
    ]

    print("rotation: ", sp_rot.as_euler('xyz'))

    if np.linalg.cond(RT) < 1/sys.float_info.epsilon:
        trans_mat  = np.linalg.inv(RT)
    else:
        trans_mat = np.identity(4)

    trans = trans_mat@(np.array([0,0,0,1]).reshape(-1, 1))

    camera_pose_obj.location = [
        trans[0],
        trans[1],
        trans[2]
    ]

def get_camera_pose_object():
    # x_axis
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1, location=(0.5, 0, 0), rotation=(np.pi / 2, 0.0, np.pi / 2))
    bpy.context.active_object.name = "x_axis"
    x_mat = bpy.data.materials.new("x_mat")
    x_mat.diffuse_color = (1, 0, 0, 1)
    bpy.context.object.data.materials.append(x_mat)

    # y_axis
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1, location=(0, 0.5, 0), rotation=(np.pi / 2, np.pi / 2, 0.0))
    bpy.context.active_object.name = "y_axis"
    y_mat = bpy.data.materials.new("y_mat")
    y_mat.diffuse_color = (0, 1, 0, 1)
    bpy.context.object.data.materials.append(y_mat)

    # z_axis
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=1, location=(0, 0, 0.5))
    bpy.context.active_object.name = "z_axis"
    z_mat = bpy.data.materials.new("z_mat")
    z_mat.diffuse_color = (0, 0, 1, 1)
    bpy.context.object.data.materials.append(z_mat)
    camera_pose = bpy.data.objects["z_axis"]
    y_axis = bpy.data.objects["y_axis"]
    x_axis = bpy.data.objects["x_axis"]

    camera_pose.select_set(True)
    y_axis.select_set(True)
    x_axis.select_set(True)
    
    bpy.ops.object.join()
    camera_pose.name = "camera_pose"

    # # カーソルはデフォルトで原点
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='BOUNDS')
    bpy.data.objects["camera_pose"].show_name = True
    bpy.data.objects["camera_pose"].show_axis = True

    return camera_pose

def make_ply_instances(ply_path, diffuse_color, material_name, geometry_tree_name):

    if not os.path.isfile(ply_path):
        return -1
    #-----------------------------------------#
    # import ply                              #
    #-----------------------------------------#
    bpy.ops.import_mesh.ply(filepath=ply_path)
    map_obj = bpy.context.active_object
    map_geo_modifier = map_obj.modifiers.new(name="Geometry Nodes", type='NODES')

    #-----------------------------------------#
    # making cube instances for visualization #
    #-----------------------------------------#

    # making geometry node group
    map_geo_modifier.node_group = bpy.data.node_groups.new(type='GeometryNodeTree', name=geometry_tree_name)
    map_geo_modifier.node_group.inputs.new(type="NodeSocketGeometry", name="Geometry")
    map_geo_modifier.node_group.outputs.new(type="NodeSocketGeometry", name="Geometry")
    
    # making geometry nodes
    in_node = map_geo_modifier.node_group.nodes.new(type='NodeGroupInput')
    in_node.location = -300, 0
    out_node = map_geo_modifier.node_group.nodes.new(type='NodeGroupOutput')
    out_node.location = 300, 0
    IoP_node = map_geo_modifier.node_group.nodes.new(type="GeometryNodeInstanceOnPoints")
    IoP_node.location = 0, 0
    ri_node = map_geo_modifier.node_group.nodes.new(type="GeometryNodeRealizeInstances")
    ri_node.location = 150, 0
    cube_node = map_geo_modifier.node_group.nodes.new(type="GeometryNodeMeshCube")
    cube_node.location = -300, -100
    # 立方体のスケール
    cube_node.inputs[0].default_value[0] = 0.05
    cube_node.inputs[0].default_value[1] = 0.05
    cube_node.inputs[0].default_value[2] = 0.05
    mat_node = map_geo_modifier.node_group.nodes.new(type="GeometryNodeReplaceMaterial")
    mat_node.location = -150, -100
    map_mat = bpy.data.materials.new(material_name)
    map_mat.diffuse_color = diffuse_color
    bpy.context.object.data.materials.append(map_mat)
    mat_node.inputs[2].default_value = bpy.data.materials[material_name]

    # linking nodes
    map_geo_modifier.node_group.links.new(in_node.outputs["Geometry"], IoP_node.inputs["Points"])
    map_geo_modifier.node_group.links.new(cube_node.outputs["Mesh"], mat_node.inputs["Geometry"])
    map_geo_modifier.node_group.links.new(mat_node.outputs["Geometry"], IoP_node.inputs["Instance"])
    map_geo_modifier.node_group.links.new(IoP_node.outputs["Instances"], ri_node.inputs["Geometry"])
    map_geo_modifier.node_group.links.new(ri_node.outputs["Geometry"], out_node.inputs["Geometry"])

    return 0

def main():

    os.makedirs(WORKDIR_PATH, exist_ok=True)
    with open(RT_LIST_TXT_PATH, "r") as f:
        txt_list = f.read().splitlines()
    txt_list.sort()
    # trajectory points
    make_trajectory_points_ply(
        txt_list, 
        txt_dir_path=RT_TXT_DIR,
        output_path=os.path.join(WORKDIR_PATH, "trajectory_points.ply")
    )

    make_ply_instances(
        ply_path=os.path.join(WORKDIR_PATH, "trajectory_points.ply"),
        diffuse_color=(1, 0, 0, 0.2), 
        material_name="tragectory_mat", 
        geometry_tree_name="trajectory_geometry"
    )
    bpy.ops.object.select_all(action='DESELECT')

    # slam map
    map_diffuse_color = (0, 1, 0.5, 0.2)
    make_ply_instances(MAP_PLY_PATH, map_diffuse_color, material_name="map_mat", geometry_tree_name="map_geometry")
    bpy.ops.object.select_all(action='DESELECT')

    # camera pose
    camera_pose = get_camera_pose_object()
    for idx, txt_path in enumerate(txt_list):
        if idx % SKIP_FRAME != 0:
            continue
        bpy.ops.object.select_all(action='DESELECT')
        camera_pose.select_set(True)
        txt_path = os.path.join(RT_TXT_DIR, txt_path)
        RT = np.loadtxt(txt_path)

        set_campose(camera_pose_obj=camera_pose, RT=RT)
        camera_pose.keyframe_insert(data_path = "location", frame=idx)
        camera_pose.keyframe_insert(data_path = "rotation_euler", frame=idx)
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
 
if __name__ == "__main__":
    main()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WORKDIR_PATH, "vis.blend"))