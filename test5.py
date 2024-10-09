import cv2
import mediapipe as mp
import time
from imutils import face_utils 
import matplotlib.pyplot as plt 
import numpy as np 
import argparse 
import imutils 
import dlib 
import cv2 
import face_recognition

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
known_face_encodings = [] 
known_face_names = []
held_count = 0
held_center_x = []
held_center_y = []
held_start_point = []
held_end_point = []
names = []
held_dic = {}

def add_known_face(face_image_path, name):
    face_image = cv2.imread(face_image_path)
    face_location = face_recognition.face_locations(face_image)[0]
    face_encoding = face_recognition.face_encodings(face_image)[0]
    
    known_face_encodings.append(face_encoding)
    known_face_names.append(name)

def name_labeling(input_image, dic):
    results = []
    count = 0
    t1 = time.time()
    image = input_image.copy()
    image = cv2.resize(image, (0, 0), fx = 0.25, fy = 0.25)
    face_locations = face_recognition.face_locations(image)
    num = 0

    if dic == {} :
       pass
    else :
       for name in list(dic.keys()) :
          count = 0
          for (top, right, bottom, left) in face_locations :
             top *= 4
             right *= 4
             bottom *= 4
             left *= 4
             tmpx = (right + left)/2
             tmpy = (top + bottom)/2
             if abs(dic[name][0]-tmpx) < 50 and abs(dic[name][1]-tmpy) < 50 :
                results.append([left, top, right, bottom, name])
                del face_locations[count]
             count += 1

    t2 = time.time() - t1
    t3 = time.time()
    face_encodings = face_recognition.face_encodings(image, face_locations)
    t4 = time.time() - t3
    face_names = []

    print(t4)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Unknown%d" %num
 
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
 
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
 
        face_names.append(name)
        num += 1
    
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        count += 1
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        results.append([left, top, right, bottom, name])
    if count :
        return results
    else :
        return

add_known_face('c:/face/kimtaeri.jpg', 'KIMTAERI')
add_known_face("c:/face/Mingang.jpg", "Mingang")
add_known_face("c:/face/Queen.jpg", "Queen")
add_known_face("c:/face/JaehwanLee.jpg", "JaehwanLee")

