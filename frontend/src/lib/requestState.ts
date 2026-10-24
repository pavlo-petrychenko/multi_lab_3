/** State of an asynchronous request as seen by a component. */
export interface RequestState<T> {
  /** Last successful response; kept while a new request is in flight. */
  data: T | null;
  isLoading: boolean;
  /** Message of the last failure, cleared on the next attempt. */
  error: string | null;
}

/** Initial state before any request was made. */
export function idleState<T>(): RequestState<T> {
  return { data: null, isLoading: false, error: null };
}

/**
 * Turn anything thrown into a displayable message.
 *
 * @param error Value caught in a `catch`.
 */
export function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}
