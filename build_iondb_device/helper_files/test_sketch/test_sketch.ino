/* Do NOT remove this!! */
#include <SPI.h>

/* Add your library specific includes for your conditions here. */
#include <SD.h>
#include "sd2card/Sd2Card.h"

/**
@brief  Here is where you add code for your custom conditions. Add the same keywords here that you added to
		configuration.py.
*/
void
check_other_conditions(
	void
) {

}

/* Add the chip select pins you wish to check for devices on here. */
int cs_pins_to_check[] = {4, 10};

/**
@brief      Here is where you add code for your conditions that rely on the chip select pins. Add the same
			keywords here that you added to configuration.py.

@details    Make sure to return 1 when the chip select pin that your device uses has been found so that it is not
			used later. Otherwise, return 0.

@param      pin     This is the chip select pin currently being tested.
*/
int
check_chip_select_conditions(
	int cs_pin
) {
	Sd2Card card;

	if (card.init(SPI_HALF_SPEED, cs_pin)) {
		if (SD.begin(cs_pin)) {
			Serial.print(" FORMATTED_SD_CARD");
		}

		return 1;
	}

	return 0;
}

/**********************************************************************************************************************
 Do not change the code below unless you know what you are doing!
**********************************************************************************************************************/

void check_chip_select_conditions_helper();

void
setup(
	void
) {
	SPI.begin();
	Serial.begin(BAUD_RATE);

	check_chip_select_conditions_helper();
	check_other_conditions();

	Serial.println("DONE");
}

void
loop(
	void
) {}

void
check_chip_select_conditions_helper(
	void
) {
	int num_cs_pins_to_check = sizeof(cs_pins_to_check) / sizeof(int);
	int num_cs_pins_working = 0;
	int working_cs_pins[num_cs_pins_to_check];

	int i;
	for (i = 0; i < num_cs_pins_to_check; i++) {
		int skip_pin = 0;

		int j;
		for (j = 0; j < num_cs_pins_working; j++) {
			if (cs_pins_to_check[i] == working_cs_pins[j]) {
				skip_pin = 1;
				break;
			}
		}

        Serial.print("CS_PIN: ");
        Serial.println(cs_pins_to_check[i]);
		int result = check_chip_select_conditions(cs_pins_to_check[i]);

		if (result == 1) {
			num_cs_pins_to_check--;
			working_cs_pins[num_cs_pins_working++] = cs_pins_to_check[i];
			Serial.println();
			break;
		}

		Serial.println();
	}
}