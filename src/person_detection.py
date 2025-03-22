import cv2
import numpy as np
from ultralytics import YOLO
import os

class PersonDetector:
    def __init__(self):
        # Initialize YOLO model
        self.model = YOLO('yolov8n.pt')
        
    def process_video(self, video_path, output_path=None):
        """
        Process a video file and count people
        Returns the total count of people detected and cumulative counts
        """
        if output_path is None:
            output_path = 'output_' + os.path.basename(video_path)
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Error opening video file")
            
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Initialize video writer with H.264 codec
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # Using H.264 codec
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            # Fallback to XVID if H.264 is not available
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            output_path = output_path.replace('.mp4', '.avi')  # Change extension to .avi
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        total_people = 0
        frame_count = 0
        cumulative_counts = []
        total_unique_people = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            # Run YOLO detection
            results = self.model(frame)
            
            # Process detections
            people_count = 0
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Only count if it's a person (class 0 in COCO dataset)
                    if box.cls == 0:
                        people_count += 1
                        # Draw bounding box
                        x1, y1, x2, y2 = box.xyxy[0]
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # Update counts
            total_people = max(total_people, people_count)
            total_unique_people += people_count
            cumulative_counts.append(people_count)
            
            # Add count text to frame
            cv2.putText(frame, f'Current Count: {people_count}', (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Max Count: {total_people}', (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Total People: {total_unique_people}', (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Write frame to output video
            out.write(frame)
            frame_count += 1
            
        # Release resources
        cap.release()
        out.release()
        
        return {
            'total_count': total_people,
            'total_unique_people': total_unique_people,
            'cumulative_counts': cumulative_counts,
            'output_path': output_path
        } 