# coding: utf-8 -*-
# (C) 2021, Markus Bergholz
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    author: Markus Bergholz
    name: talk
    type: notification
    short_description: write playbook output to nextcloud talk
    description:
      - This callback writes playbook output to a nextcloud talk conversation
'''

import os
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler
from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'markuman.nextcloud.talk'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        params = {}
        self.nc = NextcloudHandler(params, self._display.warning)
        self.channel = os.environ.get('NEXTCLOUD_TALK_CALLBACK_CHANNEL')
        self.headers = {
            'Accept': 'application/json',
            'OCS-APIRequest': 'true'
        }

    def log(self, result, category):
        data = result._result
        taskname = result._task.name
        task_action = result._task.action
        changed = data.get('changed')

        message = f"TASK[{taskname}]: {task_action} - {category}\n\tchanged: {changed}"

        r, change = self.nc.talk(message, self.channel)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.log(result, 'FAILED')

    def v2_runner_on_ok(self, result):
        self.log(result, 'OK')

    def v2_runner_on_skipped(self, result):
        self.log(result, 'SKIPPED')

    def v2_runner_on_unreachable(self, result):
        self.log(result, 'UNREACHABLE')

    def v2_runner_on_async_failed(self, result):
        self.log(result, 'ASYNC_FAILED')

    def v2_playbook_on_start(self, playbook):
        self.playbook = playbook._file_name
        playbook = self.playbook
        message = f"________________________________________\nPlaybook: {playbook}"
        r, change = self.nc.talk(message, self.channel)

    def v2_playbook_on_import_for_host(self, result, imported_file):
        self.log(result, 'IMPORTED', imported_file)

    def v2_playbook_on_not_import_for_host(self, result, missing_file):
        self.log(result, 'NOTIMPORTED', missing_file)
