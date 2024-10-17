<script>
  import coreInstance from "$lib/core/coreInstance.svelte.js";
  import GeometryGenerationSection from "./GeometryGenerationSection.svelte";
  import ExportSection from "./ExportSection.svelte";
  import ResetSection from "./ResetSection.svelte";
</script>

{#if coreInstance.progress === null}
  <div
    class="w-full max-h-full bg-black/50 shadow-xl rounded-lg p-6 space-y-4 flex flex-col overflow-x-hidden overflow-y-auto"
  >
    {#if coreInstance.mesh.exportableData}
      <ExportSection />
      <ResetSection />
    {:else if coreInstance.error}
      <ResetSection />
    {:else}
      <GeometryGenerationSection />
    {/if}
  </div>
{/if}
