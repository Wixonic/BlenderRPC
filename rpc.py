import bpy
import json
from bpy.app.handlers import persistent
import requests
import time

update_delay = 10.0

def main():
	global app_version
	app_version = "Blender " + bpy.app.version_string

	global GPUName
	GPUName = bpy.context.preferences.addons["cycles"].preferences.devices[0].name

	global start_time
	start_time = int(round(time.time() * 1000))

	bpy.app.handlers.load_post.append(start_timer)
	bpy.app.handlers.render_init.append(render_started)
	bpy.app.handlers.render_complete.append(render_ended)
	bpy.app.handlers.render_cancel.append(render_ended)
	bpy.app.handlers.render_frame_pre.append(render_frame)

	start_timer(None)

@persistent
def start_timer(dummy):
	if bpy.app.timers.is_registered(update):
		bpy.app.timers.unregister(update)

	bpy.app.timers.register(update)

@persistent
def render_started(dummy):
	if bpy.app.timers.is_registered(update):
		bpy.app.timers.unregister(update)

	scene = bpy.context.scene
	total_frames = scene.frame_end - scene.frame_start + 1

	start_time = int(round(time.time() * 1000))

	update(details=f"Rendering on {GPUName}", state=f"Rendering {total_frames} frames", large_image="blender-render", large_text=f"Rendering {total_frames} frames", small_image="blender", small_text=app_version, start_time=start_time)

@persistent
def render_ended(dummy):
	bpy.app.timers.register(update)

	start_time = int(round(time.time() * 1000))

	update(large_image="blender", large_text=app_version, small_image="blender", small_text=app_version, start_time=start_time)

@persistent
def render_frame(dummy):
	scene = bpy.context.scene
	total_frames = scene.frame_end - scene.frame_start + 1
	frames_done = scene.frame_current - scene.frame_start + 1
	progress_percentage = (frames_done / total_frames) * 100

	update(large_image="blender-render", large_text=f"Rendering {frames_done}/{total_frames} frames", details=f"Rendering on {GPUName}", state=f"Rendering {frames_done}/{total_frames} frames", small_image="blender", small_text=f"{progress_percentage:.2f}% completed", start_time=start_time)

def update(small_image, small_text, large_image, large_text, details, state, start_time):
	data = {
		"small_image": small_image,
		"small_text": small_text,
		"large_image": large_image,
		"large_text": large_text,
		"details": details,
		"state": state,
		"start_time": start_time
	}

	headers = {"Content-Type": "application/json"}
	response = requests.post("http://localhost:22000", data=json.dumps(data), headers=headers)
	if response.status_code != 200:
		print(f"Failed to send data: {response.status_code}, {response.text}")

	return update_delay