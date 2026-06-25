import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/tmp/slides"

# ---------- Mandelbrot colorido (mesma regiao do codigo C) ----------
W, H, MAXIT = 1000, 750, 400
xs = -2.5 + 3.5 * np.arange(W) / W          # real: igual ao codigo
ys = -1.0 + 2.0 * np.arange(H) / H          # imag: igual ao codigo
C = xs[None, :] + 1j * ys[:, None]
Z = np.zeros_like(C)
itc = np.zeros(C.shape, dtype=float)
alive = np.ones(C.shape, dtype=bool)
for i in range(MAXIT):
    Z[alive] = Z[alive] * Z[alive] + C[alive]
    esc = alive & (np.abs(Z) > 2.0)
    itc[esc] = i + 1 - np.log(np.log(np.abs(Z[esc]))) / np.log(2)  # smooth coloring
    alive &= ~esc
itc[alive] = 0  # interior -> tom escuro do colormap
plt.imsave(f"{OUT}/mandelbrot.png", itc**0.4, cmap="magma", origin="upper")

# ---------- Dados ----------
strong_w = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,31]
strong_sp = [1,1.94072,2.598745,3.335887,4.266343,5.240487,5.828508,6.553596,
             7.323513,7.847477,8.273456,9.093046,10.177792,10.508349,10.738562,20.191145]
strong_eff = [1,0.97036,0.866248,0.833972,0.853269,0.873415,0.832644,0.819199,
              0.813724,0.784748,0.752132,0.757754,0.782907,0.750596,0.715904,0.651327]
weak_w = strong_w
weak_sp = [1,1.926808,2.512146,3.18473,4.088737,5.094483,5.588235,6.181449,
           6.970538,7.571536,8.077563,9.148884,9.530627,10.191137,10.368949,20.391229]
weak_eff = [1,0.963404,0.837382,0.796182,0.817747,0.849081,0.798319,0.772681,
            0.774504,0.757154,0.734324,0.762407,0.733125,0.727938,0.691263,0.657816]

NAVY, TEAL, ORANGE = "#1B2A4A", "#1C7293", "#E8833A"
plt.rcParams.update({"font.size": 15, "axes.labelsize": 16,
                     "xtick.labelsize": 13, "ytick.labelsize": 13,
                     "legend.fontsize": 14, "axes.edgecolor": "#555"})

def chart(fname, w, y, color, ideal, ylabel, ymax=None):
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    if ideal == "linear":
        ax.plot([0, 31], [0, 31], ls="--", color="#9aa0a6", lw=2, label="Ideal (linear)")
    else:
        ax.axhline(1.0, ls="--", color="#9aa0a6", lw=2, label="Ideal (1,0)")
    ax.plot(w, y, "o-", color=color, lw=2.5, ms=7, label="Medido")
    ax.set_xlabel("Número de trabalhadores"); ax.set_ylabel(ylabel)
    ax.set_xlim(0, 32); ax.grid(True, ls="--", alpha=0.4)
    if ymax: ax.set_ylim(0, ymax)
    ax.legend(loc="upper left", framealpha=0.95)
    fig.tight_layout(); fig.savefig(f"{OUT}/{fname}", dpi=200); plt.close(fig)

chart("chart_strong_sp.png",  strong_w, strong_sp,  TEAL,   "linear", "Speed-up")
chart("chart_strong_eff.png", strong_w, strong_eff, ORANGE, "flat",   "Eficiência", 1.12)
chart("chart_weak_sp.png",    weak_w,   weak_sp,    TEAL,   "linear", "Speed-up")
chart("chart_weak_eff.png",   weak_w,   weak_eff,   ORANGE, "flat",   "Eficiência", 1.12)
print("assets gerados")
