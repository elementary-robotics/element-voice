# Voice Element

The voice element will listen to audio from the microphone and will
publish all strings on a stream named `strings`.

## Build Status

[![CircleCI](https://circleci.com/gh/elementary-robotics/element-voice.svg?style=svg&circle-token=909a614aab68a938fa77e7420b2b1651c8cf8289)](https://circleci.com/gh/elementary-robotics/element-voice)

## Running

When the element is launched without overriding the command it will
boot up and immediately begin publishing text strings to
`stream:voice:string`. All users can read on this stream and react to
voice commands as they please.
