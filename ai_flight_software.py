import csv
import json
import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. THE DETERMINISTIC PHYSICS ENGINE
class SatelliteKalmanFilter:
    def __init__(self):
        self.x = np.array([[6678.14], [-7.72]]) 
        self.P = np.eye(2) * 1.0
        self.F = np.array([[1, 1.0], [0, 1]])
        self.H = np.array([[1, 0]])
        self.Q = np.array([[0.01, 0], [0, 0.01]])
        self.R = np.array([[0.5]])

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x[0, 0] # Return expected position

    def update(self, z):
        y = z - (self.H @ self.x) 
        
        # Hard deterministic threshold (No AI Hallucinations allowed)
        if abs(y) > 1.0: 
            return True, y[0, 0] # Jamming Detected, return residual
        
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(2) - K @ self.H) @ self.P
        return False, y[0, 0]

# 2. THE NEURAL SUPERVISOR
def generate_threat_sitrep(time_sec, sensor_x, expected_x, residual):
    print(f" > Anomaly Detected! Transmitting T+{time_sec}s telemetry to GPT-5.1 for SITREP...")
    
    prompt = f"""
    Kinematic Threat Event at T+{time_sec}s:
    - Expected X (Kalman Filter): {expected_x:.2f} km
    - Raw Sensor X: {sensor_x:.2f} km
    - Residual (Error): {residual:.2f} km
    
    The deterministic flight filter has locked out the sensor due to an error > 1.0km, indicating EW spoofing.
    Write a brief, highly technical 1-sentence situation report explaining the physical impossibility of this jump.
    Return JSON: {{"sitrep": "string"}}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": "You are a tactical aerospace FDIR reporting system."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)["sitrep"]
    except Exception as e:
        return f"SITREP Generation Failed: {str(e)}"

# 3. THE MAIN PIPELINE
def execute_sentinel_pipeline():
    print("--- Sentinel Node: Kalman-Neural Centaur Pipeline Active ---")
    
    if not os.path.exists("flight_telemetry.csv"):
        print("CRITICAL ERROR: 'flight_telemetry.csv' missing.")
        return

    kf = SatelliteKalmanFilter()
    
    with open("flight_telemetry.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            t = int(row["Time_sec"])
            
            # Isolate evaluation window for testing
            if 28 <= t <= 32:
                sensor_x = float(row["Sensor_X"])
                
                # Predict where the satellite is on the actual orbital curve
                expected_x = kf.predict()
                
                # Check sensor against prediction deterministically
                is_jammed, error_residual = kf.update(sensor_x)
                
                if is_jammed:
                    # Sensor is poisoned! The Kalman Filter safely ignores it.
                    # We wake up the AI to generate the report.
                    sitrep = generate_threat_sitrep(t, sensor_x, expected_x, error_residual)
                    print(f"T+{t}s | 🚨 [EW JAMMING ISOLATED] | Truth: {expected_x:.2f} km | Report: {sitrep}")
                else:
                    print(f"T+{t}s | ✅ [NOMINAL] | Truth: {expected_x:.2f} km | Sensor Error: {error_residual:.2f} km")

    print("\n--- Pipeline Execution Terminated ---")

if __name__ == "__main__":
    execute_sentinel_pipeline()