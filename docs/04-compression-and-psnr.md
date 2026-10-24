# 4. Compression and PSNR

## The lossy step: keep the k % largest coefficients

The transforms themselves lose **nothing**. All the loss happens in one function, `core/compression.py → keep_largest(coefficients, keep_ratio)`:

1. Look at all 262,144 coefficients (the whole image, not per block).
2. Find the `k = keep_ratio × 262,144` with the **largest absolute value** (`np.argpartition`, which doesn't need a full sort).
3. Set every other coefficient to **0**.

```
coefficients:  [ 980, -3, 0.4, 41, -77, 1.2, 0.1, 15 ]
keep 25 % (2): [ 980,  0,   0,  0, -77,   0,   0,  0 ]
```

### Why this rule?

- Both transforms are orthonormal, so **the squared error in the image equals the sum of squares of the dropped coefficients**. Dropping the smallest ones gives the smallest possible error for a given count. It's optimal, not just a heuristic.
- It is **the same rule for both methods**, so at "5 %" both get exactly 13,107 numbers. That makes the comparison fair.
- It has one easy knob, `keep_ratio`, which drives the slider in the UI.

The assignment also lists thresholding, quantization and zeroing high frequencies. Ours is the "keep a fixed share of the largest" variant, and the others are close relatives:

| Method | Rule | Relation to ours |
|---|---|---|
| Thresholding | drop if `|c| < t` | ours = thresholding where `t` is picked automatically to hit k % |
| Zero high frequencies | drop the bottom-right of each DCT block | ignores the actual sizes, so it's worse for edges |
| Quantization (JPEG) | `round(c / q)` | also makes small values 0, plus coarser big values; needs entropy coding to pay off |

## Measuring quality: MSE and PSNR

**MSE** (mean squared error) is the average of `(original − reconstruction)²` over all pixels.

**PSNR** (peak signal-to-noise ratio), in decibels:

```
PSNR = 10 · log10( 255² / MSE )
```

- 255 is the largest possible pixel value.
- The log scale makes **+6 dB ≈ half the error amplitude**.
- Identical images give MSE = 0 and PSNR = ∞. The API sends `null` in that case because JSON has no infinity, and the UI shows "∞".

Rough guide:

| PSNR | What you see |
|---|---|
| > 40 dB | practically identical |
| 30–40 dB | good, artifacts visible only when zoomed in |
| 25–30 dB | clearly compressed |
| < 20 dB | badly damaged |

Before computing PSNR, the reconstruction is **rounded and clipped to 0..255** (`image_io.to_pixels`), just as a real decoder must produce valid 8-bit pixels. Code: `core/metrics.py → mse()` and `psnr()`.

**Limitation (good to mention):** PSNR measures numeric difference, not human perception. Two images with the same PSNR can look different, because blocky errors are more annoying than blurry ones. That's why the app also shows the images and error maps.

## Compression ratio and why it's not the file size

We report `compression ratio = total coefficients / non-zero coefficients`. 5 % kept gives 20:1.

A real file would be different because:

1. **Positions cost space.** For every kept coefficient you must also store *where* it was. We don't count that.
2. **Values cost bits.** A coefficient is a float. Real codecs quantize to small integers and **entropy-code** them (Huffman or arithmetic coding).
3. Zeros in long runs are cheap to encode, but not free.

So our ratio says how **sparse** the representation is, not how many bytes a file would take. The assignment asks you to state this explicitly.

## Checkpoint

- Where exactly is information lost? (Only in `keep_largest`.)
- Why is "drop the smallest" optimal for orthonormal transforms?
- Write the PSNR formula. What does 255 mean? What happens at MSE = 0?
- Why is the coefficient ratio not the real file-size ratio?
