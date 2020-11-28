import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

myMQTTClient = AWSIoTMQTTClient("clientid")
myMQTTClient.configureEndpoint("a26zkbv9c1bz6c-ats.iot.eu-west-2.amazonaws.com", 8883)
myMQTTClient.configureCredentials("/home/pi/Maskit/pi/root-ca.pem", "/home/pi/Maskit/pi/private.pem.key", "/home/pi/Maskit/pi/certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)
myMQTTClient.configureConnectDisconnectTimeout(10)
myMQTTClient.configureMQTTOperationTimeout(5)

# logger.info("Connecting...")
print("Initiating IoT Core Topic ...")
myMQTTClient.connect()

print("Publishing message from RPI...")
myMQTTClient.publish(
    topic="home/helloworld",
    QoS=1,
    payload="{'Message':'Message By RPI'}")
