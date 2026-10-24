import { useState } from "react";
import type { ImageSource, MethodId, MethodResult } from "../../api/types";
import { ErrorBanner } from "../../components/ErrorBanner";
import { Lightbox, type LightboxImage } from "../../components/Lightbox";
import { ControlsPanel } from "./ControlsPanel";
import { ImagePanel } from "./ImagePanel";
import { useCompression } from "./useCompression";
import { VIEW_DESCRIPTIONS, VIEW_OPTIONS, type ViewMode } from "./viewModes";
import styles from "./CompareView.module.css";

const DEFAULT_KEEP_RATIO = 0.05;
const DEFAULT_DWT_LEVELS = 3;

/**
 * Pick the method with the strictly higher PSNR, treating `null` (lossless) as infinity.
 *
 * @returns The better method, or `null` on a tie.
 */
function bestMethod(dct: MethodResult, dwt: MethodResult): MethodId | null {
  const dctPsnr = dct.psnr ?? Infinity;
  const dwtPsnr = dwt.psnr ?? Infinity;
  if (dctPsnr === dwtPsnr) {
    return null;
  }
  return dctPsnr > dwtPsnr ? "dct" : "dwt";
}

/** Main screen: live Original | DCT | DWT comparison at an adjustable compression level. */
export function CompareView({ source }: { source: ImageSource | null }) {
  const [keepRatio, setKeepRatio] = useState(DEFAULT_KEEP_RATIO);
  const [dwtLevels, setDwtLevels] = useState(DEFAULT_DWT_LEVELS);
  const [view, setView] = useState<ViewMode>("image");
  const [zoomed, setZoomed] = useState<LightboxImage | null>(null);
  const { data, isLoading, error } = useCompression(source, keepRatio, dwtLevels);

  const best = data && bestMethod(data.dct, data.dwt);
  const viewLabel = VIEW_OPTIONS.find((option) => option.value === view)?.label ?? "";

  return (
    <div className={styles.view}>
      <ControlsPanel
        keepRatio={keepRatio}
        onKeepRatioChange={setKeepRatio}
        dwtLevels={dwtLevels}
        onDwtLevelsChange={setDwtLevels}
        view={view}
        onViewChange={setView}
        totalCoefficients={data ? data.dct.total : null}
        isLoading={isLoading}
      />

      {error && <ErrorBanner message={error} />}

      {data && (
        <>
          <div className={isLoading ? styles.gridLoading : styles.grid}>
            <ImagePanel
              title="Original"
              subtitle={`${data.width}×${data.height} px`}
              src={data.original}
              onOpen={() => setZoomed({ src: data.original, caption: "Original" })}
            />
            <ImagePanel
              title="DCT"
              subtitle="8×8 blocks, matrix form"
              src={data.dct[view]}
              metrics={data.dct}
              color="var(--dct)"
              isBest={best === "dct"}
              onOpen={() => setZoomed({ src: data.dct[view], caption: `DCT · ${viewLabel}` })}
            />
            <ImagePanel
              title="DWT"
              subtitle={`Haar, ${data.dwt_levels} level${data.dwt_levels > 1 ? "s" : ""}`}
              src={data.dwt[view]}
              metrics={data.dwt}
              color="var(--dwt)"
              isBest={best === "dwt"}
              onOpen={() => setZoomed({ src: data.dwt[view], caption: `DWT · ${viewLabel}` })}
            />
          </div>
          <p className={styles.note}>{VIEW_DESCRIPTIONS[view]} Click an image to open it at full size.</p>
        </>
      )}

      <Lightbox image={zoomed} onClose={() => setZoomed(null)} />
    </div>
  );
}
