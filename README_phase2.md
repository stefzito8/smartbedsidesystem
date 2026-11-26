# SmartBedsideSystem – Phase 2 (Maintenance)

*SmartBedsideSystem* is a bedside care system built on a Raspberry Pi that monitors a patient's vital signs, manages emergency alarms, and regulates oxygen delivery.

The system includes the following sensors and actuators:

- A **pulse oximeter and heart-rate sensor** (MAX30102), used to measure the patient's vital signs.
- An **active buzzer module** (KY-012), used to raise an emergency alarm.
- A **pushbutton** (B3F-1020), used to silence the emergency alarm.
- A **servo motor** (MG90S), used to regulate the oxygen delivery valve.

This is the hardware supported by the current version of the system. The user stories of this phase may add new components.

The buzzer, the pushbutton, and the servo motor are connected to the Raspberry Pi through GPIO pins, while the MAX30102 sensor communicates over the I²C bus (BOARD pins 3 and 5), which is fully managed by the sensor's library. The GPIO numbering is already configured in BOARD mode (i.e., GPIO pins are referred to by their physical number on the board).

## About This Phase

You developed the first version of *SmartBedsideSystem* in the previous phase (see `README.md` for its requirements). The system is now in **maintenance**: new requirements have emerged, and you are asked to **evolve** your existing code to satisfy them.

The new requirements are described through **user stories**, starting from User Story #6. The number of user stories you are asked to implement depends on how many user stories you correctly implemented in the previous phase. Some of them **add new features**, while others **change the behavior** of existing ones. Each user story states its type at the top.

## Instructions for You

You are asked to maintain and extend your existing *SmartBedsideSystem* code. In this phase, the LLM Group and the NO_LLM Group of the previous phase are merged into a single group, the **NO_LLM Group**: all students follow the rules below.

### NO_LLM Group

- You **MUST** use **DuckDuckGo** as your **ONLY** search engine, with all AI features disabled: <https://duckduckgo.com>.
- You **CAN** also write code without the support of DuckDuckGo.
- You **CAN** use:
  - Any resource found through DuckDuckGo (e.g., documentation, tutorials, Stack Overflow).
  - The course material.
  - Code from your previous projects (including earlier lab exercises).
- You **CANNOT** use:
  - Other search engines (e.g., Google, Bing).
  - AI tools, chatbots, LLMs, or similar technologies.

### Rules for Everyone

