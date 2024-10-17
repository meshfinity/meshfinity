<script>
  let {
    icon,
    label,
    active,
    disabled,
    onClick,
    style = "default",
    extraClasses,
  } = $props();

  const stylePresets = {
    default: {
      colors: {
        default: "bg-neutral-400 text-black gel-hover-focus",
        disabled: "bg-neutral-950",
      },
      gel: {
        default: "opacity-100",
        disabled: "opacity-0",
        extraBright: true,
      },
      rounded: "rounded-full",
    },
    accent: {
      colors: {
        default: "bg-fuchsia-700 gel-accent-hover-focus",
        disabled: "bg-fuchsia-950",
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

<button
  class="{extraClasses} overflow-hidden relative transition-colors group {colorsStyles} {stylePresets[
    style
  ].rounded}"
  {disabled}
  onclick={onClick}
>
  <div
    class="pointer-events-none select-none absolute top-0 left-0 w-full h-full {stylePresets[
      style
    ].gel.extraBright
      ? 'gel-image-extra-bright'
      : 'gel-image'} transition-opacity {gelStyles}"
  ></div>

  <div
    class="select-none relative w-full h-full flex flex-row items-center justify-center space-x-2"
  >
    {#if icon}
      <div class="grow-0 shrink-0">
        <svelte:component this={icon} />
      </div>
    {/if}
    <div class="grow-0 shrink-0 font-medium">{label}</div>
  </div>
</button>

<style>
  .gel-image {
    background-image: radial-gradient(
        at center top,
        #fff6 0%,
        #fff2 60%,
        #fff2 60%,
        #fff0 100%
      ),
      linear-gradient(#fff0 0%, #fff3 50%, #fff0 50%),
      radial-gradient(at center bottom, #fff0 0%, #fff0 30%, #fff5 100%);
  }

  .gel-image-extra-bright {
    background-image: radial-gradient(
        at center top,
        #fffa 0%,
        #fff2 60%,
        #fff2 60%,
        #fff0 100%
      ),
      linear-gradient(#fff0 0%, #fff5 50%, #fff0 50%),
      radial-gradient(at center bottom, #fff0 0%, #fff0 30%, #fff9 100%);
  }

  .gel-hover-focus,
  .gel-accent-hover-focus {
    transition: box-shadow 0.3s;
  }

  .gel-hover-focus:hover,
  .gel-hover-focus:focus {
    box-shadow: 0 0 12px #fff;
  }

  .gel-accent-hover-focus:hover,
  .gel-accent-hover-focus:focus {
    box-shadow: 0 0 12px #d946ef;
  }
</style>
