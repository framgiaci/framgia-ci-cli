import sys
import os

from cleo import Command
from framgiaci.common import print_header, build_params, call_api, exec_command


class RunRspecCommand(Command):
    """
    Running custom RSPEC for changed file.

    run-rspec
    """

    def handle(self):
        print_header('Run RSPEC')

        exec_command("git --no-pager diff HEAD~1 --name-only --output=.framgia-ci-run-rspec.yml")

        diff_files = open('.framgia-ci-run-rspec.yml', 'r')

        exit_code = 0
        no_change = 1

        for file in diff_files:
            split_file_name = file.split('/');
            split_file_name[0] = 'spec'

            target_file = '/'.join(split_file_name).replace('.rb', '_spec.rb')

            if os.path.exists(target_file):
                no_change = 0
                print('Run rspec: ' + '/'.join(split_file_name).replace('.rb', '_spec.rb') + '\n')
                
                command_result = exec_command('bundle exec rspec ' + target_file)
                if command_result.returncode != 0:
                    exit_code = 1

        if no_change:
            print('Commit doesn\'t have any changed file \n')

        sys.exit(exit_code)
