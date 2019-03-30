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

### Credentials

#### Generating Credentials


You'll need to hook your own Google voice credentials into the system in order for the voice module to work. To do this, perform the following steps:

1. Go to the [Actions Console](https://console.actions.google.com/u/0/) and make a new project
2. Once at the screen with a bunch of smart home card options, click on "register device"
3.  Click on "register model" in the middle of the resulting page. Follow the prompts.
4.  Put the the `client_secret*.json` file in a new, empty folder on your machine. We'll need to use it to generate credentials for the google assistant SDK to work. All of the packages to run the voice element are installed in the docker container, so we'll mount the folder with the secret into the docker container and generate the new credentials into that folder as well.
5. Modify the `docker-compose` file to add this line in the `volumes` section:
```
- "/path/to/secret/folder:/credentials"
```
6. Modify the `docker-compose` file to just boot the container and let us pull a shell up in it
```
command: tail -f /dev/null
```
7. Now, run `docker-compose up -d` and then `docker exed -it voice bash` to pull
up a shell in the voice container. Run the following commands:
```
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
google-oauthlib-tool --scope https://www.googleapis.com/auth/assistant-sdk-prototype --scope https://www.googleapis.com/auth/gcm --save --headless --client-secrets /credentials/$my_client_secret.json
```
8. This should generate a link that you can open in a browser to authenticate and generate a credential file. If you see an error about not having your Oauth registration page set up yet, [see this document](https://developers.google.com/assistant/sdk/guides/library/python/embed/config-dev-project-and-account), it's something you just need to enable somewhere deep in the caverns of the google cloud console.
9. Once through the authentication screen, you should get a code that we can then put back into oauthlib tool. If all goes well, the tool will spit out something like:
```
credentials saved: /root/.config/google-oauthlib-tool/credentials.json
```
10. Finally, we just need to move the credentials out of the container and onto our host machine s.t. we never have to go through the most convoluted process to generate credentials ever again. Simply move them from where the tool put them into `/credentials`
```
mv /root/.config/google-oauthlib-tool/credentials.json /credentials/
```
11. Voila! We should now have credentials on your host machine. Reset the `docker-compose` file to the example configuration below
12. If you hear the google assitant saying "something went wrong", you might still need to enable the google assistant API for your project. You should be able to do this from the google cloud console.

#### Passing Credentials to the Docker Container

1. Ensure you have the `credential.json` file from the previous step in a safe place on your machine.
2. Link the `credential.json` into the `voice` container at runtime using the `volumes` section as seen below. DO NOT CHECK THIS INTO THE CODE.
3. Optionally, set the `DEVCICE_MODEL_ID` parameter in the `environment` section of the docker-compose s.t. you can trace which google voice API calls are coming from which device.

### Commands

None

### Streams
| Stream | Format | Description |
| ------ | ------ | ----------- |
| `string` | string | Published each time the voice API detects the hotword and processes speech-to-text |


### docker-compose configuration

```yaml
  voice:
    container_name: voice
    image: elementaryrobotics/element-voice
    volumes:
      - type: volume
        source: shared
        target: /shared
        volume:
          nocopy: true
      - "~/google_voice/credential.json:/code/google/credential.json"
    depends_on:
      - "nucleus"
    environment:
      - "DEVICE_MODEL_ID=SOME_DEVICE_MODEL_ID"
    privileged: true

```

Note that we need the `privileged: true` setting in order to use the computer's built-in mic hardware.
