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

  const handleBrowseClick = () => {
    const inputEl = document.createElement("input");
    inputEl.addEventListener("change", () => {
      if (inputEl.files.length > 0) {
        const file = inputEl.files[0];
        if (file.type.indexOf("image/") !== -1) {
          handleFile(file);
        } else {
          window.alert(
            "The file you selected is not an image. Please select an image file."
          );
        }
      }

      document.body.removeChild(inputEl);
    });
    inputEl.type = "file";
    inputEl.accept = "image/*";
    inputEl.style.display = "none";
    document.body.appendChild(inputEl);
    inputEl.click();
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
  class="relative w-full h-full overflow-hidden flex flex-col items-center justify-center"
>
  <div
    class="pointer-events-none select-none grow-0 shrink-0 text-4xl font-thin mb-1"
  >
    Drag any image into this window
  </div>
  <div
    class="pointer-events-none select-none grow-0 shrink-0 text-xl font-thin mb-2"
  >
    Meshfinity will convert it to a 3D model
  </div>
  <p class="select-none grow-0 shrink-0 opacity-80 text-sm">
    ...or click to <button
      class="text-fuchsia-300 underline cursor-pointer"
      on:click={handleBrowseClick}>browse files</button
    >
  </p>
</div>
