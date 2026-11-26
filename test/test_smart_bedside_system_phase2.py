import unittest
from unittest.mock import patch, MagicMock, call

from mock import max30102, GPIO
from src.smart_bedside_error import SmartBedsideError
from src.smart_bedside_system import SmartBedsideSystem


##########################################################################################
########################### Acceptance Tests for User Story #6 ###########################
##########################################################################################

class TestUserStory6(unittest.TestCase):

    @patch.object(max30102.DFRobot_BloodOxygen_S, "__init__", return_value=None)
    @patch.object(max30102.DFRobot_BloodOxygen_S, "begin")
    @patch.object(max30102.DFRobot_BloodOxygen_S, "sensor_start_collect")
    def test_spo2_sensor_initialization(self, mock_sensor_start_collect: MagicMock,
                                        mock_begin: MagicMock, mock_DFRobot_BloodOxygen_S: MagicMock):
        system = SmartBedsideSystem()
        # Assert that the sensor was instantiated without any arguments.
        mock_DFRobot_BloodOxygen_S.assert_called_once_with()
        # Assert that the sensor's begin() method was called exactly once.
        mock_begin.assert_called_once_with()
        # Assert that the sensor's data acquisition was started exactly once.
        mock_sensor_start_collect.assert_called_once_with()
        # Assert that the sensor was stored in the spo2_hr_sensor instance variable.
        self.assertIsInstance(system.spo2_hr_sensor, max30102.DFRobot_BloodOxygen_S)

    @patch.object(max30102.DFRobot_BloodOxygen_S, "get_heartbeat")
    @patch.object(max30102.DFRobot_BloodOxygen_S, "get_spo2")
    def test_read_valid_vital_signs(self, mock_get_spo2: MagicMock, mock_get_heartbeat: MagicMock):
        mock_get_spo2.return_value = 98  # Simulate a valid SpO2 reading of 98%.
        mock_get_heartbeat.return_value = 72  # Simulate a valid heart rate reading of 72 BPM.
        system = SmartBedsideSystem()
        vital_signs = system.read_vital_signs()
        # Assert that the returned list contains the SpO2 and the heart rate, in this order.
        self.assertEqual(vital_signs, [98, 72])

    @patch.object(max30102.DFRobot_BloodOxygen_S, "get_heartbeat")
    @patch.object(max30102.DFRobot_BloodOxygen_S, "get_spo2")
    def test_read_invalid_heart_rate(self, mock_get_spo2: MagicMock, mock_get_heartbeat: MagicMock):
        mock_get_spo2.return_value = 98  # Simulate a valid SpO2 reading of 98%.
        mock_get_heartbeat.return_value = -1  # Simulate an invalid heart rate reading.
        system = SmartBedsideSystem()
        # Assert that SmartBedsideError is raised when the sensor returns -1 for the heart rate.
        self.assertRaises(SmartBedsideError, system.read_vital_signs)

    @patch.object(max30102.DFRobot_BloodOxygen_S, "get_heartbeat")
    @patch.object(max30102.DFRobot_BloodOxygen_S, "get_spo2")
    def test_read_invalid_spo2(self, mock_get_spo2: MagicMock, mock_get_heartbeat: MagicMock):
        mock_get_spo2.return_value = -1  # Simulate an invalid SpO2 reading.
        mock_get_heartbeat.return_value = 72  # Simulate a valid heart rate reading of 72 BPM.
        system = SmartBedsideSystem()
        # Assert that SmartBedsideError is still raised when the sensor returns -1 for the SpO2.
        self.assertRaises(SmartBedsideError, system.read_vital_signs)


##########################################################################################
########################### Acceptance Tests for User Story #7 ###########################
##########################################################################################

