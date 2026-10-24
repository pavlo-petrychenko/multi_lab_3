import type { MethodMetrics } from "../../api/types";
import { formatCount, formatPercent, formatPsnr, formatRatio } from "../../lib/format";
import styles from "./ImagePanel.module.css";

interface ImagePanelProps {
  title: string;
  subtitle: string;
  src: string;
  /** Metrics of a compressed result; omitted for the original image. */
  metrics?: MethodMetrics;
  /** CSS color marking the method (matches the chart lines). */
  color?: string;
  /** Highlights the method with the higher PSNR. */
  isBest?: boolean;
  onOpen: () => void;
}

/** One column of the Original | DCT | DWT comparison: image plus its metrics. */
export function ImagePanel({ title, subtitle, src, metrics, color, isBest, onOpen }: ImagePanelProps) {
  return (
    <figure className={styles.panel} style={color ? { borderTopColor: color } : undefined}>
      <figcaption className={styles.caption}>
        <div>
          <h3 className={styles.title}>{title}</h3>
          <span className={styles.subtitle}>{subtitle}</span>
        </div>
        {isBest && <span className={styles.badge}>higher PSNR</span>}
      </figcaption>

      <button type="button" className={styles.imageButton} onClick={onOpen} title="Open at full size">
        <img src={src} alt={title} className={styles.image} />
      </button>

      {metrics ? (
        <dl className={styles.metrics}>
          <div className={styles.psnr}>
            <dt>PSNR</dt>
            <dd>{formatPsnr(metrics.psnr)}</dd>
          </div>
          <div>
            <dt>Kept</dt>
            <dd>
              {formatCount(metrics.kept)} ({formatPercent(metrics.kept_ratio)})
            </dd>
          </div>
          <div>
            <dt>Ratio</dt>
            <dd>{formatRatio(metrics.compression_ratio)}</dd>
          </div>
        </dl>
      ) : (
        <dl className={styles.metrics}>
          <div className={styles.psnr}>
            <dt>Reference</dt>
            <dd>8-bit grayscale</dd>
          </div>
        </dl>
      )}
    </figure>
  );
}
