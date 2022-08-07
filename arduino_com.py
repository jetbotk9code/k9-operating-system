# Importing Libraries

import serial
import time
import subprocess


def write_read(the_port, data):
    try:
        the_port.write(bytes(data, 'utf-8'))
    except:
        print("Can not write.")

    time.sleep(0.05)

    try:
        data = the_port.readline()
    except:
        print("Can not read.")

    return data


def process_usb(the_port, command):
    response = ""
    result = ""
    index = 1
    command_index = 0

    # test to see if command is in the command list
    command_list = ["COM_CHECK", "LED_ON", "LED_OFF", "FLOOR_LIGHT_ON", "FLOOR_LIGHT_OFF", "HEAD_LIGHT_ON", "HEAD_LIGHT_OFF", "RAISE_HEAD", "LOWER_HEAD", "WAG_TAIL", "RAISE_TAIL","CENTER_TAIL", "LOWER_TAIL","WIGGLE_EARS", "DRIVE_ON", "DRIVE_OFF", "PRINT_ON", "PRINT_OFF", "DRV_BAT", "SYS_BAT", "EXT_TEMP_HUM", "INT_TEMP", "READ_SWT", "GOTO_SLEEP", "VER", "PORT_NAME", "FLUSH", "SETTINGS", "OPEN_CHECK", "LIST_COMS"]

    for check_com in command_list:
        # print(index, check_com)
        if check_com == command:
            command_index = index
            break
        else:
            index += 1

    if command_index == 0:
        result = "Not a recognised command."
    else:
        if command == "VER":
            response = "b''pyserial ver: " + serial.__version__
        elif command == "PORT_NAME":
            response = the_port.name
        elif command == "FLUSH":
            # result = the_port.reset_input_buffer()
            # time.sleep(0.1)
            result = the_port.reset_output_buffer()
            response = "Port Flush"
        elif command == "SETTINGS":
            port_settings = the_port.get_settings()
            response = str(port_settings)
        elif command == "OPEN_CHECK":
            if the_port.is_open == True:
                response = "OPEN"
            else:
                response = "CLOSED"
        elif command == "LIST_COMS":
            comslen = len(command_list)
            for x in range(0, comslen - 2):
                response = response + command_list[x] + ", "
            response = response + command_list[comslen - 1]
        else:
            try:
                if the_port.is_open == True:
                    the_port.write(bytes(str(command_index) + '\r', 'utf-8'))
                else:
                    result = "Port is closed."
            except:
                result = "Can not write."

            time.sleep(0.05)

            try:
                response = str(the_port.readline())
            except:
                result = "Can not read port."

    if response == "b''":
        result = "No response"
    else:
        # Remove "b''" from begining of response
        response = response.replace("b","")
        response = response.replace("'","")

        # Remove "\\r\\n" from end of response
        res_list = response.split('\\')
        response = res_list[0]

    return response, result


def test_loop(the_port):
    control = True
    value = ""

    while control:
        comd = input("Enter a command or <q> to quit: ") # Taking input from user

        if comd == 'q':
            control = False
        else:
            print("     Jetson sent: " + comd)

            # value = write_read(the_port, num)
            
            value = process_usb(usb_port, comd)

            print("Arduino returned: " + str(value))
            print("-------------------------------")
            if value[0] == "sleep":
                control = False
                

def open_com(port_name):
    result = ""

    try:
        arduino_object = serial.Serial(port=port_name, baudrate=115200, timeout=.1)
    except:
        result = "Can not open port: " + port_name

    return arduino_object, result


# ============================== Main =============================
if __name__ == "__main__":
    print("pyserial ver:" + serial.__version__)

    # /dev/ttyACM0 (Arduino Mega or Mega 2560)
    usb_port, my_result = open_com("/dev/ttyACM0")

    if my_result == "":
        print(usb_port)

        test_loop(usb_port)

        # subprocess.call(["shutdown", "-h", "now"])
    else:
        print(my_result)

