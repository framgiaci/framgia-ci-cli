import sys
import os
import errno

from cleo import Command

from framgiaci.common import print_header, run_command, run_command_silent, write_results


class RunTestCommand(Command):
    """
    Running test tools

    test
        {--logs : show more logs output}
    " && ".join((options['command'] , options['auto_fix']))
    """

    REQUIRE_TOOLS = ['phpunit', 'rspec', 'jest']

    def handle(self):
        self.app.check_configure_file_exists()
        print_header('Running Test')
        
        if self.app.ci_reports['test']:
            if not os.path.exists('.framgia-ci-reports'):
                try:
                    oldmask = os.umask(000)
                    os.makedirs('.framgia-ci-reports', 777)
                    os.umask(oldmask)
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            test_commands = self.app.ci_reports['test']
            results = {}
            for tool, options in test_commands.items():
                if options.get('enable', True):
                    to_run_cmds = []

                    if isinstance(options['command'], str):
                        to_run_cmds.append(options['command'])
                        try:
                            to_run_cmds.append(options['auto_fix'])
                        except KeyError:
                            pass
                    elif isinstance(options['command'], list):
                        to_run_cmds = options['command']
                        try:
                            to_run_cmds.append(options['auto_fix'])
                        except KeyError:
                            pass

                    general_result = 0
                    is_require = False

                    for command in to_run_cmds:

                        #Check current command is require tool.
                        for require_tool in self.REQUIRE_TOOLS:
                            is_require = require_tool in command
                            if is_require:
                                break

                        if self.option('logs'):
                            general_result = run_command(command)
                        else:
                            general_result = run_command_silent(command)

                    results[tool] = {
                        'exit_code': general_result.returncode,
                        'comment': options.get('comment', True),
                        'ignore': False if is_require else (options.get('ignore', False) == True) # If command is require tool, cant Ignore.
                    }

            write_results(results, self.app.temp_file_name)
            sys.exit(0)
