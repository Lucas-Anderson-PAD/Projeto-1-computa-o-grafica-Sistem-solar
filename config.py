# ---------------------------------------------------------------------
# config.py
#
# Só constantes, sem lógica nenhuma - nem de grafo de cena, nem de GPU.
# Corresponde 1:1 ao bloco "CONFIGURAÇÕES GERAIS E VARIÁVEIS (Ponto
# único de alteração)" do sistema.py original (linhas 15-51); os
# valores não mudaram, só o formato de ângulo (ver nota abaixo).
# Consumido por solarsystem_scene.py (raios/órbitas/imagens) e por
# solarsystem_engine.py (velocidades).
# ---------------------------------------------------------------------
from __future__ import annotations

SUN_RADIUS = 1.0

MERCURY_ORBIT = 2.2   # astro adicional entre o sol e a terra (Mercúrio/Vênus)
MERCURY_RADIUS = 0.22

EARTH_ORBIT = 4.2
EARTH_RADIUS = 0.4

MOON_ORBIT = 0.9
MOON_RADIUS = 0.15

# Velocidades angulares em graus por segundo. sistema.py guardava isso
# em radianos/s (math.radians(...)) porque suas próprias mat4_rotation_z
# esperavam radianos; o framework's Transform.rotate (transform.py) já
# recebe graus e converte internamente, então os valores viraram graus
# diretos - mesma velocidade percebida, uma conversão a menos.
SPEED_MERCURY_ORBIT = 70.0    # translação de Mercúrio/Vênus em torno do Sol
SPEED_EARTH_ORBIT = 30.0      # translação da Terra em torno do Sol
SPEED_EARTH_SPIN = 300.0      # rotação da Terra em torno do próprio eixo
SPEED_MOON_ORBIT = 160.0      # translação da Lua em torno da Terra

BACKGROUND_SCALE = 20.0   # fundo estrelado, bem maior que a área de câmera visível

CAMERA_BOUNDS = 6.0    # câmera ortográfica: -6..6 em x e y
MAX_FPS = 30.0         # taxa de atualização máxima

# --- imagens: pasta "images" IRMÃ deste script (não um nível acima -
# main_2d.py/main_3d.py usam "../images" porque pressupõem os .py numa
# subpasta tipo "src"; aqui os .py estão soltos na raiz do repositório,
# no mesmo nível de "images", então o caminho é sem "../"). Ajuste aqui
# se mover os scripts para dentro de uma subpasta. ---
IMAGES_DIR = "images"
SUN_IMAGE = "sun.png"
EARTH_IMAGE = "terra_512.png"     # alternativa disponível: "earth.png"
MERCURY_IMAGE = "noise.png"
MOON_IMAGE = "golfball.png"       # crateras da bola de golfe combinam com a lua
BACKGROUND_IMAGE = "stars.png"

# "earth-normal.png" está em images/ mas não é usado: este projeto não
# faz normal mapping (é tudo 2D, sem iluminação - ver textured.wgsl),
# só serve se algum dia normal mapping for adicionado ao shader.

# --- shader: mesma raiz dos .py (ver observação acima sobre "../") ---
SHADER_PATH = "textured.wgsl"