- You **CANNOT** change the signatures of the provided methods, move the provided methods to other classes, or change the names of the provided classes and instance variables, **unless a user story explicitly asks you to**.
- You **CANNOT** interact with your colleagues. Work independently and do your best!
- Each **USER STORY** is accompanied by an **ACCEPTANCE TEST SUITE**.
- You **DO NOT** need to write tests, and you **CANNOT** change the existing acceptance test suites.
- The new requirements are divided into a set of **USER STORIES**, which serve as a to-do list.
- You should be able to evolve *SmartBedsideSystem* incrementally, without having to understand all the user stories upfront. **DO NOT read ahead.** Instead, address the user stories one at a time, following the order in which they are provided. Start by implementing the requirements of the first user story (User Story #6). Once a story has been **IMPLEMENTED**, move on to the **NEXT** one. A story is considered **IMPLEMENTED** when its acceptance test suite **PASSES**. Naturally, all acceptance test suites for previously implemented stories must continue to pass as well. You may need to revise your program as you progress through subsequent user stories.
- Each time you **IMPLEMENT** a user story, **COMMIT** your changes.
- Whenever a user story requires you to handle an error situation, raise a `SmartBedsideError` exception. Do **NOT** add error checks that are not required by the user stories.
- At the end of the task, remember to fill in the **POST-QUESTIONNAIRE**: <https://forms.gle/Uy7gBP4Hy6Q1ksEs9>

## Project Structure

The project is organized as follows:

```
smartbedsidesystem/
├── mock/
│   ├── __init__.py                         # Marks the folder as a Python package
│   ├── GPIO.py                             # Mock of the RPi.GPIO library
│   └── max30102.py                         # Mock of the DFRobot_BloodOxygen_S library (MAX30102 sensor)
├── src/
│   ├── __init__.py                         # Marks the folder as a Python package
│   ├── smart_bedside_error.py              # SmartBedsideError exception
│   └── smart_bedside_system.py             # SmartBedsideSystem class (to be maintained)
├── test/
│   ├── __init__.py                         # Marks the folder as a Python package
│   ├── test_smart_bedside_system.py        # OBSOLETE: acceptance tests of the previous phase (do NOT run)
│   └── test_smart_bedside_system_phase2.py # NEW: acceptance test suites for the user stories of this phase
├── README.md                               # Instructions of the previous phase (phase 1): for reference only
└── README_phase2.md                        # NEW: instructions for this phase (this file)
```

**Note:** `README.md` contains the instructions of the previous phase (phase 1). In this phase, follow **ONLY** the instructions in `README_phase2.md` (this file).

As in the previous phase, the `RPi.GPIO` and `DFRobot_BloodOxygen_S` libraries are mocked for this project (see the `mock` folder), so you can implement the new requirements of *SmartBedsideSystem* on your computer, without a Raspberry Pi or any physical component.

**Important:** The test file of the previous phase, `test/test_smart_bedside_system.py`, is now **OBSOLETE**: some of its tests no longer reflect the current requirements and will fail once you implement the user stories of this phase. Do **NOT** run it, and do **NOT** try to make it pass. It has been replaced by the new test file `test/test_smart_bedside_system_phase2.py`, which you have received for this phase.

**Running the tests:** The acceptance tests of this phase are in `test/test_smart_bedside_system_phase2.py`, grouped into one test class per user story (`TestUserStory6`, `TestUserStory7`, ..., `TestUserStory10`). In PyCharm, you can run them in two ways:

- **Tests of all user stories (recommended):** right-click on `test_smart_bedside_system_phase2.py` and select *Run*. Do **NOT** run the whole `test` folder: it would also run the obsolete test file.
- **Tests of a single user story:** click the green run icon next to the corresponding class (e.g., `class TestUserStory7`) and select *Run*. This can help you focus on a specific user story, for example while fixing a failing test.

We recommend to **ALWAYS** run the tests of **ALL** user stories: a change made for the current user story may break a previously implemented one. In any case, before **COMMITTING**, you **MUST** run all the tests in `test_smart_bedside_system_phase2.py` and make sure that the tests of the user stories implemented so far pass.

## API Usage

You already used the `RPi.GPIO` and `DFRobot_BloodOxygen_S` libraries in the previous phase. Any API element that is new in this phase is described in the user story that requires it.

## User Stories

### User Story #6 – Read the Patient's Heart Rate

**Type:** change (this story changes the behavior defined in User Story #1)

In addition to the blood oxygen saturation (SpO₂), *SmartBedsideSystem* must now also monitor the patient's **heart rate**, measured by the same MAX30102 sensor used for the SpO₂ (see User Story #1).

**Reading the Heart Rate**

To retrieve the patient's current heart rate, call the `DFRobot_BloodOxygen_S.get_heartbeat() -> int` method. It returns an integer representing the heart rate, in beats per minute (BPM).

**MAX30102 Sensor Description**

If the sensor cannot determine a valid heart rate reading, `get_heartbeat()` returns `-1` (e.g., when the finger slips off), just like `get_spo2()`.

**Requirements**

- Change the return type of `SmartBedsideSystem.read_vital_signs()` from `int` to `list`, i.e., its signature becomes `read_vital_signs(self) -> list`.
- Update `SmartBedsideSystem.read_vital_signs()` to:
  - Retrieve the patient's SpO₂ by calling `get_spo2()` on the sensor stored in `SmartBedsideSystem.spo2_hr_sensor` (as in User Story #1).
  - Retrieve the patient's heart rate by calling `get_heartbeat()` on the same sensor.
  - If `get_spo2()` returns `-1`, raise a `SmartBedsideError`.
  - If `get_heartbeat()` returns `-1`, raise a `SmartBedsideError`.
  - Otherwise, return a **list** containing the patient's vital signs, in this order: `[spo2, heart_rate]`.

**Note:** Since `read_vital_signs()` no longer returns a single value, the methods that use it (`SmartBedsideSystem.manage_alarm()` and `SmartBedsideSystem.manage_oxygen_valve()`) may no longer work correctly. Do **NOT** worry about them for now: you will update them in subsequent user stories.

Acceptance tests: `TestUserStory6` in `test/test_smart_bedside_system_phase2.py`.

> **Reminder:** Once all the tests in `TestUserStory6` pass, **COMMIT** your changes before moving on to User Story #7.

### User Story #7 – Raise the Alarm on Abnormal Heart Rate

**Type:** change (this story changes the behavior defined in User Story #2)

With heart rate monitoring now available (see User Story #6), the emergency alarm must trigger not only on **hypoxia** (low SpO₂), but also on **bradycardia** (heart rate too low) or **tachycardia** (heart rate too high).

**Alarm Rules**

Use the patient's vital signs returned by `SmartBedsideSystem.read_vital_signs()` (see User Story #6) to determine whether the alarm should be activated:

- If SpO₂ `< 88` (hypoxia), **OR** heart rate `< 50` BPM (bradycardia), **OR** heart rate `> 130` BPM (tachycardia), turn **ON** the alarm buzzer and set `SmartBedsideSystem.alarm_on` to `True`.
- Otherwise (SpO₂ `>= 88` **AND** `50 <=` heart rate `<= 130`), turn **OFF** the alarm buzzer and set `SmartBedsideSystem.alarm_on` to `False`.

**Requirements**

- Update `SmartBedsideSystem.manage_alarm() -> None` to:
  - Retrieve the patient's SpO₂ and heart rate by calling `SmartBedsideSystem.read_vital_signs()`.
  - Control the alarm buzzer according to the alarm rules described above.
  - Update `SmartBedsideSystem.alarm_on` to reflect the current alarm status.
- If the SpO₂ or the heart rate reading is invalid (i.e., the sensor returns `-1`), `SmartBedsideSystem.read_vital_signs()` raises a `SmartBedsideError` (see User Story #6). As before, do **NOT** catch it: let it propagate to the caller, leaving the alarm buzzer and `SmartBedsideSystem.alarm_on` unchanged.

Acceptance tests: `TestUserStory7` in `test/test_smart_bedside_system_phase2.py`.

> **Reminder:** Once all the tests in `TestUserStory7` pass (together with those of the previous user stories of this phase), **COMMIT** your changes before moving on to User Story #8.

### User Story #8 – Add a Visual Alarm LED

**Type:** new feature (this story also changes the behavior defined in User Story #7)

To make emergencies visible, *SmartBedsideSystem* is now equipped with a **red alarm LED**, which lights up whenever the alarm is activated.

The alarm LED is connected to the Raspberry Pi using **BOARD pin 18**.

The LED is controlled using the `GPIO.output(channel, value) -> None` function, where `channel` is the GPIO pin and `value` is a boolean value (`False` or `True`):

- `True`: turns the LED ON.
- `False`: turns the LED OFF.

**Requirements**

- Add the constant `ALARM_LED_PIN = 18` to the `SmartBedsideSystem` class, next to the other pin constants.
- Update the `SmartBedsideSystem` constructor to configure BOARD pin 18 as an output pin, using the new constant.
- Update `SmartBedsideSystem.manage_alarm()` (see User Story #7) so that the alarm LED follows the alarm buzzer:
  - When the alarm buzzer is turned **ON**, turn **ON** the alarm LED as well.
  - When the alarm buzzer is turned **OFF**, turn **OFF** the alarm LED as well.

Acceptance tests: `TestUserStory8` in `test/test_smart_bedside_system_phase2.py`.

> **Reminder:** Once all the tests in `TestUserStory8` pass (together with those of the previous user stories of this phase), **COMMIT** your changes before moving on to User Story #9.

### User Story #9 – Turn Off the Alarm LED with the Pushbutton

**Type:** change (this story changes the behavior defined in User Story #3)

When medical staff press the pushbutton to stop the alarm (see User Story #3), the alarm LED (see User Story #8) must be turned off together with the alarm buzzer.

**Pushbutton Behavior**

- If the button is pressed (`True`), turn **OFF** both the alarm buzzer and the alarm LED, and set the alarm status (boolean instance variable `SmartBedsideSystem.alarm_on`) to `False`.
- If the button is not pressed (`False`), do nothing and leave the alarm buzzer, the alarm LED, and the alarm status unchanged.

**Requirements**

- Update `SmartBedsideSystem.stop_alarm()` so that the alarm LED is turned off together with the alarm buzzer, according to the pushbutton behavior described above.

Acceptance tests: `TestUserStory9` in `test/test_smart_bedside_system_phase2.py`.

> **Reminder:** Once all the tests in `TestUserStory9` pass (together with those of the previous user stories of this phase), **COMMIT** your changes before moving on to User Story #10.

### User Story #10 – Three-Tier Oxygen Delivery

**Type:** change (this story changes the behavior defined in User Story #5)

Instead of opening the oxygen delivery valve only at `0` or `180` degrees, the oxygen delivery controller is upgraded to support a **three-tier oxygenation curve** based on the patient's SpO₂.

**Oxygen Valve Behavior**

- **Severe hypoxia** (SpO₂ `< 90`): fully open the oxygen delivery valve by setting its angle to `180.0` degrees.
- **Mild hypoxia** (`90 <=` SpO₂ `< 95`): half open the oxygen delivery valve by setting its angle to `90.0` degrees.
- **Normal oxygenation** (SpO₂ `>= 95`): fully close the oxygen delivery valve by setting its angle to `0.0` degrees.

**Requirements**

- Update `SmartBedsideSystem.manage_oxygen_valve() -> None` to:
  - Retrieve the patient's SpO₂ by calling `SmartBedsideSystem.read_vital_signs()`. Remember that this method now returns a list (see User Story #6).
  - Set the valve angle according to the behavior described above, by calling `SmartBedsideSystem.set_o2_valve_angle()` (see User Story #4).
- As before, if `SmartBedsideSystem.read_vital_signs()` raises a `SmartBedsideError`, do **NOT** catch it: let it propagate to the caller, leaving the valve and `SmartBedsideSystem.o2_valve_angle` unchanged.

Acceptance tests: `TestUserStory10` in `test/test_smart_bedside_system_phase2.py`.

> **Reminder:** Once all the tests in `TestUserStory10` pass (together with those of the previous user stories of this phase), **COMMIT** and **PUSH** your changes to complete the task. Then, fill in the **POST-QUESTIONNAIRE**: <https://forms.gle/Uy7gBP4Hy6Q1ksEs9>
