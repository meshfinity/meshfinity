<script>
  import Canvas from "$lib/components/shared/Canvas.svelte";
  import ViewportRenderer from "$lib/renderers/ViewportRenderer.svelte.js";
  import coreInstance from "$lib/core/coreInstance.svelte.js";
</script>

<Canvas
  Renderer={ViewportRenderer}
  controlsEnabled={coreInstance.mesh.positions && coreInstance.mesh.indices}
/>
