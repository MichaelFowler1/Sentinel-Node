import csv
import numpy as np

class SatelliteKalmanFilter:
    def __init__(self):
        # INITIALIZATION FIX:
        # Initial X-velocity is exactly 0.0 at launch, not -7.72
        self.x = np.array([[6678.14], [0.0]]) 
        
        # Initial covariance matrix (State uncertainty estimate)
        self.P = np.eye(2) * 1.0
        
        # State transition matrix (Kinematic model: x = x + v*dt)
        dt = 1.0
        self.F = np.array([[1, dt],
                           [0, 1]])
        
        # Observation model (Mapping state to measurement space; position only)
        self.H = np.array([[1, 0]])
        
        # Process noise covariance (Kinematic model uncertainty)
        self.Q = np.array([[0.01, 0],
                           [0, 0.01]])
        
        # Measurement noise covariance (Sensor variance, approx. 50m atmospheric jitter)
        self.R = np.array([[0.5]])

    def predict(self):
        # Propagate the state and covariance matrices forward
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q

    def update(self, z):
        # Calculate the measurement residual
        y = z - (self.H @ self.x) 
        
        # Threat Detection Logic
        # Residuals exceeding 1km indicate physically impossible kinematics. 
        # Reject the update to mitigate EW spoofing/jamming.
        if abs(y) > 1.0: 
            return True # Jamming Detected
        
        # Calculate optimal Kalman Gain
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # Update state estimate and covariance matrix with valid sensor data
        self.x = self.x + K @ y
        self.P = (np.eye(2) - K @ self.H) @ self.P
        
        return False

def run_advanced_flight_software():
    kf = SatelliteKalmanFilter()
    print("--- Sentinel Node: Kalman FDIR Active ---")
    
    with open("flight_telemetry.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            t = int(row["Time_sec"])
            z = float(row["Sensor_X"])
            true_x = float(row["True_X"])
            
            # Predict state forward
            kf.predict()
            
            # Update state with sensor measurement
            is_jammed = kf.update(z)
            
            # Calculate state error
            est_x = kf.x[0,0]
            error = abs(est_x - true_x) * 1000 # Error mapped in meters
            
            if t % 10 == 0 or is_jammed:
                status = "[JAMMING REJECTED]" if is_jammed else "[NOMINAL]"
                print(f"T+{t}s {status} | Error: {error:.2f}m")

if __name__ == "__main__":
    run_advanced_flight_software()