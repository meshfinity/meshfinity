<script>
  import { fade } from "svelte/transition";
  import {
    FADE_OUT_DURATION,
    customFadeIn,
    customFadeOut,
  } from "$lib/transitions/fade.js";
  import BackgroundRenderer from "$lib/renderers/BackgroundRenderer.js";
  import Canvas from "$lib/components/shared/Canvas.svelte";
  import Splash from "$lib/components/layout/Splash.svelte";
  import Viewport from "$lib/components/editor/Viewport.svelte";
  import DragNDrop from "$lib/components/layout/DragNDrop.svelte";
  import Progress from "$lib/components/layout/Progress.svelte";
  import RembgPreview from "$lib/components/layout/RembgPreview.svelte";
  import EditSidebar from "$lib/components/editor/EditSidebar/EditSidebar.svelte";
  import SupportSidebar from "$lib/components/editor/SupportSidebar/SupportSidebar.svelte";
  import coreInstance from "$lib/core/coreInstance.svelte.js";

  let { splashEnabled } = $props();

  let backgroundVisible = $state(false);
  let splashVisible = $state(false);
  let mainVisible = $state(false);

  $effect(() => {
    if (splashEnabled) {
      window.setTimeout(() => {
        backgroundVisible = true;
        window.setTimeout(() => {
          splashVisible = true;
        }, 300);
      }, 300);
    } else {
      backgroundVisible = true;
      splashVisible = false;
      mainVisible = true;
    }
  });

  function handleSplashAnimationFinished() {
    splashVisible = false;
    mainVisible = true;
  }
</script>

<div
  class="absolute top-0 left-0 w-full h-full overflow-hidden bg-black text-white"
>
  {#if backgroundVisible}
    <div
      class="select-none absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none"
      in:fade={{ duration: splashEnabled ? 300 : 0 }}
    >
      <Canvas Renderer={BackgroundRenderer} />
    </div>
  {/if}

  {#if splashVisible}
    <div
      class="pointer-events-none select-none absolute top-0 left-0 w-full h-full overflow-hidden"
      out:fade={{ duration: FADE_OUT_DURATION }}
    >
      <Splash onAnimationFinished={handleSplashAnimationFinished} />
    </div>
  {/if}

  {#if mainVisible}
    <div
      class="absolute top-0 left-0 w-full h-full overflow-hidden"
      in:fade={splashEnabled ? customFadeIn : { duration: 0 }}
      out:fade={splashEnabled ? customFadeOut : { duration: 0 }}
    >
      <div class="absolute top-0 left-0 w-full h-full overflow-hidden">
        <Viewport />
      </div>

      {#if !coreInstance.mesh.previewReady && !coreInstance.progress}
        <div
          class="pointer-events-none select-none absolute top-0 left-0 w-full h-full overflow-hidden"
          in:fade={customFadeIn}
          out:fade={customFadeOut}
        >
          <DragNDrop />
        </div>
      {/if}

      {#if coreInstance.progress}
        <div
          class="pointer-events-none select-none absolute top-0 left-0 w-full h-full overflow-hidden"
          in:fade={customFadeIn}
          out:fade={customFadeOut}
        >
          <Progress />
        </div>
      {/if}

      {#if coreInstance.mesh.rembgPreviewDataUrl}
        <div
          class="pointer-events-none select-none absolute top-0 left-0 w-full h-full overflow-hidden"
          in:fade={customFadeIn}
          out:fade={customFadeOut}
        >
          <RembgPreview />
        </div>
      {/if}

      <div class="absolute top-[24px] right-[24px] w-[320px]">
        <EditSidebar />
      </div>

      <div class="absolute bottom-[24px] right-[24px] w-[320px]">
        <SupportSidebar />
      </div>
    </div>
  {/if}
</div>
