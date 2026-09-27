# ---------------------------------------------------------------------
# main_solarsystem.py
#
# Equivalente à classe Engine do sistema.py original - mas só a parte
# de setup de janela/GPU (canvas/adapter/device/context) e do loop de
# quadro (draw_frame); a parte de "montar o grafo de cena" virou
# solarsystem_scene.py e a parte de "animar" virou
# solarsystem_engine.py, então este arquivo não constrói mais nada de
# cena, só orquestra. Estrutura calcada em main_2d.py/main_3d.py:
# variáveis globais de estado do frame, initialize(), update()/draw(),
# on_key(), main(). O pipeline WGPU em si (Shader/Pipeline, ver
# shader.py/pipeline.py) substitui o _create_pipeline()/render_pass do
# sistema.py original - reflexão do WGSL em vez de bind groups
# montados à mão - e Renderer (renderer.py) substitui o
# encoder/submit que estava dentro de draw_frame.
# ---------------------------------------------------------------------
from __future__ import annotations

import time
from typing import Any

import wgpu
from rendercanvas.glfw import RenderCanvas, loop

from camera2d import Camera2D
from shader import Shader
from pipeline import Pipeline
from scene import Scene
from renderer import Renderer

from config import CAMERA_BOUNDS, MAX_FPS, SHADER_PATH
from solarsystem_scene import build_scene

canvas: RenderCanvas
device: wgpu.GPUDevice
context: Any
renderer: Renderer
camera: Camera2D
scene: Scene
last_t: float = 0.0


def initialize (device: wgpu.GPUDevice, target_format: str) -> None:
  """Monta o Shader/Pipeline (a parte que era o _create_pipeline() do
  sistema.py original, aqui feita por reflexão via Shader - ver
  shader.py/wgslreflect.py), pede a build_scene (solarsystem_scene.py)
  o grafo de cena pronto, e registra tudo em Scene (scene.py)."""
  global camera, scene

  camera = Camera2D(-CAMERA_BOUNDS, CAMERA_BOUNDS, -CAMERA_BOUNDS, CAMERA_BOUNDS)

  shader = Shader(device, SHADER_PATH)
  shader.set_vertex_buffers([
    {"array_stride": 2 * 4, "step_mode": "vertex",
     "attributes": [{"format": "float32x2", "offset": 0, "var_name": "coord"}]},
    {"array_stride": 2 * 4, "step_mode": "vertex",
     "attributes": [{"format": "float32x2", "offset": 0, "var_name": "texcoord"}]},
  ])
  pipeline = Pipeline(shader, target_format, depth_stencil=None)

  root, solarsystem_engine = build_scene(device, shader)
  root.set_pipeline(pipeline)

  scene = Scene(root)
  scene.add_engine(solarsystem_engine)


def update (dt: float) -> None:
  scene.update(dt)

def draw () -> None:
  """Equivalente a draw_frame() do sistema.py original: mede dt,
  atualiza a cena, pega a textura atual do canvas e delega a passada
  de render inteira a Renderer.render (renderer.py) - encoder/
  render_pass/submit deixam de ser escritos aqui."""
  global last_t
  t = time.perf_counter()
  update(t - last_t)
  last_t = t

  target_texture = context.get_current_texture()
  renderer.render(target_texture, scene, camera)

def on_key (event: Any) -> None:
  if event["key"] == "q":
    canvas.close()


def main () -> None:
  global canvas, device, context, renderer, last_t

  canvas = RenderCanvas(size=(800, 800), title="Grafo de Cena - Mini Sistema Solar 2D",
                         update_mode="continuous", max_fps=MAX_FPS)
  adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
  device = adapter.request_device_sync()
  context = canvas.get_context("wgpu")
  # formato preferido COM "-srgb": a GPU codifica de linear para sRGB
  # automaticamente na saída - Texture (texture.py) já sobe as imagens
  # como rgba8unorm-srgb, então essa etapa continua correta sem esforço extra.
  target_format = context.get_preferred_format(device.adapter)
  context.configure(device=device, format=target_format, alpha_mode="opaque")

  renderer = Renderer(device, depth_test=False, clear_value=(0.0, 0.0, 0.0, 1.0))

  initialize(device, target_format)

  canvas.add_event_handler(on_key, "key_down")
  last_t = time.perf_counter()
  canvas.request_draw(draw)
  loop.run()

if __name__ == "__main__":
  main()
