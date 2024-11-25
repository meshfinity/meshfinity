import viewportCameraInstance from "../renderers/viewportCameraInstance.js";
import Mesh from "./Mesh.svelte.js";
import GeometryGenerationInputs from "./stageInputs/GeometryGenerationInputs.svelte";

export default class Core {
  isBeforeSetup = $state(true);
  setupProgress = $state(null);
  setupError = $state(null);

  progress = $state(null);
  error = $state(null);
  mesh = new Mesh();
  geometryGenerationInputs = new GeometryGenerationInputs();

  constructor() {
    this.resetAll();
  }

  resetAll() {
    this.progress = null;
    this.error = null;
    this.mesh.reset();
    this.geometryGenerationInputs.reset();
    viewportCameraInstance.reset();
  }

  setup() {
    window.pywebview.api.setup();
  }

  runGeometryGenerationStage() {
    window.pywebview.api.push_inputs({
      stage: "GeometryGenerationStage",
      imageBase64: this.geometryGenerationInputs.imageBase64,
      removeBackground: this.geometryGenerationInputs.removeBackground,
      settingsPreset: this.geometryGenerationInputs.settingsPreset,
    });
  }

  pushEvent(event) {
    switch (event.type) {
      case "error":
        this._handleErrorEvent(event.event);
        break;
      case "setupProgress":
        this._handleSetupProgressEvent(event.event);
        break;
      case "progress":
        this._handleProgressEvent(event.event);
        break;
      case "previewRembg":
        this._handlePreviewRembgEvent(event.event);
        break;
      case "previewGeometry":
        this._handlePreviewGeometryEvent(event.event);
        break;
      case "previewTexture":
        this._handlePreviewTextureEvent(event.event);
        break;
      case "exportableData":
        this._handleExportableDataEvent(event.event);
        break;
    }
  }

  _handleErrorEvent(event) {
    console.error(event);
    window.alert(
      `Oops! Looks like Meshfinity encountered an error. Please click the Chat button and report this error.\n\nError: ${event.traceback}`
    );

    if (this.isBeforeSetup || this.setupProgress) {
      // If error occurs before or during setup, we can't continue running the app
      this.setupError = event;
      this.setupProgress = null;
    } else {
      this.error = event;
      this.progress = null;
    }
  }

  _handleSetupProgressEvent(event) {
    this.setupProgress = event;
    this.isBeforeSetup = false;
  }

  _handleProgressEvent(event) {
    this.progress = event;
  }

  _handlePreviewRembgEvent(event) {
    this.mesh.rembgPreviewDataUrl = `data:image/png;base64,${event.imageBase64}`;
  }

  _handlePreviewGeometryEvent(event) {
    this.mesh.positions = new Float32Array(event.positions);
    if (event.texCoords) {
      this.mesh.texCoords = new Float32Array(event.texCoords);
    }
    this.mesh.normals = new Float32Array(event.normals);
    this.mesh.indices = new Uint32Array(event.indices);
  }

  _handlePreviewTextureEvent(event) {
    const image = new Image();
    image.addEventListener("load", () => {
      this.mesh.coarseTextureImage = image;
    });
    image.src = `data:image/png;base64,${event.imageBase64}`;
  }

  _handleExportableDataEvent(event) {
    this.mesh.exportableData = event;
  }
}
