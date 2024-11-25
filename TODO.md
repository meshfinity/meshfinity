- On Windows, check if using old IE/Edge or Chromium WebView, if not Chromium then ask people to download the WebView Evergreen Installer
- Open button instead of drag-n-drop
- Audio (add dependencies to to build-mac-\*.sh and build-win.ps1)
- Replace expensive psrdnoise in shader with cheap LUT

- torch CUDA version on Windows
- rembg[gpu] could be used on CUDA devices, but not on Mac, since regular onnxruntime ships with Core ML backend
- Ensure closing app during download _actually_ stops download on Windows

```js
//
// VERY IMPORTANT:
// Ensure the audio mute button is always visible even when there is an error,
// either setup error or "normal" error
//

let hasStartedIntroPlayback = $state(false);
$effect(() => {
  if (splashVisible && !hasStartedIntroPlayback) {
    hasStartedIntroPlayback = true;
    window.setTimeout(() => {
      if (!setupErrorVisible) {
        // We can play the intro sound effect here, if there hasn't been an error
      }
    }, 300);
  }
});

// FIXME: How to ensure this happens only once intro sound playback has FINISHED ??
let hasStartedBgmPlayback = $state(false);
$effect(() => {
  if (mainVisible && !hasStartedBgmPlayback) {
    hasStartedBgmPlayback = true;
    // Start background music here
  }
});
```
