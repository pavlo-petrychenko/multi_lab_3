import type { CompareResponse, ExperimentsResponse, ImageSource, SampleInfo } from "./types";

/** Error thrown when the API answers with a non-2xx status. */
export class ApiError extends Error {
  /**
   * @param message Human-readable reason taken from the response body.
   * @param status HTTP status code.
   */
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Fetch a JSON endpoint under `/api` and throw {@link ApiError} on failure.
 *
 * @param path Path relative to `/api`, e.g. `/samples`.
 * @param init Standard `fetch` options.
 */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, init);
  if (!response.ok) {
    throw new ApiError(await readErrorMessage(response), response.status);
  }
  return (await response.json()) as T;
}

/**
 * Extract FastAPI's `detail` field, which is a string for HTTP errors and a list for validation errors.
 *
 * @param response Failed response.
 */
async function readErrorMessage(response: Response): Promise<string> {
  const fallback = `Request failed with status ${response.status}`;
  const body: unknown = await response.json().catch(() => null);
  if (!body || typeof body !== "object" || !("detail" in body)) {
    return fallback;
  }
  const { detail } = body as { detail: unknown };
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail.map((item: { msg?: string }) => item.msg ?? String(item)).join("; ");
  }
  return fallback;
}

/**
 * Build multipart form data with either the uploaded file or the sample id.
 *
 * @param source Selected input image.
 */
function sourceForm(source: ImageSource): FormData {
  const form = new FormData();
  if (source.kind === "upload") {
    form.append("file", source.file);
  } else {
    form.append("sample_id", source.sampleId);
  }
  return form;
}

/**
 * List bundled sample images.
 *
 * @param signal Abort signal to cancel the request.
 */
export function fetchSamples(signal?: AbortSignal): Promise<SampleInfo[]> {
  return request<SampleInfo[]>("/samples", { signal });
}

/** Parameters of a single comparison. */
export interface CompressParams {
  /** Share of coefficients to keep, in (0, 1]. */
  keepRatio: number;
  /** Haar decomposition depth. */
  dwtLevels: number;
}

/**
 * Compress the image with both methods at the same level.
 *
 * @param source Selected input image.
 * @param params Compression level and Haar depth.
 * @param signal Abort signal to cancel the request.
 */
export function compressImage(
  source: ImageSource,
  params: CompressParams,
  signal?: AbortSignal,
): Promise<CompareResponse> {
  const form = sourceForm(source);
  form.append("keep_ratio", String(params.keepRatio));
  form.append("dwt_levels", String(params.dwtLevels));
  return request<CompareResponse>("/compress", { method: "POST", body: form, signal });
}

/** Parameters of the experiment sweep. */
export interface ExperimentParams {
  /** Compression levels to test, each in (0, 1]. */
  keepRatios: number[];
  /** Haar decomposition depth. */
  dwtLevels: number;
}

/**
 * Run both methods at several compression levels.
 *
 * @param source Selected input image.
 * @param params Levels to test and Haar depth.
 * @param signal Abort signal to cancel the request.
 */
export function runExperiments(
  source: ImageSource,
  params: ExperimentParams,
  signal?: AbortSignal,
): Promise<ExperimentsResponse> {
  const form = sourceForm(source);
  params.keepRatios.forEach((ratio) => form.append("keep_ratios", String(ratio)));
  form.append("dwt_levels", String(params.dwtLevels));
  return request<ExperimentsResponse>("/experiments", { method: "POST", body: form, signal });
}
