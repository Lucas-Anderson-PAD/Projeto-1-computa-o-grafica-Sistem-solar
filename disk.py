# ---------------------------------------------------------------------
# disk.py
#
# Única forma geométrica que o framework não tinha pronta (ele já vem
# com quad.py/cube.py/sphere.py/square.py/triangle.py, mas nenhum leque
# de triângulos). A malha (vértices/texcoords/índices) é a mesma conta
# que estava no Disk(TexturedShape) do sistema.py original; o que muda
# é o encaixe: aqui ela vira um Shape (shape.py) comum, desenhado via
# State/commit_matrix (state.py, shader.py) exatamente como
# quad.py/square.py/cube.py fazem - sem buffer de matriz nem bind group
# próprios, o framework já cuida disso para qualquer Shape.
# ---------------------------------------------------------------------
from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
import wgpu
from shape import Shape

if TYPE_CHECKING:
  from state import State

class Disk (Shape):
  """Flat unit-radius disk (triangle fan) centered at the origin, in the
  xy plane. Texcoord inscribes the disk in the [0,1]x[0,1] texture
  square, t growing down - same convention as every other textured shape
  here (see Quad/Grid/Square). Coord/texcoord buffers bound at slots
  0/1, same layout as Square, since t runs opposite to y."""

  # WebGPU has no triangle-fan topology (only triangle-list/-strip); the
  # fan is triangulated via indices instead - (center, i, i+1) per
  # segment - the same workaround Square uses for its 4 corners.
  def __init__ (self, device: wgpu.GPUDevice, segments: int = 48) -> None:
    """Builds a `segments`-sided fan: one center vertex plus one per rim
    segment. Raises if segments < 3 - fewer than that isn't a polygon."""
    if segments < 3:
      raise ValueError(f"Disk needs segments >= 3, got {segments}")

    coords = [0.0, 0.0]
    texcoords = [0.5, 0.5]
    for i in range(segments):
      theta = 2.0 * math.pi * i / segments
      x, y = math.cos(theta), math.sin(theta)
      coords.extend([x, y])
      texcoords.extend([0.5 + 0.5*x, 0.5 - 0.5*y])   # t cresce para baixo

    indices = []
    for i in range(1, segments + 1):
      nxt = 1 if i == segments else i + 1
      indices.extend([0, i, nxt])

    self.nind: int = len(indices)
    bcoord = np.array(coords, dtype='float32')
    btexcoord = np.array(texcoords, dtype='float32')
    bindex = np.array(indices, dtype='uint32')
    self.coord_vbo: wgpu.GPUBuffer = device.create_buffer_with_data(data=bcoord, usage=wgpu.BufferUsage.VERTEX)
    self.texcoord_vbo: wgpu.GPUBuffer = device.create_buffer_with_data(data=btexcoord, usage=wgpu.BufferUsage.VERTEX)
    self.ibo: wgpu.GPUBuffer = device.create_buffer_with_data(data=bindex, usage=wgpu.BufferUsage.INDEX)

  def draw (self, st: State) -> None:
    first_instance = st.get_shader().commit_matrix(st)
    st.render_pass.set_vertex_buffer(0, self.coord_vbo)
    st.render_pass.set_vertex_buffer(1, self.texcoord_vbo)
    st.render_pass.set_index_buffer(self.ibo, wgpu.IndexFormat.uint32)
    st.render_pass.draw_indexed(self.nind, 1, 0, 0, first_instance)
