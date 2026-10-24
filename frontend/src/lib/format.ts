/**
 * Format a PSNR value; `null` stands for identical images.
 *
 * @param psnr PSNR in dB or `null`.
 */
export function formatPsnr(psnr: number | null): string {
  return psnr === null ? "∞ dB" : `${psnr.toFixed(2)} dB`;
}

/**
 * Format a 0..1 share as a percentage with up to two significant decimals.
 *
 * @param ratio Value between 0 and 1.
 */
export function formatPercent(ratio: number): string {
  const percent = ratio * 100;
  return `${Number(percent.toPrecision(percent < 1 ? 2 : 3))}%`;
}

/**
 * Format a compression ratio as `N:1`; `null` means nothing was kept.
 *
 * @param ratio `total / kept` or `null`.
 */
export function formatRatio(ratio: number | null): string {
  return ratio === null ? "—" : `${ratio.toFixed(1)}:1`;
}

/**
 * Format an integer with thousands separators.
 *
 * @param value Integer to format.
 */
export function formatCount(value: number): string {
  return value.toLocaleString("en-US");
}
