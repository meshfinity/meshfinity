<script>
  import { onMount } from "svelte";
  import "../app.css";

  onMount(() => {
    window.pywebview.api.check_for_updates();
  });
</script>

<svelte:window on:contextmenu={(event) => event.preventDefault()} />

<slot />
