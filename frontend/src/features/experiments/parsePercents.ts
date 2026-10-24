/** Result of parsing the compression-levels text field. */
export type ParsedPercents = { ok: true; ratios: number[] } | { ok: false; message: string };

/**
 * Parse a list like `"50, 20, 10, 5"` (percent of kept coefficients) into ratios in (0, 1].
 *
 * Duplicates are removed and the result is sorted from least to most aggressive.
 *
 * @param text Comma- or space-separated percentages.
 */
export function parsePercents(text: string): ParsedPercents {
  const parts = text.split(/[\s,;]+/).filter(Boolean);
  if (parts.length === 0) {
    return { ok: false, message: "Enter at least one percentage." };
  }

  const percents = parts.map(Number);
  const invalid = parts.filter((_, index) => !(percents[index] > 0 && percents[index] <= 100));
  if (invalid.length > 0) {
    return { ok: false, message: `Invalid value(s): ${invalid.join(", ")}. Use numbers in (0, 100].` };
  }

  const ratios = [...new Set(percents)].sort((a, b) => b - a).map((percent) => percent / 100);
  return { ok: true, ratios };
}
