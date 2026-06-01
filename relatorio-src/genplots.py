import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/tmp/relatorio"

# ---- Strong scaling (problema fixo: 800x600, MAX_ITER=10000) ----
strong_w = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,31]
strong_sp = [1,1.94072,2.598745,3.335887,4.266343,5.240487,5.828508,6.553596,
             7.323513,7.847477,8.273456,9.093046,10.177792,10.508349,10.738562,20.191145]
strong_eff = [1,0.97036,0.866248,0.833972,0.853269,0.873415,0.832644,0.819199,
              0.813724,0.784748,0.752132,0.757754,0.782907,0.750596,0.715904,0.651327]

# ---- Weak scaling (carga ~ N via MAX_ITER) ----
weak_w = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,31]
weak_sp = [1,1.926808,2.512146,3.18473,4.088737,5.094483,5.588235,6.181449,
           6.970538,7.571536,8.077563,9.148884,9.530627,10.191137,10.368949,20.391229]
weak_eff = [1,0.963404,0.837382,0.796182,0.817747,0.849081,0.798319,0.772681,
            0.774504,0.757154,0.734324,0.762407,0.733125,0.727938,0.691263,0.657816]
weak_time = [10.78518,11.220187,12.804295,13.448854,13.074383,12.58651,13.399998,
             13.823886,13.787825,14.11974,14.559463,14.021968,14.563222,14.665052,
             15.440807,16.232599]

BLUE, ORANGE, GREEN = "#1f6fb2", "#e8833a", "#2e9e5b"

def base(ax):
    ax.grid(True, ls="--", alpha=0.4)
    ax.set_xlabel("Numero de trabalhadores")
    ax.set_xlim(0, 32)

# Fig 1: strong speedup
fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.plot([0,31],[0,31], ls="--", color="gray", label="Ideal (linear)")
ax.plot(strong_w, strong_sp, "o-", color=BLUE, ms=4, label="Medido")
ax.set_ylabel("Speed-up"); ax.set_title("Speed-up forte"); base(ax); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_strong_speedup.png", dpi=150); plt.close(fig)

# Fig 2: strong efficiency
fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.axhline(1.0, ls="--", color="gray", label="Ideal (1,0)")
ax.plot(strong_w, strong_eff, "s-", color=ORANGE, ms=4, label="Medido")
ax.set_ylabel("Eficiencia"); ax.set_title("Eficiencia (escala forte)")
ax.set_ylim(0, 1.1); base(ax); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_strong_eff.png", dpi=150); plt.close(fig)

# Fig 3: weak speedup
fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.plot([0,31],[0,31], ls="--", color="gray", label="Ideal (linear)")
ax.plot(weak_w, weak_sp, "o-", color=GREEN, ms=4, label="Medido")
ax.set_ylabel("Speed-up"); ax.set_title("Speed-up fraco"); base(ax); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_weak_speedup.png", dpi=150); plt.close(fig)

# Fig 4: weak time (deve permanecer ~constante)
fig, ax = plt.subplots(figsize=(4.2, 3.0))
ax.plot(weak_w, weak_time, "D-", color=BLUE, ms=4, label="Tempo paralelo")
ax.axhline(weak_time[0], ls="--", color="gray", label="Ideal (constante)")
ax.set_ylabel("Tempo (s)"); ax.set_title("Escala fraca: tempo de execucao")
ax.set_ylim(0, 20); base(ax); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(f"{OUT}/fig_weak_time.png", dpi=150); plt.close(fig)

print("figuras geradas")
