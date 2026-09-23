# Copyright 2026 Michael Fowler
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0

import numpy as np
from astropy import units as u
from astropy.time import Time
from poliastro.bodies import Earth
from poliastro.twobody import Orbit
import csv

def generate_telemetry():
    # 1. Orbital Kinematics Initialization
    r_earth = Earth.R.to(u.km).value
    altitude = 300 
    r = (r_earth + altitude) * u.km
    
    # Calculate velocity for circular Low Earth Orbit (LEO)
    v = np.sqrt(Earth.k / r).to(u.km / u.s)
    
    r_vec = [r.value, 0, 0] * u.km
    v_vec = [0, v.value, 0] * u.km / u.s
    
    epoch = Time("2026-05-08 00:00:00", scale="utc")
    surrogate_orbit = Orbit.from_vectors(Earth, r_vec, v_vec, epoch)
    
    print("--- Sentinel Node: Kinematic Surrogate Generator ---")
    print("Initializing atmospheric jitter and EW spoofing profiles...")
    
    # --- Environmental & Threat Parameters ---
    noise_std_dev = 0.05  # 50m Gaussian noise simulating sensor variance/atmospheric drag
    jamming_offset = 5.0  # 5km hard offset for EW coordinate spoofing
    
    # 2. Simulation Loop & Data Export
    # Export ground truth and degraded sensor data for downstream FDIR ingestion
    with open("flight_telemetry.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Time_sec", "True_X", "True_Y", "True_Z", "Sensor_X", "Sensor_Y", "Sensor_Z", "Jamming_Active"])
        
        for t_sec in range(61):
            # Propagate ground truth state
            current_state = surrogate_orbit.propagate(t_sec * u.s)
            true_x, true_y, true_z = current_state.r.value
            
            # --- Apply Environmental Noise ---
            # Introduce Gaussian distribution to simulate standard sensor deviation
            sensor_x = true_x + np.random.normal(0, noise_std_dev)
            sensor_y = true_y + np.random.normal(0, noise_std_dev)
            sensor_z = true_z + np.random.normal(0, noise_std_dev)
            
            # --- Apply Electronic Warfare (EW) Spoofing ---
            jamming_active = False
            if t_sec >= 30:  # Initiate coordinate spoofing at T+30s threshold
                jamming_active = True
                sensor_x += jamming_offset
                sensor_y += jamming_offset
                
            # Write state vector to CSV
            writer.writerow([t_sec, true_x, true_y, true_z, sensor_x, sensor_y, sensor_z, jamming_active])
            
            # Output telemetry status (10Hz intervals)
            if t_sec % 10 == 0:
                status = "[JAMMED] " if jamming_active else "[NOMINAL]"
                print(f"T+{t_sec}s {status} -> True X: {true_x:.2f} | Sensor X: {sensor_x:.2f}")

    print("\n[SUCCESS] Telemetry export complete: 'flight_telemetry.csv'.")

if __name__ == "__main__":
    generate_telemetry()