import torch

# YOLOv5s 모델 로드 (최초 실행 시 자동 다운로드됨)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# 샘플 이미지 URL
img = 'https://ultralytics.com/images/zidane.jpg'

# 객체 감지 실행
results = model(img)

# 결과 출력
results.print()   # 콘솔에 감지 결과 출력
results.show()    # 이미지 창으로 감지 결과 시각화
