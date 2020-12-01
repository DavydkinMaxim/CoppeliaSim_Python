# рабочая версия
# Make sure to have CoppeliaSim running, with followig scene loaded:
#
# scenes/synchronousImageTransmissionViaRemoteApi.ttt
#
# Do not launch simulation, and make sure that the B0 resolver
# is running. Then run this script
#
# The client side (i.e. this script) depends on:
#
# b0RemoteApi (Python script), which depends several libraries present
# in the CoppeliaSim folder
import os
import array
import math

import cv2 as cv
import numpy as np


os.add_dll_directory(r'C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu')

import b0RemoteApi
import time

with b0RemoteApi.RemoteApiClient('b0RemoteApi_V-REP', 'b0RemoteApi9') as client:
    client.doNextStep = True
    client.runInSynchronousMode = True

    # ***************ПОВОРОТ РИСУНКА**********************************************************
    def rotateImage(image, angle):
        center = tuple(np.array(image.shape[0:2]) / 2)
        rot_mat = cv.getRotationMatrix2D(center, angle, 1.0)
        return cv.warpAffine(image, rot_mat, image.shape[0:2], flags=cv.INTER_LINEAR)
    # ***************************************************************************************


    # %%%%%%%%%%%%%%%%%%%%%%%% ОПРЕДЕЛЕНИЕ КОНТУРА %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def track_green_object(image):

        # Blur the image to reduce noise
        blur = cv.GaussianBlur(image, (5, 5), 0)

        # Convert BGR to HSV
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)

        # Threshold the HSV image for only green colors
        lower_green = np.array([40, 70, 70])
        upper_green = np.array([80, 200, 200])

        # Threshold the HSV image to get only green colors
        mask = cv.inRange(hsv, lower_green, upper_green)

        # Blur the mask
        bmask = cv.GaussianBlur(mask, (5, 5), 0)

        # Take the moments to get the centroid
        moments = cv.moments(bmask)
        m00 = moments['m00']
        centroid_x, centroid_y = None, None
        if m00 != 0:
            centroid_x = int(moments['m10'] / m00)
            centroid_y = int(moments['m01'] / m00)

        # Assume no centroid
        ctr = None

        # Use centroid if it exists
        if centroid_x != None and centroid_y != None:
            ctr = (centroid_x, centroid_y)
        return ctr
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%



    def simulationStepStarted(msg):
        simTime = msg[1][b'simulationTime'];
        # print('Simulation step started. Simulation time: ', simTime)


    def simulationStepDone(msg):
        simTime = msg[1][b'simulationTime'];
        # print('Simulation step done. Simulation time: ', simTime);
        client.doNextStep = True



    def imageCallback(msg):

        # ++++++++++++++++++++++++ПЕРЕДАЧА РИСУНКА В COPPELLIASIM +++++++++++++++++++++++++++++++++++++++++
        # client.simxSetVisionSensorImage(passiveVisionSensorHandle[1], False, msg[2], client.simxDefaultPublisher())

        # +++++++++++++++++++++вывод потока видео++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        while (msg[0]):
            image: object
            image = msg[2]
            img = array.array('B', image)
            resolution = msg[1]
            img = np.array(img, dtype=np.uint8)
            img.resize([resolution[1], resolution[0], 3])
            ret = track_green_object(img)
            if ret:
                cv.rectangle(img, (ret[0] - 50, ret[1] - 50), (ret[0] + 50, ret[1] + 50), (0xff, 0xf4, 0x0d), 4)
            # img = img.ravel()
            img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            cv.imshow('pic', rotateImage(img, 180))
            msg[0] = 0




            if cv.waitKey(1) & msg[0]:
                break
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++





    def stepSimulation():
        if client.runInSynchronousMode:
            while not client.doNextStep:
                client.simxSpinOnce()
            client.doNextStep = False
            client.simxSynchronousTrigger()
        else:
            client.simxSpinOnce()


    client.simxAddStatusbarMessage('Hello world!', client.simxDefaultPublisher())


    # +++++++++++++++++ ОПРЕДЕЛЕНИЕ HANDLE ОБЪЕКТОВ СЦЕНЫ +++++++++++++++++++++++++++++++++++++++++++++
    visionSensorHandle = client.simxGetObjectHandle('Vision_sensor', client.simxServiceCall())



        # passiveVisionSensorHandle = client.simxGetObjectHandle('PassiveVisionSensor', client.simxServiceCall())

    if client.runInSynchronousMode:
        client.simxSynchronous(True)

    # dedicatedSub=client.simxCreateSubscriber(imageCallback,1,True)
    # client.simxGetVisionSensorImage(visionSensorHandle[1],False,dedicatedSub)

    # +++++++++++++++++++++ ПОЛУЧЕНИЕ ИЗОБРАЖЕНИЕ И ПЕРЕХОД В ПОДПРОГРАММУ imageCallback ++++++++++++++++
    client.simxGetVisionSensorImage(visionSensorHandle[1], False, client.simxDefaultSubscriber(imageCallback))



    client.simxGetSimulationStepStarted(client.simxDefaultSubscriber(simulationStepStarted));
    client.simxGetSimulationStepDone(client.simxDefaultSubscriber(simulationStepDone));
    client.simxStartSimulation(client.simxDefaultPublisher())


    while True:
            stepSimulation() #!!!!!!!!!!






    client.simxStopSimulation(client.simxDefaultPublisher())
