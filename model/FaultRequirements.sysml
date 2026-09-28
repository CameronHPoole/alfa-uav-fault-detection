package FaultRequirements {
    private import Types::*;
    private import CarbonZ_System::*; // Imports CarbonZ_T28 and FlightController structures

    public requirement def FaultDetectionRequirements {
        // Formally bind the requirement to the Carbon-Z T-28 system definition
        subject aircraft : CarbonZ_T28;
        
        // Configuration Attributes (Single Source of Truth)
        attribute max_roll_rms : AngleError = 8.0 [deg];
        attribute max_pitch_rms : AngleError = 6.0 [deg];
        attribute max_yaw_rms : AngleError = 10.0 [deg];
        attribute max_airspeed_rms : SpeedError = 3.5 [m/s];

        /* =========================================================================
         * Executable Requirements (Text + Machine-Readable Assertions)
         * ========================================================================= */

        requirement roll_fault_detection {
            doc /* The flight control system must trigger a roll control fault if the roll tracking Root-Mean-Square (RMS) error exceeds 8.0 degrees. */
            
            // Machine-executable constraint checking the flight controller telemetry against the threshold
            assert { aircraft.fcs.roll_rms_monitor <= max_roll_rms }
        }
        
        requirement pitch_fault_detection {
            doc /* The flight control system must trigger a pitch control fault if the pitch tracking Root-Mean-Square (RMS) error exceeds 6.0 degrees. */
            
            assert { aircraft.fcs.pitch_rms_monitor <= max_pitch_rms }
        }
        
        requirement yaw_fault_detection {
            doc /* The flight control system must trigger a yaw control fault if the yaw tracking Root-Mean-Square (RMS) error exceeds 10.0 degrees. */
            
            assert { aircraft.fcs.yaw_rms_monitor <= max_yaw_rms }
        }
        
        requirement airspeed_fault_detection {
            doc /* The flight control system must trigger an airspeed sensor fault if the airspeed Root-Mean-Square (RMS) error exceeds 3.5 meters per second. */
            
            assert { aircraft.fcs.airspeed_rms_monitor <= max_airspeed_rms }
        }
    }
}