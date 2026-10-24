/** Smallest share of coefficients the slider can select (0.1 %). */
export const MIN_KEEP_RATIO = 0.001;

/** Largest share of coefficients the slider can select (100 %, lossless). */
export const MAX_KEEP_RATIO = 1;

/** Number of discrete slider positions. */
export const SLIDER_STEPS = 1000;

const LOG_MIN = Math.log10(MIN_KEEP_RATIO);
const LOG_MAX = Math.log10(MAX_KEEP_RATIO);

/**
 * Map a slider position to a keep ratio on a logarithmic scale.
 *
 * A log scale gives the interesting low range (0.1–10 %) as much room as 10–100 %.
 * The result is rounded to two significant digits so values stay readable.
 *
 * @param position Slider position in `0..SLIDER_STEPS`.
 */
export function sliderToKeepRatio(position: number): number {
  const exponent = LOG_MIN + (position / SLIDER_STEPS) * (LOG_MAX - LOG_MIN);
  return Number((10 ** exponent).toPrecision(2));
}

/**
 * Inverse of {@link sliderToKeepRatio}.
 *
 * @param ratio Keep ratio in `[MIN_KEEP_RATIO, MAX_KEEP_RATIO]`.
 */
export function keepRatioToSlider(ratio: number): number {
  return Math.round(((Math.log10(ratio) - LOG_MIN) / (LOG_MAX - LOG_MIN)) * SLIDER_STEPS);
}
