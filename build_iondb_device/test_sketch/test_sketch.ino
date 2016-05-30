#include <Arduino.h>
#include <SPI.h>
#include <SD.h>
#include "sd2card/Sd2Card.h"

int cs_pins[] = {PINS};

void
setup(
)
{
    SPI.begin();
    Serial.begin(9600);

    int num_cs_pins_to_check = sizeof(cs_pins) / sizeof(int);

    int i;
    for (i = 0; i < num_cs_pins_to_check; i++) {
        Serial.print(cs_pins[i]);

        Sd2Card card;
        if (card.init(SPI_HALF_SPEED, cs_pins[i])) {
            Serial.print(" SD_CARD");

            if (SD.begin(cs_pins[i])) {
                Serial.print(", SD_FORMATTED");
            }

            Serial.println();
            break;
        }

        Serial.println();
    }
}

void
loop(
)
{}