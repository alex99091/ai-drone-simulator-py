import torch

class HumanDetector:
    def __init__(self):
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', trust_repo=True)
        self.model.classes = [0]  # Person only

    def detect(self, frame):
        results = self.model(frame)
        return results.xyxy[0].cpu().numpy()