import time
from datetime import datetime
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import boto3
import json

# AWS IoT Core setup
aws_iot_endpoint = "your-iot-endpoint.amazonaws.com"
thing_name = "YourThingName"
topic = "your/topic"

# Initialize Boto3 client
iot_client = boto3.client('iot-data', region_name='your-region')

# Modbus client setup
client = ModbusClient(method='rtu', port='/dev/ttyUSB0', baudrate=9600, timeout=3)
client.connect()

def read_daily_energy():
    # Read the registers for daily energy generated and consumed
    generated = client.read_input_registers(0x330C, 2, unit=1)
    consumed = client.read_input_registers(0x330E, 2, unit=1)

    # Convert the register values to float (assuming they are in Wh and need to be converted to kWh)
    daily_generated = generated.registers[0] / 100.0  # example conversion
    daily_consumed = consumed.registers[0] / 100.0    # example conversion

    return daily_generated, daily_consumed

def send_to_aws_iot(daily_generated, daily_consumed):
    message = {
        "timestamp": datetime.utcnow().isoformat(),
        "daily_generated_kWh": daily_generated,
        "daily_consumed_kWh": daily_consumed
    }

    response = iot_client.publish(
        topic=topic,
        qos=1,
        payload=json.dumps(message)
    )

    print(f"Published to AWS IoT: {message}")
    return response

def main():
    while True:
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            daily_generated, daily_consumed = read_daily_energy()

            # Send data to AWS IoT
            send_to_aws_iot(daily_generated, daily_consumed)
            time.sleep(60)  # Ensure the script waits for a minute to avoid duplicate submissions

        time.sleep(30)  # Check the time every 30 seconds

if __name__ == "__main__":
    main()
