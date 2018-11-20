import sys
import os
import errno
import docker
import time
import threading
import subprocess

from cleo import Command

from framgiaci.common import print_header, run_command, write_results, listen_event


class RunBuildCommand(Command):
    """
    Build project on local machine

    build
    """

    def __init__ (self):
        self.workspace = '/home/workspace'
        super(RunBuildCommand, self).__init__()

    def handle(self):
        self.app.check_configure_file_exists()
        print_header('Build project')
        client = docker.DockerClient(base_url='unix://var/run/docker.sock')

        thread = threading.Thread(target=listen_event, args=(client,))
        thread.daemon = True
        thread.start()
        
        network = client.networks.create("FramgiaCI-" + str(time.time()), driver="bridge")
        build_commands = self.app.ci_reports['build']

        containers = []
        for build, details in build_commands.items():
            self.start_service(client, network, details['services'], containers)

            main_container = self.start_container(client, network, details, main_container=True)

            try:
                main_container.restart()
            except Exception as e:
                print(e)

            print_header('Preparing..')

            framgia_ci_run_exist = False
            for command in details['prepare']:
                print("[+] Running: ", command)
                if 'framgia-ci run' == command:
                    command += ' --local'
                    framgia_ci_run_exist = True
                output = main_container.exec_run(command, workdir=self.workspace, tty=True, privileged=True, stream=True, socket=True)
                for line in output[1]:
                    print(line.decode('utf-8'), end="\n")

            if framgia_ci_run_exist == False:
                print("[+] Running: ", 'framgia-ci run --local')
                output = main_container.exec_run('framgia-ci run --local', workdir=self.workspace, tty=True, privileged=True, stream=True, socket=True)
                for line in output[1]:
                    print(line.decode('utf-8'), end="\n")

            containers.append(main_container.id)
        self.clean(client, network, containers)

    def start_service(self, client, network, services, containers):
        for service, details in services.items():
            container = self.start_container(client, network, details, service=service)
            containers.append(container.id)

        return containers

    def start_container(self, client, network, details, main_container=False, service=None):
        print("Pulling image " + details['image'])
        client.images.pull(details['image'])

        environment = []
        if 'environment' in details:
            environment = details['environment']

        if main_container:
            pwd = subprocess.check_output("pwd", shell=True).rstrip()
            container = client.containers.run(
                details['image'],
                environment=environment,
                detach=True,
                command=['/bin/bash'],
                volumes= 
                    {
                        pwd: {'bind': self.workspace, 'mode': 'rw'},
                        '/usr/bin/framgia-ci': {'bind': '/usr/bin/framgia-ci', 'mode': 'rw'},
                    },
                stdin_open=True,
                # tty=True,
                network=network.name,
            )

        else:
            container = client.containers.run(
                details['image'],
                detach=True,
                environment=environment,
                stdin_open=True,
                tty=True
            )

            network.connect(container, aliases=[service])

        return container

    def clean(self, client, network, containers):
        for container in containers:
            _container = client.containers.get(container)

            if _container.status == 'running':
                _container.kill(9)
                _container.remove()

        try:
            network.remove()
        except docker.errors.APIError:
            pass

