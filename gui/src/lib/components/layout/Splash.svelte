<script>
  let { onAnimationFinished } = $props();

  let timeoutId = null;

  $effect(() => {
    timeoutId = window.setTimeout(() => onAnimationFinished(), 4000);
    return () => {
      if (timeoutId !== null) {
        window.clearTimeout(timeoutId);
        timeoutId = null;
      }
    };
  });
</script>

<div
  class="w-full h-full overflow-hidden flex flex-row items-center justify-center"
>
  <div
    class="grow-0 shrink-0 relative flex flex-row items-center justify-center container-animate"
  >
    <div class="grow-0 shrink-0 relative">
      <img src="logo.png" alt="Meshfinity logo" class="invisible w-32 h-32" />
      <img
        src="logo.png"
        alt="Meshfinity logo"
        class="absolute top-0 left-0 w-32 h-32 logo-icon-animate"
      />
    </div>
    <div
      class="grow-0 shrink-0 relative overflow-hidden logo-text-mask pl-[36px]"
    >
      <img src="wordmark.png" alt="Meshfinity" class="invisible h-20" />
      <img
        src="wordmark.png"
        alt="Meshfinity"
        class="absolute top-0 left-0 h-20 logo-text-animate"
      />
    </div>
  </div>
</div>

<style>
  .container-animate {
    animation: container-keyframes 1.5s forwards;
  }

  .logo-icon-animate {
    animation: icon-keyframes 1.5s forwards;
    animation-timing-function: ease-in-out;
  }

  .logo-text-animate {
    animation: text-keyframes 1.5s forwards;
    animation-delay: 0.9s;
    animation-timing-function: cubic-bezier(0.165, 0.84, 0.44, 1);
    opacity: 0;
  }

  .logo-text-mask {
    mask-image: linear-gradient(
      to right,
      transparent 0,
      transparent 2%,
      #fff 8%,
      #fff 100%
    );
  }

  @keyframes container-keyframes {
    0% {
      transform: translateX(400px);
    }

    100% {
      transform: translateX(0);
    }
  }

  @keyframes icon-keyframes {
    0% {
      transform: translate(0, 48px) scale(0.5);
      opacity: 0;
    }

    100% {
      transform: translate(0, 0) scale(1);
      opacity: 1;
    }
  }

  @keyframes text-keyframes {
    0% {
      transform: translateX(-600px) scale(0.6);
      opacity: 0;
    }

    100% {
      transform: translateX(36px) scale(1);
      opacity: 1;
    }
  }
</style>
