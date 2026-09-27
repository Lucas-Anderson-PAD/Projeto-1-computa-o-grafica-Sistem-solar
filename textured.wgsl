// textured.wgsl (na raiz do projeto, junto dos .py - ver config.py)
//
// Substitui o shader inline (device.create_shader_module(code="""...""")
// dentro de Engine._create_pipeline) do sistema.py original: mesma
// conta (M * posição, depois textureSample), só que como arquivo WGSL
// separado, lido por reflexão (wgslreflect.py) em vez de bind groups
// montados manualmente em Python. group(0)="matrix" é a StorageArray de
// matrizes por instância (uniformbuffer.py/StorageArray, uma linha por
// Node desenhado); group(1)="global" é a projeção da câmera (a antiga
// Uniforms.M do original virou duas peças: a matriz por-instância aqui
// e a projeção comum a todo o quadro, escrita por Shader.commit_global -
// ver shader.py); group(2)=tex/samp é a textura, igual ao bind group 1
// do original. Não há grupo "material": a aparência inteira é a
// textura amostrada, sem cor/opacidade por instância - por isso este
// shader não precisa de material.py/PhongMaterial/ColorMaterial.

struct Matrix {
  vertex: mat4x4<f32>,
};
@group(0) @binding(0) var<storage, read> matrix: array<Matrix>;

struct Global {
  projection: mat4x4<f32>,
};
@group(1) @binding(0) var<uniform> global: Global;

@group(2) @binding(0) var tex: texture_2d<f32>;
@group(2) @binding(1) var samp: sampler;

struct VertexOutput {
  @builtin(position) position: vec4<f32>,
  @location(0) texcoord: vec2<f32>,
};

@vertex
fn vs_main (
  @builtin(instance_index) instance: u32,
  @location(0) coord: vec2<f32>,
  @location(1) texcoord: vec2<f32>,
) -> VertexOutput {
  var output: VertexOutput;
  let m = matrix[instance].vertex;
  // Mfinal = projection * (matriz acumulada do nó, já em espaço de
  // câmera - a Camera2D usa view = identidade, então "vertex" aqui já
  // é a matriz de modelo pura, ver State.load_matrices).
  output.position = global.projection * m * vec4<f32>(coord, 0.0, 1.0);
  output.texcoord = texcoord;
  return output;
}

@fragment
fn fs_main (input: VertexOutput) -> @location(0) vec4<f32> {
  return textureSample(tex, samp, input.texcoord);
}
