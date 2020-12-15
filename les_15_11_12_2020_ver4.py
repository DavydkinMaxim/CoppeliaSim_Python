'''  Файл синхронизации с тьюториала CoppeliaSim'''
''' Если хочешь синхронизации скопируй этот файл в новый и изменяй'''
import b0RemoteApi
import math
import time
global kp, kv
kp =0.5
kv = 100*math.pi/180

with b0RemoteApi.RemoteApiClient('b0RemoteApi_pythonClient', 'b0RemoteApi1') as client:  # Имя клиента: PYTHON_CODE
                                                                                        # Channel name: b0RemoteApi
    doNextStep = True                                                                   # doNextStep переменная которая определяет выполнился ли шаг или нет

    def simulationStepDone(msg):                         # подпрограмма вызываемая после выполнения шага
        simTime = msg[1][b'simulationTime'];
        #print('Simulation step done. Simulation time: ', simTime);
        global doNextStep
        doNextStep = True


    client.simxSynchronous(True)


#########################################Определеям Handle объектов###########################################################
    errHandle_LeftMotor, objHandle_LeftMotor  =   client.simxGetObjectHandle('LeftMotor', client.simxServiceCall())
    errHandle_RighttMotor, objHandle_RightMotor = client.simxGetObjectHandle('RightMotor', client.simxServiceCall())



    client.simxGetSimulationStepDone(client.simxDefaultSubscriber(simulationStepDone));
    client.simxStartSimulation(client.simxDefaultPublisher())

    #startTime = time.time()
    while True:                                            # бесконечный цикл выполнения
        if doNextStep:
            doNextStep = False
            client.simxSynchronousTrigger()
        #print('HI')
        errFloat_LeftSensor, data_LeftSensor =  client.simxGetFloatSignal('Left_sensor_data',client.simxServiceCall())
        errFloat_RightSensor, data_RightSensor = client.simxGetFloatSignal('Right_sensor_data', client.simxServiceCall())
        err = data_LeftSensor - data_RightSensor
        P = kp*err
        leftspeed = 0.5 + P;
        rightspeed = 0.5 - P;
        print(data_LeftSensor)
        client.simxSetJointTargetVelocity(objHandle_LeftMotor, leftspeed*kv, client.simxServiceCall())
        client.simxSetJointTargetVelocity(objHandle_RightMotor, -rightspeed*kv, client.simxServiceCall())

        client.simxSpinOnce()
    client.simxStopSimulation(client.simxDefaultPublisher())