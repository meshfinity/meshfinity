<script>
  import AppLayout from "$lib/components/layout/AppLayout.svelte";
  import coreInstance from "$lib/core/coreInstance.svelte.js";

  $effect(() => {
    window._pywebviewCoreInstance = coreInstance;
  });
</script>

<AppLayout splashEnabled={true} />
