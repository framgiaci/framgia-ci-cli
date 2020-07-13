#!/usr/local/bin/python
# coding: utf-8

import sys
import fcntl
from framgiaci.version import __version__
from framgiaci.report_app import ReportApplication
from framgiaci.commands.run_finish import RunFinishCommand
from framgiaci.commands.run_report import RunReportCommand
from framgiaci.commands.init_template import InitTemplateCommand
from framgiaci.commands.run_all import RunAllCommand
from framgiaci.commands.check_config import CheckConfigCommand
from framgiaci.commands.show_config import ShowConfigCommand
from framgiaci.commands.run_notify import RunNotifyCommand
from framgiaci.commands.test_connect import TestConnectCommand
from framgiaci.commands.run_upload import RunUploadCommand
from framgiaci.commands.run_rspec import RunRspecCommand
from framgiaci.commands.run_test import RunTestCommand

YAML_CONFIGURE_FILE = 'framgia-ci.yml'
RESULT_TEMP_FILE = '.framgia-ci-result.temp.yml'

COMMANDS = [
    RunTestCommand, RunReportCommand, RunFinishCommand, InitTemplateCommand,
    CheckConfigCommand, ShowConfigCommand, RunAllCommand, RunNotifyCommand,
    TestConnectCommand, RunUploadCommand, RunRspecCommand
]

def main():
    fcntl.fcntl(1, fcntl.F_SETFL, 0)
    print('Framgia CI V3 Tool', __version__)
    app = ReportApplication()
    app.load_config(YAML_CONFIGURE_FILE, RESULT_TEMP_FILE)
    for command in COMMANDS:
        app.register_command(command)
    app.run()
    sys.exit(0)

if __name__ == '__main__':
    main()
