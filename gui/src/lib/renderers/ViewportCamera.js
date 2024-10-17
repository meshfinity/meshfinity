import { mat3, mat4 } from "gl-matrix";

export default class ViewportCamera {
  constructor() {
    this.projMat = mat4.create();
    this.viewMat = mat4.create();
    this.modelMat = mat4.create();
    this.normalMat = mat3.create();

    this._rotX = 0;
    this._rotY = 0;
    this._distance = 4.0;
  }

  update(width, height) {
    mat4.identity(this.projMat);
    mat4.perspective(
      this.projMat,
      (63.0 * Math.PI) / 180.0,
      width / height,
      0.1,
      1000.0
    );

    mat4.identity(this.viewMat);
    mat4.translate(this.viewMat, this.viewMat, [0.0, 0.0, -this._distance]);

    mat4.identity(this.modelMat);
    mat4.rotateX(this.modelMat, this.modelMat, this._rotX);
    mat4.rotateY(this.modelMat, this.modelMat, this._rotY);

    mat3.normalFromMat4(this.normalMat, this.modelMat);
  }

  onPointerMove({ dx, dy }) {
    this._rotY += dx * 0.025;
    while (this._rotY > Math.PI * 2) {
      this._rotY -= Math.PI * 2;
    }
    while (this._rotY < -Math.PI * 2) {
      this._rotY += Math.PI * 2;
    }
    this._rotX += dy * 0.025;
    this._rotX = Math.max(-Math.PI * 0.5, Math.min(this._rotX, Math.PI * 0.5));
  }

  onWheel({ signY }) {
    const MIN_DISTANCE = 2.0;
    const MAX_DISTANCE = 8.0;
    this._distance += signY * Math.log(this._distance);
    this._distance = Math.max(
      MIN_DISTANCE,
      Math.min(this._distance, MAX_DISTANCE)
    );
  }
}
