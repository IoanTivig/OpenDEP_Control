#include <Arduino.h>

// Define the pins for all the components //
// Illumination (LIHGT) //
int LIGHT_LED_PIN = 3; // Illumination LED connected to digital pin 3 (PWM)

// Function Generator (GEN) //
int gen_W_CLK_PIN = 4; // Function Generator W_CLK connected to digital pin 4
int gen_FQ_UD_PIN = 5; // Function Generator FQ_UD connected to digital pin 5
int gen_DATA_PIN = 6; // Function Generator DATA connected to digital pin 6
int gen_RESET_PIN = 7; // Function Generator RESET connected to digital pin 7

// Instances of the components

// Other variables
const String device_ID = "OPENDEP_INSTRUMENT";
int light_LED_dim_percentage = 100;
bool light_LED_status = false;

// Commands related


void setup() {
    // Illumination setup
    pinMode(LIGHT_LED_PIN, OUTPUT);
    TCCR2B = TCCR2B & 0b11111000 | 0x01;  // Adjusts the PMW PIN frequecy (Timer02) to max possible so the LED won't flicker

    Serial.begin(115200);
    // AD9850 function generator setup
}

void loop() {
    // generator.setFrequency(10);
    if (Serial.available() > 0) {
        // Command parsing
        String command = Serial.readString();
        command.trim(); // Remove any leading/trailing whitespace
        int max_command_keywords = 5; // Maximum number of keywords in a command
        String command_keywords[max_command_keywords-1]; // Array of pointers to the keywords
        splitAndTrim(command, command_keywords, max_command_keywords);

        // Illumination System Commands
        if (command_keywords[0] == "PARSE") {
            Serial.println("Command parsed");
        }

        else if (command_keywords[0] == "OPENDEP" and command_keywords[1] == "LIGHT") {
            // LED Light Turn ON Command
            if (command_keywords[2] == "ON") {
                lightSwitchLED(true);
                Serial.println("Light is turned ON");

            // LED Light Turn ON Command
            } else if (command_keywords[2] == "OFF") {
                lightSwitchLED(false);
                Serial.println("Light is turned OFF");

            // LED Light Dim Command
            } else if (command_keywords[2] == "DIM") {
                int dimValue = command_keywords[3].toInt();
                lightDimLED(dimValue);
                Serial.print("Light is dimmed to ");
                Serial.print(dimValue);
                Serial.println("%");
            } else {
              Serial.println("INVALID COMMAND");
            }

        // Device Information Commands
        } else if (command_keywords[0] == "OPENDEP") {
            // Device Information Command
            if (command_keywords[1] == "INFO") {
                infoDevice();

            // Light Information Command
            } else if (command_keywords[1] == "COMMANDS") {
                infoCommands();
            } else if (command_keywords[1] == "ID") {
                Serial.println(device_ID);
            } else {
              Serial.println("INVALID COMMAND");
            }
        } else {
          Serial.println("INVALID COMMAND");
        }
    }
}
/* Function for information that will return
 * all available information about the device
 * or possible actions
 * All information functions start with info_*/

void infoDevice() {
    Serial.println("Name: OpenDep Control; "
                   "Software version: Alpha 0.1; "
                   "Author: Ioan Cristian Tivig; "
                   "Description: Control the OpenDEP device");
}

void infoCommands() {
    Serial.println("OPENDEP LIGHT ON: Turn ON the LED; "
                   "OPENDEP LIGHT OFF: Turn OFF the LED; "
                   "OPENDEP LIGHT DIM [PERCENTAGE]: Dim the LED to a certain percentage");
}

/* Functions for Illumination control
 * All illumination functions start with light_
 * Here you can control the LED of the illumination
 * and the vent attached to the radiator*/
void lightSwitchLED(bool status) {
    if (status) {
        int dimValue = map(light_LED_dim_percentage, 0, 100, 0, 255);
        analogWrite(LIGHT_LED_PIN, dimValue);
        light_LED_status = true;
    } else if (!status) {
        digitalWrite(LIGHT_LED_PIN, LOW);
        light_LED_status = false;
    }
}

void lightDimLED(int percentage) {
    light_LED_dim_percentage = percentage;
    int dimValue = map(percentage, 0, 100, 0, 255);
    analogWrite(LIGHT_LED_PIN, dimValue);
}

/* Functions for Function Generator control
 * All illumination functions start with gen_
 * Here you can control the AC field and its parameters
 * like frequency, wave type, Vpp, etc.*/


/* Helper functions */
void splitAndTrim(String input, String words[], int maxWords) {
    int wordCount = 0;
    int idx = 0;
    while (idx < input.length() && wordCount < maxWords) {
        int spaceIdx = input.indexOf(' ', idx);
        if (spaceIdx == -1) {
            words[wordCount] = input.substring(idx);
            break;
        } else {
            words[wordCount] = input.substring(idx, spaceIdx);
            idx = spaceIdx + 1;
            wordCount++;
        }
    }
}