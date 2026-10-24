import { useState, type FormEvent } from "react";
import type { ImageSource } from "../../api/types";
import { Card } from "../../components/Card";
import { ErrorBanner } from "../../components/ErrorBanner";
import { Lightbox, type LightboxImage } from "../../components/Lightbox";
import { SegmentedControl, type SegmentOption } from "../../components/SegmentedControl";
import { parsePercents } from "./parsePercents";
import { PsnrChart } from "./PsnrChart";
import { ResultsTable } from "./ResultsTable";
import { useExperiments } from "./useExperiments";
import styles from "./ExperimentsView.module.css";

const DEFAULT_PERCENTS = "50, 20, 10, 5, 2, 1";

const LEVEL_OPTIONS: readonly SegmentOption<number>[] = [1, 2, 3, 4, 5].map((level) => ({
  value: level,
  label: String(level),
}));

/** Second screen: run both methods at several compression levels and compare them in a table and a chart. */
export function ExperimentsView({ source }: { source: ImageSource | null }) {
  const [percentsText, setPercentsText] = useState(DEFAULT_PERCENTS);
  const [dwtLevels, setDwtLevels] = useState(3);
  const [zoomed, setZoomed] = useState<LightboxImage | null>(null);
  const { data, isLoading, error, run } = useExperiments(source);

  const parsed = parsePercents(percentsText);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (parsed.ok) {
      run({ keepRatios: parsed.ratios, dwtLevels });
    }
  };

  return (
    <div className={styles.view}>
      <Card title="Experiment setup">
        <form className={styles.form} onSubmit={onSubmit}>
          <label className={styles.field}>
            <span>Kept coefficients, % (comma-separated)</span>
            <input
              className={styles.input}
              value={percentsText}
              onChange={(event) => setPercentsText(event.target.value)}
              aria-invalid={!parsed.ok}
            />
          </label>
          <label className={styles.field}>
            <span>Haar levels</span>
            <SegmentedControl label="Haar levels" options={LEVEL_OPTIONS} value={dwtLevels} onChange={setDwtLevels} />
          </label>
          <button type="submit" className={styles.run} disabled={!parsed.ok || !source || isLoading}>
            {isLoading ? "Running…" : "Run experiments"}
          </button>
        </form>
        {!parsed.ok && <p className={styles.validation}>{parsed.message}</p>}
      </Card>

      {error && <ErrorBanner message={error} />}

      {data && (
        <>
          <Card title={`PSNR vs compression · Haar ${data.dwt_levels} level${data.dwt_levels > 1 ? "s" : ""}`}>
            <PsnrChart levels={data.levels} />
          </Card>
          <Card title="Results">
            <ResultsTable levels={data.levels} onOpenImage={setZoomed} />
            <p className={styles.note}>
              Ratio = total coefficients / non-zero coefficients. It ignores the cost of storing coefficient positions and
              entropy coding, so it is not the real file-size ratio.
            </p>
          </Card>
        </>
      )}

      <Lightbox image={zoomed} onClose={() => setZoomed(null)} />
    </div>
  );
}
