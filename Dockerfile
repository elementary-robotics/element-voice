FROM elementaryrobotics/atom

ARG DEBIAN_FRONTEND=noninteractive

#
# Apt-get installs
#
RUN apt-get install -y portaudio19-dev libffi-dev libssl-dev libmpg123-dev sox libsox-fmt-all

# Want to copy over the contents of this repo to the code
#	section so that we have the source
ADD . /code

WORKDIR /code/google
RUN pip3 install -r requirements.txt

# Install the sounds
WORKDIR /code
RUN mkdir /usr/local/share/sounds
RUN cp sounds/* /usr/local/share/sounds

# Here, we'll build and install the code s.t. our launch script,
#	now located at /code/launch.sh, will launch our element/app



#
# TODO: build code
#

# Finally, specify the command we should run when the app is launched
WORKDIR /code
RUN chmod +x launch.sh
CMD ["/bin/bash", "launch.sh"]
