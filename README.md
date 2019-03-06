## Voice

### Build Status

[![CircleCI](https://circleci.com/gh/elementary-robotics/element-voice.svg?style=svg&circle-token=909a614aab68a938fa77e7420b2b1651c8cf8289)](https://circleci.com/gh/elementary-robotics/element-voice)

### Overview

The voice element will listen to audio from the microphone and will
publish all strings on a stream named `strings`. For now the voice element
only runs on Linux systems, but we should be able to get it up and running
on Mac/Windows without too much effort.

Currently uses Google Voice as a backend. All voice commands should be
prepended with "OK Google".

### Commands

None

### Streams
| Stream | Format | Description |
| ------ | ------ | ----------- |
| `string` | string | Published each time the voice API detects the hotword and processes speech-to-text |


### docker-compose configuration

```yaml
  voice:
    omage: elementaryrobotics/element-voice
    volumes:
      - type: volume
        source: shared
        target: /shared
        volume:
          nocopy: true
    depends_on:
      - "nucleus"
    privileged: true

```

Note that we need the `privileged: true` setting in order to use the computer's built-in mic hardware.
