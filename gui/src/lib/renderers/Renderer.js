export default class Renderer {
  constructor(canvas, gl) {
    this._canvas = canvas;
    this._gl = gl;

    this._gl.clearColor(0.4, 0.6, 0.9, 0.0);
    this._gl.clearDepth(1.0);
    this._gl.enable(gl.DEPTH_TEST);
  }

  render() {
    this._gl.viewport(0, 0, this._canvas.width, this._canvas.height);
    this._gl.clear(this._gl.COLOR_BUFFER_BIT | this._gl.DEPTH_BUFFER_BIT);
  }

  _compileShader(type, source) {
    const shader = this._gl.createShader(type);
    this._gl.shaderSource(shader, source);
    this._gl.compileShader(shader);

    if (!this._gl.getShaderParameter(shader, this._gl.COMPILE_STATUS)) {
      console.error(
        "Shader compilation failed: " + this._gl.getShaderInfoLog(shader)
      );
      this._gl.deleteShader(shader);
      return null;
    }

    return shader;
  }

  _createShaderProgram(vtxSource, fragSource) {
    const vtxShader = this._compileShader(this._gl.VERTEX_SHADER, vtxSource);
    const fragShader = this._compileShader(
      this._gl.FRAGMENT_SHADER,
      fragSource
    );

    const program = this._gl.createProgram();
    this._gl.attachShader(program, vtxShader);
    this._gl.attachShader(program, fragShader);
    this._gl.linkProgram(program);

    if (!this._gl.getProgramParameter(program, this._gl.LINK_STATUS)) {
      console.error(
        "Shader program linking failed: " + this._gl.getProgramInfoLog(program)
      );
      this._gl.deleteShader(vtxShader);
      this._gl.deleteShader(fragShader);
      this._gl.deleteProgram(program);
      return null;
    }

    return program;
  }
}
