'''  Файл синхронизации с тьюториала CoppeliaSim'''
''' Если хочешь синхронизации скопируй этот файл в новый и изменяй'''
import b0RemoteApi
import time

with b0RemoteApi.RemoteApiClient('b0RemoteApi_pythonClient', 'b0RemoteApi') as client:  # Имя клиента: PYTHON_CODE
                                                                                        # Channel name: b0RemoteApi
    doNextStep = True                                                                   # doNextStep переменная которая определяет выполнился ли шаг или нет

    def simulationStepDone(msg):                         # подпрограмма вызываемая после выполнения шага
        simTime = msg[1][b'simulationTime'];
        #print('Simulation step done. Simulation time: ', simTime);
        global doNextStep
        doNextStep = True


    client.simxSynchronous(True)
    client.simxGetSimulationStepDone(client.simxDefaultSubscriber(simulationStepDone));
    client.simxStartSimulation(client.simxDefaultPublisher())

    #startTime = time.time()
    while True:                                            # бесконечный цикл выполнения
        if doNextStep:
            doNextStep = False
            client.simxSynchronousTrigger()
        print('HI')


        client.simxSpinOnce()
    client.simxStopSimulation(client.simxDefaultPublisher())