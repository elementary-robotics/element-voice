#!/usr/bin/env python

# google voice client, start listen voice input by google assistant and publish text to ros node
# Copyright (C) 2018 Elemtary Robotics Inc.
from __future__ import print_function

import argparse
import os.path
import json

import google.auth.transport.requests
import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

from multiprocessing import Process
import pygame

from atom import Element

class Sounds(object):
    """
    Class that plays all sounds
    """
    def __init__(self):
        self.sounds = {}

    def load_sound(self, name, filename):
        self.sounds[name] = pygame.mixer.Sound(filename)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()
            print ("Played sound {}".format(name))
            return True
        else:
            print("Sound {} not supported!".format(name))
            return False

    def command_cb(self, data):
        data_str = str(data).decode('ascii')
        print("In commmand cb")
        return "Success" if self.play_sound(data_str) else "Failure"

def sound_thread():
    """
    Registers all of the sound playback commands for this element
    and handles when they're called
    """
    pygame.init()

    sound_element = Element("sound")

    sounds = Sounds()
    #sounds.load_sound("success", "/usr/local/share/sounds/success.mp3")
    sounds.load_sound("fail", "/usr/local/share/sounds/fail.wav")

    # Register our callback to play sounds
    sound_element.command_add("play_sound", sounds.command_cb)
    sound_element.command_loop()


def process_event(event, assistant, element, sound_start):
    """
    Publishes the event on our data stream
    """

    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        sound_start.play()

    # If speech finished, then we want to publish the string
    if (event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED):

        # Get the text and publish it
        speech_text = event.args["text"]

        # Write the entry
        element.entry_write("string", {"data" : speech_text})

        # Stop the conversation
        assistant.stop_conversation()

    # Always print the event
    print(event)

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    parser.add_argument('--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=True,
                        help='The device model ID registered with Google')

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s ' +
        Assistant.__version_str__())

    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

    # Set up the sound playback
    pygame.init()
    sound_start = pygame.mixer.Sound("/usr/local/share/sounds/on_conversation_start.wav")

    # Set up the process that will play sounds for other processes. This
    #   is needed until we get a shared PulseAudio system up and running
    #   s.t. all elements can play their own sounds
    sound_process = Process(target=sound_thread)
    sound_process.start()

    with Assistant(credentials, args.device_model_id) as assistant:

        # Create our element
        element = Element("voice")

        # Start the assistant
        events = assistant.start()

        for event in events:
            process_event(event, assistant, element, sound_start)

if __name__ == '__main__':
    main()
