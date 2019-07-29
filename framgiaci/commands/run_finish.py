import sys

from cleo import Command

from framgiaci.common import print_header, read_results


class RunFinishCommand(Command):
    """
    Running finish command tools

    finish
        {--logs : show more logs output}
    """

    def handle(self):
        is_good_build = True
        result_text = ''
        for tool, result in read_results(self.app.temp_file_name).items():
            if result['exit_code'] != 0:
                if result['ignore'] == True:
                    if 'execute_time' in result:
                        format_str = "[!] %s: failed but ignored - [t] execute time: "+ result["execute_time"] + "\n"
                    else:
                        format_str = "[!] %s: failed but ignored \n"
                    
                else:
                    if 'execute_time' in result:
                        format_str = "[x] %s: failed - [t] execute time: " + result["execute_time"] + "\n"
                    else:
                        format_str = "[!] %s: failed \n"
                    
                    is_good_build = False
            else:
                if 'execute_time' in result:
                    format_str = "[o] %s: success - [t] execute time: " + result["execute_time"] + "\n"
                else:
                    format_str = "[!] %s: success \n"
                
            result_text += format_str % tool

        if is_good_build:
            print_header('[o] Build Success!')
            print(result_text)
            sys.exit(0)
        else:
            print_header('[x] Build Fail!')
            print(result_text)
            sys.exit(1)
