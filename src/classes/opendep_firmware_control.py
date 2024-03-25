import time

import serial.tools.list_ports
import serial

class OpenDepFirmware:
    serial_inst = serial.Serial()
    serial_inst.baudrate = 115200
    serial_inst.port = "COM3"
    port_list = []


    def __init__(self):
        self.get_all_ports()

    def set_baudrate(self, baudrate):
        self.serial_inst.baudrate = baudrate

    def set_port(self, port):
        self.serial_inst.port = port

    def get_all_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_list = []
        for onePort in ports:
            self.port_list.append(str(onePort))

    def connect_instrument(self):
        self.serial_inst.open()

    def disconnect_instrument(self):
        self.serial_inst.close()

    def verify_connection(self):
        if self.serial_inst.is_open:
            return True
        else:
            return False

    def send_command(self, command):
        self.serial_inst.write(command.encode('utf-8'))
        print("COMMAND: " + command)
        response = self.serial_inst.readline().decode('utf-8')
        print("RESPONSE: " + response)
        return response

    def ledON(self):
        command = "OPENDEP LIGHT ON"
        self.serial_inst.write(command.encode('utf-8'))
        msg = self.serial_inst.readline()
        print(msg.decode('utf-8'))

    def ledOFF(self):
        command = "OPENDEP LIGHT OFF"
        self.serial_inst.write(command.encode('utf-8'))
        msg = self.serial_inst.readline()
        print(msg.decode('utf-8'))

    def ledDIM(self, value):
        command = "OPENDEP LIGHT DIM " + str(value)
        self.serial_inst.write(command.encode('utf-8'))
        msg = self.serial_inst.readline()
        print(msg.decode('utf-8'))


if __name__ == "__main__":
    instrument = OpenDepFirmware()

    val = input("Select port: COM")

    for x in range(0, len(instrument.port_list)):
        if instrument.port_list[x].startswith("COM" + str(val)):
            portVar = "COM" + str(val)
            print(portVar)
            print("Selected port is: " + instrument.port_list[x])

    while True:
        command = input("Insert command: ")
        if command == "ON":
            instrument.send_command("OPENDEP LIGHT ON")
        elif command == "OFF":
            instrument.send_command("OPENDEP LIGHT OFF")
        elif command == "DIM":
            instrument.ledDIM(50)
        elif command == "EXIT":
            instrument.serial_inst.close()
            break
        else:
            print("Invalid command")


