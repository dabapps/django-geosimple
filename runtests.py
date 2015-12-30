#!/usr/bin/env python
import sys
import subprocess
import logging


logger = logging.getLogger(__name__)
FLAKE8_ARGS = ['geosimple/', '--ignore=E501', '--exclude=__init__.py']


def exit_on_failure(command, message=None):
    if command:
        sys.exit(command)


def flake8_main(args):
    print('Running: flake8', args)
    command = subprocess.call(['flake8'] + args)
    logger.info('Success. flake8 passed.') if command else None
    return command


def django_main():
    print('Running: django tests')
    command = subprocess.call(['python', 'manage.py', 'test'])
    return command


exit_on_failure(flake8_main(FLAKE8_ARGS))
exit_on_failure(django_main())
