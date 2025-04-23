import cv2

class Visualizer:
    @staticmethod
    def get_center_of_largest_person(boxes):
        if boxes is None or len(boxes) == 0:
            return None
        largest = max(boxes, key=lambda box: (box[2]-box[0]) * (box[3]-box[1]))
        x1, _, x2, _ = largest[:4]
        return int((x1 + x2) / 2)

    @staticmethod
    def draw(frame, boxes, drone_x):
        for box in boxes:
            x1, y1, x2, y2, *_ = map(int, box)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(frame, (drone_x - 10, 10), (drone_x + 10, 30), (255, 0, 0), -1)
        return frame
