<script>
  import Button from "$lib/components/shared/Button.svelte";
  import SpeakerXMark from "$lib/components/icons/outline/SpeakerXMark.svelte";
  import SpeakerWave from "$lib/components/icons/outline/SpeakerWave.svelte";

  let { afterUnmute } = $props();

  let isAudioEnabled = $state(null);
  const updateIsAudioEnabled = async () => {
    isAudioEnabled = await window.pywebview.api.get_audio_enabled();
  };
  $effect(() => {
    updateIsAudioEnabled();
  });

  const disableAudio = async () => {
    await window.pywebview.api.disable_audio();
    await updateIsAudioEnabled();
  };

  const enableAudio = async () => {
    await window.pywebview.api.enable_audio();
    await updateIsAudioEnabled();
    if (afterUnmute) {
      afterUnmute();
    }
  };
</script>

{#if isAudioEnabled !== null}
  <div class="absolute top-[24px] left-[24px]">
    <Button
      icon={isAudioEnabled ? SpeakerWave : SpeakerXMark}
      ariaLabel="Mute"
      extraClasses="grow-0 shrink-0 basis-0 p-2"
      style="dark"
      onClick={() => {
        if (isAudioEnabled) {
          disableAudio();
        } else {
          enableAudio();
        }
      }}
    />
  </div>
{/if}
