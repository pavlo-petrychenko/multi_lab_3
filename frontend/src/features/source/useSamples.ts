import { useEffect, useState } from "react";
import { fetchSamples } from "../../api/client";
import type { SampleInfo } from "../../api/types";
import { errorMessage, idleState, type RequestState } from "../../lib/requestState";

/** Load the list of bundled sample images once on mount. */
export function useSamples(): RequestState<SampleInfo[]> {
  const [state, setState] = useState<RequestState<SampleInfo[]>>(() => ({ ...idleState(), isLoading: true }));

  useEffect(() => {
    const controller = new AbortController();
    fetchSamples(controller.signal)
      .then((data) => setState({ data, isLoading: false, error: null }))
      .catch((error: unknown) => {
        if (!controller.signal.aborted) {
          setState({ data: null, isLoading: false, error: errorMessage(error) });
        }
      });
    return () => controller.abort();
  }, []);

  return state;
}
