<script>
  import Button from "$lib/components/shared/Button.svelte";
  import ArrowPath from "$lib/components/icons/outline/ArrowPath.svelte";
  import coreInstance from "$lib/core/coreInstance.svelte.js";
</script>

<div class="grow-0 shrink-0 w-full space-y-4 flex flex-col">
  <Button
    icon={ArrowPath}
    label="Reset"
    extraClasses="w-full grow-0 shrink-0 p-2"
    onClick={() => coreInstance.resetAll()}
  />
</div>
