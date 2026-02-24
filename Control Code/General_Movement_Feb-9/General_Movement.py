# Edited 2/9 Liv

#General Python Code to move the robot to a positon



from standardbots import models, StandardBotsRobot

sdk = StandardBotsRobot(
  url='http://192.168.110.5:3000',
  token='oetrwf0e-yyquw-8eopsk-z8egwu6g',
  robot_kind=StandardBotsRobot.RobotKind.Live,
)

with sdk.connection():
 # sdk.movement.enable().ok()
 # sdk.movement.brakes.unbrake().ok()
  sdk.movement.position.move(
    position=models.Position(
      unit_kind=models.LinearUnitKind.Meters,
      x=0.5,
      y=0.0,
      z=0.5,
    ),
    orientation=models.Orientation(
      kind=models.OrientationKindEnum.Quaternion,
      quaternion=models.Quaternion(1.0, 0.0, -1.0, 0.0),
    ),
  )#.ok()