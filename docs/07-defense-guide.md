# 7. Defense guide

The assignment's defense requirements: demonstrate the result, explain the technologies, show your own code, explain the algorithms, and answer questions about the results.

## 5-minute demo script

1. **Run it**: `docker compose up --build` → http://localhost:8080. "One container: FastAPI serves the React build and the API."
2. **Compare tab, cameraman, 5 %**: "Same budget for both, 13,107 of 262,144 coefficients. DCT 30.9 dB, DWT 30.3 dB."
3. **Drag to 1 %**: "Both collapse to 16.2 dB. That's fewer coefficients than there are 8×8 block averages." (chapter 5)
4. **Haar levels → 5**: "DWT jumps to 26 dB, because multi-resolution needs only 256 numbers for the coarse image."
5. **Coefficients view**: "Here's the DCT grid of 8×8 spectra, and here's the wavelet sub-band pyramid."
6. **Error ×5 view**: "DCT errors follow the 8×8 grid; Haar errors follow edges."
7. **Experiments tab → Run**: show the table and chart. "The PSNR requirement at ≥ 3 levels is covered here."
8. **Code**: open `core/dct.py` (`dct_matrix`, `dct2`, `forward_dct_blockwise`), then `core/haar.py` (`haar_step`, `haar2d_level`, `forward_haar2d`), then `core/compression.py`, then `core/metrics.py`.
9. **Tests**: `uv run pytest`. "The DCT is verified against the textbook formula, and both transforms are verified to be perfectly invertible."

## Likely questions and short answers

**Why is the DCT computed as `T·B·Tᵀ`?**
`T` holds the 8 cosine basis vectors as rows. `T·B` applies a 1-D DCT to the columns, and `·Tᵀ` applies it to the rows. The 2-D DCT is separable, so it equals the double-sum formula. Our test checks this.

**How do you compute the inverse?**
`T` is orthonormal, so `T⁻¹ = Tᵀ` and `B = Tᵀ·C·T`. No matrix inversion is needed.

**What is `C[0,0]`?**
The DC coefficient: `8 × average brightness` of the block (for N = 8, `N × mean`).

**Why 8×8?**
Local smoothness gives good energy compaction, the computation is cheap, and it's the JPEG standard. Larger blocks compact better on smooth areas but smear edges across a bigger area. Smaller blocks compact worse.

**What does one Haar step do?**
`a = (x0+x1)/√2` and `d = (x0−x1)/√2`: a scaled average and difference. Rows first, then columns, gives LL/HL/LH/HH. The next levels repeat this on LL.

**Why √2?**
It makes the transform orthonormal: energy is preserved, the error equals the energy of the dropped coefficients, and magnitudes are comparable to the DCT ones.

**How do you compress?**
Keep the k % of coefficients with the largest magnitude, chosen globally, and set the rest to 0. For an orthonormal transform this minimises MSE for a given count, and it's the same rule for both methods, so the comparison is fair.

**Did you use library DCT/DWT functions?**
No. Only NumPy for arrays and matrix multiplication (allowed by the assignment) and Pillow for reading and writing files. No `scipy.fft.dct`, `pywt`, or `cv2.dct`. See `pyproject.toml`.

**What is PSNR and why is it in dB?**
`10·log10(255²/MSE)`. The log scale matches how we perceive error ratios. Above 40 dB the images are practically identical.

**Why isn't your compression ratio the file size?**
We count non-zero coefficients only. A real file also stores their positions and entropy-codes the values.

**Why do both methods give the same PSNR at 1 %?**
With 3 Haar levels, LL3 consists of 4,096 values equal to `8 × mean` of each 8×8 patch, which are exactly the 4,096 DCT DC terms. 1 % = 2,621 < 4,096, so both keep the same averages and lose the same blocks.

**Which method is better?**
They're about equal at moderate compression, with DCT marginally ahead because cosines are smooth. At strong compression a multi-level wavelet wins clearly (24.5 vs 8.6 dB at 0.5 %). JPEG 2000 uses wavelets for that reason.

**What artifacts does each method produce, and why?**
DCT gives an 8×8 grid (blocks are compressed independently) and ringing near edges (missing high cosines). Haar gives steps and blocks of different sizes (its basis is piecewise constant) but no fixed grid.

**How would you improve this?**
Quantization + entropy coding for real file sizes; smoother wavelets (CDF 9/7); keeping the DC/LL coefficients always; color images through YCbCr.

**Why a web app / why this architecture?**
The math (`core`) is pure and separate from the web layer, so it can be tested and shown in isolation. `services` hold the use cases, and `api` is thin. React gives a responsive comparison UI, and Docker makes it start with one command.
