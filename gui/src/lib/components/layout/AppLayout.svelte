<script>
  import { fade } from "svelte/transition";
  import {
    FADE_IN_DURATION,
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
  import SetupProgress from "$lib/components/layout/SetupProgress.svelte";
  import RembgPreview from "$lib/components/layout/RembgPreview.svelte";
  import EditSidebar from "$lib/components/editor/EditSidebar/EditSidebar.svelte";
  import SupportSidebar from "$lib/components/editor/SupportSidebar/SupportSidebar.svelte";
  import coreInstance from "$lib/core/coreInstance.svelte.js";

  let backgroundVisible = $state(false);
  let foregroundVisible = $state(false);

  let splashFinished = $state(false);
  let setupErrorVisible = $derived(
    foregroundVisible && !!coreInstance.setupError
  );
  let splashVisible = $derived(
    foregroundVisible &&
      !setupErrorVisible &&
      (!splashFinished ||
        coreInstance.isBeforeSetup ||
        coreInstance.setupProgress?.state === "verifying")
  );
  let setupProgressVisible = $derived(
    foregroundVisible &&
      !setupErrorVisible &&
      !splashVisible &&
      coreInstance.setupProgress
  );
  let mainVisible = $derived(
    foregroundVisible &&
      !setupErrorVisible &&
      !splashVisible &&
      !setupProgressVisible
  );

  $effect(() => {
    window.setTimeout(() => {
      backgroundVisible = true;
      window.setTimeout(() => {
        foregroundVisible = true;
      }, 300);
    }, 300);
  });

  $effect(() => {
    if (window.pywebview.api.get_audio_enabled()) {
      window.pywebview.api.enable_audio();
    }
  });

  let hasStartedIntroPlayback = $state(false);
  $effect(() => {
    if (splashVisible && !hasStartedIntroPlayback) {
      hasStartedIntroPlayback = true;
      window.setTimeout(() => {
        if (!setupErrorVisible) {
          window.pywebview.api.play_sound("intro.ogg", false);
        }
      }, 300);
    }
  });

  let hasStartedBgmPlayback = $state(false);
  $effect(() => {
    if (mainVisible && !hasStartedBgmPlayback) {
      hasStartedBgmPlayback = true;
      window.pywebview.api.play_sound("main.ogg", true);
    }
  });
</script>

<div
  class="absolute top-0 left-0 w-full h-full overflow-hidden bg-black text-white"
>
  {#if backgroundVisible}
    <div
      class="select-none absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none"
      in:fade={{ duration: FADE_IN_DURATION }}
    >
      <Canvas Renderer={BackgroundRenderer} />
    </div>
  {/if}

  {#if splashVisible}
    <div
      class="pointer-events-none select-none absolute top-0 left-0 w-full h-full overflow-hidden"
      out:fade={{ duration: FADE_OUT_DURATION }}
    >
      <Splash onAnimationFinished={() => (splashFinished = true)} />
    </div>
  {/if}

  {#if setupProgressVisible}
    <div
      class="pointer-events-none select-none absolute top-0 left-0 w-full h-full overflow-hidden"
      in:fade={customFadeIn}
      out:fade={customFadeOut}
    >
      <SetupProgress />
    </div>
  {/if}

  {#if setupErrorVisible}
    <div
      class="absolute top-0 left-0 w-full h-full overflow-hidden flex flex-col items-center justify-center"
      in:fade={customFadeIn}
      out:fade={customFadeOut}
    >
      <p class="pointer-events-none select-none text-center text-white/80">
        We&apos;re sorry, Meshfinity has encountered an error while setting up.<br
        />
        If this is your first time using Meshfinity, please ensure your device is
        connected to the internet.<br />
        Close this window and re-launch Meshfinity to try again.
      </p>
      <p class="mt-4 pointer-events-none select-none text-center text-white/50">
        If this error persists, click the &quot;Chat&quot; button in the
        bottom-right to get help.
      </p>

      <div class="absolute bottom-[24px] right-[24px] w-[160px]">
        <SupportSidebar chatOnly={true} />
      </div>
    </div>
  {/if}

  {#if mainVisible}
    <div
      class="absolute top-0 left-0 w-full h-full overflow-hidden"
      in:fade={customFadeIn}
      out:fade={customFadeOut}
    >
      <div class="absolute top-0 left-0 w-full h-full overflow-hidden">
        <Viewport />
      </div>

      {#if !coreInstance.mesh.previewReady && !coreInstance.progress}
        <div
          class="absolute top-0 left-0 w-full h-full overflow-hidden"
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
