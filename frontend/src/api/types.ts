/**
 * TypeScript mirrors of the backend response schemas (`backend/app/api/schemas.py`).
 * Field names keep the backend's snake_case so the two files can be compared line by line.
 */

/** Identifier of a compression method. */
export type MethodId = "dct" | "dwt";

/** A bundled sample image. */
export interface SampleInfo {
  id: string;
  name: string;
  /** PNG data URL of the prepared grayscale image. */
  thumbnail: string;
}

/** Size and quality numbers of one compression result. */
export interface MethodMetrics {
  /** Number of non-zero coefficients after compression. */
  kept: number;
  /** Total number of coefficients. */
  total: number;
  /** `kept / total`, between 0 and 1. */
  kept_ratio: number;
  /** PSNR in dB; `null` means the images are identical (infinite PSNR). */
  psnr: number | null;
  /** `total / kept`; `null` when nothing was kept. */
  compression_ratio: number | null;
}

/** One method's output in the comparison view. */
export interface MethodResult extends MethodMetrics {
  /** Reconstructed image. */
  image: string;
  /** Log-magnitude coefficient map. */
  coefficients: string;
  /** Amplified absolute error map. */
  error: string;
}

/** Response of `POST /api/compress`. */
export interface CompareResponse {
  original: string;
  width: number;
  height: number;
  keep_ratio: number;
  dwt_levels: number;
  dct: MethodResult;
  dwt: MethodResult;
}

/** One method's output in a single experiment row. */
export interface ExperimentMethodResult extends MethodMetrics {
  image: string;
}

/** DCT and DWT results at one compression level. */
export interface ExperimentLevel {
  keep_ratio: number;
  dct: ExperimentMethodResult;
  dwt: ExperimentMethodResult;
}

/** Response of `POST /api/experiments`. */
export interface ExperimentsResponse {
  original: string;
  dwt_levels: number;
  levels: ExperimentLevel[];
}

/** Where the input image comes from: a bundled sample or a user upload. */
export type ImageSource = { kind: "sample"; sampleId: string } | { kind: "upload"; file: File };
