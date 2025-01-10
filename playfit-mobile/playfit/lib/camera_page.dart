import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:playfit/workout_analyzer.dart';
import 'package:playfit/image_converter.dart';

class CameraView extends StatefulWidget {
  const CameraView({super.key});

  @override
  State<CameraView> createState() => _CameraViewState();
}

class _CameraViewState extends State<CameraView> {
  CameraController? _controller;
  bool _isDetecting = false;
  final WorkoutAnalyzer _workoutAnalyzer = WorkoutAnalyzer();

  @override
  void initState() {
    super.initState();
    initCamera();
  }

  Future<void> initCamera() async {
    final cameras = await availableCameras();
    _controller = CameraController(
      cameras.firstWhere(
          (camera) => camera.lensDirection == CameraLensDirection.front),
      ResolutionPreset.medium,
    );
    await _controller?.initialize();

    if (mounted) {
      setState(() {});
    }

    _controller?.startImageStream((image) async {
      if (_isDetecting) {
        return;
      }

      _isDetecting = true;
      try {
        final inputImage = ImageUtils.getInputImage(image, _controller);
        await _workoutAnalyzer.detectWorkout(inputImage, WorkoutType.squat);
      } catch (e) {
        debugPrint('Error processing image: $e');
      } finally {
        _isDetecting = false;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pose Estimation'),
      ),
      body: _controller != null && _controller!.value.isInitialized
          ? Stack(
              children: [
                CameraPreview(_controller!),
                Align(
                  alignment: Alignment.bottomCenter,
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: ValueListenableBuilder<Map<WorkoutType, int>>(
                      valueListenable: _workoutAnalyzer.workoutCounts,
                      builder: (context, workoutCounts, child) {
                        return Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              'Count: ${workoutCounts[WorkoutType.squat]}',
                              style: const TextStyle(
                                color: Colors.black,
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        );
                      },
                    ),
                  ),
                ),
              ],
            )
          : const Center(child: CircularProgressIndicator()),
    );
  }

  @override
  void dispose() {
    _workoutAnalyzer.dispose();
    _controller?.dispose();
    super.dispose();
  }
}
