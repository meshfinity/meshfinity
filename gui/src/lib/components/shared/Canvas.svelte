<script>
  let { Renderer, controlsEnabled } = $props();

  let canvas = $state(null);
  let canvasClientWidth = $state(0),
    canvasClientHeight = $state(0);
  let devicePixelRatio = $state(0);
  let canvasWidth = $derived(canvasClientWidth * devicePixelRatio);
  let canvasHeight = $derived(canvasClientHeight * devicePixelRatio);

  let gl = null;
  let renderer = null;
  let animationFrame = null;

  let activePointerId = null;
  let prevPointerX = null,
    prevPointerY = null;

  const init = () => {
    gl = canvas.getContext("webgl2");
    renderer = new Renderer(canvas, gl);
    animationFrame = window.requestAnimationFrame(animate);
  };

  const destroy = () => {
    if (animationFrame !== null) {
      window.cancelAnimationFrame(animationFrame);
    }
    animationFrame = null;
    renderer = null;
    gl = null;
  };

  const animate = () => {
    if (animationFrame === null) {
      return;
    }

    animationFrame = window.requestAnimationFrame(animate);

    if (renderer) {
      renderer.render();
    }
  };

  $effect(() => {
    init();
    return () => {
      destroy();
    };
  });
</script>

<svelte:window bind:devicePixelRatio />

<canvas
  bind:this={canvas}
  class="w-full h-full"
  bind:clientWidth={canvasClientWidth}
  bind:clientHeight={canvasClientHeight}
  width={canvasWidth}
  height={canvasHeight}
  onpointerdown={(event) => {
    event.preventDefault();
    event.stopPropagation();

    if (activePointerId !== null) {
      return;
    }

    activePointerId = event.pointerId;
    const bounds = canvas.getBoundingClientRect();
    const x = event.clientX - bounds.x;
    const y = event.clientY - bounds.y;
    prevPointerX = x;
    prevPointerY = y;

    if (controlsEnabled && renderer?.onPointerDown) {
      renderer.onPointerDown({ x, y, dx: 0, dy: 0 });
    }
  }}
  onpointermove={(event) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.pointerId !== activePointerId) {
      return;
    }

    if (controlsEnabled && renderer?.onPointerMove) {
      const bounds = canvas.getBoundingClientRect();
      const x = event.clientX - bounds.x;
      const y = event.clientY - bounds.y;
      renderer.onPointerMove({
        x,
        y,
        dx: x - prevPointerX,
        dy: y - prevPointerY,
      });
      prevPointerX = x;
      prevPointerY = y;
    }
  }}
  onpointerup={(event) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.pointerId !== activePointerId) {
      return;
    }

    if (controlsEnabled && renderer?.onPointerUp) {
      const bounds = canvas.getBoundingClientRect();
      const x = event.clientX - bounds.x;
      const y = event.clientY - bounds.y;
      renderer.onPointerUp({
        x,
        y,
        dx: x - prevPointerX,
        dy: y - prevPointerY,
      });
    }

    activePointerId = null;
    prevPointerX = null;
    prevPointerY = null;
  }}
  onwheel={(event) => {
    event.preventDefault();
    event.stopPropagation();

    if (controlsEnabled && renderer?.onWheel) {
      renderer.onWheel({
        deltaY: event.deltaY,
      });
    }
  }}
></canvas>
