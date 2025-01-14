import bpy
from . import rpc

bl_info = {
    "name": "BlenderRPC",
    "author": "Wixonic",
    "version": (1, 0, 0),
    "blender": (4, 3, 0),
    "description": "Blender add-on for WixiBot RPC",
    "category": "System"
}

class BlenderRPC(bpy.types.Operator):
    bl_idname = "system.blender_rpc"
    bl_label = "Blender RPC"
    bl_options = {"REGISTER"}

    def execute(self, context):
        try:
            rpc.main()
            return {"FINISHED"}
        except Exception as e:
            self.report({"ERROR"}, f"RPC failed: {e}")
            return {"CANCELLED"}

def register():
    bpy.utils.register_class(BlenderRPC)

def unregister():
    bpy.utils.unregister_class(BlenderRPC)

if __name__ == "__main__":
    register()
