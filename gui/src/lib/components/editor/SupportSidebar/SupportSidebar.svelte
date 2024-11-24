<script>
  import SupportSection from "./SupportSection.svelte";

  let { chatOnly } = $props();
</script>

<div
  class="w-full max-h-full bg-black/50 shadow-xl rounded-lg px-6 py-6 space-y-4 flex flex-col overflow-x-hidden overflow-y-auto"
>
  <SupportSection {chatOnly} />
</div>
