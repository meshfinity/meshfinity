<script>
  import coreInstance from "$lib/core/coreInstance.svelte.js";
</script>

<div
  class="w-full h-full overflow-hidden flex flex-col items-start justify-end p-6 {coreInstance.progress &&
  coreInstance.mesh.previewReady
    ? 'pb-[112px]'
    : ''}"
>
  <img
    src={coreInstance.mesh.rembgPreviewDataUrl}
    class="grow-0 shrink-0 w-[192px] h-[192px] bg-black/50 backdrop-blur rounded-md shadow-xl"
    alt=""
  />
</div>
