<script>
  import AppLayout from "$lib/components/layout/AppLayout.svelte";
  import EdgeUpgradeLayout from "$lib/components/layout/EdgeUpgradeLayout.svelte";
  import coreInstance from "$lib/core/coreInstance.svelte.js";

  let isLegacyEdge = $state(null);
  let alreadyInitialized = $state(false);

  $effect(() => {
    isLegacyEdge = /edge|trident|msie/gi.test(navigator.userAgent);

    if (!alreadyInitialized && isLegacyEdge === false) {
      alreadyInitialized = true;
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
