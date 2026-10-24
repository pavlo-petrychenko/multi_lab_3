import { useCallback, useEffect, useRef, useState } from "react";
import { runExperiments, type ExperimentParams } from "../../api/client";
import type { ExperimentsResponse, ImageSource } from "../../api/types";
import { errorMessage, idleState, type RequestState } from "../../lib/requestState";

/** Request state of the sweep plus a function that starts it. */
export interface ExperimentsController extends RequestState<ExperimentsResponse> {
  run: (params: ExperimentParams) => void;
}

/**
 * Run the multi-level experiment sweep on demand.
 *
 * Results are cleared when the source image changes, because they would no
 * longer describe the selected image. Starting a new run aborts the previous one.
 *
 * @param source Selected input image.
 */
export function useExperiments(source: ImageSource | null): ExperimentsController {
  const [state, setState] = useState<RequestState<ExperimentsResponse>>(idleState);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    controllerRef.current?.abort();
    setState(idleState());
  }, [source]);

  useEffect(() => () => controllerRef.current?.abort(), []);

  const run = useCallback(
    (params: ExperimentParams) => {
      if (!source) {
        return;
      }
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      setState((previous) => ({ ...previous, isLoading: true, error: null }));

      runExperiments(source, params, controller.signal)
        .then((data) => setState({ data, isLoading: false, error: null }))
        .catch((error: unknown) => {
          if (!controller.signal.aborted) {
            setState((previous) => ({ ...previous, isLoading: false, error: errorMessage(error) }));
          }
        });
    },
    [source],
  );

  return { ...state, run };
}
