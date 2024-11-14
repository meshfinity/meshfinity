<script>
  import "../app.css";
</script>

<svelte:window on:contextmenu={(event) => event.preventDefault()} />

<slot />
