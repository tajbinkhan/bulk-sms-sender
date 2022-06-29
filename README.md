# Bulk SMS Sender

## Description

This script will send mass SMS out to many people using the Twilio API.

Your contacts must be specified in a CSV file, where the first column is the phone number.

The message is read from a message file and sent to all contacts.

Contacts will not recieve the message twice as the script will remove duplicate numbers automatically.

Finally, a cost estimate is provided and the user is prompted to confirm (Y/n) before sending commences.
