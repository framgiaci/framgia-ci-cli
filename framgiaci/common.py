import os
import yaml
import sys
import pycurl
import json
import hashlib
import hmac
import subprocess
import time

from io import BytesIO

def run_command(command):
    try:
        procR = {"cmd": 0, "time": "0s"}
        timeStarted = time.time()      
        print("[+] Running: ", command)
        subproc = subprocess.run(command, shell=True, timeout=7200)
        timeDelta = time.time() - timeStarted 
        procR["cmd"] = subproc
        procR["time"] = str(timeDelta) + "s"
        return procR

    except Exception as e:
        print('[!] Error:', e)
        return 1

def exec_command_silent(command):
    try:
        return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=7200)

    except Exception as e:
        print('[!] Error:', e)
        return 1

def exec_command(command):
    try:
        return subprocess.run(command, shell=True, timeout=7200)

    except Exception as e:
        print('[!] Error:', e)
        return 1

def run_command_silent(command):
    try:
        procR = {"cmd": 0, "time": "0s"}
        timeStarted = time.time() 
        print("[+] Running: ", command)
        subproc =  subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=7200)
        timeDelta = time.time() - timeStarted 
        procR["cmd"] = subproc
        procR["time"] = str(timeDelta) + "s"
        return procR

    except Exception as e:
        print('[!] Error:', e)
        return 1

def read_yaml_file(file):
    try:
        with open(file, "r") as f:
            return yaml.load(f.read())
    except Exception as e:
        print('Can not read file', file)
        sys.exit(1)


def read_results(temp_file):
    return read_yaml_file(temp_file)

def read_diff_files(temp_file):
    try:
        with open(temp_file, "r") as f:
            return yaml.load(f.readline())
    except Exception as e:
        print('Can not read file', temp_file)
        sys.exit(1)


def write_results(results, temp_file):
    with open(temp_file, 'a+') as outfile:
        yaml.safe_dump(results, outfile, default_flow_style=False)


def print_header(text):
    print("\n------------------------------------------")
    print(text)
    print("------------------------------------------\n")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.realpath(__file__))

    return os.path.join(base_path, relative_path)

def buid_template_file_path(template_dir, file_name):
    return os.path.join(resource_path(template_dir), "%s.yml" % file_name)

def read_template_file(template_dir, file_name):
    return read_yaml_file(buid_template_file_path(template_dir, file_name))

def merge_test_config(base, overwrite):
    if not base:
        return overwrite
    result = {}
    merged_tools = [key for key in overwrite.keys()] + [key for key in base.keys()]
    merged_tools = list(set(merged_tools))
    defaults = {
        'comment': True,
        'ignore': False,
        'enable': True
    }
    for tool in merged_tools:
        if tool not in overwrite:
            result[tool] = base[tool]
        else:
            result[tool] = {}
            for key, value in defaults.items():
                result[tool][key] = overwrite[tool].get(key, base[tool].get(key, defaults[key]))
            result[tool]['command'] = overwrite[tool].get('command', base[tool]['command'])
            for key in [k for k in overwrite[tool].keys() if k not in list(defaults.keys()) + ['command']]:
                result[tool][key] = overwrite[tool][key]

    return result

def build_params():
    repo = os.environ.get('FRAMGIACI_REPO').split('/')
    message = str(repo[0])+str(repo[1])+str(os.environ.get('FRAMGIACI_BUILD_NUMBER'))+str(os.environ.get('FRAMGIACI_COMMIT'))
    return {
        'workspace': {
            'path': os.environ.get('FRAMGIACI_DIR')
        },
        'repo': {
            'owner': repo[0],
            'name': repo[1],
            'full_name': os.environ.get('FRAMGIACI_REPO')
        },
        'build': {
            'number': os.environ.get('FRAMGIACI_BUILD_NUMBER'),
            'commit': os.environ.get('FRAMGIACI_COMMIT'),
            'branch': os.environ.get('FRAMGIACI_BRANCH'),
            'pull_request_number': os.environ.get('FRAMGIACI_PULL_REQUEST')
        },
        'job': {
            'number': os.environ.get('FRAMGIACI_JOB_NUMBER')
        },
        'token': hmac.new(b'b51333889a8aef7f6f97e164d7cba1b0e1c5d2c2', message.encode(), hashlib.sha256).hexdigest()
    }

def call_api(url, is_post=False, params={}, headers=[], files=[]):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.FOLLOWLOCATION, True)
    c.setopt(c.WRITEDATA, buffer)
    if is_post:
        postfields = []
        for k,v in params.items():
            postfields.append((k, json.dumps(v)))
        if files != []:
            for tag, file in files:
                postfields.append((tag, (c.FORM_FILE, file)))
        c.setopt(c.HTTPPOST, postfields)

    if headers != []:
        c.setopt(c.HTTPHEADER, headers)

    c.perform()
    c.close()

    body = buffer.getvalue()
    body = body.decode('iso-8859-1')
    try:
        return json.loads(body)
    except Exception:
        return {'errorCode': 'Server Error !'}

def listen_event(client):
    events = client.events()
    for event in events:
        my_event = json.loads(event.decode('utf-8'))
        _action = my_event['Action']
        _type = my_event['Type']
        _actor = my_event['Actor']
        
        if _type == 'image':
            _status = my_event['status']
            print("Type:" + _type + " Status:" + _status + " ID:" + _actor['ID'])
        # print(event)
