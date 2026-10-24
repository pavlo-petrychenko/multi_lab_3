import { useEffect } from "react";
import styles from "./Lightbox.module.css";

/** Image opened in the lightbox. */
export interface LightboxImage {
  src: string;
  caption: string;
}

interface LightboxProps {
  image: LightboxImage | null;
  onClose: () => void;
}

/**
 * Full-screen overlay showing one image at its native pixel size, so compression
 * artifacts (8×8 blocks, Haar steps) are clearly visible. Closes on click or Escape.
 */
export function Lightbox({ image, onClose }: LightboxProps) {
  useEffect(() => {
    if (!image) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [image, onClose]);

  if (!image) {
    return null;
  }

  return (
    <div className={styles.overlay} onClick={onClose} role="dialog" aria-modal="true" aria-label={image.caption}>
      <figure className={styles.figure}>
        <img src={image.src} alt={image.caption} className={styles.image} />
        <figcaption>{image.caption} · click or press Esc to close</figcaption>
      </figure>
    </div>
  );
}
