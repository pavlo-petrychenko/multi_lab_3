import { Card } from "../../components/Card";
import { SegmentedControl, type SegmentOption } from "../../components/SegmentedControl";
import { formatCount, formatPercent } from "../../lib/format";
import { SLIDER_STEPS, keepRatioToSlider, sliderToKeepRatio } from "../../lib/keepScale";
import { VIEW_OPTIONS, type ViewMode } from "./viewModes";
import styles from "./ControlsPanel.module.css";

const PRESETS = [0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005];

const LEVEL_OPTIONS: readonly SegmentOption<number>[] = [1, 2, 3, 4, 5].map((level) => ({
  value: level,
  label: String(level),
}));

interface ControlsPanelProps {
  keepRatio: number;
  onKeepRatioChange: (ratio: number) => void;
  dwtLevels: number;
  onDwtLevelsChange: (levels: number) => void;
  view: ViewMode;
  onViewChange: (view: ViewMode) => void;
  /** Total coefficient count of the current image, used to show the absolute budget. */
  totalCoefficients: number | null;
  isLoading: boolean;
}

/** Compression level slider with presets, Haar depth selector and the view switch. */
export function ControlsPanel({
  keepRatio,
  onKeepRatioChange,
  dwtLevels,
  onDwtLevelsChange,
  view,
  onViewChange,
  totalCoefficients,
  isLoading,
}: ControlsPanelProps) {
  return (
    <Card title="Compression level" actions={isLoading && <span className={styles.loading}>Computing…</span>}>
      <div className={styles.sliderRow}>
        <input
          type="range"
          min={0}
          max={SLIDER_STEPS}
          value={keepRatioToSlider(keepRatio)}
          onChange={(event) => onKeepRatioChange(sliderToKeepRatio(Number(event.target.value)))}
          className={styles.slider}
          aria-label="Share of coefficients to keep"
        />
        <div className={styles.value}>
          <strong>{formatPercent(keepRatio)}</strong>
          <span>
            {totalCoefficients
              ? `${formatCount(Math.round(totalCoefficients * keepRatio))} coefficients kept`
              : "of coefficients kept"}
          </span>
        </div>
      </div>

      <div className={styles.presets}>
        {PRESETS.map((preset) => (
          <button
            key={preset}
            type="button"
            className={preset === keepRatio ? styles.presetActive : styles.preset}
            onClick={() => onKeepRatioChange(preset)}
          >
            {formatPercent(preset)}
          </button>
        ))}
        <button type="button" className={styles.preset} onClick={() => onKeepRatioChange(1)}>
          100% (lossless)
        </button>
      </div>

      <div className={styles.row}>
        <label className={styles.field}>
          <span>Haar levels</span>
          <SegmentedControl label="Haar levels" options={LEVEL_OPTIONS} value={dwtLevels} onChange={onDwtLevelsChange} />
        </label>
        <label className={styles.field}>
          <span>Show</span>
          <SegmentedControl label="Panel content" options={VIEW_OPTIONS} value={view} onChange={onViewChange} />
        </label>
      </div>
    </Card>
  );
}
