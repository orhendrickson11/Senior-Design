# StandardBots SDK Model Classification

## 1.Core Arm Motion Control (Primary Motion API)

These classes are responsible for commanding arm movement.

```python
ArmPositionUpdateRequest
ArmPositionUpdateKindEnum
ArmPositionUpdateRequestKindEnum
ArmPositionUpdateControlledRequest
```

Purpose:
These are the main request structures used to move the robotic arm.
They define how position updates are sent to the robot (either joint space or Cartesian space).

---

## 2.Joint-Level Control and Data Structures

These classes represent joint rotations, joint states, and joint-based commands.

```python
ArmJointRotations
ArmJointRotationsList
JointRotations
JointAngles
JointAnglesArray
JointPoseRequest
JointPoseResponse
JointState
JointStateDisturbance
JointsPositionResponse
JointsStateResponse
```

These structures are used when controlling or querying the robot in joint space.

---

## 3.Cartesian / Pose-Based Motion Control

These classes relate to Cartesian (XYZ + orientation) control.

```python
CartesianOffsetRequest
CartesianPoseRequest
CombinedArmPosition
PoseDistanceRequest
PoseOperationsRequest
```

Purpose:
These allow the robot to be controlled in Cartesian coordinates instead of individual joint angles.

`TooltipPosition` and `PositionAndOrientation` belong conceptually to this category.

---

## 4.Motion Events and Streaming Feedback

These classes are related to execution monitoring and event streaming.

```python
ArmPositionUpdateEvent
ArmPositionUpdateEventStream
ArmPositionUpdateFailureEvent
ArmPositionUpdateCanceledEvent
ArmPositionUpdateRequestResponseEventStreamDetails
ArmPositionUpdateRequestResponseEventStreamSubscriptionKindEnum
ArmPositionUpdateRequestResponseFormat
ArmPositionUpdateRequestResponseKindEnum
```

Purpose:
These are used for monitoring movement execution, subscribing to status streams, and handling failures or cancellations.

---

## 5.Motion Limits and Dynamic Constraints

These classes define motion limits and behavior constraints.

```python
MaxJointAcclerations
MaxJointSpeeds
MaxJointTorques
SpeedProfile
MovementKindEnum
```

Purpose:
 They configure how motion is executed:

- Maximum speed
- Acceleration limits
- Torque limits
- Motion interpolation style (e.g., linear vs joint)

------

## 6.Gripper and Peripheral Device Control

These classes control end-effectors and hardware I/O.

```python
IOStateUpdateRequest
DHAGGripperCommandRequest
DHCGIGripperCommandRequest
DHPGCGripperCommandRequest
OnRobot2FG14GripperCommandRequest
OnRobot2FG7GripperCommandRequest
OnRobot3FG15GripperCommandRequest
Robotiq2FGripperCommandRequest
RobotiqEPickGripperCommandRequest
SchunkEGxGripperCommandRequest
```

Purpose:
These are used for controlling grippers and external actuators.

------

## 7.System-Level and Operational Control

These classes manage higher-level system functions.

```python
StartRecordingRequest
StopRecordingRequest
PlayRoutineRequest
SaveRecordingRequest
ToggleRecorderBotRequest
ToggleTeleopBotRequest
ROSControlUpdateRequest
RegisterPeerRequest
UnregisterPeerRequest
TriggerFaultRequest
```

Purpose:

- Recording and playback of routines
- Teleoperation toggling
- ROS integration
- Fault handling
- System registration
