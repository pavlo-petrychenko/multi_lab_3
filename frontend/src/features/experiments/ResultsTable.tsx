import type { ExperimentLevel, ExperimentMethodResult } from "../../api/types";
import type { LightboxImage } from "../../components/Lightbox";
import { formatCount, formatPercent, formatPsnr, formatRatio } from "../../lib/format";
import styles from "./ResultsTable.module.css";

interface ResultsTableProps {
  levels: ExperimentLevel[];
  onOpenImage: (image: LightboxImage) => void;
}

/**
 * Compare PSNR values treating `null` (lossless) as infinity.
 *
 * @returns `true` when `a` is strictly better than `b`.
 */
function isBetter(a: ExperimentMethodResult, b: ExperimentMethodResult): boolean {
  return (a.psnr ?? Infinity) > (b.psnr ?? Infinity);
}

/** Experiment results: one row per compression level with metrics and thumbnails of both methods. */
export function ResultsTable({ levels, onOpenImage }: ResultsTableProps) {
  return (
    <div className={styles.wrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Kept</th>
            <th>Coefficients</th>
            <th>Ratio</th>
            <th className={styles.dct}>DCT PSNR</th>
            <th className={styles.dwt}>DWT PSNR</th>
            <th>DCT</th>
            <th>DWT</th>
          </tr>
        </thead>
        <tbody>
          {levels.map((level) => {
            const percent = formatPercent(level.keep_ratio);
            return (
              <tr key={level.keep_ratio}>
                <td>{percent}</td>
                <td>
                  {formatCount(level.dct.kept)} / {formatCount(level.dct.total)}
                </td>
                <td>{formatRatio(level.dct.compression_ratio)}</td>
                <td className={isBetter(level.dct, level.dwt) ? styles.best : undefined}>
                  {formatPsnr(level.dct.psnr)}
                </td>
                <td className={isBetter(level.dwt, level.dct) ? styles.best : undefined}>
                  {formatPsnr(level.dwt.psnr)}
                </td>
                <td>
                  <button
                    type="button"
                    className={styles.thumbButton}
                    onClick={() => onOpenImage({ src: level.dct.image, caption: `DCT · kept ${percent}` })}
                  >
                    <img src={level.dct.image} alt={`DCT at ${percent}`} className={styles.thumb} />
                  </button>
                </td>
                <td>
                  <button
                    type="button"
                    className={styles.thumbButton}
                    onClick={() => onOpenImage({ src: level.dwt.image, caption: `DWT · kept ${percent}` })}
                  >
                    <img src={level.dwt.image} alt={`DWT at ${percent}`} className={styles.thumb} />
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
