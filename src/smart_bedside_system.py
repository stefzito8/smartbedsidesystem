from src.smart_bedside_error import SmartBedsideError

try:
    import RPi.GPIO as GPIO
except ImportError:
    from mock import GPIO

try:
    from pinpong.libs.dfrobot_max30102 import DFRobot_BloodOxygen_S
except ImportError:
    from mock.max30102 import DFRobot_BloodOxygen_S


class SmartBedsideSystem:

    # BOARD (physical) numbers of the pins the components are connected to.
    BUZZER_PIN = 22  # KY-012 active buzzer used as the alarm (see User Story #2).
    BUTTON_PIN = 16  # B3F-1020 pushbutton used to stop the alarm (see User Story #3).
    O2_SERVO_PIN = 12  # MG90S servo motor controlling the oxygen delivery valve (see User Story #4).
    ALARM_LED_PIN = 18 # red led used as alarm (USer Story #8)

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)  # Refer to the GPIO pins by their physical number on the board.
        GPIO.setwarnings(False)  # Disable warnings.

        self.spo2_hr_sensor = DFRobot_BloodOxygen_S()  # Replace None by initializing the MAX30102 sensor (see User Story #1).
        self.spo2_hr_sensor.begin()
        self.spo2_hr_sensor.sensor_start_collect()

        GPIO.setup(self.BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.ALARM_LED_PIN, GPIO.OUT, initial=GPIO.LOW)
        self.alarm_on = False  # Replace None by initializing the alarm status (see User Story #2).

        GPIO.setup(self.BUTTON_PIN, GPIO.IN)

        GPIO.setup(self.O2_SERVO_PIN, GPIO.OUT)
        self.o2_servo = GPIO.PWM(self.O2_SERVO_PIN, 50)  # Replace None by initializing the servo motor's PWM instance (see User Story #4).
        self.o2_servo.start(5.0)
        self.o2_valve_angle = 0.0  # Replace None by initializing the valve angle, in degrees (see User Story #4).

    def read_vital_signs(self) -> list:
        """
        Read the patient's blood oxygen saturation (SpO₂).
        Returns: int: SpO₂ percentage (70–100).
        Raises: SmartBedsideError: If the sensor returns an invalid reading (-1).
        """
        ox_saturation= self.spo2_hr_sensor.get_spo2()
        heart_rate= self.spo2_hr_sensor.get_heartbeat()
        if ox_saturation == -1:
            raise SmartBedsideError
        elif heart_rate == -1:
            raise SmartBedsideError
        else:
            return [ox_saturation, heart_rate]



    def manage_alarm(self) -> None:
        """
        Activate or deactivate the alarm based on the patient's blood oxygen saturation (SpO₂).
        Raises: SmartBedsideError: If the SpO₂ reading is invalid (propagated from read_vital_signs()).
        """
        vital_signs = self.read_vital_signs()

        if vital_signs[0] < 88:
            GPIO.output(self.BUZZER_PIN, True)
            GPIO.output(self.ALARM_LED_PIN, True)
            self.alarm_on = True
        elif vital_signs[1] < 50:
            GPIO.output(self.BUZZER_PIN, True)
            GPIO.output(self.ALARM_LED_PIN, True)
            self.alarm_on = True
        elif vital_signs[1] > 130:
            GPIO.output(self.BUZZER_PIN, True)
            GPIO.output(self.ALARM_LED_PIN, True)
            self.alarm_on = True
        else:
            GPIO.output(self.BUZZER_PIN, False)
            GPIO.output(self.ALARM_LED_PIN, False)
            self.alarm_on = False

    def stop_alarm(self) -> None:
        """
        Stop the alarm if the pushbutton is pressed. Otherwise, leave the alarm unchanged.
        """
        if GPIO.input(self.BUTTON_PIN):
            GPIO.output(self.BUZZER_PIN, False)
            self.alarm_on = False

    def set_o2_valve_angle(self, angle: float) -> None:
        """
        Set the oxygen delivery valve to the specified angle by controlling the servo motor.
        Args: angle (float): The target valve angle in degrees, between 0 and 180 degrees, inclusive.
        Raises: SmartBedsideError: If the target angle is outside the valid range of 0 to 180 degrees.
        """
        if  not (0.0 <= angle <= 180.0):
            raise SmartBedsideError

        duty_cycle = 5.0 + (angle / 180.0) * 5.0
        self.o2_servo.ChangeDutyCycle(duty_cycle)
        self.o2_valve_angle = angle


    def manage_oxygen_valve(self) -> None:
        """
        Automatically regulate the oxygen delivery valve based on the
        patient's blood oxygen saturation (SpO₂).
        If SpO₂ is below 95%, fully open the oxygen delivery valve.
        Otherwise, fully close the oxygen delivery valve.
        Raises: SmartBedsideError: If the SpO₂ reading is invalid (propagated from read_vital_signs()).
        """
        spo2 = self.read_vital_signs()

        if spo2 < 95:
            self.set_o2_valve_angle(180.0)
        else:
            self.set_o2_valve_angle(0.0)
