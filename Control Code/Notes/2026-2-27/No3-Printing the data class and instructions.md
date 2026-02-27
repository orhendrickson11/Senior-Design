

Questions: You need to first know which variables or structs the SDK has defined, and then print them out.

Code that prints the data class and instructions :

```python
import inspect
from standardbots import models

def show_class_info(cls):
    print("\n==============================")
    print("CLASS:", cls.__name__)
    print("signature:", inspect.signature(cls))
    print("__annotations__:", getattr(cls, "__annotations__", None))

    # Print dataclass fields if the class is a dataclass
    fields = getattr(cls, "__dataclass_fields__", None)
    if fields:
        print("dataclass fields:", list(fields.keys()))

    # Auto-generated SDK models may include property mappings
    for key in ("openapi_types", "attribute_map", "swagger_types"):
        if hasattr(cls, key):
            try:
                print(f"{key}:", getattr(cls, key))
            except Exception as e:
                print(f"{key}: <error reading> {e}")

# 1) Inspect the main request structure to see its defined fields
show_class_info(models.ArmPositionUpdateRequest)

# 2) Inspect the joint rotations list container to understand how it is constructed
show_class_info(models.ArmJointRotationsList)

# 3) Inspect the single joint rotations structure (tuple of 6 joints)
show_class_info(models.ArmJointRotations)

# 4) Additionally, list all model names containing joint/rotation/request keywords
#    to ensure nothing relevant is missed
print("\n--- names in models containing keywords ---")
keywords = ("Joint", "Rotation", "Rotations", "Request", "ArmPosition")
names = [n for n in dir(models) if any(k in n for k in keywords)]
print("count:", len(names))
print(names)
```

```cmd
#Outputs
==============================CLASS: ArmPositionUpdateRequest signature: (kind: Optional[standardbots.auto_generated.models.ArmPositionUpdateRequestKindEnum] = None, tooltip_positions: Optional[List[standardbots.auto_generated.models.PositionAndOrientation]] = None, tooltip_position: Optional[standardbots.auto_generated.models.PositionAndOrientation] = None, joint_rotations: Optional[List[standardbots.auto_generated.models.ArmJointRotations]] = None, joint_rotation: Optional[standardbots.auto_generated.models.ArmJointRotations] = None, movement_kind: Optional[standardbots.auto_generated.models.MovementKindEnum] = None, speed_profile: Optional[standardbots.auto_generated.models.SpeedProfile] = None) -> None __annotations__: {'kind': typing.Optional[standardbots.auto_generated.models.ArmPositionUpdateRequestKindEnum], 'tooltip_positions': typing.Optional[typing.List[standardbots.auto_generated.models.PositionAndOrientation]], 'tooltip_position': typing.Optional[standardbots.auto_generated.models.PositionAndOrientation], 'joint_rotations': typing.Optional[typing.List[standardbots.auto_generated.models.ArmJointRotations]], 'joint_rotation': typing.Optional[standardbots.auto_generated.models.ArmJointRotations], 'movement_kind': typing.Optional[standardbots.auto_generated.models.MovementKindEnum], 'speed_profile': typing.Optional[standardbots.auto_generated.models.SpeedProfile]} dataclass fields: ['kind', 'tooltip_positions', 'tooltip_position', 'joint_rotations', 'joint_rotation', 'movement_kind', 'speed_profile'] 

============================== CLASS: List signature: (*args, **kwargs) __annotations__: None 

============================== CLASS: ArmJointRotations signature: (joints: Optional[Tuple[float, float, float, float, float, float]] = None) -> None __annotations__: {'joints': typing.Optional[typing.Tuple[float, float, float, float, float, float]]} dataclass fields: ['joints'] 

--- names in models containing keywords --- count: 66 ['ArmJointRotations', 'ArmJointRotationsList', 'ArmPositionUpdateCanceledEvent', 'ArmPositionUpdateControlledRequest', 'ArmPositionUpdateEvent', 'ArmPositionUpdateEventStream', 'ArmPositionUpdateFailureEvent', 'ArmPositionUpdateFailureEventKind', 'ArmPositionUpdateKindEnum', 'ArmPositionUpdateRequest', 'ArmPositionUpdateRequestKindEnum', 'ArmPositionUpdateRequestResponseEventStreamDetails', 'ArmPositionUpdateRequestResponseEventStreamSubscriptionKindEnum', 'ArmPositionUpdateRequestResponseEventStreamSubscriptionsList', 'ArmPositionUpdateRequestResponseFormat', 'ArmPositionUpdateRequestResponseKindEnum', 'CameraFrameRequest', 'CartesianOffsetRequest', 'CartesianPoseRequest', 'CombinedArmPosition', 'DHAGGripperCommandRequest', 'DHCGIGripperCommandRequest', 'DHPGCGripperCommandRequest', 'EngageEmergencyStopRequest', 'GripperCommandRequest', 'IOStateUpdateRequest', 'JointAngles', 'JointAnglesArray', 'JointPoseRequest', 'JointPoseResponse', 'JointRotations', 'JointState', 'JointStateDisturbance', 'JointsPositionResponse', 'JointsStateResponse', 'MaxJointAcclerations', 'MaxJointSpeeds', 'MaxJointTorques', 'OnRobot2FG14GripperCommandRequest', 'OnRobot2FG7GripperCommandRequest', 'OnRobot3FG15GripperCommandRequest', 'PayloadStateRequest', 'PlayRoutineRequest', 'PoseDistanceRequest', 'PoseOperationsRequest', 'ROSControlUpdateRequest', 'RegisterPeerRequest', 'Robotiq2FGripperCommandRequest', 'RobotiqEPickGripperCommandRequest', 'SaveRecordingRequest', 'SchunkEGxGripperCommandRequest', 'SendMessageRequest', 'SetArmPositionControlledResponse', 'SetBoltHeadPositionRequest', 'SetFilterTypeRequest', 'SetGripperBoundsRequest', 'SetRatioControlRequest', 'SetRobotFrameRequest', 'SpeechToTextRequest', 'StartRecordingRequest', 'StopRecordingRequest', 'TextToSkillRequest', 'ToggleRecorderBotRequest', 'ToggleTeleopBotRequest', 'TriggerFaultRequest', 'UnregisterPeerRequest']
```

