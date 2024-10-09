# 서론
 기존에 지정된 구역을 감시, 기록하는 CCTV 장치는 범죄 예방 가능성을 향상시키고 사후 처리를 수월하게 만들어주는 장치 및 시스템을 가지고 있다. 또한 액티브 트래킹 기능을 가지고 있는 카메라의 경우 감시구역에 들어온 물체를 지속적으로 따라가며 촬영하거나 이상 징후를 트래킹하며 관찰할 수 있는 시스템을 가지고 있기도 하다. 하지만 이러한 CCTV 카메라의 경우 여러 복잡한 상황 속에서 능동적인 대처를 할 수 없으며 공간적 제약과 같은 한계를 분명하게 가지고 있다. 이에 따라 최근 국내 드론 시장 규모가 급격하게 성장하고 있고 드론이 다양한 산업 분야에 활용되고 있음에 주목하여 현대사회, 특히 대한민국의 치안에 중대한 역할을 하고 있는 CCTV 카메라를 대체하며 상위호환 역할을 수행할 수 있는 다목적 순찰 드론을 연구하였다. 먼저 사용자와의 원활하고 직관적인 통신을 위한 GUI를 구현하고, 이에 따라 드론 기체에 존재하는 여러 센서 및 카메라를 활용하여 현재 위치를 특정하고 GUI에 표시할 수 있도록 한다. 장애물 감지는 적외선 센서(tof), 위치 특정은 기체 하단의 이미지 센서를 통한 mission pad 인식, 화재 감지 및 얼굴 인식은 카메라를 통해 받아온 frame을 이미지 처리하여 구현한다. 이를 통해 평시에는 정해진 루트를 반복하며 순찰하며 특이사항이 발생하지 않았는지 검사하는 향상된 CCTV 역할을 자동화하여 수행할 수 있고, 특수 상황 발생 시 GUI에 상대적인 위치를 marking하여 위치 정보를 제공하고, 미리 타겟으로 삼은 대상을 발견할 시 해당하는 대상을 추적하여 특정 상황을 해결함에 있어 큰 역할을 수행할 수 있도록 한다.

# 주요 기능

![image](https://github.com/user-attachments/assets/6d0356a2-603e-4dce-a5b9-f02121da4f8a)

# 주요 동작
![image](https://github.com/user-attachments/assets/bc334644-d2be-4b1e-8b09-ca6082b2f238)
![image](https://github.com/user-attachments/assets/741ed295-2163-42a4-8ef4-95a067c55761)
![image](https://github.com/user-attachments/assets/ff047d6c-525e-4a99-8142-fd41d604271f)


# 시스템 흐름도
![image](https://github.com/user-attachments/assets/6dae22a5-af9a-48ab-a548-ed7d5b27c443)
![image](https://github.com/user-attachments/assets/e51d896e-35b7-45c4-8ce1-f0c0408eeb85)
![image](https://github.com/user-attachments/assets/a40d5ef1-5909-4c37-a15c-4dc5b8a0ff4e)

# 사용 AI Model 소개
Face Recognition : Google사 Mediapipe, Dlib

먼저 google사에서 개발한 mediapipe는 주로 인체를 대상으로 컴퓨터 비전 인식 기능을 탑재하고 있는 여러 service를 제공한다. AI modeling이 이미 되어 있는 face detection 기능을 사용하였다. python의 with 구문을 통해 해당 face detection class에서 탐지한 좌표를 얻어 와서 본 논문의 주제에 활용한다.
dlib는 인공신경망 model인 ResNet-34에서 주로 영감을 얻어 신경망을 재구성됐으며 높은 정확도를 가지는 얼굴 인식 모델이다. 학습시키길 원하는 사람의 사진을 해당 모듈의 함수에 upload하면 dlib는 해당 사진에서 vector scaling을 통해 얼굴을 추출하여 학습한다. 이후 관련된 함수를 통해 새로운 frame 또는 image를 가져오면 학습된 얼굴인지를 파악하고 이름을 labeling 할 수 있으며 mediapipe와 마찬가지로 좌표 또한 얻어올 수 있다. 얻어온 좌표들을 활용해 해당 모듈들을 switching하며 모듈 통합 알고리즘을 구현한다.

Fire Detection : AlexNet, InceptionVX

![image](https://github.com/user-attachments/assets/40a73392-451b-4c45-a6e3-82dd4b4ccb4f)
