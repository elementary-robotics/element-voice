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

from atom import Element

def process_event(event, assistant, element):
    """
    Publishes the event on our data stream
    """

    # If speech finished, then we want to publish the string
    if (event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED):

        # Get the text and publish it
        speech_text = event.args["text"]

        # Write the entry
        element.entry_write("string", {"d" : speech_text})

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

    with Assistant(credentials, args.device_model_id) as assistant:

        # Create our element
        element = Element("voice")

        # Start the assistant
        events = assistant.start()

        for event in events:
            process_event(event, assistant, element)

if __name__ == '__main__':
    main()
