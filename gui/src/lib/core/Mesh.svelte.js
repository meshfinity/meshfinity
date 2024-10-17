export default class Mesh {
  rembgPreviewDataUrl = $state(null);

  positions = $state(null);
  texCoords = $state(null);
  normals = $state(null);
  indices = $state(null);
  previewReady = $derived(!!this.positions && !!this.indices);

  coarseTextureImage = $state(null);

  exportableData = $state(null);

  reset() {
    this.rembgPreviewDataUrl = null;
    this.positions = null;
    this.texCoords = null;
    this.normals = null;
    this.indices = null;
    this.coarseTextureImage = null;
    this.exportableData = null;
  }
}
