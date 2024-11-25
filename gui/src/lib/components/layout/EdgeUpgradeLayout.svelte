<script>
  const downloadWebView2 = () => {
    window.pywebview.api.webbrowser_open(
      "https://developer.microsoft.com/en-us/microsoft-edge/webview2"
    );
  };
</script>

<div
  class="absolute top-0 left-0 w-full h-full overflow-hidden bg-neutral-950 text-white flex flex-col items-center justify-center"
>
  <p class="text-center">
    Meshfinity requires Microsoft Edge WebView2 to run properly.<br />Please
    download and install the
    <button
      class="text-cyan-500 underline cursor-pointer"
      on:click={downloadWebView2}>WebView2 Evergreen Bootstrapper</button
    >, then close and re-open Meshfinity.
  </p>
</div>
