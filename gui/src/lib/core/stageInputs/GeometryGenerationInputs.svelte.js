export default class GeometryGenerationInputs {
  filename = $state(null);
  imageBase64 = $state(null);
  removeBackground = $state(true);
  settingsPreset = $state("balanced");

  reset() {
    this.filename = null;
    this.imageBase64 = null;
    // Don't reset settings - user may intend to preserve these between generations
  }
}
