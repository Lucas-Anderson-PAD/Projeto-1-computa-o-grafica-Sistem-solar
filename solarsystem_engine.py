# ---------------------------------------------------------------------
# solarsystem_engine.py
#
# Equivalente à função avulsa atualizar_cena(dt) + ao dict `angulos`
# do sistema.py original. Vira uma classe porque o framework anima por
# subclasse de Engine (engine.py), registrada em Scene.add_engine
# (scene.py) e chamada uma vez por quadro por Scene.update(dt) - mesmo
# papel que luxor/luxorengine.py's LuxorEngine cumpre para a luminária:
# guardar um ângulo acumulado por Transform e, a cada update, resetar
# esse Transform (load_identity) e girar (rotate) para o novo ângulo -
# mesma ideia de "cada pivô é um nó de rotação pura" do original, só
# que sem reescrever mat4_rotation_z(angulo) manualmente a cada quadro.
# ---------------------------------------------------------------------
from __future__ import annotations

from engine import Engine
from transform import Transform
from config import SPEED_MERCURY_ORBIT, SPEED_EARTH_ORBIT, SPEED_EARTH_SPIN, SPEED_MOON_ORBIT


class SolarSystemEngine (Engine):
  """Drives the four rotating pivots: Mercury/Venus's orbit, Earth's
  orbit, Earth's own spin, and the Moon's orbit."""

  def __init__ (self, trf_mercury_pivot: Transform, trf_earth_pivot: Transform,
                trf_earth_spin: Transform, trf_moon_pivot: Transform) -> None:
    self.trf_mercury_pivot = trf_mercury_pivot
    self.trf_earth_pivot = trf_earth_pivot
    self.trf_earth_spin = trf_earth_spin
    self.trf_moon_pivot = trf_moon_pivot
    self.angle_mercury = 0.0
    self.angle_earth_orbit = 0.0
    self.angle_earth_spin = 0.0
    self.angle_moon = 0.0

  def update (self, dt: float) -> None:
    """Called once per frame by Scene.update (scene.py). Acumula cada
    ângulo e reaplica como rotação absoluta - mesma lógica de
    angulos[...] += SPEED * dt seguido de mat4_rotation_z(angulos[...])
    do sistema.py original, agora via Transform.rotate (transform.py)."""
    self.angle_mercury += SPEED_MERCURY_ORBIT * dt
    self.angle_earth_orbit += SPEED_EARTH_ORBIT * dt
    self.angle_earth_spin += SPEED_EARTH_SPIN * dt
    self.angle_moon += SPEED_MOON_ORBIT * dt

    self.trf_mercury_pivot.load_identity()
    self.trf_mercury_pivot.rotate(self.angle_mercury, 0.0, 0.0, 1.0)

    self.trf_earth_pivot.load_identity()
    self.trf_earth_pivot.rotate(self.angle_earth_orbit, 0.0, 0.0, 1.0)

    self.trf_earth_spin.load_identity()
    self.trf_earth_spin.rotate(self.angle_earth_spin, 0.0, 0.0, 1.0)

    self.trf_moon_pivot.load_identity()
    self.trf_moon_pivot.rotate(self.angle_moon, 0.0, 0.0, 1.0)
