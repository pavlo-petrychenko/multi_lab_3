import styles from "./ErrorBanner.module.css";

/** Inline error message shown above the content that failed to load. */
export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className={styles.banner} role="alert">
      {message}
    </div>
  );
}
