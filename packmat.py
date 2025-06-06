import cv2
from ultralytics import YOLO
from collections import defaultdict
from flask import Blueprint, request, jsonify

class ObjectTracker:
    def __init__(self):
        self.tracks = defaultdict(lambda: {"centroid": None, "counted": False})

    def update_tracks(self, detected_objects, line_y, counter):
        new_tracks = defaultdict(lambda: {"centroid": None, "counted": False})
        for obj_id, track in self.tracks.items():
            track["matched"] = False

        for centroid, bbox in detected_objects:
            matched_id = None
            min_distance = float("inf")

            for obj_id, track in self.tracks.items():
                prev_centroid = track["centroid"]
                if prev_centroid is None:
                    continue
                distance = ((centroid[0] - prev_centroid[0]) ** 2 + (centroid[1] - prev_centroid[1]) ** 2) ** 0.5
                if distance < min_distance and distance < 50:
                    min_distance = distance
                    matched_id = obj_id

            if matched_id is not None:
                new_tracks[matched_id] = self.tracks[matched_id]
                new_tracks[matched_id]["centroid"] = centroid
                new_tracks[matched_id]["bbox"] = bbox
                new_tracks[matched_id]["matched"] = True

                if not new_tracks[matched_id]["counted"] and self.crosses_line(centroid, line_y):
                    counter += 1
                    new_tracks[matched_id]["counted"] = True
            else:
                new_id = len(new_tracks) + 1
                new_tracks[new_id] = {"centroid": centroid, "bbox": bbox, "counted": False, "matched": True}

        self.tracks = {obj_id: track for obj_id, track in new_tracks.items() if track["matched"]}
        return counter

    @staticmethod
    def crosses_line(centroid, line_y):
        _, cy = centroid
        return line_y - 5 <= cy <= line_y + 5


class VideoProcessor:
    def __init__(self, video_path, output_path, model_path=r"jerrycan_bundle_detection.pt", line_y=250):
        self.cap = cv2.VideoCapture(video_path)
        self.model = YOLO(model_path)
        self.output_path = output_path
        self.line_y = line_y
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_time_ms = int(1000 / self.fps)
        self.output_video = cv2.VideoWriter(
            output_path, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, (self.frame_width, self.frame_height)
        )
        self.counter = 0
        self.tracker = ObjectTracker()

    def process_video(self):
        if not self.cap.isOpened():
            raise ValueError("Error: Could not open video.")

        frame_id = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Video ended.")
                break

            frame_id += 1
            results = self.model(frame, conf=0.50)
            cv2.line(frame, (0, self.line_y), (self.frame_width, self.line_y), (255, 255, 255), 2)
            detected_objects = self.process_detections(results, frame)
            self.counter = self.tracker.update_tracks(detected_objects, self.line_y, self.counter)
            self.display_counter(frame)
            self.output_video.write(frame)

        self.cleanup()
        return self.counter

    def process_detections(self, results, frame):
        detected_objects = []
        for result in results[0].boxes:
            xyxy = result.xyxy[0].tolist()
            cls = int(result.cls[0])
            if cls == 0:
                x1, y1, x2, y2 = map(int, xyxy)
                centroid = self.get_centroid(x1, y1, x2, y2)
                detected_objects.append((centroid, (x1, y1, x2, y2)))
                self.draw_detection(frame, x1, y1, x2, y2, centroid)
        return detected_objects

    @staticmethod
    def get_centroid(x1, y1, x2, y2):
        return (x1 + x2) // 2, (y1 + y2) // 2

    @staticmethod
    def draw_detection(frame, x1, y1, x2, y2, centroid):
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.circle(frame, centroid, 5, (0, 0, 255), -1)
        cv2.putText(frame, "jerrycan_bundle", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def display_counter(self, frame):
        cv2.putText(frame, f"Counter: {self.counter}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def cleanup(self):
        self.cap.release()
        self.output_video.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    video_path = r'check-video.mp4'
    model_path = r'jerrycan_bundle_detection.pt'
    output_path = r'output_video.mp4'

    video_processor = VideoProcessor(video_path, output_path, model_path)
    count = video_processor.process_video()
    print(f"Total objects counted: {count}")
