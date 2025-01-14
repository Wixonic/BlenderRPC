import bpy
import json
import requests
import time
from bpy.app.handlers import persistent

bl_info = {
    "name": "BlenderRPC",
    "author": "Wixonic",
    "version": (1, 0, 0),
    "blender": (2, 8, 0),
    "description": "Blender add-on for WixiBot RPC",
    "category": "System"
}

update_delay = 10.0
app_version = ""
start_time = 0
GPUName = "Unknown GPU"

@persistent
def start_timer(dummy):
    global app_version, start_time, GPUName
    app_version = "Blender " + bpy.app.version_string
    start_time = int(round(time.time() * 1000))
    
    try:
        GPUName = bpy.context.preferences.addons["cycles"].preferences.devices[0].name
    except (KeyError, IndexError, AttributeError):
        GPUName = "Unknown GPU"
    
    bpy.app.timers.register(update)
    print("Start timer")

@persistent
def render_started(dummy):
    if bpy.app.timers.is_registered(update):
        bpy.app.timers.unregister(update)
    
    scene = bpy.context.scene
    total_frames = scene.frame_end - scene.frame_start + 1
    
    start_time = int(round(time.time() * 1000))
    update(small_image="blender", small_text=app_version, large_image="blender-render", large_text=f"Rendering {total_frames} frames", details=f"Rendering on {GPUName}", state=f"Rendering {total_frames} frames")
    
    print("Render started")

@persistent
def render_ended(dummy):
    bpy.app.timers.register(update)
    
    start_time = int(round(time.time() * 1000))
    update(large_image="blender", large_text=app_version)
    
    print("Render ended")

@persistent
def render_frame(dummy):
    scene = bpy.context.scene
    total_frames = scene.frame_end - scene.frame_start + 1
    frames_done = scene.frame_current - scene.frame_start + 1
    progress_percentage = (frames_done / total_frames) * 100
    
    update(small_image="blender", small_text=f"{progress_percentage:.2f}% completed", large_image="blender_render", large_text=f"Rendering {frames_done}/{total_frames} frames",  details=f"Rendering on {GPUName}", state=f"Rendering {frames_done}/{total_frames} frames")
    
    print("Render frame")

def update(small_image=None, small_text=None, large_image=None, large_text=None, details=None, state=None, start_time=start_time):
    data = {
        "small_image": small_image,
        "small_text": small_text,
        "large_image": large_image,
        "large_text": large_text,
        "details": details,
        "state": state,
        "start_time": start_time
    }

    try:
        response = requests.post("http://localhost:22000", data=json.dumps(data))
        if response.status_code != 200:
            print(f"Failed to send data: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Request error: {e}")

    print("Update")
    return update_delay

def register():
    try:
        start_timer(None)
    except Exception as e:
        print(f"Failed to launch: {e}")
    
    bpy.app.handlers.load_post.append(start_timer)
    bpy.app.handlers.render_init.append(render_started)
    bpy.app.handlers.render_complete.append(render_ended)
    bpy.app.handlers.render_cancel.append(render_ended)
    bpy.app.handlers.render_pre.append(render_frame)
    
    print("Blender RPC registered")

def unregister():
    bpy.app.handlers.load_post.remove(start_timer)
    bpy.app.handlers.render_init.remove(render_started)
    bpy.app.handlers.render_complete.remove(render_ended)
    bpy.app.handlers.render_cancel.remove(render_ended)
    bpy.app.handlers.render_pre.remove(render_frame)
    
    print("Blender RPC unregistered")

if __name__ == "__main__":
    register()