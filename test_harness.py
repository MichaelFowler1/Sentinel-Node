import numpy as np
import csv
from flight_software import SatelliteKalmanFilter

def run_stress_test(jamming_intensity_km):
    kf = SatelliteKalmanFilter()
    true_positions = []
    estimated_positions = []
    detection_time = None
    
    # Simulation Constraints
    dt = 1.0
    total_time = 60
    jamming_start = 30
    
    print(f"\n>>> EVALUATING THREAT INTENSITY: {jamming_intensity_km} km offset")
    
    # Initialize dynamic kinematic baseline
    current_true_x = 6678.14
    # FIX: Velocity set to 0.0 to match the filter's initial state
    velocity = 0.0  
    
    for t in range(total_time):
        # 1. Propagate kinematic state
        current_true_x += velocity * dt
        
        # 2. Inject environmental noise (Gaussian distribution)
        sensor_x = current_true_x + np.random.normal(0, 0.05)
        
        # 3. Inject Electronic Warfare (EW) spoofing offset
        if t >= jamming_start:
            sensor_x += jamming_intensity_km
            
        # 4. Execute FDIR pipeline (Predict/Update state)
        kf.predict()
        is_jammed = kf.update(sensor_x)
        
        # Log anomaly detection latency
        if is_jammed and detection_time is None:
            detection_time = t - jamming_start
            
        true_positions.append(current_true_x)
        estimated_positions.append(kf.x[0,0])

    # 5. Compute Post-Jamming Root-Mean-Square Error (RMSE)
    post_jam_true = np.array(true_positions[jamming_start:])
    post_jam_est = np.array(estimated_positions[jamming_start:])
    rmse = np.sqrt(np.mean((post_jam_true - post_jam_est)**2))
    
    return detection_time, rmse

if __name__ == "__main__":
    intensities = [0.5, 5.0, 50.0]
    results = {}

    print("--- Sentinel Node: EW Jamming Performance Evaluation ---")
    for level in intensities:
        # Renamed variable to avoid shadowing the dt constraint
        dt_latency, error = run_stress_test(level)
        results[level] = {"Latency": dt_latency, "RMSE": error}

    print("\n" + "="*40)
    print("FINAL PERFORMANCE REPORT")
    print("="*40)
    print(f"{'Intensity':<15} | {'Det. Speed':<12} | {'Accuracy (RMSE)'}")
    for level, data in results.items():
        det = f"{data['Latency']}s" if data['Latency'] is not None else "FAILED"
        print(f"{level:<15} | {det:<12} | {data['RMSE']:.4f} km")