import { useEffect, useState } from "react";
import type { ImageSource } from "./api/types";
import { SegmentedControl, type SegmentOption } from "./components/SegmentedControl";
import { CompareView } from "./features/compare/CompareView";
import { ExperimentsView } from "./features/experiments/ExperimentsView";
import { SourcePicker } from "./features/source/SourcePicker";
import { useSamples } from "./features/source/useSamples";
import styles from "./App.module.css";

type Tab = "compare" | "experiments";

const TABS: readonly SegmentOption<Tab>[] = [
  { value: "compare", label: "Compare" },
  { value: "experiments", label: "Experiments" },
];

/**
 * Root component: page header, input image picker and the two tabs.
 *
 * The selected image lives here because both tabs work on the same input.
 * The first sample is selected automatically once the list arrives.
 */
export function App() {
  const samples = useSamples();
  const [source, setSource] = useState<ImageSource | null>(null);
  const [tab, setTab] = useState<Tab>("compare");

  useEffect(() => {
    const first = samples.data?.[0];
    if (first) {
      setSource((current) => current ?? { kind: "sample", sampleId: first.id });
    }
  }, [samples.data]);

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Lossy image compression: DCT vs DWT</h1>
          <p className={styles.subtitle}>
            Lab 3 · hand-written 8×8 matrix DCT and Haar wavelet transform, compared by PSNR
          </p>
        </div>
        <SegmentedControl label="Section" options={TABS} value={tab} onChange={setTab} />
      </header>

      <main className={styles.main}>
        <SourcePicker samples={samples.data} samplesError={samples.error} source={source} onChange={setSource} />
        {tab === "compare" ? <CompareView source={source} /> : <ExperimentsView source={source} />}
      </main>
    </div>
  );
}
