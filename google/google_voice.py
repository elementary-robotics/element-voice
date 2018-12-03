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

from multiprocessing import Process, Queue
import pygame

from atom import Element
from atom.messages import Response

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

class SoundElement(object):
    """
    Element for playing back sounds
    """
    def __init__(self, queue):
        self.q = queue

    def command_cb(self, data):
        self.q.put(data.decode('ascii'))
        return Response(data="Success")

def sound_element_thread(sound_queue):
    """
    Registers all of the sound playback commands for this element
    and handles when they're called
    """

    elem = Element("sound")

    # Register our callback to play sounds
    elem_class = SoundElement(sound_queue)
    elem.command_add("play_sound", elem_class.command_cb)
    elem.command_loop()


def sound_playback_thread(sound_queue):
    """
    Load the sounds and handle the queue to play them
    """
    pygame.init()

    sounds = Sounds()
    sounds.load_sound("success", "/usr/local/share/sounds/success.wav")
    sounds.load_sound("fail", "/usr/local/share/sounds/fail.wav")
    sounds.load_sound("on_start", "/usr/local/share/sounds/on_conversation_start.wav")

    # Loop, reading from the queue and playing sounds
    while True:

        sound = sound_queue.get()
        sounds.play_sound(sound)


def process_event(event, assistant, element, sound_queue):
    """
    Publishes the event on our data stream
    """

    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        sound_queue.put("on_start")

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

    # Set up the sound thread
    sound_queue = Queue()
    sound_thread = Process(target=sound_playback_thread, args=(sound_queue,))
    sound_thread.start()

    # Set up the process that will play sounds for other processes. This
    #   is needed until we get a shared PulseAudio system up and running
    #   s.t. all elements can play their own sounds
    sound_element = Process(target=sound_element_thread, args=(sound_queue,))
    sound_element.start()

    with Assistant(credentials, args.device_model_id) as assistant:

        # Create our element
        element = Element("voice")

        # Start the assistant
        events = assistant.start()

        for event in events:
            process_event(event, assistant, element, sound_queue)

if __name__ == '__main__':
    main()
