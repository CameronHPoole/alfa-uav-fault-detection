package CarbonZ_System {
    private import Types::*;
    private import FaultRequirements::*;

    /* Component Architecture Definitions */
    part def FlightController {
        attribute roll_rms_monitor : AngleError;
        attribute pitch_rms_monitor : AngleError;
        attribute yaw_rms_monitor : AngleError;
        attribute airspeed_rms_monitor : SpeedError;
    }

    part def CarbonZ_T28 {
        part fcs : FlightController;
    }

    /* System Deployment and Verification Mapping */
    part t28_instance : CarbonZ_T28;
    
    // Satisfying the requirements using the specific system instance
    satisfy FaultDetectionRequirements.roll_fault_detection by t28_instance.fcs;
    satisfy FaultDetectionRequirements.pitch_fault_detection by t28_instance.fcs;
    satisfy FaultDetectionRequirements.yaw_fault_detection by t28_instance.fcs;
    satisfy FaultDetectionRequirements.airspeed_fault_detection by t28_instance.fcs;
}
