import { useEffect, useState } from "react";

/**
 * Return `value` only after it stopped changing for `delayMs`.
 *
 * Used so dragging the slider sends one request when the user pauses
 * instead of one request per pixel of movement.
 *
 * @param value Rapidly changing value.
 * @param delayMs Quiet period in milliseconds.
 */
export function useDebouncedValue<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delayMs);
    return () => window.clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
