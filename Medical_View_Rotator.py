bl_info = {
    "name": "Medical View Rotator (Fixed)",
    "author": "Takashi",
    "version": (1, 2),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > ViewTools",
    "description": "Z正方向基準、360度シームレス回転ツール",
    "category": "3D View",
}

import bpy
from mathutils import Quaternion, Vector
import math

class ViewRotationProperties(bpy.types.PropertyGroup):
    def update_view(self, context):
        # 1. 基準姿勢 (0ポジション): 
        # Z正方向からXY面を見下ろす（上がY+、右がX+）
        # Blenderのデフォルトの単位クォータニオン (1, 0, 0, 0) がこの状態
        base_rot = Quaternion((1.0, 0.0, 0.0, 0.0))

        # 2. 各軸の回転量をラジアンに変換 (360度対応)
        # subtype='ANGLE' を外したため、ここで確実に度数からラジアンへ変換
        rad_x = math.radians(self.rot_x)
        rad_y = math.radians(self.rot_y)
        rad_z = math.radians(self.rot_z)

        # 3. 視点（カメラ）の独立した回転を生成
        # 視点操作として直感的に動くよう、回転軸の方向を整理
        rot_x_q = Quaternion((1.0, 0.0, 0.0), rad_x)  # X軸周りの回転
        rot_y_q = Quaternion((0.0, 1.0, 0.0), rad_y)  # Y軸周りの回転
        rot_z_q = Quaternion((0.0, 0.0, 1.0), rad_z)  # Z軸周りの回転

        # 回転を合成 (クォータニオンの乗算)
        # 軸の入れ替わりを防ぐため、基準に対して各軸を正しくブレンド
        final_quat = base_rot @ rot_z_q @ rot_y_q @ rot_x_q

        # 3Dビューへの適用
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.region_3d.view_rotation = final_quat

    # 360度1回転を正確に行うため、subtypeを削除し、範囲を-180〜180に設定
    rot_x: bpy.props.FloatProperty(
        name="X", default=0.0, min=-180.0, max=180.0, update=update_view
    )
    rot_y: bpy.props.FloatProperty(
        name="Y", default=0.0, min=-180.0, max=180.0, update=update_view
    )
    rot_z: bpy.props.FloatProperty(
        name="Z", default=0.0, min=-180.0, max=180.0, update=update_view
    )

class VIEW3D_PT_CustomRotationPanel(bpy.types.Panel):
    bl_label = "自由視点ビュー"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ViewTools'

    def draw(self, context):
        layout = self.layout
        props = context.scene.view_rot_props
        
        col = layout.column(align=True)
        col.prop(props, "rot_x", slider=True)
        col.prop(props, "rot_y", slider=True)
        col.prop(props, "rot_z", slider=True)
        
        layout.operator("view3d.reset_medical_view", text="リセット")

class VIEW3D_OT_ResetMedicalView(bpy.types.Operator):
    bl_idname = "view3d.reset_medical_view"
    bl_label = "Reset View"
    def execute(self, context):
        props = context.scene.view_rot_props
        props.rot_x = 0.0
        props.rot_y = 0.0
        props.rot_z = 0.0
        return {'FINISHED'}

classes = [ViewRotationProperties, VIEW3D_PT_CustomRotationPanel, VIEW3D_OT_ResetMedicalView]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.view_rot_props = bpy.props.PointerProperty(type=ViewRotationProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.view_rot_props

if __name__ == "__main__":
    register()