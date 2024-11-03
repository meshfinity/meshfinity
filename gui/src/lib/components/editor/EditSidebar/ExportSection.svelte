<script>
  import coreInstance from "$lib/core/coreInstance.svelte.js";
  import Button from "$lib/components/shared/Button.svelte";
  import ArrowDownTray from "$lib/components/icons/outline/ArrowDownTray.svelte";

  function handleExport() {
    const defaultFilenameParts =
      coreInstance.geometryGenerationInputs.filename.split(".");
    defaultFilenameParts.pop();
    const defaultFilename = defaultFilenameParts.join(".").replace(/\s/g, "_");
    window.pywebview.api.export_data(
      coreInstance.mesh.exportableData,
      defaultFilename + ".obj"
    );
  }
</script>

<div class="grow-0 shrink-0 w-full space-y-4 flex flex-col">
  <Button
    icon={ArrowDownTray}
    label="Export"
    style="accent"
    extraClasses="w-full grow-0 shrink-0 p-2"
    onClick={handleExport}
  />
</div>
