<script>
  import ChevronDown from "$lib/components/icons/outline/ChevronDown.svelte";

  let {
    value = $bindable(),
    options,
    active,
    disabled,
    style = "default",
    extraClasses,
  } = $props();

  const stylePresets = {
    default: {
      colors: {
        default: "bg-fuchsia-950 text-white gel-hover-focus",
        disabled: "bg-neutral-950 text-neutral-500",
      },
      gel: {
        default: "opacity-100",
        disabled: "opacity-0",
      },
      rounded: "rounded-full",
    },
  };

  let colorsStyles = $state("");
  let gelStyles = $state("");
  $effect(() => {
    if (disabled) {
      colorsStyles = stylePresets[style].colors.disabled;
      gelStyles = stylePresets[style].gel.disabled;
    } else if (active) {
      colorsStyles = stylePresets[style].colors.active;
      gelStyles = stylePresets[style].gel.active;
    } else {
      colorsStyles = stylePresets[style].colors.default;
      gelStyles = stylePresets[style].gel.default;
    }
  });
</script>

<div
  class="{extraClasses} overflow-hidden relative transition-colors group {colorsStyles} {stylePresets[
    style
  ].rounded}"
>
  <div
    class="pointer-events-none select-none absolute top-0 left-0 w-full h-full {stylePresets[
      style
    ].gel.extraBright
      ? 'gel-image-extra-bright'
      : 'gel-image'} transition-opacity {gelStyles}"
  ></div>

  <div
    class="pointer-events-none select-none absolute top-1/2 right-2 -translate-y-1/2 w-5 h-5 flex items-center justify-center"
  >
    <ChevronDown />
  </div>

  <select
    class="overflow-hidden bg-transparent text-inherit px-3 py-1 w-full h-full"
    {disabled}
    bind:value
  >
    {#each options as option}
      <option class="bg-black text-white" value={option.value}
        >{option.label}</option
      >
    {/each}
  </select>
</div>

<style>
  .gel-image {
    background-image: radial-gradient(
        at center top,
        #fff3 0%,
        #fff1 60%,
        #fff1 60%,
        #fff0 100%
      ),
      linear-gradient(#fff0 0%, #fff3 50%, #fff0 50%),
      radial-gradient(at center bottom, #fff0 0%, #fff0 30%, #fff1 100%);
  }

  .gel-hover-focus {
    transition: box-shadow 0.3s;
  }

  .gel-hover-focus:hover,
  .gel-hover-focus:has(*:focus) {
    box-shadow: 0 0 12px #d946ef;
  }
</style>