class TestUserStory7(unittest.TestCase):

    @patch.object(GPIO, "setup")
    def test_buzzer_initialization(self, mock_gpio_setup: MagicMock):
        system = SmartBedsideSystem()
        accepted_calls = [
            call(system.BUZZER_PIN, GPIO.OUT),
            call(system.BUZZER_PIN, GPIO.OUT, initial=GPIO.LOW),
        ]
        # Assert that the buzzer pin was configured as an output pin (optionally starting LOW, i.e. OFF).
        found = False
        for accepted_call in accepted_calls:
            if accepted_call in mock_gpio_setup.call_args_list:
                found = True
        self.assertTrue(found)
        # Assert that the alarm status is initialized to OFF.
        self.assertFalse(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_bradycardia(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [95, 49]  # Normal SpO2 (95%), bradycardia (49 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = False
        system.manage_alarm()
        # Assert that the buzzer was turned ON (updated in phase 2, see User Story #8).
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, True)
        # Assert that the alarm status was updated to ON.
        self.assertTrue(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_no_bradycardia(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [95, 50]  # Normal SpO2 (95%), normal heart rate (50 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = True
        system.manage_alarm()
        # Assert that the buzzer was turned OFF (updated in phase 2, see User Story #8).
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, False)
        # Assert that the alarm status was updated to OFF.
        self.assertFalse(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_tachycardia(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [95, 131]  # Normal SpO2 (95%), tachycardia (131 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = False
        system.manage_alarm()
        # Assert that the buzzer was turned ON (updated in phase 2, see User Story #8).
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, True)
        # Assert that the alarm status was updated to ON.
        self.assertTrue(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_no_tachycardia(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [95, 130]  # Normal SpO2 (95%), normal heart rate (130 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = True
        system.manage_alarm()
        # Assert that the buzzer was turned OFF (updated in phase 2, see User Story #8).
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, False)
        # Assert that the alarm status was updated to OFF.
        self.assertFalse(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_hypoxia_and_normal_heart_rate(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [87, 75]  # Hypoxia (87%), normal heart rate (75 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = False
        system.manage_alarm()
        # Assert that the buzzer was turned ON (updated in phase 2, see User Story #8).
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, True)
        # Assert that the alarm status was updated to ON.
        self.assertTrue(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_no_hypoxia(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [88, 75]  # Normal SpO2 (88%), normal heart rate (75 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = True
        system.manage_alarm()
        # Assert that the buzzer was turned OFF.
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, False)
        # Assert that the alarm status was updated to OFF.
        self.assertFalse(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_invalid_vital_signs(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.side_effect = SmartBedsideError  # Simulate an invalid SpO2 or heart rate reading.
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = True
        # Assert that the SmartBedsideError is propagated to the caller.
        self.assertRaises(SmartBedsideError, system.manage_alarm)
        # Assert that the buzzer output was not changed.
        mock_gpio_output.assert_not_called()
        # Assert that the alarm status was not changed.
        self.assertTrue(system.alarm_on)


##########################################################################################
########################### Acceptance Tests for User Story #8 ###########################
##########################################################################################

class TestUserStory8(unittest.TestCase):

    @patch.object(GPIO, "setup")
    def test_alarm_led_initialization(self, mock_gpio_setup: MagicMock):
        system = SmartBedsideSystem()
        # Assert that the alarm LED is connected to BOARD pin 18.
        self.assertEqual(system.ALARM_LED_PIN, 18)
        accepted_calls = [
            call(system.ALARM_LED_PIN, GPIO.OUT),
            call(system.ALARM_LED_PIN, GPIO.OUT, initial=GPIO.LOW),
        ]
        # Assert that the alarm LED pin was configured as an output pin (optionally starting LOW, i.e. OFF).
        found = False
        for accepted_call in accepted_calls:
            if accepted_call in mock_gpio_setup.call_args_list:
                found = True
        self.assertTrue(found)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_led_on(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [87, 75]  # Hypoxia (87%), normal heart rate (75 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = False
        system.manage_alarm()
        # Assert that both the buzzer and the alarm LED were turned ON.
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, True)
        mock_gpio_output.assert_any_call(system.ALARM_LED_PIN, True)
        # Assert that the alarm status was updated to ON.
        self.assertTrue(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_alarm_led_off(self,
            mock_read_vital_signs: MagicMock, mock_gpio_output: MagicMock):
        mock_read_vital_signs.return_value = [95, 75]  # Normal SpO2 (95%), normal heart rate (75 BPM).
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = True
        system.manage_alarm()
        # Assert that both the buzzer and the alarm LED were turned OFF.
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, False)
        mock_gpio_output.assert_any_call(system.ALARM_LED_PIN, False)
        # Assert that the alarm status was updated to OFF.
        self.assertFalse(system.alarm_on)

##########################################################################################
########################### Acceptance Tests for User Story #9 ###########################
##########################################################################################

class TestUserStory9(unittest.TestCase):

    @patch.object(GPIO, "setup")
    def test_button_initialization(self, mock_gpio_setup: MagicMock):
        system = SmartBedsideSystem()
        accepted_calls = [
            call(system.BUTTON_PIN, GPIO.IN),
            call(system.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN),
        ]
        # Assert that the button pin was configured as an input pin (optionally with a pull-down).
        found = False
        for accepted_call in accepted_calls:
            if accepted_call in mock_gpio_setup.call_args_list:
                found = True
        self.assertTrue(found)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_stop_alarm_button_pressed_led_off(self,
            mock_gpio_input: MagicMock, mock_gpio_output: MagicMock):
        mock_gpio_input.return_value = True  # Simulate the pushbutton being pressed.
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = True
        system.stop_alarm()
        # Assert that both the buzzer and the alarm LED were turned OFF.
        mock_gpio_output.assert_any_call(system.BUZZER_PIN, False)
        mock_gpio_output.assert_any_call(system.ALARM_LED_PIN, False)
        # Assert that the alarm status was updated to OFF.
        self.assertFalse(system.alarm_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_stop_alarm_button_not_pressed_led_unchanged(self,
            mock_gpio_input: MagicMock, mock_gpio_output: MagicMock):
        mock_gpio_input.return_value = False  # Simulate the pushbutton not being pressed.
        system = SmartBedsideSystem()
        mock_gpio_output.reset_mock()  # Ignore GPIO.output calls made by the constructor.
        system.alarm_on = True
        system.stop_alarm()
        # Assert that neither the buzzer nor the alarm LED was changed.
        mock_gpio_output.assert_not_called()
        # Assert that the alarm status remains ON.
        self.assertTrue(system.alarm_on)

##########################################################################################
########################### Acceptance Tests for User Story #10 ##########################
##########################################################################################

class TestUserStory10(unittest.TestCase):

    @patch.object(GPIO, "PWM")
    @patch.object(GPIO, "setup")
    def test_o2_servo_initialization(self, mock_gpio_setup: MagicMock, mock_gpio_pwm: MagicMock):
        system = SmartBedsideSystem()
        # Assert that the servo motor pin was configured as an output pin.
        mock_gpio_setup.assert_any_call(system.O2_SERVO_PIN, GPIO.OUT)
        # Assert that the PWM instance was created with the correct pin and frequency.
        mock_gpio_pwm.assert_called_once_with(system.O2_SERVO_PIN, 50)
        # Assert that the PWM signal was started with a 5.0% duty cycle.
        mock_gpio_pwm.return_value.start.assert_called_once_with(5.0)
        # Assert that the servo angle was initialized to 0 degrees.
        self.assertEqual(system.o2_valve_angle, 0.0)

    @patch.object(GPIO, "PWM")
    def test_set_o2_valve_angle_invalid_above_limit(self, mock_gpio_pwm: MagicMock):
        system = SmartBedsideSystem()
        mock_gpio_pwm.return_value.reset_mock()  # Ignore servo calls made by the constructor.
        # Assert that SmartBedsideError is raised for an invalid angle.
        self.assertRaises(SmartBedsideError, system.set_o2_valve_angle, 181)
        # Assert that the servo position was not changed.
        mock_gpio_pwm.return_value.ChangeDutyCycle.assert_not_called()

    @patch.object(GPIO, "PWM")
    def test_set_o2_valve_angle_invalid_below_limit(self, mock_gpio_pwm: MagicMock):
        system = SmartBedsideSystem()
        mock_gpio_pwm.return_value.reset_mock()  # Ignore servo calls made by the constructor.
        # Assert that SmartBedsideError is raised for an invalid angle.
        self.assertRaises(SmartBedsideError, system.set_o2_valve_angle, -1)
        # Assert that the servo position was not changed.
        mock_gpio_pwm.return_value.ChangeDutyCycle.assert_not_called()

    @patch.object(GPIO, "PWM")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_oxygen_valve_severe_hypoxia(self,
            mock_read_vital_signs: MagicMock, mock_gpio_pwm: MagicMock):
        mock_read_vital_signs.return_value = [89, 75]  # Severe hypoxia (89%).
        system = SmartBedsideSystem()
        mock_gpio_pwm.return_value.reset_mock()  # Ignore servo calls made by the constructor.
        system.manage_oxygen_valve()
        # Assert that the servo duty cycle was set to 10.0% (valve fully open).
        mock_gpio_pwm.return_value.ChangeDutyCycle.assert_called_once_with(10.0)
        # Assert that the stored valve angle was updated to 180 degrees.
        self.assertEqual(system.o2_valve_angle, 180.0)

    @patch.object(GPIO, "PWM")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_oxygen_valve_mild_hypoxia_lower_bound(self,
            mock_read_vital_signs: MagicMock, mock_gpio_pwm: MagicMock):
        mock_read_vital_signs.return_value = [90, 75]  # Mild hypoxia (90%).
        system = SmartBedsideSystem()
        mock_gpio_pwm.return_value.reset_mock()  # Ignore servo calls made by the constructor.
        system.manage_oxygen_valve()
        # Assert that the servo duty cycle was set to 7.5% (valve half open).
        mock_gpio_pwm.return_value.ChangeDutyCycle.assert_called_once_with(7.5)
        # Assert that the stored valve angle was updated to 90 degrees.
        self.assertEqual(system.o2_valve_angle, 90.0)

    @patch.object(GPIO, "PWM")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_oxygen_valve_mild_hypoxia_upper_bound(self,
            mock_read_vital_signs: MagicMock, mock_gpio_pwm: MagicMock):
        mock_read_vital_signs.return_value = [94, 75]  # Mild hypoxia (94%).
        system = SmartBedsideSystem()
        mock_gpio_pwm.return_value.reset_mock()  # Ignore servo calls made by the constructor.
        system.manage_oxygen_valve()
        # Assert that the servo duty cycle was set to 7.5% (valve half open).
        mock_gpio_pwm.return_value.ChangeDutyCycle.assert_called_once_with(7.5)
        # Assert that the stored valve angle was updated to 90 degrees.
        self.assertEqual(system.o2_valve_angle, 90.0)

    @patch.object(GPIO, "PWM")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_oxygen_valve_normal_oxygenation(self,
            mock_read_vital_signs: MagicMock, mock_gpio_pwm: MagicMock):
        mock_read_vital_signs.return_value = [95, 75]  # Normal oxygenation (95%).
        system = SmartBedsideSystem()
        mock_gpio_pwm.return_value.reset_mock()  # Ignore servo calls made by the constructor.
        system.manage_oxygen_valve()
        # Assert that the servo duty cycle was set to 5.0% (valve fully closed).
        mock_gpio_pwm.return_value.ChangeDutyCycle.assert_called_once_with(5.0)
        # Assert that the stored valve angle was updated to 0 degrees.
        self.assertEqual(system.o2_valve_angle, 0.0)

    @patch.object(GPIO, "PWM")
    @patch.object(SmartBedsideSystem, "read_vital_signs")
    def test_manage_oxygen_valve_invalid_vital_signs(self,
            mock_read_vital_signs: MagicMock, mock_gpio_pwm: MagicMock):
        mock_read_vital_signs.side_effect = SmartBedsideError  # Simulate an invalid SpO2 or heart rate reading.
        system = SmartBedsideSystem()
        mock_gpio_pwm.return_value.reset_mock()  # Ignore servo calls made by the constructor.
        system.o2_valve_angle = 90.0
        # Assert that the SmartBedsideError is propagated to the caller.
        self.assertRaises(SmartBedsideError, system.manage_oxygen_valve)
        # Assert that the servo position was not changed.
        mock_gpio_pwm.return_value.ChangeDutyCycle.assert_not_called()
        # Assert that the stored valve angle was not changed.
        self.assertEqual(system.o2_valve_angle, 90.0)


##########################################################################################
######################## Run the acceptance tests of ALL user stories ####################
##########################################################################################

if __name__ == "__main__":
    unittest.main()
