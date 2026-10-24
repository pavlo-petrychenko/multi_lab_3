# 2. DCT — Discrete Cosine Transform

## Intuition: any row of 8 pixels is a mix of 8 cosine waves

Take 8 pixel values. The DCT finds how much of each of 8 "standard" cosine patterns you have to mix together to get exactly those 8 values.

```
u = 0  ────────────────   constant (average brightness, "DC")
u = 1  ‾‾‾‾‾‾‾‾\________   half a wave: left bright, right dark
u = 2  ‾‾\______/‾‾‾‾‾‾‾   one full wave
 ...
u = 7  /\/\/\/\/\/\/\/\    fastest wave: pixel-to-pixel flicker
```

- **Coefficient 0** (DC) is the average.
- **Low u** means slow changes (smooth gradients).
- **High u** means fast changes (sharp edges, noise, fine texture).

Smooth content therefore needs only the first few coefficients.

### Worked example (a real row of 8 pixels)

```
pixels      = [ 52,  55,  61,  66,  70,  61,  64,  73]
DCT coeffs  = [177.5, -14.4, -5.7, -6.7, 7.1, -3.1, -0.7, 2.4]
```

The first coefficient is big and the rest quickly get small. Keep only the first **3 of 8** and invert:

```
reconstructed = [53.1, 55.7, 59.8, 64.0, 66.8, 67.8, 67.7, 67.2]
original      = [52,   55,   61,   66,   70,   61,   64,   73  ]
```

That's already close, using 37 % of the numbers.

## The DCT matrix `T`

All 8 cosine patterns are stacked as the rows of one 8×8 matrix:

```
T[0, x] = √(1/N)
T[u, x] = √(2/N) · cos( (2x + 1) · u · π / (2N) )      for u = 1..N-1,  x = 0..N-1
```

The √ factors make every row have length 1 and every pair of rows perpendicular, so `T` is **orthonormal**:

```
T · Tᵀ = I     ⇒     T⁻¹ = Tᵀ
```

This gives the inverse for free: you just transpose the matrix. Code: `core/dct.py → dct_matrix()`. Test: `test_dct_matrix_is_orthonormal`.

## 1-D → 2-D: `C = T · B · Tᵀ`

An image block `B` is 8×8, so it has to be transformed in both directions:

```mermaid
flowchart LR
    B["Block B<br/>8×8 pixels"] -->|"T · B<br/>transform each column"| M["T·B"]
    M -->|"· Tᵀ<br/>transform each row"| C["C = T·B·Tᵀ<br/>8×8 coefficients"]
    C -->|"Tᵀ · C · T"| B2["Block B again"]
```

- `T · B`: each **column** of B is multiplied by T, which gives a 1-D DCT of each column.
- `(…) · Tᵀ`: each **row** of the result gets a 1-D DCT as well.
- Inverse: `B = Tᵀ · C · T`, because `Tᵀ·T = I` cancels each side.

This is the **matrix representation** the assignment asks for. Code: `dct2()` and `idct2()`, both one line each.

### What the 8×8 coefficient block means

```
           horizontal frequency →
         ┌────┬────┬────┬─  ─┬────┐
vertical │ DC │    │    │    │    │   C[0,0] = 8 × average brightness of the block
freq. ↓  ├────┼────┼────┼─  ─┼────┤
         │    │ low freqs     │    │   top-left: smooth changes, large values
         ├────┼────┼────┼─  ─┼────┤
         │    │    │      high│    │   bottom-right: fine detail, usually ≈ 0
         └────┴────┴────┴─  ─┴────┘
```

A real block from the cameraman (edge of the coat): `C[0,0] = 1053.9`, and most values in the bottom-right are between −10 and +10.

## Why 8×8 blocks?

- A whole 512×512 image is not smooth overall, but **small pieces of it usually are**, so the DCT compacts energy much better locally.
- An 8×8 matrix product is cheap, and blocks are independent.
- It's what JPEG uses, so the results are familiar.

**The price:** each block is compressed on its own, so at strong compression neighbouring blocks don't match at their borders. That causes the famous **blocking artifacts** (a visible 8×8 grid).

## How our code does it

```python
blocks = split_into_blocks(image, 8)    # shape (64, 64, 8, 8): a grid of 64×64 blocks
coeffs = T @ blocks @ T.T               # NumPy broadcasts the 8×8 product over all 4096 blocks
image  = merge_blocks(coeffs)           # back to 512×512, each block holds its own spectrum
```

- `core/blocks.py`: `split_into_blocks` is a pure `reshape` + `swapaxes`, with no copying and no loops.
- `core/dct.py`: `forward_dct_blockwise` / `inverse_dct_blockwise`.
- `test_dct2_matches_textbook_definition` checks our matrix version against the textbook double-sum formula, computed with four nested loops.

## Checkpoint

- What does coefficient `C[0,0]` represent? What about `C[7,7]`?
- Write down `C = T·B·Tᵀ`. Which side transforms rows, and which transforms columns?
- Why is the inverse `Tᵀ·C·T`, and why don't we need to invert a matrix?
- Why split into 8×8 blocks? What artifact does that cause?
- Where in the code is the DCT matrix built?
