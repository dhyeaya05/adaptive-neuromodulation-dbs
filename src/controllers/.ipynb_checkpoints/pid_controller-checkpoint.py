"""
PID Controller Implementation
Proportional-Integral-Derivative controller for DBS
"""

import numpy as np
from .base_controller import BaseController


class PIDController(BaseController):
    """
    PID Controller for Deep Brain Stimulation
    
    Control law: u(t) = Kp*e(t) + Ki*∫e(τ)dτ + Kd*de(t)/dt
    
    Parameters
    ----------
    kp : float
        Proportional gain
    ki : float
        Integral gain
    kd : float
        Derivative gain
    dt : float
        Time step in seconds
    anti_windup : bool
        Enable anti-windup for integral term
    windup_limit : float
        Maximum absolute value for integral term
    """
    
    def __init__(self, 
                 kp: float = 2.0, 
                 ki: float = 0.5, 
                 kd: float = 0.1,
                 dt: float = 0.001,
                 anti_windup: bool = True,
                 windup_limit: float = 10.0,
                 **kwargs):
        super().__init__(dt=dt, **kwargs)
        
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.anti_windup = anti_windup
        self.windup_limit = windup_limit
        
        # Internal state
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_control = 0.0
        
        # Store parameters
        self.params.update({
            'kp': kp,
            'ki': ki,
            'kd': kd,
            'anti_windup': anti_windup,
            'windup_limit': windup_limit
        })
    
    def compute_control(self, measurement: float, setpoint: float) -> float:
        """
        Compute PID control signal
        
        Parameters
        ----------
        measurement : float
            Current measured beta power
        setpoint : float
            Target beta power
            
        Returns
        -------
        float
            Control signal (stimulation amplitude in mA)
        """
        # Calculate error (note: negative because we want to reduce beta power)
        # Higher beta power -> more stimulation needed
        error = measurement - setpoint
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term with anti-windup
        self.integral += error * self.dt
        if self.anti_windup:
            self.integral = np.clip(self.integral, 
                                   -self.windup_limit, 
                                   self.windup_limit)
        i_term = self.ki * self.integral
        
        # Derivative term
        derivative = (error - self.prev_error) / self.dt
        d_term = self.kd * derivative
        
        # Compute raw control signal
        control = p_term + i_term + d_term
        
        # Apply saturation limits (0-5 mA)
        control = self.apply_saturation(control, min_val=0.0, max_val=5.0)
        
        # Optional: Apply rate limiting
        # control = self.apply_rate_limit(control, self.prev_control, max_rate=2.0)
        
        # Update state
        self.prev_error = error
        self.prev_control = control
        self.update_time()
        self.log_control(control, error)
        
        return control
    
    def reset(self):
        """Reset controller state"""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_control = 0.0
        self.time = 0.0
        self.control_history = []
        self.error_history = []
    
    def tune_ziegler_nichols(self, ku: float, tu: float, method: str = 'classic'):
        """
        Auto-tune PID gains using Ziegler-Nichols method
        
        Parameters
        ----------
        ku : float
            Ultimate gain (gain at stability boundary)
        tu : float
            Ultimate period (oscillation period at ku)
        method : str
            Tuning method: 'classic', 'pessen', 'some_overshoot', 'no_overshoot'
        """
        if method == 'classic':
            self.kp = 0.6 * ku
            self.ki = 2.0 * self.kp / tu
            self.kd = self.kp * tu / 8.0
        elif method == 'pessen':
            self.kp = 0.7 * ku
            self.ki = 2.5 * self.kp / tu
            self.kd = 0.15 * self.kp * tu
        elif method == 'some_overshoot':
            self.kp = 0.33 * ku
            self.ki = 2.0 * self.kp / tu
            self.kd = self.kp * tu / 3.0
        elif method == 'no_overshoot':
            self.kp = 0.2 * ku
            self.ki = 2.0 * self.kp / tu
            self.kd = self.kp * tu / 3.0
        else:
            raise ValueError(f"Unknown tuning method: {method}")
        
        # Update params dict
        self.params.update({'kp': self.kp, 'ki': self.ki, 'kd': self.kd})
        
        print(f"PID tuned using {method} Ziegler-Nichols:")
        print(f"  Kp = {self.kp:.4f}")
        print(f"  Ki = {self.ki:.4f}")
        print(f"  Kd = {self.kd:.4f}")
    
    def get_tuning_recommendations(self) -> dict:
        """
        Get PID tuning recommendations based on current behavior
        
        Returns
        -------
        dict
            Tuning recommendations
        """
        if len(self.error_history) < 100:
            return {"message": "Not enough data for recommendations"}
        
        errors = np.array(self.error_history[-100:])
        
        recommendations = {}
        
        # Check steady-state error
        steady_state_error = np.mean(errors[-20:])
        if abs(steady_state_error) > 0.1:
            recommendations['integral'] = "Increase Ki to reduce steady-state error"
        
        # Check oscillations
        zero_crossings = np.sum(np.diff(np.sign(errors)) != 0)
        if zero_crossings > 10:
            recommendations['derivative'] = "Increase Kd to reduce oscillations"
            recommendations['proportional'] = "Consider reducing Kp"
        
        # Check response speed
        settling_idx = np.where(np.abs(errors) < 0.1)[0]
        if len(settling_idx) > 0:
            settling_time = settling_idx[0] * self.dt
            if settling_time > 5.0:
                recommendations['speed'] = "Increase Kp for faster response"
        
        return recommendations if recommendations else {"message": "Tuning looks good!"}
    
    def __repr__(self) -> str:
        return f"PIDController(Kp={self.kp}, Ki={self.ki}, Kd={self.kd})"
