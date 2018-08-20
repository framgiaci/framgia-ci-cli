import sys
import os
import errno

from cleo import Command

from framgiaci.common import print_header, run_command, write_results


class RunTestCommand(Command):
    """
    Running test tools

    test
    " && ".join((options['command'] , options['auto_fix']))
    """

    def handle(self):
        self.app.check_configure_file_exists()
        print_header('Running Test')
        if self.app.ci_reports['test']:
            if not os.path.exists('.framgia-ci-reports'):
                try:
                    os.makedirs('.framgia-ci-reports', 777)
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

                    for command in to_run_cmds:
                        general_result = run_command(command)

                    results[tool] = {
                        'exit_code': general_result,
                        'comment': options.get('comment', True),
                        'ignore': options.get('ignore', False) == True
                    }
            write_results(results, self.app.temp_file_name)
            sys.exit(0)
