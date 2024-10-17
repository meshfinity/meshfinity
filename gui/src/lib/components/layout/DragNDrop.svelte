<script>
  import coreInstance from "$lib/core/coreInstance.svelte.js";

  const handleFile = (file) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => {
      coreInstance.geometryGenerationInputs.filename = file.name;
      coreInstance.geometryGenerationInputs.imageBase64 =
        reader.result.split(",")[1];
      coreInstance.runGeometryGenerationStage();
    });
    reader.readAsDataURL(file);
  };
</script>

<svelte:window
  on:dragover={(event) => {
    event.preventDefault();
    event.stopPropagation();
  }}
  on:drop={(event) => {
    event.preventDefault();
    event.stopPropagation();

    for (const item of event.dataTransfer.items) {
      if (item.kind === "file") {
        const file = item.getAsFile();
        if (file.type.indexOf("image/") !== -1) {
          handleFile(file);
          return;
        }
      }
    }

    for (const file of event.dataTransfer.files) {
      if (file.type.indexOf("image/") !== -1) {
        handleFile(file);
        return;
      }
    }
  }}
/>

<div
  class="relative w-full h-full overflow-hidden flex flex-col items-center justify-center space-y-1"
>
  <div class="grow-0 shrink-0 text-4xl font-thin">
    Drag any image into this window
  </div>
  <div class="grow-0 shrink-0 text-xl font-thin opacity-75">
    Meshfinity will convert it to a 3D model
  </div>
</div>
