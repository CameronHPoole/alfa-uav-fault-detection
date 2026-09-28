package FaultBehaviors {
    private import Types::*;
    private import FaultRequirements::*;
    private import CarbonZ_System::*;

    /* =========================================================================
     * PART 1: Parametric Constraint for Fault Calculation
     * ========================================================================= */
    calculation def EvaluateRmsFault {
        in current_rms : AngleError;
        in threshold_rms : AngleError;
        out fault_triggered : Boolean;
        
        // Simple mathematical logic mapping
        return fault_triggered = (current_rms > threshold_rms);
    }

    /* =========================================================================
     * PART 2: Fail-Safe Action Definitions
     * ========================================================================= */
    action def ExecuteReturnToHome {
        doc /* Commands the flight controller to lock controls, climb to safe altitude, and navigate back to the launch coordinates. */
        
        action climb_to_safe_altitude;
        action navigate_to_home_gps;
        action autonomous_landing;
        
        first climb_to_safe_altitude then navigate_to_home_gps;
        then autonomous_landing;
    }

    /* =========================================================================
     * PART 3: Flight Controller State Machine
     * ========================================================================= */
    state def FlightControlStateMachine {
        // Accessing the system instance to check values
        inout drone_fcs : FlightController;

        entry;
        initial state NormalFlight {
            doc /* System operates optimally, monitoring telemetry. */
            
            // Continuous verification step using our requirement attributes
            expr { 
                EvaluateRmsFault(
                    current_rms = drone_fcs.roll_rms_monitor, 
                    threshold_rms = FaultDetectionRequirements.max_roll_rms
                ).fault_triggered == false 
            }
        }

        // State transition triggered if ANY fault calculation returns true
        transition NormalFlight_to_FailSafe
            first NormalFlight
            then FailSafeMode
            accept fault_event : Boolean
            if EvaluateRmsFault(drone_fcs.roll_rms_monitor, FaultDetectionRequirements.max_roll_rms).fault_triggered or
               EvaluateRmsFault(drone_fcs.pitch_rms_monitor, FaultDetectionRequirements.max_pitch_rms).fault_triggered;

        state FailSafeMode {
            doc /* Fail-Safe engaged due to degraded structural control tracking. */
            
            entry;
            // Execute the action defined above upon entering this state
            do ExecuteReturnToHome;
        }
    }
}
