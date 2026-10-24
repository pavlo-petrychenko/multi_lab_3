import { useEffect, useState } from "react";
import { compressImage } from "../../api/client";
import type { CompareResponse, ImageSource } from "../../api/types";
import { errorMessage, idleState, type RequestState } from "../../lib/requestState";
import { useDebouncedValue } from "../../lib/useDebouncedValue";

const DEBOUNCE_MS = 200;

/**
 * Keep the Original | DCT | DWT comparison in sync with the selected parameters.
 *
 * Every change of source, level or depth triggers a new request; the slider value is
 * debounced and any outdated request is aborted, so only the latest result is shown.
 * The previous result stays visible while the next one is loading.
 *
 * @param source Selected input image, or `null` before anything is selected.
 * @param keepRatio Share of coefficients to keep, in (0, 1].
 * @param dwtLevels Haar decomposition depth.
 */
export function useCompression(
  source: ImageSource | null,
  keepRatio: number,
  dwtLevels: number,
): RequestState<CompareResponse> {
  const debouncedKeepRatio = useDebouncedValue(keepRatio, DEBOUNCE_MS);
  const [state, setState] = useState<RequestState<CompareResponse>>(idleState);

  useEffect(() => {
    if (!source) {
      return;
    }
    const controller = new AbortController();
    setState((previous) => ({ ...previous, isLoading: true, error: null }));

    compressImage(source, { keepRatio: debouncedKeepRatio, dwtLevels }, controller.signal)
      .then((data) => setState({ data, isLoading: false, error: null }))
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setState((previous) => ({ ...previous, isLoading: false, error: errorMessage(error) }));
        }
      });

    return () => controller.abort();
  }, [source, debouncedKeepRatio, dwtLevels]);

  return state;
}
