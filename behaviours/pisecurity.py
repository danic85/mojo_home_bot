#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nmap
from functools import partial
from time import sleep
from simple_salesforce import Salesforce
from behaviours.behaviour import Behaviour

try:
    import RPi.GPIO as GPIO
except ImportError as e:
    pass


class Pisecurity(Behaviour):
    routes = {
        '^security on$': 'on',
        '^security off$': 'off',
        '^test security$': 'test',
        '^monitor room$': 'monitor_with_salesforce',
        '^stop monitoring room$': 'stop_monitor_with_salesforce'
    }

    PIR_PIN = 23
    PIR_LED_PIN = 17

    SECURITY_OFF = 0
    SECURITY_TEST = 1
    SECURITY_ON = 2

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.assistant = kwargs.get('assistant', None)
        self.security = self.SECURITY_OFF
        self.security_override = False

    def monitor_with_salesforce(self):
        self.logging.info('Monitoring Room')
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.PIR_PIN, GPIO.BOTH, self.__detect_motion_salesforce, bouncetime=300)
        return 'Monitoring room on Salesforce'
        
    def stop_monitor_with_salesforce(self):
        self.logging.info('Stop Monitoring Room')
        GPIO.remove_event_detect(self.PIR_PIN)
        return 'Stopped monitoring room on Salesforce'

    def test(self):
        response = self.on()
        if response is not None:
            self.security = self.SECURITY_TEST
            # test LED output
            GPIO.output(self.PIR_LED_PIN, GPIO.HIGH)
            sleep(2)
            GPIO.output(self.PIR_LED_PIN, GPIO.LOW)

        return response + ' (Test)'

    def on(self):
        if self.security == self.SECURITY_OFF:
            try:
                self.logging.info('Starting PIR')
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                GPIO.setup(self.PIR_LED_PIN, GPIO.OUT)
                GPIO.add_event_detect(self.PIR_PIN, GPIO.BOTH, self.__motion_sensor, bouncetime=300)
                self.security = self.SECURITY_ON
                return 'Security Enabled'
            except NameError as e:
                return 'Could not start security: ' + str(e)
        return None

    def off(self):
        if self.security != self.SECURITY_OFF:
            try:
                self.logging.info('Stopping PIR')
                GPIO.remove_event_detect(self.PIR_PIN)
                self.security = self.SECURITY_OFF
                return 'Security Disabled'
            except NameError as e:
                return 'Could not stop security: ' + str(e)
        return None

    # Callback function to run when motion detected
    def __motion_sensor(self, PIR_PIN):
        GPIO.output(self.PIR_LED_PIN, GPIO.LOW)
        if GPIO.input(self.PIR_PIN):  # True = Rising
            GPIO.output(self.PIR_LED_PIN, GPIO.HIGH)
            if self.security == self.SECURITY_ON:
                self.logging.info('Taking Security Picture')
                if self.assistant is not None:
                    msg = {"chat": {"id": self.assistant.config.get_or_request('Admin')}, "text": 'camera'}
                    self.assistant.handle(msg)
                else:
                    self.logging.error('Assistant not set')
                    
    def __detect_motion_salesforce(self, PIR_PIN):
        if GPIO.input(self.PIR_PIN):  # True = Rising
            sf = Salesforce(username=self.assistant.config.get_or_request('SFUsername'), 
                            password=self.assistant.config.get_or_request('SFPassword'), 
                            security_token=self.assistant.config.get_or_request('SFToken'))
            results = sf.query("SELECT Id FROM Room__c WHERE Name = 'Archie'");
            room_id = None
            items = list(results.items())
            for key, value in items:
                if key == 'records':
                    for k, v in value[0].items():
                        if k == 'Id':
                            room_id = v
                            break
            self.logging.info('RoomId: ' + room_id)
            if (room_id):
                motion = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                sf.Room__c.update(room_id, {'Motion_Detected__c': motion})
            else:
                self.logging.error('Could not find room')
