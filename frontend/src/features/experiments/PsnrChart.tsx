import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ExperimentLevel } from "../../api/types";
import { formatPercent } from "../../lib/format";

/**
 * PSNR as a function of the share of kept coefficients, one line per method.
 *
 * Levels are ordered from least to most aggressive compression, so quality falls
 * from left to right. Lossless points (infinite PSNR) are left out of the lines.
 */
export function PsnrChart({ levels }: { levels: ExperimentLevel[] }) {
  const points = levels.map((level) => ({
    label: formatPercent(level.keep_ratio),
    dct: level.dct.psnr,
    dwt: level.dwt.psnr,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={points} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey="label"
          stroke="var(--text-muted)"
          fontSize={12}
          label={{ value: "kept coefficients", position: "insideBottom", offset: -4, fill: "var(--text-muted)", fontSize: 12 }}
          height={40}
        />
        <YAxis
          stroke="var(--text-muted)"
          fontSize={12}
          unit=" dB"
          width={64}
          domain={["auto", "auto"]}
        />
        <Tooltip
          formatter={(value) => (typeof value === "number" ? `${value.toFixed(2)} dB` : "∞ dB")}
          contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8 }}
        />
        <Legend verticalAlign="top" height={28} />
        <Line type="monotone" dataKey="dct" name="DCT 8×8" stroke="var(--dct)" strokeWidth={2} dot={{ r: 4 }} connectNulls />
        <Line type="monotone" dataKey="dwt" name="Haar DWT" stroke="var(--dwt)" strokeWidth={2} dot={{ r: 4 }} connectNulls />
      </LineChart>
    </ResponsiveContainer>
  );
}
