"""
Base Controller Class
Abstract base class for all DBS controllers
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import numpy as np


class BaseController(ABC):
    """
    Abstract base class for DBS controllers
    
    All controllers must implement:
    - compute_control(): Calculate stimulation amplitude
    - reset(): Reset internal state
    - get_params(): Return controller parameters
    """
    
    def __init__(self, dt: float = 0.001, **kwargs):
        """
        Initialize base controller
        
        Parameters
        ----------
        dt : float
            Time step in seconds (default: 1ms)
        **kwargs : dict
            Additional controller-specific parameters
        """
        self.dt = dt
        self.time = 0.0
        self.control_history = []
        self.error_history = []
        self.params = kwargs
        
    @abstractmethod
    def compute_control(self, measurement: float, setpoint: float) -> float:
        """
        Compute control signal based on measurement and setpoint
        
        Parameters
        ----------
        measurement : float
            Current measured value (e.g., beta power)
        setpoint : float
            Desired target value
            
        Returns
        -------
        float
            Control signal (stimulation amplitude in mA)
        """
        pass
    
    @abstractmethod
    def reset(self):
        """Reset controller internal state"""
        pass
    
    def get_params(self) -> Dict[str, Any]:
        """
        Get controller parameters
        
        Returns
        -------
        dict
            Controller parameters and configuration
        """
        return {
            'dt': self.dt,
            'time': self.time,
            **self.params
        }
    
    def update_time(self):
        """Increment internal time counter"""
        self.time += self.dt
    
    def log_control(self, control: float, error: float):
        """
        Log control signal and error for analysis
        
        Parameters
        ----------
        control : float
            Control signal value
        error : float
            Error value (setpoint - measurement)
        """
        self.control_history.append(control)
        self.error_history.append(error)
    
    def get_history(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get control and error history
        
        Returns
        -------
        tuple
            (control_history, error_history) as numpy arrays
        """
        return (
            np.array(self.control_history),
            np.array(self.error_history)
        )
    
    def apply_saturation(self, control: float, 
                        min_val: float = 0.0, 
                        max_val: float = 5.0) -> float:
        """
        Apply saturation limits to control signal
        
        Parameters
        ----------
        control : float
            Raw control signal
        min_val : float
            Minimum allowed value (default: 0 mA)
        max_val : float
            Maximum allowed value (default: 5 mA)
            
        Returns
        -------
        float
            Saturated control signal
        """
        return np.clip(control, min_val, max_val)
    
    def apply_rate_limit(self, control: float, 
                        prev_control: float,
                        max_rate: float = 2.0) -> float:
        """
        Apply rate limiting to control signal
        
        Parameters
        ----------
        control : float
            Desired control signal
        prev_control : float
            Previous control signal
        max_rate : float
            Maximum rate of change (mA/s)
            
        Returns
        -------
        float
            Rate-limited control signal
        """
        max_change = max_rate * self.dt
        delta = control - prev_control
        
        if abs(delta) > max_change:
            return prev_control + np.sign(delta) * max_change
        return control
    
    def __repr__(self) -> str:
        """String representation of controller"""
        return f"{self.__class__.__name__}(dt={self.dt})"
