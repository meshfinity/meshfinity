<script>
  let { checked = $bindable(), label, extraClasses } = $props();
  const inputId = `checkbox-${Math.floor(Math.random() * 999999999)}`;
</script>

<div class="{extraClasses} flex flex-row items-center justify-center space-x-2">
  <input
    class="grow-0 shrink-0 gel-hover-focus"
    id={inputId}
    type="checkbox"
    bind:checked
  />
  <label for={inputId} class="grow shrink overflow-hidden text-ellipsis"
    >{label}</label
  >
</div>

<style>
  .gel-hover-focus {
    transition: box-shadow 0.3s;
  }

  .gel-hover-focus:hover,
  .gel-hover-focus:focus {
    box-shadow: 0 0 12px #d946ef;
  }
</style>
