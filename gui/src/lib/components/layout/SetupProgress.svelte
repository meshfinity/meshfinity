<script>
  import coreInstance from "$lib/core/coreInstance.svelte.js";
</script>

<div
  class="w-full h-full overflow-hidden flex flex-col items-center justify-center p-12"
>
  <div class="grow-0 shrink-0 text-4xl font-thin drop-shadow-xl mb-8">
    Meshfinity is setting up...
  </div>
  <div
    class="grow-0 shrink-0 w-[75%] h-[24px] rounded-lg bg-black/50 border border-fuchsia-950 overflow-hidden mb-8"
  >
    <div
      class="gel-progress-bar bg-fuchsia-900 relative absolute top-0 left-0 h-full overflow-hidden"
      style="width: {(coreInstance.setupProgress.value || 0.01) * 100.0}%;"
    >
      <div class="gel-progress-bar-inner absolute top-0 w-[144px] h-full"></div>
    </div>
  </div>
  <p class="drop-shadow-sm text-center text-sm text-white/80 mb-4">
    Meshfinity needs to download machine learning models which are too large
    (2.2 GB)<br />to be included with the application bundle. This only happens
    on first launch.
  </p>
  <div class="grow-0 shrink-0 drop-shadow-sm text-sm text-white/80">
    {coreInstance.setupProgress.label}
  </div>
</div>

<style>
  .gel-progress-bar {
    background-image: radial-gradient(
        at center top,
        #fff6 0%,
        #fff2 60%,
        #fff2 60%,
        #fff0 100%
      ),
      linear-gradient(#fff0 0%, #fff4 50%, #fff0 50%),
      radial-gradient(at center bottom, #fff0 0%, #fff0 30%, #fff3 100%);
    transition: width 0.4s;
  }

  .gel-progress-bar-inner {
    background-image: radial-gradient(
        at center top,
        #fff7 0%,
        #fff2 40%,
        #fff0 70%
      ),
      radial-gradient(at center bottom, #fff3 0%, #fff2 30%, #fff0 70%);
    transition: width 0.4s;
    animation: gel-progress-bar-inner-keyframes 6s;
    animation-iteration-count: infinite;
    animation-timing-function: linear;
  }

  @keyframes gel-progress-bar-inner-keyframes {
    0% {
      left: -144px;
    }

    100% {
      left: 100%;
    }
  }
</style>
