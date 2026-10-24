# 5. DCT vs DWT

## Side by side

| | DCT (ours: 8×8 blocks) | Haar DWT (ours: 1–5 levels) |
|---|---|---|
| Basis | smooth cosine waves | step-shaped "average/difference" functions |
| Works on | independent 8×8 blocks | the whole image, at several scales |
| Knows *what* frequency | yes, very precisely | roughly (per level) |
| Knows *where* it is | only to the nearest block | yes, edges stay localised |
| Typical artifact | **blocking**: a visible 8×8 grid, plus ringing near edges | **blockiness of varying size** (Haar is piecewise constant), no fixed grid |
| Used in | JPEG, MPEG, H.26x video | JPEG 2000 (with smoother wavelets such as CDF 9/7) |

## Our measured results (cameraman, 512×512)

Haar with 3 levels:

| Kept | Ratio | DCT PSNR | DWT PSNR |
|---:|---:|---:|---:|
| 50 % | 2:1 | 54.08 | 53.60 |
| 20 % | 5:1 | 39.70 | 39.44 |
| 10 % | 10:1 | 34.22 | 33.78 |
| 5 % | 20:1 | 30.91 | 30.35 |
| 2 % | 50:1 | 26.83 | 26.08 |
| 1 % | 100:1 | 16.24 | 16.24 |

Regenerate it with `uv run python -m scripts.run_experiments`; the output also includes `reports/psnr.png`, which plots every Haar depth.

Effect of Haar depth at strong compression:

| Kept | DCT | Haar 1 level | Haar 3 levels | Haar 5 levels |
|---:|---:|---:|---:|---:|
| 10 % | 34.2 | 10.0 | 33.8 | 34.2 |
| 2 % | 26.8 | 5.5 | 26.1 | **28.1** |
| 1 % | 16.2 | 5.1 | 16.2 | **26.3** |
| 0.5 % | 8.6 | 4.9 | 8.6 | **24.5** |

## How to read these numbers

1. **At moderate compression (≥ 2 %)** DCT and Haar-3 are within ~0.5 dB of each other, with DCT slightly ahead. Cosines are smooth, and smooth bases fit natural images a bit better than Haar's hard steps.

2. **The "1 % cliff".** At 1 % both drop to *exactly* 16.24 dB. This isn't a coincidence:
   - The DCT has 64×64 = **4,096 DC coefficients** (one per block), and each one is `8 × block average`.
   - Haar with 3 levels has a 64×64 LL corner, also **4,096 numbers**, each one `2³ × average of an 8×8 patch`. *They're the same numbers.*
   - 1 % of 262,144 is **2,621 < 4,096**, so neither method can even keep every block's average brightness. Whole blocks turn black, and both methods lose exactly the same blocks.

3. **More Haar levels win at extreme compression.** With 5 levels the "average" part shrinks to 16×16 = 256 numbers, so the budget is enough for the coarse picture *and* the most important edges. At 0.5 % Haar-5 gives **24.5 dB vs 8.6 dB** for DCT. This is the multi-resolution advantage of wavelets, and the reason JPEG 2000 degrades more gracefully than JPEG.

4. **One level is terrible.** LL1 alone is 65,536 numbers (25 % of everything). At 10 % the budget can't even cover that.

## Which is "better"?

- At **mild to medium compression** they're roughly equal. The DCT is marginally better in PSNR, but it shows a grid on smooth areas.
- At **strong compression** a multi-level wavelet is clearly better: it degrades into a coarser image instead of breaking into blocks.
- **Haar specifically** is the simplest wavelet. Its blocky steps are its weakness, and smoother wavelets (Daubechies, CDF 9/7) would beat the DCT more convincingly.

## Checkpoint

- Name the typical artifact of each method and explain where it comes from.
- Why are the results identical at 1 % with 3 levels?
- Why do more Haar levels help at strong compression?
- Which standards use each transform?
