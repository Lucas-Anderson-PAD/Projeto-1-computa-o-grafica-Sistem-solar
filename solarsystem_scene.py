# ---------------------------------------------------------------------
# solarsystem_scene.py
#
# Corresponde ao bloco "CONSTRUÇÃO DA CENA" do sistema.py original
# (a parte que criava texturas e montava a hierarquia pivô+posição de
# cada astro). A hierarquia é idêntica à original; o que muda é quem
# resolve cada peça:
#   - Node (node.py) faz o papel do Node caseiro de sistema.py:
#     world_matrix = pai.world_matrix @ local_matrix, calculado por
#     Node.get_model_matrix/State.push_matrix em vez de
#     Node.update(parent_matrix) escrito à mão.
#   - Transform (transform.py) faz o papel de local_matrix: translate/
#     scale/rotate compõem matriz igual a mat4_translation/mat4_scale/
#     mat4_rotation_z do original.
#   - Texture/Sampler/TextureSet (texture.py/sampler.py/textureset.py)
#     substituem a classe TextureSet caseira (mesma ideia - textura +
#     sampler num bind group), mas a textura já sai pronta como
#     rgba8unorm-srgb, sem o load_texture_rgba manual do original.
#   - Square (square.py) substitui a classe Square caseira; Disk
#     (disk.py, novo neste projeto) substitui a classe Disk caseira.
# SolarSystemEngine (solarsystem_engine.py) é quem depois gira os
# quatro Transforms de pivô que build_scene devolve.
# ---------------------------------------------------------------------
from __future__ import annotations

import wgpu

from node import Node
from transform import Transform
from shader import Shader
from texture import Texture
from sampler import Sampler
from textureset import TextureSet
from square import Square
from disk import Disk

from config import (
  SUN_RADIUS, MERCURY_ORBIT, MERCURY_RADIUS, EARTH_ORBIT, EARTH_RADIUS,
  MOON_ORBIT, MOON_RADIUS, BACKGROUND_SCALE, IMAGES_DIR,
  SUN_IMAGE, EARTH_IMAGE, MERCURY_IMAGE, MOON_IMAGE, BACKGROUND_IMAGE,
)
from solarsystem_engine import SolarSystemEngine


def _load_texture_set (device: wgpu.GPUDevice, shader: Shader, filename: str) -> TextureSet:
  """Loads one image into a Texture+Sampler pair and registers it as a
  TextureSet under `shader` - see Shader.add_texture_set (shader.py).
  Every astro/fundo tem sua própria TextureSet, mas todas usam os
  mesmos varnames "tex"/"samp": tudo bem, Shader.add_texture_set indexa
  o bind group por instância de TextureSet, não por varname (mesmo
  padrão que main_3d.py usa para reaproveitar a PhongMaterial `white`
  sob mais de um Node)."""
  tex = Texture(device, "tex", f"{IMAGES_DIR}/{filename}")
  samp = Sampler(device, "samp")
  ts = TextureSet([tex, samp])
  shader.add_texture_set(ts)
  return ts


def build_scene (device: wgpu.GPUDevice, shader: Shader) -> tuple[Node, SolarSystemEngine]:
  """Builds the solar-system Node hierarchy (background, sun, Mercury/
  Venus, Earth+Moon) and its matching SolarSystemEngine. Returns the
  root Node still without a Pipeline set - main_solarsystem.py attaches
  one via Node.set_pipeline once it exists, same as sistema.py's root
  only got its pipeline indirectly through Engine._create_pipeline."""

  # --- texturas ---
  sun_ts = _load_texture_set(device, shader, SUN_IMAGE)
  earth_ts = _load_texture_set(device, shader, EARTH_IMAGE)
  mercury_ts = _load_texture_set(device, shader, MERCURY_IMAGE)
  moon_ts = _load_texture_set(device, shader, MOON_IMAGE)
  star_ts = _load_texture_set(device, shader, BACKGROUND_IMAGE)

  # --- fundo: textura de espaço, bem maior que a área visível ---
  trf_background = Transform()
  trf_background.scale(BACKGROUND_SCALE, BACKGROUND_SCALE, 1.0)
  background = Node(trf=trf_background, apps=[star_ts], shps=[Square(device)])

  # --- sol: estático, no centro ---
  trf_sun = Transform()
  trf_sun.scale(SUN_RADIUS, SUN_RADIUS, 1.0)
  sun = Node(trf=trf_sun, apps=[sun_ts], shps=[Disk(device)])

  # --- astro adicional (Mercúrio/Vênus): translação em torno do Sol ---
  trf_mercury_shape = Transform()
  trf_mercury_shape.scale(MERCURY_RADIUS, MERCURY_RADIUS, 1.0)
  mercury_shape = Node(trf=trf_mercury_shape, apps=[mercury_ts], shps=[Disk(device)])

  trf_mercury_pos = Transform()
  trf_mercury_pos.translate(MERCURY_ORBIT, 0.0, 0.0)
  mercury_pos = Node(trf=trf_mercury_pos, nodes=[mercury_shape])

  trf_mercury_pivot = Transform()   # girado a cada quadro por SolarSystemEngine
  mercury_pivot = Node(trf=trf_mercury_pivot, nodes=[mercury_pos])

  # --- lua: translação em torno da terra; pendurada em earth_pos, NÃO
  # em earth_spin, para não herdar a rotação da terra no próprio eixo ---
  trf_moon_shape = Transform()
  trf_moon_shape.scale(MOON_RADIUS, MOON_RADIUS, 1.0)
  moon_shape = Node(trf=trf_moon_shape, apps=[moon_ts], shps=[Disk(device)])

  trf_moon_pos = Transform()
  trf_moon_pos.translate(MOON_ORBIT, 0.0, 0.0)
  moon_pos = Node(trf=trf_moon_pos, nodes=[moon_shape])

  trf_moon_pivot = Transform()   # girado a cada quadro por SolarSystemEngine
  moon_pivot = Node(trf=trf_moon_pivot, nodes=[moon_pos])

  # --- terra: translação em torno do sol + rotação própria em torno do
  # eixo (a textura da terra, com continentes bem marcados, deixa essa
  # rotação visível) ---
  trf_earth_shape = Transform()
  trf_earth_shape.scale(EARTH_RADIUS, EARTH_RADIUS, 1.0)
  earth_shape = Node(trf=trf_earth_shape, apps=[earth_ts], shps=[Disk(device)])

  trf_earth_spin = Transform()   # rotação da terra em torno do próprio eixo
  earth_spin = Node(trf=trf_earth_spin, nodes=[earth_shape])

  trf_earth_pos = Transform()
  trf_earth_pos.translate(EARTH_ORBIT, 0.0, 0.0)
  # lua é irmã de earth_spin: herda a órbita da terra, não o spin
  earth_pos = Node(trf=trf_earth_pos, nodes=[earth_spin, moon_pivot])

  trf_earth_pivot = Transform()   # translação da terra em torno do sol
  earth_pivot = Node(trf=trf_earth_pivot, nodes=[earth_pos])

  # --- raiz da cena: fundo primeiro (sem depth buffer, a ordem de
  # desenho é o que garante a sobreposição correta) ---
  root = Node(nodes=[background, sun, mercury_pivot, earth_pivot])
  engine = SolarSystemEngine(trf_mercury_pivot, trf_earth_pivot, trf_earth_spin, trf_moon_pivot)
  return root, engine
