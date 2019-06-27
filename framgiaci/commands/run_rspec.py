import sys
import os

from cleo import Command
from framgiaci.common import print_header, build_params, call_api, exec_command, run_command


class RunRspecCommand(Command):
    """
    Running custom RSPEC for changed file.

    run-rspec
        {--all : Run all spec files.}
        {--spec-dir=spec/ : Define where is spec files in a single directory}
        {--output-dir=.framgia-ci-reports/ : Define output directory}
    """

    def handle(self):
        rspec = 'rspec'
        if exec_command('type rspec').returncode == 0:
            rspec = 'rspec'
        elif exec_command('type bundle exec rspec').returncode == 0:
            rspec = 'bundle exec rspec'
        else:
            print('Program rspec not found!')
            sys.exit(1)

        print_header('Run RSPEC')

        # Get spec directory from option, resolve extra slash.
        spec_dir = '/'.join(self.option('spec-dir').strip('/').split('/'))
        output_dir = '/'.join(self.option('output-dir').strip('/').split('/'))

        exit_code = 0
        if self.option('all'):
            general_result = run_command(rspec + " --format html --out " + output_dir + "/rspec.html " + spec_dir)
            exit_code = general_result.returncode
        else:
            exec_command("git --no-pager diff HEAD~1 --name-only --output=.framgia-ci-run-rspec.yml")

            diff_files = open('.framgia-ci-run-rspec.yml', 'r')
            no_change = 1

            for file in diff_files:
                split_file_name = file.split('/');
                split_file_name[0] = 'spec'

                target_file = '/'.join(split_file_name).replace('.rb', '_spec.rb')

                if os.path.exists(target_file):
                    no_change = 0
                    print('Run rspec: ' + '/'.join(split_file_name).replace('.rb', '_spec.rb') + '\n')
                    
                    command_result = exec_command(rspec + ' --format html --out ' + output_dir + '/framgia-ci/rspec.html ' + target_file)
                    if command_result.returncode != 0:
                        exit_code = 1

            if no_change:
                print('Commit doesn\'t have any changed file \n')

        sys.exit(exit_code)
