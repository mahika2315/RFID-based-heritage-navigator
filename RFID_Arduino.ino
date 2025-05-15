#include <SPI.h>
#include <MFRC522.h>

// Define pins for the RFID reader
#define SS_PIN 8
#define RST_PIN 7

MFRC522 mfrc522(SS_PIN, RST_PIN); // Create an MFRC522 instance

void setup() {
  Serial.begin(9600);  // Initialize serial communication
  SPI.begin();         // Initialize SPI bus
  mfrc522.PCD_Init();  // Initialize the RFID reader
  Serial.println("RFID Reader is ready. Bring a tag near the reader.");
}

void loop() {
  // Check if a new card is present
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    // Send a message indicating a tag is detected
    Serial.print("");  // Reader ID (fixed as R1 since it's a single reader)

    // Print the Tag's Unique ID
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? "0" : "");  // Add leading zero for single hex digits
      Serial.print(mfrc522.uid.uidByte[i], HEX);              // Print each byte in HEX
    }
    Serial.println();

    // Halt communication with the card
    mfrc522.PICC_HaltA();
  }
}
