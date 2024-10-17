PYTORCH_ENABLE_MPS_FALLBACK=1 because an operation used by TripoSR is not implemented for Metal. It may still be faster than running entirely on CPU.

rembg[gpu] could be used on CUDA devices, but not on Mac, since regular onnxruntime ships with Core ML backend
Install rembg or rembg[gpu], but uninstall the rembg package itself (so only custom rembg_offline is available), but keep all the dependencies it downloaded (except pooch since we don't want it to connect to the network)

Windows: browser sniff to see if system has obsolete Edge. Display a nice page asking user to download the WebView2 runtime and restart.

Replace expensive psrdnoise in shader with cheap LUT
