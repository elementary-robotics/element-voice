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

def process_event(event, assistant):
    """Pretty prints events.

    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.

    Args:
        event(event.Event): The current event to process.
        device_id(str): The device ID of the new instance.
    """
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        print("start")

    print(event)

    if (event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED):
        speech_text = event.args["text"]
        print("speech text: " + speech_text)
        assistant.stop_conversation()

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
        events = assistant.start()

        print('device_model_id:', args.device_model_id + '\n' +
              'device_id:', assistant.device_id + '\n')

        for event in events:
            process_event(event, assistant)

if __name__ == '__main__':
    main()
