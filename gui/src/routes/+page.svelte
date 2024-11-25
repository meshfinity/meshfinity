<script>
  import AppLayout from "$lib/components/layout/AppLayout.svelte";
  import EdgeUpgradeLayout from "$lib/components/layout/EdgeUpgradeLayout.svelte";
  import coreInstance from "$lib/core/coreInstance.svelte.js";

  let isLegacyEdge = $state(null);

  $effect(() => {
    isLegacyEdge = /edge|trident|msie/gi.test(navigator.userAgent);

    if (isLegacyEdge === false) {
      window._pywebviewCoreInstance = coreInstance;
      window.pywebview.api.check_for_updates();
      coreInstance.setup();
    }
  });
</script>

{#if isLegacyEdge === false}
  <AppLayout />
{:else if isLegacyEdge === true}
  <EdgeUpgradeLayout />
{:else}
  <!-- isLegacyEdge === null -->
{/if}
