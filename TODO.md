- Mute button
- Load TripoSR/etc. on start instead of when geometry generation is called first, so we don't get audio stutter

- torch CUDA version on Windows
- rembg[gpu] could be used on CUDA devices, but not on Mac, since regular onnxruntime ships with Core ML backend
- Ensure closing app during download _actually_ stops download on Windows
