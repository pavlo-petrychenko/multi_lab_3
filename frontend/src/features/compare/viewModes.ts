import type { SegmentOption } from "../../components/SegmentedControl";

/** What the DCT and DWT panels display. */
export type ViewMode = "image" | "coefficients" | "error";

/** Options for the view switch. */
export const VIEW_OPTIONS: readonly SegmentOption<ViewMode>[] = [
  { value: "image", label: "Reconstruction" },
  { value: "coefficients", label: "Coefficients" },
  { value: "error", label: "Error ×5" },
];

/** One-line explanation of each view, shown under the panels. */
export const VIEW_DESCRIPTIONS: Record<ViewMode, string> = {
  image: "Images decoded from the kept coefficients only.",
  coefficients:
    "log(1 + |c|) of the kept coefficients; black = dropped. DCT shows one 8×8 spectrum per block, DWT shows the LL / HL / LH / HH sub-band pyramid.",
  error: "|original − reconstruction| × 5; brighter = larger error. DCT errors follow the 8×8 grid, DWT errors follow edges.",
};
