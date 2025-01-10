import 'dart:math';
import 'package:flutter/material.dart';
import 'package:google_mlkit_pose_detection/google_mlkit_pose_detection.dart';

enum WorkoutType {
  squat,
  jumpingJack,
  pushUp,
  pullUp,
}

class WorkoutAnalyzer {
  final PoseDetector _poseDetector = PoseDetector(
    options: PoseDetectorOptions(
      mode: PoseDetectionMode.stream,
    ),
  );
  ValueNotifier<Map<WorkoutType, int>> workoutCounts = ValueNotifier({
    WorkoutType.squat: 0,
    WorkoutType.jumpingJack: 0,
    WorkoutType.pushUp: 0,
    WorkoutType.pullUp: 0,
  });
  final Map<WorkoutType, bool> _workoutStatus = {
    WorkoutType.squat: false,
    WorkoutType.jumpingJack: false,
    WorkoutType.pushUp: false,
    WorkoutType.pullUp: false,
  };

  Future<void> detectWorkout(InputImage inputImage, WorkoutType workout) async {
    try {
      final poses = await _poseDetector.processImage(inputImage);

      if (poses.isEmpty) {
        return;
      }

      final pose = poses.first;

      switch (workout) {
        case WorkoutType.squat:
          detectSquat(pose);
          break;
        case WorkoutType.jumpingJack:
          detectJumpingJack(pose);
          break;
        case WorkoutType.pushUp:
          detectPushUp(pose);
          break;
        case WorkoutType.pullUp:
          detectPullUp(pose);
          break;
      }
    } catch (e) {
      debugPrint('Error detection pose: $e');
    }
  }

  void detectSquat(Pose pose) {
    final leftHip = pose.landmarks[PoseLandmarkType.leftHip];
    final rightHip = pose.landmarks[PoseLandmarkType.rightHip];
    final leftKnee = pose.landmarks[PoseLandmarkType.leftKnee];
    final rightKnee = pose.landmarks[PoseLandmarkType.rightKnee];
    final leftAnkle = pose.landmarks[PoseLandmarkType.leftAnkle];
    final rightAnkle = pose.landmarks[PoseLandmarkType.rightAnkle];

    if (leftHip == null ||
        rightHip == null ||
        leftKnee == null ||
        rightKnee == null ||
        leftAnkle == null ||
        rightAnkle == null) {
      return;
    }

    final leftKneeAngle = calculateAngle(leftHip, leftKnee, leftAnkle);
    final rightKneeAngle = calculateAngle(rightHip, rightKnee, rightAnkle);

    if (leftKneeAngle <= 90 || rightKneeAngle <= 90) {
      if (!_workoutStatus[WorkoutType.squat]!) {
        incrementWorkoutCount(WorkoutType.squat);
        _workoutStatus[WorkoutType.squat] = true;
      }
    } else {
      _workoutStatus[WorkoutType.squat] = false;
    }
  }

  void detectJumpingJack(Pose pose) {
    final leftShoulder = pose.landmarks[PoseLandmarkType.leftShoulder];
    final rightShoulder = pose.landmarks[PoseLandmarkType.rightShoulder];
    final leftHip = pose.landmarks[PoseLandmarkType.leftHip];
    final rightHip = pose.landmarks[PoseLandmarkType.rightHip];
    final leftAnkle = pose.landmarks[PoseLandmarkType.leftAnkle];
    final rightAnkle = pose.landmarks[PoseLandmarkType.rightAnkle];

    if (leftShoulder == null ||
        rightShoulder == null ||
        leftHip == null ||
        rightHip == null ||
        leftAnkle == null ||
        rightAnkle == null) {
      return;
    }

    // Determine if the detected pose is a jumping jack
    final shoulderDistance = (leftShoulder.x - rightShoulder.x).abs();
    final hipDistance = (leftHip.x - rightHip.x).abs();
    final ankleDistance = (leftAnkle.x - rightAnkle.x).abs();

    // Define criteria for detecting jumping jack more robustly
    final shoulderToHipRatio = shoulderDistance / hipDistance;
    final ankleToHipRatio = ankleDistance / hipDistance;

    // Additional checks for jumping jack movement (optional)
    bool armsUp = leftShoulder.y < leftHip.y && rightShoulder.y < rightHip.y;
    bool legsApart = ankleDistance > hipDistance * 1.5;

    if (shoulderToHipRatio > 1.5 &&
        ankleToHipRatio < 2.0 &&
        armsUp &&
        legsApart) {
      if (!_workoutStatus[WorkoutType.jumpingJack]!) {
        incrementWorkoutCount(WorkoutType.jumpingJack);
        _workoutStatus[WorkoutType.jumpingJack] = true;
      }
    } else {
      _workoutStatus[WorkoutType.jumpingJack] = false;
    }
  }

