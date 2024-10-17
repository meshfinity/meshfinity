export const FADE_OUT_DURATION = 300;
export const FADE_X_DURATION = 500;
export const FADE_IN_DURATION = 300;
export const FADE_TOTAL_DURATION =
  FADE_OUT_DURATION + FADE_X_DURATION + FADE_IN_DURATION;

export const customFadeIn = {
  duration: FADE_TOTAL_DURATION,
  easing: (x) => {
    return x < 1.0 - FADE_IN_DURATION / FADE_TOTAL_DURATION
      ? 0.0
      : (x - (FADE_OUT_DURATION + FADE_X_DURATION) / FADE_TOTAL_DURATION) *
          (FADE_TOTAL_DURATION / FADE_IN_DURATION);
  },
};

export const customFadeOut = {
  duration: FADE_OUT_DURATION,
};