cap = cv2.VideoCapture(0)
with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=1) as face_detection:
  while cap.isOpened():
    count = 0
    test = []
    sorted_test = []
    center_x = []
    center_y = []
    sub_count = 0
    sub_count2 = 0
    sub_count3 = 0
    suc_count = 0

    temp = {}
    temp2 = {}
    temp4 = {}
    temp3 = []

    t1 = time.time()
    success, image = cap.read()
    if not success:
      break

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = face_detection.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.detections:
      for detection in results.detections:
        count += 1
        
        test.append(mp_drawing.draw_detection(image, detection))

        held_start_point.append((0, 0))
        held_end_point.append((0, 0))

      for point in test :
         if point[0] == None and point[1] == None :
            count -= 1
         elif point[0] == None :
            temp[point[1]] = point[0]
         elif point[1] == None :
            temp2[point[0]] = point[1]
         else :
            temp4[point[0]] = point[1]

      if len(temp4) == 0 :
         temp3 = list(temp.keys()) + list(temp2.keys())
         temp3 = sorted(temp3)
         for point in temp3 :
            if point in temp.keys() :
               sorted_test.append([temp[point], point])
            elif point in temp2.keys() :
               sorted_test.append([point, temp2[point]])

      else :
        temp3 = list(temp.keys()) + list(temp2.keys()) + list(temp4.keys())
        temp3 = sorted(temp3)
        for point in temp3 :
           if point in temp.keys() :
              sorted_test.append([temp[point], point])
           elif point in temp2.keys() :
               sorted_test.append([point, temp2[point]])
           elif point in temp4.keys() :
               sorted_test.append([point, temp4[point]])

      #print(sorted_test)

      for point in sorted_test :
        if point[0] == None and point[1] == None :
          pass
        elif point[0] == None :
          a = (held_start_point[sub_count3][0] + point[1][0] - held_end_point[sub_count3][0], held_start_point[sub_count3][1] + point[1][1] - held_end_point[sub_count3][1])
          cv2.rectangle(image, a, point[1], (255, 255, 255), 2)
          held_start_point[sub_count3] = a
          held_end_point[sub_count3] = point[1]
        elif point[1] == None :
          b = (held_end_point[sub_count3][0] + point[0][0] - held_start_point[sub_count3][0], held_end_point[sub_count3][1] + point[0][1] - held_start_point[sub_count3][1])
          cv2.rectangle(image, point[0], b, (255, 255, 255), 2)
          held_end_point[sub_count3] = b
          held_start_point[sub_count3] = point[0]
        else :
          held_start_point[sub_count3] = point[0]
          held_end_point[sub_count3] = point[1]
        sub_count3 += 1

      sub_count3 = 0

      for n in range(0, count) :
        center_x.append((held_start_point[n][0] + held_end_point[n][0])/2)
        center_y.append((held_start_point[n][1] + held_end_point[n][1])/2)

      copy_hsp = held_start_point
      copy_hep = held_end_point

      if held_count < count :
        c1 = name_labeling(image, held_dic)
        num = 0

        if c1 :
            names = []
            held_center_x = []
            held_center_y = []
            held_dic = {}

            font = cv2.FONT_HERSHEY_DUPLEX
            for info in c1 :
                names.append(info[4])
                cv2.putText(image, info[4], (info[2], info[3]), font, 1, (0, 0, 0), 1)
                held_center_x.append(int((info[0]+info[2])/2))
                held_center_y.append(int((info[1]+info[3])/2))

            for x, y in zip(center_x, center_y) :
               for hx, hy in zip(held_center_x, held_center_y) :
                  if abs(x - hx) < 50 and abs(y - hy) < 50 :
                     del copy_hsp[sub_count3]
                     del copy_hep[sub_count3]
               sub_count3 += 1
            sub_count3 = 0

            if len(c1) < count :
               for hsp, hep in zip(copy_hsp, copy_hep) :
                  if hsp == (0, 0) and hep == (0, 0) :
                    pass
                  else :
                    names.append('Unidentified%d' %num)
                    held_center_x.append((hsp[0]+hep[0])/2)
                    held_center_y.append((hsp[1]+hep[1])/2)
                    num += 1

            temp = {tx : name for tx, name in zip(held_center_x, names)}
            temp2 = {tx : ty for tx, ty in zip(held_center_x, held_center_y)}
            temp = dict(sorted(temp.items()))
            temp2 = dict(sorted(temp2.items()))
            held_center_x.sort()
            held_center_y = list(temp2.values())
            names = list(temp.values())
            for name, c in zip(names, range(0, count)) :
               held_dic[name] = [held_center_x[c], held_center_y[c]]
        else :
            count = 0

      elif held_count == count :
        for x, y in zip(center_x, center_y) :
           for name in list(held_dic.keys()) :
              #print(held_dic, names, count)

              if abs(x - held_dic[name][0]) < 50 and abs(y - held_dic[name][1]) < 50 :
                 cv2.putText(image, name, held_end_point[sub_count], font, 1, (0, 0, 0), 1)
                 held_dic[name] = [x, y]
                 suc_count += 1
           sub_count += 1
        sub_count = 0
        if suc_count == count :
           pass
        else :
           count = 0

      else :
        for x, y in zip(center_x, center_y) :
           for name in list(held_dic.keys()) :
              #print(held_dic, names)

              if abs(x - held_dic[name][0]) < 50 and abs(y - held_dic[name][1]) < 50 :
                 cv2.putText(image, name, held_end_point[sub_count], font, 1, (0, 0, 0), 1)
                 held_dic[name] = [x, y]
              else :
                 del held_dic[name]
                 names.remove(name)
           sub_count += 1

    else :
      names = []
      held_center_x = []
      held_center_y = []
      held_dic = {}
      test = None

    #print(held_dic, names, count)
    held_count = count
    cv2.imshow('MediaPipe Face Detection', image)
    if cv2.waitKey(1) & 0xFF == 27:
      break
    t2 = time.time() - t1
    #print(t2)
cap.release()