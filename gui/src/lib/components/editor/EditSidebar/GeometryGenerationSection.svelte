<script>
  import coreInstance from "$lib/core/coreInstance.svelte.js";
  import Checkbox from "$lib/components/shared/Checkbox.svelte";
  import Select from "$lib/components/shared/Select.svelte";

  const presetDescriptions = {
    retro: {
      bold: "Retro",
      normal:
        "mode generates low-resolution models in the style of late 90's videogames.",
    },
    balanced: {
      bold: "Balanced",
      normal:
        "mode is ideal for most users. The output mesh will appear smooth, but the polygon count will be kept low enough for manual artist modification.",
    },
    extreme: {
      bold: "X-treme",
      normal:
        "mode is slow and may be unstable, but generates a higher resolution mesh and texture.",
    },
  };
</script>

<div class="grow-0 shrink-0 w-full space-y-4 flex flex-col">
  <Checkbox
    extraClasses="grow-0 shrink-0"
    bind:checked={coreInstance.geometryGenerationInputs.removeBackground}
    label="Automatically remove background"
  />
  <Select
    extraClasses="grow-0 shrink-0 w-full"
    bind:value={coreInstance.geometryGenerationInputs.settingsPreset}
    options={[
      { value: "retro", label: "\ud83d\udc7e Retro" },
      { value: "balanced", label: "\ud83d\ude01 Balanced" },
      { value: "extreme", label: "\ud83e\udd75 X-treme" },
    ]}
  />
  <p class="text-xs">
    <span class="font-bold"
      >{presetDescriptions[coreInstance.geometryGenerationInputs.settingsPreset]
        .bold}</span
    >
    <span class="opacity-75"
      >{presetDescriptions[coreInstance.geometryGenerationInputs.settingsPreset]
        .normal}</span
    >
  </p>
</div>
