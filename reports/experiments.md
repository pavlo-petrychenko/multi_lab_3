# Experiments — cameraman

512×512 grayscale, DCT 8×8 blocks, Haar DWT with 3 levels, global top-k coefficient selection.
Compression ratio = total coefficients / non-zero coefficients (no entropy coding).

| Kept, % | Kept coefficients | Compression ratio | DCT PSNR, dB | DWT PSNR, dB | Better |
|---:|---:|---:|---:|---:|:---:|
| 50 | 131,072 / 262,144 | 2.0:1 | 54.08 | 53.60 | DCT |
| 20 | 52,429 / 262,144 | 5.0:1 | 39.70 | 39.44 | DCT |
| 10 | 26,214 / 262,144 | 10.0:1 | 34.22 | 33.78 | DCT |
| 5 | 13,107 / 262,144 | 20.0:1 | 30.91 | 30.35 | DCT |
| 2 | 5,243 / 262,144 | 50.0:1 | 26.83 | 26.08 | DCT |
| 1 | 2,621 / 262,144 | 100.0:1 | 16.24 | 16.24 | = |
