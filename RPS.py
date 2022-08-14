from Timer import Timer
from flask import Flask, request, jsonify
import requests
from flask_apscheduler import APScheduler
import sched, time
from datetime import datetime, timedelta
import json
from gtts import gTTS
import os
from mutagen.mp3 import MP3

emailId = 'mohammedali.turkumani@gmail.com'
node_server = '192.168.80.184:3000'
my_ip = "192.168.229.148"
interval = 10
seconds_debug = "50"
audioDBjsonfile = 'audioDB.json'


# set configuration values
class Config:
    SCHEDULER_API_ENABLED = True
# create app
app = Flask(__name__)
app.config.from_object(Config())

# initialize scheduler
scheduler = APScheduler()
# if you don't wanna use a config, you can set options here:
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
task_sche = sched.scheduler(time.time, time.sleep)

def save_json(ob, fp):
    with open(fp, 'w') as f:
        json.dump(ob, f)
        
def load_json(file_name):
    return json.load(open(file_name))
    
def parse_dd(task_date, task_time):
    month, day, year = task_date.split()
    hours, minutes = task_time.split(":")
    months = {
        "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
        "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
        "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
    }
    for i in months:
        if months[i] == month:
            month = i
    return year, month, day[0:-1], hours, minutes, seconds_debug

def comp_timestamp(task_date, task_time):
    year, month, day, hours, minutes, seconds = parse_dd(task_date, task_time)
    tmp = year + "-" + month + "-" + day + "-" + \
        hours + "-" + minutes + "-" + seconds
    # print(tmp)
    # getting date for any further manipulation
    datetimee = datetime.strptime(tmp, '%Y-%m-%d-%H-%M-%S')
    return int(datetimee.timestamp())

def tts(mytext,name):
    language = 'en'
    myobj = gTTS(text=mytext, lang=language, slow=False)
    myobj.save(name+ ".mp3")
    audio = MP3(name+ ".mp3")
    audio_len = audio.info.length
    # windows
    for ite in range(3):
        time.sleep(4+audio_len)
        os.system("start "+name+".mp3")

def reboot_json_read():
    audioDB = dict()
    try:
        audioDBold = load_json(audioDBjsonfile)
    except:
        save_json(audioDB, audioDBjsonfile)
        return
    
    now_timestamp = int(datetime.now().timestamp())
    for tasktimestamp in audioDBold:
        if int(tasktimestamp) < now_timestamp:
            continue
        else:
            task_text = audioDBold[tasktimestamp]
            audioDB[tasktimestamp] = audioDBold[tasktimestamp]
            task_sche.enterabs(int(tasktimestamp), priority=1, action=tts, argument=(task_text,str(tasktimestamp),))
    print(task_sche.queue)
    save_json(audioDB, audioDBjsonfile)
        
@app.route('/esp', methods=['POST'])
def reset_counter():
    content = request.get_data() 
    print(t.elapsed())
    t.reset()
    return ""

@app.route('/node-audio',methods=['POST'])
# saves requests pf task in a json file
def audionode():
    content = request.json
    task_date = content["task_alarm_date"]
    task_time = content["task_alarm_time"]
    task_text = content["task_name"]
    tasktimestampcurr = comp_timestamp(task_date, task_time)
    now_timestamp = int(datetime.now().timestamp())    
    if tasktimestampcurr > now_timestamp:
        audioDB = load_json(audioDBjsonfile)
        audioDB[tasktimestampcurr] = task_text
        task_sche.enterabs(int(tasktimestampcurr), priority=1, action=tts, argument=(task_text,str(tasktimestampcurr),))
        save_json(audioDB, audioDBjsonfile)
    return ""

@scheduler.task('interval', id='do_job_1', seconds=2*interval, misfire_grace_time=None)
def job1():
    if t.elapsed()>interval:
        # alarm node
        r = requests.post('http://'+node_server+'/api/v1/users/SentEmail', json={'email': emailId})

@scheduler.task('interval', id='do_job_2', seconds=20, misfire_grace_time=2)
def runnn():
    # print(task_sche.queue)
    task_sche.run()
    
@scheduler.task('interval', id='do_job_3', seconds=60*5, misfire_grace_time=None)
def deletemp3files():
    # listing mp3 files
    mp3files = glob.glob("*.mp3")
    now_timestamp = int(datetime.now().timestamp())
    for mp3f in mp3files:
        mp3file_timestamp = int(mp3f[0:-4])
        if mp3file_timestamp < now_timestamp:
            os.system("del /f "+str(mp3file_timestamp)+".mp3")
            
def update_audioDB():
    now_timestamp = int(datetime.now().timestamp())
    audioDB = dict()
    audioDBold = load_json(audioDBjsonfile)
    for tasktimestamp in audioDBold:
        if int(tasktimestamp) < now_timestamp:
            continue
        else:
            task_text = audioDBold[tasktimestamp]
            audioDB[tasktimestamp] = audioDBold[tasktimestamp]
            task_sche.enterabs(int(tasktimestamp), priority=1, action=tts, argument=(task_text,str(tasktimestamp),))
    save_json(audioDB, audioDBjsonfile)
    
    
if __name__ == '__main__':
    t = Timer()
    reboot_json_read()
    app.run(my_ip)
    
