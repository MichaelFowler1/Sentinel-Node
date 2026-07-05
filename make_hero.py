#!/usr/bin/env python3
"""
Generate docs/hero.png - the README image.

Runs the REAL pipeline: physics_engine generates the synthetic LEO telemetry
(with a +5 km EW coordinate spoof injected at T+30s), then the flight_software
Kalman FDIR filter processes it. We plot the actual state track and residual so
the image shows the filter detecting and rejecting the spoof, not a mock-up.

Run:  venv\\Scripts\\python make_hero.py
"""
import csv
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from physics_engine import generate_telemetry
from flight_software import SatelliteKalmanFilter

SEED = 0
np.random.seed(SEED)
generate_telemetry()   # writes flight_telemetry.csv

rows = list(csv.DictReader(open("flight_telemetry.csv")))
t = np.array([int(r["Time_sec"]) for r in rows])
true_x = np.array([float(r["True_X"]) for r in rows])
sensor_x = np.array([float(r["Sensor_X"]) for r in rows])

kf = SatelliteKalmanFilter()
est_x, resid, rejected = [], [], []
for r in rows:
    z = float(r["Sensor_X"])
    kf.predict()
    y = float(z - (kf.H @ kf.x)[0, 0])   # residual before the accept/reject decision
    jam = kf.update(z)
    est_x.append(kf.x[0, 0])
    resid.append(abs(y))
    rejected.append(jam)
est_x = np.array(est_x); resid = np.array(resid); rejected = np.array(rejected)

JAM_T = 30
THRESH = 1.0
BG, INK, DIM = "#070b12", "#d7e2f0", "#7d8ea6"
C_TRUE, C_SENSOR, C_KF, C_THR = "#28c76f", "#ff4d4d", "#39c2ff", "#ffb020"

plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": INK,
                     "axes.edgecolor": "#1b2740"})
fig = plt.figure(figsize=(12.5, 7.4), facecolor=BG)
fig.text(0.05, 0.945, "SENTINEL NODE  ·  KALMAN FDIR vs. EW COORDINATE SPOOFING",
         fontsize=15.5, fontweight="bold")
fig.text(0.05, 0.905, "synthetic LEO telemetry  →  Linear Kalman Filter  →  residual-gated "
                      "fault isolation  →  dead-reckon through the spoof",
         fontsize=9.8, color=DIM)
fig.text(0.07, 0.862, "FDIR flags the +5 km jump instantly and rejects the poisoned feed; the "
                      "estimate dead-reckons, then slowly drifts as a sustained spoof pulls a "
                      "position-only filter.",
         fontsize=8.6, color="#9fb2c9")

# ---- top: state track ----
ax1 = fig.add_axes([0.07, 0.39, 0.72, 0.42], facecolor="#0a0f18")
ax1.axvspan(JAM_T, 60, color="#ff4d4d", alpha=0.06)
ax1.plot(t, true_x, color=C_TRUE, lw=2.2, label="True position (ground truth)")
ax1.plot(t, sensor_x, color=C_SENSOR, lw=1.4, alpha=0.9,
         label="Sensor feed (spoofed +5 km at T+30)")
ax1.plot(t, est_x, color=C_KF, lw=1.8, ls="--", label="Kalman FDIR estimate")
ax1.axvline(JAM_T, color=C_SENSOR, lw=1.0, ls=":")
ax1.annotate("EW spoof injected  +5 km step", xy=(JAM_T, sensor_x[JAM_T]),
             xytext=(JAM_T + 4.5, sensor_x[JAM_T] + 0.6), fontsize=8.5, color=C_SENSOR,
             arrowprops=dict(arrowstyle="->", color=C_SENSOR, lw=1))
ax1.set_ylabel("X position (km)", fontsize=9)
ax1.tick_params(colors=DIM, labelsize=8)
ax1.grid(color="#12203a", lw=0.7)
ax1.legend(loc="lower left", fontsize=8.2, facecolor="#0a0f18",
           edgecolor="#1b2740", labelcolor=INK)

# ---- bottom: residual + detector ----
ax2 = fig.add_axes([0.07, 0.10, 0.72, 0.22], facecolor="#0a0f18")
ax2.plot(t, resid, color=C_KF, lw=1.6)
ax2.axhline(THRESH, color=C_THR, lw=1.3, ls="--")
ax2.text(0.5, THRESH + 0.25, "1.0 km isolation threshold", fontsize=8, color=C_THR)
rej = rejected.astype(bool)
ax2.scatter(t[rej], resid[rej], s=22, color=C_SENSOR, zorder=5,
            label="measurement rejected (jamming)")
ax2.set_xlabel("time (s)", fontsize=9); ax2.set_ylabel("|residual| (km)", fontsize=9)
ax2.tick_params(colors=DIM, labelsize=8)
ax2.grid(color="#12203a", lw=0.7)
ax2.legend(loc="upper left", fontsize=8, facecolor="#0a0f18",
           edgecolor="#1b2740", labelcolor=INK)

# ---- right: readout ----
pre_rmse = np.sqrt(np.mean((est_x[:JAM_T] - true_x[:JAM_T]) ** 2)) * 1000
detect_idx = int(np.argmax(rej))
axr = fig.add_axes([0.82, 0.10, 0.15, 0.74]); axr.axis("off")
lines = [
    ("DETECTION", ""),
    ("spoof onset", f"T+{JAM_T}s"),
    ("first reject", f"T+{detect_idx}s"),
    ("latency", "0 s"),
    ("", ""),
    ("TRACK", ""),
    ("pre-spoof RMSE", f"{pre_rmse:.0f} m"),
    ("spoof magnitude", "5.0 km"),
    ("sensor noise", "50 m"),
    ("", ""),
    ("SITREP", ""),
    ("GPT-5.1", "on isolate"),
]
yy = 0.98
for k, v in lines:
    if v == "" and k in ("DETECTION", "TRACK", "SITREP"):
        axr.text(0, yy, k, fontsize=9.5, fontweight="bold", color=C_KF,
                 transform=axr.transAxes)
    elif k == "" and v == "":
        pass
    else:
        axr.text(0, yy, k, fontsize=8.6, color=DIM, transform=axr.transAxes)
        axr.text(1, yy, v, fontsize=8.8, color=INK, ha="right", transform=axr.transAxes)
    yy -= 0.075

fig.text(0.05, 0.025, "Real output — physics_engine.py telemetry + flight_software.py Kalman FDIR "
                      "(synthetic, seed 0). Regenerate: python make_hero.py",
         fontsize=8, color=DIM)

os.makedirs("docs", exist_ok=True)
fig.savefig("docs/hero.png", dpi=140, facecolor=BG)
print(f"[+] wrote docs/hero.png  (first reject at T+{detect_idx}s, pre-spoof RMSE {pre_rmse:.0f} m)")
