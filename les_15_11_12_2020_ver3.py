'''  Файл синхронизации с тьюториала CoppeliaSim'''
''' Если хочешь синхронизации скопируй этот фаайл в новый и изменяй'''
import b0RemoteApi
import time
import math

global Left_sensor_py
global Right_sensor_py
global objHand_LeftMotor
global objHand_RightMotor
global P
global kp
kp = 0.5
global kv
kv = (300 * math.pi) / 180
print('kv =', kv)
global err
global leftspeed
global rightspeed

with b0RemoteApi.RemoteApiClient('b0RemoteApi_pythonClient', 'b0RemoteApi_test5') as client:
    doNextStep = True
    # получаем HANDLE левого мотора
    errHand_LeftMotor, objHand_LeftMotor = client.simxGetObjectHandle('LeftMotor', client.simxServiceCall());
    # получаем HANDLE правого мотора
    errHand_RightMotor, objHand_RightMotor = client.simxGetObjectHandle('RightMotor', client.simxServiceCall());


    # попадаем при старте

    def simulationStepStarted(msg):
        simTime = msg[1][b'simulationTime'];
        # получаем сигнал с левого датчика
        errLS_py, Left_sensor_py = client.simxGetFloatSignal('Left_sensor_data', client.simxServiceCall());
        # получаем сигнал с правого датчика
        errRS_py, Right_sensor_py = client.simxGetFloatSignal('Right_sensor_data', client.simxServiceCall());
        # print('Left_sensor =', Left_sensor_py);
        # print('Right_sensor =', Right_sensor_py);
        # print('Simulation step started. Simulation time: ',simTime)
        err = Left_sensor_py - Right_sensor_py;
        P = kp * err;
        leftspeed = 0.5 + P;
        rightspeed = 0.5 - P;
        print('Left_speed =', leftspeed * kv);
        print('Right_speed =', rightspeed * kv);
        client.simxSetJointTargetVelocity(objHand_LeftMotor, leftspeed * kv, client.simxServiceCall());
        client.simxSetJointTargetVelocity(objHand_RightMotor, -rightspeed * kv, client.simxServiceCall());


    def simulationStepDone(msg):  # попадаем при окончании
        simTime = msg[1][b'simulationTime'];
        # print('Simulation step done. Simulation time: ',simTime);
        global doNextStep
        doNextStep = True


    client.simxSynchronous(True)
    # вызов подпрограммы при старте
    client.simxGetSimulationStepStarted(client.simxDefaultSubscriber(simulationStepStarted));
    # вызов подпрограммы при окончании
    client.simxGetSimulationStepDone(client.simxDefaultSubscriber(simulationStepDone));
    client.simxStartSimulation(client.simxDefaultPublisher())

    while True:
        if doNextStep:
            doNextStep = False
            client.simxSynchronousTrigger()  # выполняется следующий шаг
        client.simxSpinOnce()
    client.simxStopSimulation(client.simxDefaultPublisher())