  void detectPushUp(Pose pose) {
    final leftWrist = pose.landmarks[PoseLandmarkType.leftWrist];
    final rightWrist = pose.landmarks[PoseLandmarkType.rightWrist];
    final leftElbow = pose.landmarks[PoseLandmarkType.leftElbow];
    final rightElbow = pose.landmarks[PoseLandmarkType.rightElbow];
    final leftShoulder = pose.landmarks[PoseLandmarkType.leftShoulder];
    final rightShoulder = pose.landmarks[PoseLandmarkType.rightShoulder];

    if (leftWrist == null ||
        rightWrist == null ||
        leftElbow == null ||
        rightElbow == null ||
        leftShoulder == null ||
        rightShoulder == null) {
      return;
    }

    final leftElbowAngle = calculateAngle(leftShoulder, leftElbow, leftWrist);
    final rightElbowAngle =
        calculateAngle(rightShoulder, rightElbow, rightWrist);

    // final chestY = (leftShoulder.y + rightShoulder.y) / 2;
    // const double groundThreshold = 400;
    const double elbowAngleThreshold = 90;

    if (leftElbowAngle <= elbowAngleThreshold &&
        rightElbowAngle <= elbowAngleThreshold) {
      debugPrint('Elbow angle: $leftElbowAngle, $rightElbowAngle');
      // debugPrint('Chest Y: $chestY');
      if (!_workoutStatus[WorkoutType.pushUp]!) {
        incrementWorkoutCount(WorkoutType.pushUp);
        _workoutStatus[WorkoutType.pushUp] = true;
      }
    } else {
      _workoutStatus[WorkoutType.pushUp] = false;
    }
  }

  void detectPullUp(Pose pose) {
    final leftWrist = pose.landmarks[PoseLandmarkType.leftWrist];
    final rightWrist = pose.landmarks[PoseLandmarkType.rightWrist];
    final leftElbow = pose.landmarks[PoseLandmarkType.leftElbow];
    final rightElbow = pose.landmarks[PoseLandmarkType.rightElbow];
    final leftShoulder = pose.landmarks[PoseLandmarkType.leftShoulder];
    final rightShoulder = pose.landmarks[PoseLandmarkType.rightShoulder];

    if (leftShoulder == null ||
        rightShoulder == null ||
        leftElbow == null ||
        rightElbow == null ||
        leftWrist == null ||
        rightWrist == null) {
      return;
    }

    final leftElbowAngle = calculateAngle(leftWrist, leftElbow, leftShoulder);
    final rightElbowAngle =
        calculateAngle(rightWrist, rightElbow, rightShoulder);

    const double elbowAngleThreshold = 40.0;

    if ((leftElbowAngle <= elbowAngleThreshold &&
        rightElbowAngle <= elbowAngleThreshold)) {
      if (!_workoutStatus[WorkoutType.pullUp]!) {
        incrementWorkoutCount(WorkoutType.pullUp);
        _workoutStatus[WorkoutType.pullUp] = true;
      }
    } else {
      _workoutStatus[WorkoutType.pullUp] = false;
    }
  }

  double calculateAngle(PoseLandmark a, PoseLandmark b, PoseLandmark c) {
    final aPoint = Offset(a.x, a.y);
    final bPoint = Offset(b.x, b.y);
    final cPoint = Offset(c.x, c.y);

    final vectorBA = Offset(aPoint.dx - bPoint.dx, aPoint.dy - bPoint.dy);
    final vectorBC = Offset(cPoint.dx - bPoint.dx, cPoint.dy - bPoint.dy);

    final dotProduct = vectorBA.dx * vectorBC.dx + vectorBA.dy * vectorBC.dy;
    final magnitudeBA =
        sqrt(vectorBA.dx * vectorBA.dx + vectorBA.dy * vectorBA.dy);
    final magnitudeBC =
        sqrt(vectorBC.dx * vectorBC.dx + vectorBC.dy * vectorBC.dy);

    final cosine = dotProduct / (magnitudeBA * magnitudeBC);
    final angle = acos(cosine) * 180 / pi;

    return angle;
  }

  void incrementWorkoutCount(WorkoutType workoutType) {
    workoutCounts.value = {
      ...workoutCounts.value,
      workoutType: workoutCounts.value[workoutType]! + 1,
    };
  }

  void dispose() {
    _poseDetector.close();
  }
}
