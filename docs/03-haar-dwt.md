# 3. Haar DWT — wavelet transform

## Intuition: averages and differences

Take pixels in **pairs**. For each pair, store:

- how bright the pair is on average (**approximation**), and
- how different the two pixels are (**detail**).

```
pixels:        10   12  |  50   52
                 ╲ ╱         ╲ ╱
average:          11          51        ← a smaller, blurrier copy of the signal
difference:       -1          -1        ← tiny, because neighbours are similar
```

From `average` and `difference` you get the pair back exactly: `x0 = avg + diff` and `x1 = avg − diff`. If you **throw away the small differences**, you get `[11, 11, 51, 51]`, which is almost the original.

### The √2 version (what our code uses)

Instead of `/2`, we divide by `√2`:

```
a = (x0 + x1) / √2          x0 = (a + d) / √2
d = (x0 − x1) / √2          x1 = (a − d) / √2
```

The pictures look the same, but now the transform is **orthonormal** like the DCT: it keeps total energy, so coefficient sizes in the DCT and the DWT can be compared directly with one shared "keep largest k %" rule.

```
haar_step([10, 12, 50, 52]) = [15.6, 72.1, -1.4, -1.4]
                               └─ a ────┘  └─ d ────┘
```

Code: `core/haar.py → haar_step()` and `inverse_haar_step()`.

## 2-D: rows, then columns → four sub-bands

1. Apply the step to **every row**. The left half holds row averages, the right half holds row differences.
2. Apply the step to **every column** of that result.

```
 original          after rows            after columns
┌──────────┐      ┌─────┬─────┐         ┌─────┬─────┐
│          │      │     │     │         │ LL  │ HL  │
│  image   │ ───► │ avg │ dif │  ───►   ├─────┼─────┤
│          │      │     │     │         │ LH  │ HH  │
└──────────┘      └─────┴─────┘         └─────┴─────┘
```

| Sub-band | Rows | Columns | What it contains |
|---|---|---|---|
| **LL** | average | average | the image at half size (blurry) |
| **HL** | difference | average | **vertical** edges (changes left↔right) |
| **LH** | average | difference | **horizontal** edges (changes up↕down) |
| **HH** | difference | difference | diagonal detail, noise |

Worked 2×2 example (`test_2d_level_sub_bands_of_known_block`):

```
[[1, 2],      haar2d_level      [[ 5, -1],     LL = 5 = 2 × average (2.5)
 [3, 4]]      ────────────►      [-2,  0]]     HL = -1 (left darker than right)
                                               LH = -2 (top darker than bottom), HH = 0
```

Code: `haar2d_level()` is literally `haar_step(haar_step(image).T).T`. The `.T` (transpose) turns columns into rows so we can reuse the same 1-D step.

## Multiple levels: transform LL again

LL is just a smaller image, so we can decompose **it** again, and again:

```
level 1             level 2                 level 3
┌─────┬─────┐       ┌──┬──┬─────┐           ┌┬┬──┬─────┐
│ LL1 │ HL1 │       │LL│HL│     │           ├┼┤HL│     │
├─────┼─────┤  ──►  ├──┼──┤ HL1 │    ──►    ├┴┼──┤ HL1 │
│ LH1 │ HH1 │       │LH│HH│     │           │LH│HH│     │
└─────┴─────┘       ├──┴──┼─────┤           ├──┴──┼─────┤
                    │ LH1 │ HH1 │           │ LH1 │ HH1 │
                    └─────┴─────┘           └─────┴─────┘
```

You can see this pyramid in the app under **Coefficients**.

- After `L` levels the LL corner is `(512 / 2^L)²` numbers: 256×256 for L=1, 64×64 for L=3, **16×16 for L=5**.
- Each LL value equals `2^L × the average of a 2^L × 2^L patch`.
- The inverse goes in reverse, from the smallest LL corner back to the full size (`inverse_haar2d`).

**Why levels matter:** more levels mean the "average" part is stored with fewer numbers, so more of the coefficient budget can go to details. At very strong compression this is the difference between a recognisable image and a mess (see chapter 5).

## How it differs from the DCT in one sentence

The DCT asks **"which frequencies are in this 8×8 block?"**. Haar asks **"what's the average here, and where exactly are the edges, at several scales?"**. Wavelets know *where* something happens as well as *how fast it changes*.

## Checkpoint

- Compute by hand the Haar step of `[4, 6, 10, 10]` (with /2 for simplicity).
- What do LL, HL, LH and HH contain? Which one looks like a small copy of the image?
- What does one more decomposition level change?
- Why do we divide by √2 rather than 2?
- Why is the image size required to be divisible by 2^levels?
