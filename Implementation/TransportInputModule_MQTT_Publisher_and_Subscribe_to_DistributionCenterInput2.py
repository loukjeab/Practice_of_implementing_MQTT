# Import required modules
from TransportInputModule_Library import *
import paho.mqtt.publish as publish 
import paho.mqtt.client as mqtt


from time import sleep

# Initialize variables

Conveyor = {'A': 0, 'B': 0, 'D': 0, 'H': 0, 'I': 0, 'P': 0, 'R': 0, 'VL': 0, 'Q': 0}
Switch = {'N': 0, 'T': 0, 'F': 0, 'W': 0, 'E': 0, 'G': 0, 'K': 0, 'S': 0, 'O': 0}

# Define MQTT broker host and port for DCI2
# DCI2 = Distribution Center Input 2
DCI2_broker_host = "192.168.200.161"
DCI2_broker_port = 1883
DCI2_topic = "input2/output_piece_ready"

# Define TIM client
TIM_client = mqtt.Client()

# Initialize the Transport Input Module
TIM = TransportInputModule_Library("192.168.200.235")


def check_workpiece_end_of_conveyor(conveyor_name, next_conveyor_name, switch_name, switch_pre_pos, switch_post_pos):
    # Wait until a workpiece is detected at the end of the conveyor
    while not TIM.check_conveyor_workpiece_end(conveyor_name):
        sleep(0.5)

    # Move the switch to the desired position
    TIM.set_switch(switch_name, pos=switch_pre_pos)

    sleep(1)

    # Update the status of the conveyor and switch
    Conveyor[conveyor_name] = "0"
    publish.single("Transport_Ingoing/Conveyor_" + conveyor_name + "/Status", Conveyor[conveyor_name], hostname="192.168.200.161")

    while not TIM.check_switch_position_reached(switch_name):
        sleep(0.5)
    
    print("Found workpiece at the switch " + switch_name)
    Switch[switch_name] = "Found workpiece at the switch " + switch_name
    publish.single("Transport_Ingoing/Switch_" + switch_name + "/Status", Switch[switch_name], hostname="192.168.200.161")

    # Wait until the workpiece reaches inside the switch
    while not TIM.check_switch_workpiece(switch_name):
        sleep(0.5)
    TIM.set_switch(switch_name, pos=switch_post_pos)

    # Update the status of the switch
    Switch[switch_name] = "0"
    publish.single("Transport_Ingoing/Switch_" + switch_name + "/Status", Switch[switch_name], hostname="192.168.200.161")

    # Update the status of the next conveyor
 
    print("Found workpiece at the conveyor " + next_conveyor_name)
    Conveyor[next_conveyor_name] = "Found workpiece at the conveyor " + next_conveyor_name
    publish.single("Transport_Ingoing/Conveyor_" + next_conveyor_name + "/Status", Conveyor[next_conveyor_name], hostname="192.168.200.161")
    
    sleep(1)

def TIM_on_connect(TIM_client, userdata, flags, rc):
    # Subscribe to a topic
    TIM_client.subscribe(DCI2_topic)
    print("Connected with result code " + str(rc))

def TIM_on_message(TIM_client, userdata, msg):
    global message_received
    # Set the value of message_received to the payload of the received message
    message_received = msg.payload.decode()
    print(msg.topic + " " + message_received)
    return message_received

def TIM_DCI2():
    # Loop until message_received is "True"
    while not TIM_on_message:
        sleep(0.5)
    # Set switch W to position 1
    TIM.set_switch("W", pos=1)

    # Loop until switch W has reached position 1
    while not TIM.check_switch_position_reached("W"):
        sleep(0.5)

    # Loop until a workpiece is detected at switch W
    while not TIM.check_switch_workpiece("W"):
        sleep(0.5)

    # Set switch W to position 2
    TIM.set_switch("W", pos=2)

    sleep(1)


def main():
    
    TIM.set_conveyor_speed_all(30000) 

    # Move all conveyors forward
    for conveyor_id in ['A', 'B', 'D', 'H', 'I', 'L', 'P', 'R', 'V', 'Q']:
        TIM.conveyor_forward(conveyor_id)

    # Set all switches to position 0
    for switch_id in ['N','T','F','W','E','G','K','S','O']:
        TIM.set_switch(switch_id,pos=0)

    sleep(5)

    # Set callback functions for TIM_client
    TIM_client.on_connect = TIM_on_connect
    TIM_client.on_message = TIM_on_message

    # Connect to MQTT broker
    TIM_client.connect(DCI2_broker_host, DCI2_broker_port, 60)

    # Start the MQTT client loop
    TIM_client.loop_start()

    while True:
        # Loop until message_received is "True"
        while not TIM_on_message:
            sleep(0.5)
        # Execute TIM_DCI2 function
        TIM_DCI2()

if __name__ == "__main__":
    main()




    