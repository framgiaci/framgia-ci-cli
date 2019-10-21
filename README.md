# Framgia CI CLI Tool

[![PyPI](https://img.shields.io/pypi/status/framgia-ci.svg)](https://pypi.python.org/pypi/framgia-ci/)
[![PyPI](https://img.shields.io/pypi/v/framgia-ci.svg)](https://pypi.python.org/pypi/framgia-ci/)
[![PyPI](https://img.shields.io/pypi/pyversions/framgia-ci.svg)]([![PyPI](https://img.shields.io/pypi/v/framgia-ci.svg)](https://pypi.python.org/pypi/framgia-ci/))

- A part of **Framgia CI** service
- A tool for managing project configuration, as well as running test commands with **Framgia CI** Service
- Written in Python
- Authors: **Tran Duc [@wataridori](https://github.com/wataridori) Thang** - **Nguyen Anh [@vigov5](https://github.com/vigov5) Tien**

## Install
### Linux
#### Pre-compiled executale file
- For running inside **Docker Container**, which does not contain Python in almost cases
```
// Using curl
# curl -o /usr/bin/framgia-ci https://raw.githubusercontent.com/framgiaci/framgia-ci-cli/master/dist/framgia-ci && chmod +x /usr/bin/framgia-ci

// Using wget
# wget -O /usr/bin/framgia-ci https://raw.githubusercontent.com/framgiaci/framgia-ci-cli/master/dist/framgia-ci && chmod +x /usr/bin/framgia-ci
```
#### Install by using `pip`
- Requirement: **python 3.5**
- Command:
```
// Install
# pip install -i https://test.pypi.org/simple/ framgia-ci

// Update
# pip install --upgrade -i https://test.pypi.org/simple/ framgia-ci
```

### Mac OS
#### Install by using `pip`
- Requirement: **python 3.5** (You may have to install `python3` by using `brew` first)
- Command:
```
// Install python3
$ brew install python3

// Install framgia-ci
# pip3 install -i https://test.pypi.org/simple/ framgia-ci

// Update
# pip3 install --upgrade -i https://test.pypi.org/simple/ framgia-ci
```

## Usage
- Command lists
```
build                       Build project on local machine
check-config                Validate config file
finish                      Running finish command tools
init                        Init new config file base-ed on template. Supported project type: php, ruby, android
report                      Running report command to send copying request to CI Report service
notify                      Running notify command to send notify request to CI Report service
upload                      Running upload command to send zipped bundle reports to CI Report service
run                         Running test, upload, finish command
run --logs                  Running test, upload, finish command with verbose
run --local                 Running test, finish command. For running at local machine
run-rspec                   Running custom RSPEC for changed file.
run-rspec --all             Running all spec files {--all : Run all spec files.}
run-rspec --spec-dir=spec/  Define where is spec files in a single directory {--spec-dir=spec/ : Define where is spec files in a single directory}
run-rspec --output-dir=     Define output directory {--output-dir=.framgia-ci-reports/ : Define output directory}
show-config                 Display current config
test                        Running test tools
test-connect                Test connection to specific host and port
```

For example
```
// Init .framgia-ci.yml configuration file for php project
framgia-ci init php

// Run test commands defined in .framgia-ci.yml
framgia-ci test

// Run all test, upload, finish commands. This should only be run inside framgia ci service
framgia-ci run

// Run test and show results at local machine
framgia-ci run --local

// Check mysql connection in localhost
framgia-ci test-connect 127.0.0.1 3306

// Build project on local machine
// This feature requires your computer must install **Docker**
framgia-ci build
```

## Framgia CI Configuration
- All additional configurations for Framgia CI Service **MUST** be stored in `.framgia-ci.yml` file.
- The configurations have to be written in `yaml` format.
- Example configuration file:
```
project_type: php
build:
  general_test:
    image: framgiaciteam/laravel-workspace:latest
    services:
      mysql:
        image: mysql:5.7
        environment:
          MYSQL_DATABASE: homestead
          MYSQL_USER: homestead
          MYSQL_PASSWORD: secret
          MYSQL_ROOT_PASSWORD: root
      mysql_test:
        image: mysql:5.7
        environment:
          MYSQL_DATABASE: homestead_test
          MYSQL_USER: homestead_test
          MYSQL_PASSWORD: secret
          MYSQL_ROOT_PASSWORD: root
    prepare:
      - php artisan config:clear
      - composer install
      - framgia-ci test-connect mysql_test 3306 60
      - php artisan migrate --database=mysql_test
test:
  eslint:
    ignore: false
    command: eslint --format=checkstyle
      --output-file=.framgia-ci-reports/eslint.xml
      resources/assets/js/ --ext .js
    auto_fix: eslint resources/assets/js/ --fix
  phpcpd:
    ignore: true
    command: phpcpd --log-pmd=.framgia-ci-reports/phpcpd.xml app
  phpmd:
    ignore: true
    command: phpmd app xml cleancode,codesize,controversial,design,naming,unusedcode --reportfile .framgia-ci-reports/phpmd.xml
  pdepend:
    ignore: true
    command: pdepend --summary-xml=.framgia-ci-reports/pdepend.xml
      --jdepend-chart=.framgia-ci-reports/pdepend.svg
      --overview-pyramid=.framgia-ci-reports/pyramid.svg
      app
  phpmetrics:
    ignore: true
    command: phpmetrics --report-html=.framgia-ci-reports/metrics.html
      --report-xml=.framgia-ci-reports/metrics.xml
      app
  phpcs:
    ignore: false
    command: echo '' | phpcs --standard=Framgia --report-checkstyle=.framgia-ci-reports/phpcs.xml --ignore=app/Supports/* app
    auto_fix: phpcbf --standard=Framgia app --fix
  phpunit:
    ignore: false
    command:
      - php -dzend_extension=xdebug.so vendor/bin/phpunit
        --coverage-clover=.framgia-ci-reports/coverage-clover.xml
        --coverage-html=.framgia-ci-reports/coverage
#deploy:
  #rocketeer:
    #image: fdplugins/ssh-php:php5
    #when:
      #branch: master
      #status: ['sucess', 'false']
    #commands:
      #- php rocketeer.phar deploy --on=staging --no-interaction
cache:
  #git:
    #folder: .git
  composer:
    folder: vendor
    file: composer.lock
  nodejs:
    folder: node_modules
    file: yarn.lock
```
- `project_type` key: Define the type of the project. Currently supports `php`, `ruby` and `android`. This key is **required**
- `build` key: `general_test` key: include `image` key, `services` key and `prepare` key. `image` key: define main environment base on Docker image, `services` key: define which services used by project, such as: mysql, redis,.. and `prepare` key: define commands which ran on main enviroment before running test.
- `test` key: Define test section with customizable commands. This section is **required**
- `phpcpd`, `phpmd`, `phpcs`, `phpunit` ...: Configuration for each test tools. All of them will be executed, even if the other test tools are success or not.
- `ignore` key: Define whether the build should be considered as `failed` or not when the test tool is failed. The default value is `false`. If you set it to `true`, the build will be considered as success even when the command returns `false` (with non-zero `exit code`)
- `command`: The section that defines command(s) that are expected to be run. If there are more than one commands in this section, `framgia-ci` will try to run them in the order from top to bottom. However, if one of them is failed, the entire section will be stopped, and the below commands will not be executed.
- All the reports file (if existed) **MUST** be exported to a folder named `.framgia-ci-reports`
- You can also use `from` keyword to extend from default template. For example:
```
from: php
test:
  phpcs:
    ignore: true # Extend the default configuration from php template, but override the ignore property for phpcs tool
```

Contribution
--------------
View contribution guidelines [here](./CONTRIBUTING.md)
