<script>
  import Button from "$lib/components/shared/Button.svelte";
  import ChatBubbleOvalLeft from "$lib/components/icons/outline/ChatBubbleOvalLeft.svelte";
  import Heart from "$lib/components/icons/outline/Heart.svelte";
</script>

<div class="grow-0 shrink-0 w-full space-y-4 flex flex-col">
  <div
    class="grow-0 shrink-0 w-full flex flex-row items-center justify-center space-x-2"
  >
    <Button
      icon={ChatBubbleOvalLeft}
      label="Chat"
      extraClasses="grow shrink basis-0 p-2"
      onClick={() =>
        window.pywebview.api.webbrowser_open("https://www.meshfinity.com/chat")}
    />
    <Button
      icon={Heart}
      label="Donate"
      extraClasses="grow shrink basis-0 p-2"
      onClick={() =>
        window.pywebview.api.webbrowser_open(
          "https://www.meshfinity.com/donate"
        )}
    />
  </div>
</div>
