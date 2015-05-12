using System;
using System.Collections.Generic;
using System.Linq;
using KRPC.Service;
using KRPC.Service.Attributes;

namespace KRPCInfernalRobotics.Services
{
    [KRPCService (GameScene = GameScene.Flight)]
    public static class InfernalRobotics
    {
        [KRPCProperty]
        public static IList<ControlGroup> ServoGroups {
            get {
                if (!IRWrapper.APIReady)
                    throw new InvalidOperationException ("InfernalRobotics is not available");
                return IRWrapper.IRController.ServoGroups.Select (x => new ControlGroup (x)).ToList ();
            }
        }

        [KRPCProcedure]
        public static ControlGroup ServoGroupWithName (string name)
        {
            var servoGroup = IRWrapper.IRController.ServoGroups.FirstOrDefault (x => x.Name == name);
            return servoGroup != null ? new ControlGroup (servoGroup) : null;
        }

        [KRPCProcedure]
        public static Servo ServoWithName (string name)
        {
            var servo = IRWrapper.IRController.ServoGroups.SelectMany (x => x.Servos).FirstOrDefault (x => x.Name == name);
            return servo != null ? new Servo (servo) : null;
        }
    }
}
