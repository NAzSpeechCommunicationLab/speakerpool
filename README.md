# SpeakerPool
Remote speech data collection with Flask

# Setup
git clone https://github.com/tschnoor/SpeakerPool.git

cd speakerpool

create the virtual environment

activate the virtual environment

pip install -r requirements.txt

sudo apt-get install libsndfile1-dev

to run:
  
sudo SCRIPT_NAME=/speakerpool ./sp-env/bin/gunicorn -c gunicorn.conf.py -b 127.0.0.1:5003 run:app


*Had to implement the temporary solution for setting the SCRIPT_NAME (URL prefix) described in this issue: https://github.com/benoitc/gunicorn/issues/679


