import ray
import robomaster
from robomaster import robot
import numpy as np
import cv2
import pygame

import tflearn
from tflearn.layers.core import input_data, dropout, fully_connected
from tflearn.layers.conv import conv_2d, max_pool_2d, avg_pool_2d, global_avg_pool
from tflearn.layers.normalization import local_response_normalization, batch_normalization
from tflearn.layers.merge_ops import merge
from tflearn.layers.estimator import regression
import os

import mediapipe as mp
import face_recognition
import imutils 
from imutils import face_utils
import dlib

def init():
	pygame.init()
	win = pygame.display.set_mode((400, 400))

def getKey(keyName):
	ans = False
	for eve in pygame.event.get(): pass
	keyInput = pygame.key.get_pressed()
	myKey = getattr(pygame, 'K_{}'.format(keyName))
	if keyInput[myKey]:
		ans = True
	pygame.display.update()
	return ans

@ray.remote
class Engine(object) :

    def __init__(self, type = None) :
        self._type = type
        
        if type == 'drone' :
            self._engine_on = False
            robomaster.config.LOCAL_IP_STR = "192.168.10.2"
            self._drone = robot.Drone()
            self._drone.initialize()
            self._drone_tof = self._drone.sensor
            self._drone_flight = self._drone.flight
            self._drone_flight.mission_pad_on()
            self._drone_cam = self._drone.camera
            self._drone_cam.start_video_stream(False)

            self._isTakeoff = 0
            self._isMoving = 0
            self._autoSpeed = 25
            
            self._ex_tof = None
            self._ex_frame = None
            self._ex_mid = 1.0
        
        elif type == 'frame' :
            self._engine_on = False

            self._font = cv2.FONT_HERSHEY_DUPLEX
            self._mp_face_detection = mp.solutions.face_detection
            self._mp_drawing = mp.solutions.drawing_utils
            self._known_encodings = []
            self._known_names = []
            self._held_count = 0
            self._held_center_x = []
            self._held_center_y = []
            self._held_start_point = []
            self._held_end_point = []
            self._names = []
            self._held_dic = {}
            self._eyes_dic = {}
            self._squares_dic = {}
            self._camOn = False

            self.add_knowns("c:/face/wonbin.jpg", "Wonbin")
            self.add_knowns("c:/face/kimtaeri.jpg", "Taeri Kim")
            self.add_knowns("c:/face/junyunjin.jpg", "Yunjin Jun")
            self.add_knowns("c:/face/JaehwanLee.jpg", "Jaehwan Lee")

        elif type == 'fire detection' :
            self._engine_on = False
            self._model = self.construct_inception(224, 224, training = False)
            self._model.load(os.path.join("models/InceptionV1-OnFire", "inceptiononv1onfire"), weights_only = True)
            self._rows = 224
            self._cols = 224

    def camera_on(self) :
        self._camOn = True
        return
    
    def camera_off(self) :
        self._camOn = False
        cv2.destroyAllWindows()
        return

    def re_sensing(self) :
        self._held_count = 0
        return

    def autoUp(self) :
        if self._autoSpeed == 60 :
            return
        self._autoSpeed += 1
        return
    
    def autoDown(self) :
        if self._autoSpeed == 10 :
            return
        self._autoSpeed -= 1
        return

    def drone_off(self) :
        self._drone.close()
        return

    def mid_check(self, mid = None) :
        if self._ex_mid == mid or mid == -1.0 :
            pass
        else :
            self._isMoving = 0

    def set_engine(self) :
        self._engine_on = True
        return

    def construct_inception(self, x, y, training = False) :
        network = input_data(shape=[None, y, x, 3])

        conv1_7_7 = conv_2d(network, 64, 5, strides=2, activation='relu', name = 'conv1_7_7_s2')

        pool1_3_3 = max_pool_2d(conv1_7_7, 3,strides=2)
        pool1_3_3 = local_response_normalization(pool1_3_3)

        conv2_3_3_reduce = conv_2d(pool1_3_3, 64,1, activation='relu',name = 'conv2_3_3_reduce')
        conv2_3_3 = conv_2d(conv2_3_3_reduce, 128,3, activation='relu', name='conv2_3_3')

        conv2_3_3 = local_response_normalization(conv2_3_3)
        pool2_3_3 = max_pool_2d(conv2_3_3, kernel_size=3, strides=2, name='pool2_3_3_s2')

        inception_3a_1_1 = conv_2d(pool2_3_3, 64, 1, activation='relu', name='inception_3a_1_1')

        inception_3a_3_3_reduce = conv_2d(pool2_3_3, 96,1, activation='relu', name='inception_3a_3_3_reduce')
        inception_3a_3_3 = conv_2d(inception_3a_3_3_reduce, 128,filter_size=3,  activation='relu', name = 'inception_3a_3_3')
        inception_3a_5_5_reduce = conv_2d(pool2_3_3,16, filter_size=1,activation='relu', name ='inception_3a_5_5_reduce' )
        inception_3a_5_5 = conv_2d(inception_3a_5_5_reduce, 32, filter_size=5, activation='relu', name= 'inception_3a_5_5')
        inception_3a_pool = max_pool_2d(pool2_3_3, kernel_size=3, strides=1, )
        inception_3a_pool_1_1 = conv_2d(inception_3a_pool, 32, filter_size=1, activation='relu', name='inception_3a_pool_1_1')

        inception_3a_output = merge([inception_3a_1_1, inception_3a_3_3, inception_3a_5_5, inception_3a_pool_1_1], mode='concat', axis=3)

        inception_3b_1_1 = conv_2d(inception_3a_output, 128,filter_size=1,activation='relu', name= 'inception_3b_1_1' )
        inception_3b_3_3_reduce = conv_2d(inception_3a_output, 128, filter_size=1, activation='relu', name='inception_3b_3_3_reduce')
        inception_3b_3_3 = conv_2d(inception_3b_3_3_reduce, 192, filter_size=3,  activation='relu',name='inception_3b_3_3')
        inception_3b_5_5_reduce = conv_2d(inception_3a_output, 32, filter_size=1, activation='relu', name = 'inception_3b_5_5_reduce')
        inception_3b_5_5 = conv_2d(inception_3b_5_5_reduce, 96, filter_size=5,  name = 'inception_3b_5_5')
        inception_3b_pool = max_pool_2d(inception_3a_output, kernel_size=3, strides=1,  name='inception_3b_pool')
        inception_3b_pool_1_1 = conv_2d(inception_3b_pool, 64, filter_size=1,activation='relu', name='inception_3b_pool_1_1')

        inception_3b_output = merge([inception_3b_1_1, inception_3b_3_3, inception_3b_5_5, inception_3b_pool_1_1], mode='concat',axis=3,name='inception_3b_output')

        pool3_3_3 = max_pool_2d(inception_3b_output, kernel_size=3, strides=2, name='pool3_3_3')
        inception_4a_1_1 = conv_2d(pool3_3_3, 192, filter_size=1, activation='relu', name='inception_4a_1_1')
        inception_4a_3_3_reduce = conv_2d(pool3_3_3, 96, filter_size=1, activation='relu', name='inception_4a_3_3_reduce')
        inception_4a_3_3 = conv_2d(inception_4a_3_3_reduce, 208, filter_size=3,  activation='relu', name='inception_4a_3_3')
        inception_4a_5_5_reduce = conv_2d(pool3_3_3, 16, filter_size=1, activation='relu', name='inception_4a_5_5_reduce')
        inception_4a_5_5 = conv_2d(inception_4a_5_5_reduce, 48, filter_size=5,  activation='relu', name='inception_4a_5_5')
        inception_4a_pool = max_pool_2d(pool3_3_3, kernel_size=3, strides=1,  name='inception_4a_pool')
        inception_4a_pool_1_1 = conv_2d(inception_4a_pool, 64, filter_size=1, activation='relu', name='inception_4a_pool_1_1')

        inception_4a_output = merge([inception_4a_1_1, inception_4a_3_3, inception_4a_5_5, inception_4a_pool_1_1], mode='concat', axis=3, name='inception_4a_output')

        pool5_7_7 = avg_pool_2d(inception_4a_output, kernel_size=5, strides=1)
        if(training):
            pool5_7_7 = dropout(pool5_7_7, 0.4)
        loss = fully_connected(pool5_7_7, 2,activation='softmax')

        if(training):
            network = regression(loss, optimizer='momentum',
                                loss='categorical_crossentropy',
                                learning_rate=0.001)
        else:
            network = loss

        model = tflearn.DNN(network, checkpoint_path='inceptiononv1onfire',
                            max_checkpoints=1, tensorboard_verbose=2)

        return model

    def add_knowns(self, path, name) :
        face_image = cv2.imread(path)
        face_encoding = face_recognition.face_encodings(face_image)[0]

        self._known_encodings.append(face_encoding)
        self._known_names.append(name)

    def name_labeling(self, frame, dic) :
        results = []
        num = 0
        count = 0
        small_image = cv2.resize(frame, (0, 0), fx = 0.25, fy = 0.25)
        face_locations = face_recognition.face_locations(small_image)

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
                    if abs(dic[name][0] - tmpx) < 50 and abs(dic[name][1] - tmpy) < 50 :
                        results.append([left, top, right, bottom, name])
                        del face_locations[count]
                    count += 1

        face_encodings = face_recognition.face_encodings(small_image, face_locations)
        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self._known_encodings, face_encoding, tolerance=0.5)
            name = "Unknown%d" %num
 
            face_distances = face_recognition.face_distance(self._known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index] :
                name = self._known_names[best_match_index]
 
            face_names.append(name)
            num += 1
        
        for (top, right, bottom, left), name in zip(face_locations, face_names) :
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            count += 1
            results.append([left, top, right, bottom, name])

        if count :
            return results
        else :
            return

    def main_operation(self, command = None, held_frame = None) :
        if self._type == 'drone' :
            if command :
                if command == 'take off' :
                    self._drone_flight.takeoff()
                    self._isTakeoff = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == 'land' :
                    self._drone_flight.land()
                    self._isTakeoff = 0
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == 'stop' :
                    self._drone_flight.stop()
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command[0:6] == 'rotate' :
                    self._drone_flight.rotate(int(command[6:]))
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                
                elif command == '1to2' :
                    self._drone_flight.jump(0, 90, 80, self._autoSpeed, yaw = 90, mid1 = 'm1', mid2 = 'm2')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '1to3' :
                    self._drone_flight.jump(-90, 90, 80, self._autoSpeed, yaw = 135, mid1 = 'm1', mid2 = 'm3')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '1to4' :
                    self._drone_flight.jump(-90, 0, 80, self._autoSpeed, yaw = 180, mid1 = 'm1', mid2 = 'm4')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                
                elif command == '1to2x' :
                    self._drone_flight.curve(-30, 50, 80, 0, 100, 80, self._autoSpeed, mid = 'm1')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '1to3x' :
                    self._drone_flight.curve(-25, 70, 80, -100, 100, 80, self._autoSpeed, mid = 'm1')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '1to4x' :
                    self._drone_flight.curve(-50, 30, 80, -100, 0, 80, self._autoSpeed, mid = 'm1')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]

                elif command == '2to1' :
                    self._drone_flight.jump(0, -90, 80, self._autoSpeed, yaw = -90, mid1 = 'm2', mid2 = 'm1')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '2to3' :
                    self._drone_flight.jump(-90, 0, 80, self._autoSpeed, yaw = 180, mid1 = 'm2', mid2 = 'm3')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '2to4' :
                    self._drone_flight.jump(-90, -90, 80, self._autoSpeed, yaw = -135, mid1 = 'm2', mid2 = 'm4')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]

                elif command == '2to1x' :
                    self._drone_flight.curve(-30, -50, 80, 0, -100, 80, self._autoSpeed, mid = 'm2')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '2to3x' :
                    self._drone_flight.curve(-50, -30, 80, -100, 0, 80, self._autoSpeed, mid = 'm2')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '2to4x' :
                    self._drone_flight.curve(-70, -25, 80, -100, -100, 80, self._autoSpeed, mid = 'm2')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]

                elif command == '3to1' :
                    self._drone_flight.jump(90, -90, 80, self._autoSpeed, yaw = -45, mid1 = 'm3', mid2 = 'm1')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '3to2' :
                    self._drone_flight.jump(90, 0, 80, self._autoSpeed, yaw = 0, mid1 = 'm3', mid2 = 'm2')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '3to4' :
                    self._drone_flight.jump(0, -90, 80, self._autoSpeed, yaw = -90, mid1 = 'm3', mid2 = 'm4')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                
                elif command == '3to1x' :
                    self._drone_flight.curve(70, -25, 80, 100, -100, 80, self._autoSpeed, mid = 'm3')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '3to2x' :
                    self._drone_flight.curve(50, -30, 80, 100, 0, 80, self._autoSpeed, mid = 'm3')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '3to4x' :
                    self._drone_flight.curve(30, -50, 80, 0, -100, 80, self._autoSpeed, mid = 'm3')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]

                elif command == '4to1' :
                    self._drone_flight.jump(90, 0, 80, self._autoSpeed, yaw = 0, mid1 = 'm4', mid2 = 'm1')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '4to2' :
                    self._drone_flight.jump(90, 90, 80, self._autoSpeed, yaw = 45, mid1 = 'm4', mid2 = 'm2')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '4to3' :
                    self._drone_flight.jump(0, 90, 80, self._autoSpeed, yaw = 90, mid1 = 'm4', mid2 = 'm3')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                
                elif command == '4to1x' :
                    self._drone_flight.curve(50, 30, 80, 100, 0, 80, self._autoSpeed, mid = 'm4')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '4to2x' :
                    self._drone_flight.curve(25, 70, 80, 100, 100, 80, self._autoSpeed, mid = 'm4')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]
                elif command == '4to3x' :
                    self._drone_flight.curve(30, 50, 80, 0, 100, 80, self._autoSpeed, mid = 'm4')
                    self._isMoving = 1
                    return [[self._ex_mid, 0, 0], [0, 0, 0, self._ex_tof, self._ex_frame], [self._isTakeoff, 0, 0]]

                self._drone_flight.rc(command[0], command[1], command[2], command[3])

            mid = self._drone.get_status('mid')
            self.mid_check(mid)
            if mid == -1.0 :
                mid = self._ex_mid
            self._ex_mid = mid

            x = self._drone.get_status('x')
            y = self._drone.get_status('y')

            vx = self._drone.get_status('vgx')
            vy = self._drone.get_status('vgy')

            yaw = self._drone.get_status('yaw')
            bat = self._drone.get_status('bat')
            height = self._drone.get_status('tof')
            tof = self._drone_tof.get_ext_tof()
            if tof :
                self._ex_tof = tof
            else :
                tof = self._ex_tof

            try :
                frame = self._drone_cam.read_video_frame(0, 'newest')
            
            except : 
                frame = self._ex_frame
            
            else :
                self._ex_frame = frame

            return [[mid, x, y], [yaw, bat, height, tof, frame], [self._isTakeoff, vx, vy]]
        
        elif self._type == 'frame' :
            if self._engine_on :
                with self._mp_face_detection.FaceDetection(model_selection = 0, min_detection_confidence = 1) as face_detection :
                    count = 0
                    coordis = []
                    eyes_list = []
                    sorted_coordis = []
                    center_x = []
                    center_y = []
                    rows = []
                    columns = []
                    sub_count = 0
                    sub_count2 = 0
                    sub_count3 = 0
                    suc_count = 0

                    temp = {}
                    temp2 = {}
                    temp3 = []
                    temp4 = {}

                    image = held_frame
                    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                    image.flags.writeable = False
                    results = face_detection.process(image)

                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    if results.detections :
                        for detection in results.detections :
                            count += 1
                            
                            coordi0, eyes = self._mp_drawing.draw_detection(image, detection)
                            coordis.append(coordi0)
                            eyes_list.append(eyes)

                            self._held_start_point.append((0, 0))
                            self._held_end_point.append((0, 0))
                        
                        self._eyes_dic = {tuple(points) : eye for points, eye in zip(coordis, eyes_list)}

                        for point in coordis :
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
                                    sorted_coordis.append([temp[point], point])
                                elif point in temp2.keys() :
                                    sorted_coordis.append([point, temp2[point]])

                        else :
                            temp3 = list(temp.keys()) + list(temp2.keys()) + list(temp4.keys())
                            temp3 = sorted(temp3)
                            for point in temp3 :
                                if point in temp.keys() :
                                    sorted_coordis.append([temp[point], point])
                                elif point in temp2.keys() :
                                    sorted_coordis.append([point, temp2[point]])
                                elif point in temp4.keys() :
                                    sorted_coordis.append([point, temp4[point]])
                        
                        self._eyes_dic = {tuple(points) : self._eyes_dic[tuple(points)] for points in sorted_coordis}
                        eyes_list = list(self._eyes_dic.values())

                        for point in sorted_coordis :
                            if point[0] == None and point[1] == None :
                                pass
                            elif point[0] == None :
                                tempv = (self._held_start_point[sub_count3][0] + point[1][0] - self._held_end_point[sub_count3][0], self._held_start_point[sub_count3][1] + point[1][1] - self._held_end_point[sub_count3][1])
                                cv2.rectangle(image, tempv, point[1], (255, 255, 255), 2)
                                self._held_start_point[sub_count3] = tempv
                                self._held_end_point[sub_count3] = point[1]
                            elif point[1] == None :
                                tempv = (self._held_end_point[sub_count3][0] + point[0][0] - self._held_start_point[sub_count3][0], self._held_end_point[sub_count3][1] + point[0][1] - self._held_start_point[sub_count3][1])
                                cv2.rectangle(image, point[0], tempv, (255, 255, 255), 2)
                                self._held_end_point[sub_count3] = tempv
                                self._held_start_point[sub_count3] = point[0]
                            else :
                                self._held_start_point[sub_count3] = point[0]
                                self._held_end_point[sub_count3] = point[1]
                            sub_count3 += 1
                        sub_count3 = 0

                        for n in range(0, count) :
                            center_x.append((self._held_start_point[n][0] + self._held_end_point[n][0])/2)
                            center_y.append((self._held_start_point[n][1] + self._held_end_point[n][1])/2)
                            rows.append(self._held_end_point[n][0] - self._held_start_point[n][0])
                            columns.append(self._held_end_point[n][1] - self._held_start_point[n][1])
                        
                        squares = [row * column for row, column in zip(rows, columns)]
                        self._squares_dic = {(cx, cy) : square for cx, cy, square in zip(center_x, center_y, squares)}
                        self._eyes_dic = {(cx, cy) : eye for cx, cy, eye in zip(center_x, center_y, eyes_list)}

                        copy_hsp = self._held_start_point
                        copy_hep = self._held_end_point

                        if self._held_count < count :
                            recognition = self.name_labeling(image, self._held_dic)
                            num = 0

                            if recognition :
                                self._names = []
                                self._held_center_x = []
                                self._held_center_y = []
                                self._held_dic = {}

                                for info in recognition :
                                    self._names.append(info[4])
                                    cv2.putText(image, info[4], (info[2], info[1]), self._font, 1, (0, 0, 0), 1)
                                    cv2.line(image, (info[2], info[1] + 5), (info[2] + 20 * len(info[4]), info[1] + 5), (224, 224, 224), 2)
                                    self._held_center_x.append(int((info[0]+info[2])/2))
                                    self._held_center_y.append(int((info[1]+info[3])/2))
                                
                                for x, y in zip(center_x, center_y) :
                                    for hx, hy in zip(self._held_center_x, self._held_center_y) :
                                        if abs(x - hx) < 50 and abs(y - hy) < 50 :
                                            del copy_hsp[sub_count3]
                                            del copy_hep[sub_count3]
                                    sub_count3 += 1
                                sub_count3 = 0

                                if len(recognition) < count :
                                    for hsp, hep in zip(copy_hsp, copy_hep) :
                                        if hsp == (0, 0) and hep == (0, 0) :
                                            pass
                                        else :
                                            self._names.append('Unidentified%d' %num)
                                            self._held_center_x.append((hsp[0]+hep[0])/2)
                                            self._held_center_y.append((hsp[1]+hep[1])/2)
                                            num += 1

                                temp = {tx : name for tx, name in zip(self._held_center_x, self._names)}
                                temp2 = {tx : ty for tx, ty in zip(self._held_center_x, self._held_center_y)}
                                temp = dict(sorted(temp.items()))
                                temp2 = dict(sorted(temp2.items()))
                                self._held_center_x.sort()
                                self._held_center_y = list(temp2.values())
                                self._names = list(temp.values())

                                for name, c in zip(self._names, range(0, count)) :
                                    self._held_dic[name] = [self._held_center_x[c], self._held_center_y[c]]
                            
                            else :
                                for hsp, hep in zip(copy_hsp, copy_hep) :
                                    cv2.putText(image, "Identifying...", (hep[0], hsp[1]), self._font, 1, (0, 0, 0), 1)
                                    cv2.line(image, (hep[0], hsp[1] + 5), (hep[0] + 280, hsp[1] + 5), (224, 224, 224), 2)
                                count = 0

                        elif self._held_count == count :
                            for x, y in zip(center_x, center_y) :
                                for name in list(self._held_dic.keys()) :
                                    if abs(x - self._held_dic[name][0]) < 50 and abs(y - self._held_dic[name][1]) < 50 :
                                        cv2.putText(image, name, (self._held_end_point[sub_count][0], self._held_start_point[sub_count][1]), self._font, 1, (0, 0, 0), 1)
                                        cv2.line(image, (self._held_end_point[sub_count][0], self._held_start_point[sub_count][1] + 5), (self._held_end_point[sub_count][0] + 20 * len(name), self._held_start_point[sub_count][1] + 5), (224, 224, 224), 2)
                                        self._held_dic[name] = [x, y]
                                        suc_count += 1
                                sub_count += 1
                            sub_count = 0

                            if suc_count == count :
                                pass
                            else :
                                count = 0

                        else :
                            for x, y in zip(center_x, center_y) :
                                for name in list(self._held_dic.keys()) :
                                    if abs(x - self._held_dic[name][0]) < 50 and abs(y - self._held_dic[name][1]) < 50 :
                                        cv2.putText(image, name, (self._held_end_point[sub_count][0], self._held_start_point[sub_count][1]), self._font, 1, (0, 0, 0), 1)
                                        cv2.line(image, (self._held_end_point[sub_count][0], self._held_start_point[sub_count][1] + 5), (self._held_end_point[sub_count][0] + 20 * len(name), self._held_start_point[sub_count][1] + 5), (224, 224, 224), 2)
                                        self._held_dic[name] = [x, y]
                                    else :
                                        del self._held_dic[name]
                                        self._names.remove(name)
                                sub_count += 1
                    else :
                        self._names = []
                        self._held_center_x = []
                        self._held_center_y = []
                        self._held_dic = {}
                        self._eyes_dic = {}
                        self._squares_dic = {}

                    self._held_count = count

                    if self._camOn :
                        cv2.imshow('eyesight', image)
                        cv2.waitKey(1)
                        
                return [self._held_dic, self._eyes_dic, self._squares_dic, image.shape]
            return [None, None, None, None]
        
        elif self._type == 'fire detection' :
            if self._engine_on :
                frame = np.array(held_frame)
                small_frame = cv2.resize(frame, (self._rows, self._cols), cv2.INTER_AREA)
                output = self._model.predict([small_frame])

                if round(output[0][0]) == 1 :
                    return 1
                else :
                    return 0
            return 0