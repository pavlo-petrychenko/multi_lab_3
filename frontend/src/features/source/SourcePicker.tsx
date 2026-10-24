import { useRef, type ChangeEvent, type DragEvent } from "react";
import type { ImageSource, SampleInfo } from "../../api/types";
import { Card } from "../../components/Card";
import { ErrorBanner } from "../../components/ErrorBanner";
import styles from "./SourcePicker.module.css";

interface SourcePickerProps {
  samples: SampleInfo[] | null;
  samplesError: string | null;
  source: ImageSource | null;
  onChange: (source: ImageSource) => void;
}

/**
 * Lets the user choose the input image: one of the bundled samples or an own file.
 * Any uploaded image is converted to 512×512 grayscale by the server.
 */
export function SourcePicker({ samples, samplesError, source, onChange }: SourcePickerProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const selectFile = (file: File | undefined) => {
    if (file) {
      onChange({ kind: "upload", file });
    }
  };

  const onInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    selectFile(event.target.files?.[0]);
    event.target.value = "";
  };

  const onDrop = (event: DragEvent<HTMLButtonElement>) => {
    event.preventDefault();
    selectFile(event.dataTransfer.files[0]);
  };

  return (
    <Card title="Input image">
      {samplesError && <ErrorBanner message={`Could not load samples: ${samplesError}`} />}
      <div className={styles.options}>
        {samples?.map((sample) => {
          const isSelected = source?.kind === "sample" && source.sampleId === sample.id;
          return (
            <button
              key={sample.id}
              type="button"
              className={isSelected ? styles.selected : styles.option}
              onClick={() => onChange({ kind: "sample", sampleId: sample.id })}
            >
              <img src={sample.thumbnail} alt="" className={styles.thumbnail} />
              <span>{sample.name}</span>
            </button>
          );
        })}
        <button
          type="button"
          className={source?.kind === "upload" ? styles.selectedUpload : styles.upload}
          onClick={() => inputRef.current?.click()}
          onDragOver={(event) => event.preventDefault()}
          onDrop={onDrop}
        >
          <span className={styles.uploadIcon} aria-hidden>
            +
          </span>
          <span className={styles.uploadName}>{source?.kind === "upload" ? source.file.name : "Upload or drop"}</span>
        </button>
        <input ref={inputRef} type="file" accept="image/*" hidden onChange={onInputChange} />
      </div>
      <p className={styles.hint}>Images are converted to grayscale, center-cropped and resized to 512×512.</p>
    </Card>
  );
}
