# -*- coding: utf-8 -*-
# (C) 2021, Markus Bergholz
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = '''
author:
  - "Markus Bergholz (@markuman)"
name: talk
type: notification
short_description: write playbook output to nextcloud talk
description:
  - This callback writes playbook output to a nextcloud talk conversation.
requirements:
  - enable in configuration, for example with E(ANSIBLE_CALLBACKS_ENABLED=markuman.nextcloud.talk)
options:
  channel:
    description: Token of the Nextcloud Talk conversation.
    type: str
    required: true
    env:
      - name: NEXTCLOUD_TALK_CALLBACK_CHANNEL
    ini:
      - section: callback_nextcloud_talk
        key: channel
extends_documentation_fragment:
  - markuman.nextcloud.nextcloud.plugin_connectivity
'''

from ansible.plugins.callback import CallbackBase
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudError
from ansible_collections.markuman.nextcloud.plugins.module_utils.nextcloud import NextcloudHandler


def _fail(msg):
    raise NextcloudError(msg)


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'markuman.nextcloud.talk'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self.nc = None
        self.channel = None
        self.disabled = False

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)
        self.channel = self.get_option('channel')
        params = dict((key, self.get_option(key)) for key in ('host', 'user', 'api_token', 'ssl_mode'))
        try:
            self.nc = NextcloudHandler(params, _fail)
        except NextcloudError as e:
            self.disabled = True
            self._display.warning('markuman.nextcloud.talk callback disabled: {0}'.format(e))

    def send(self, message):
        if self.disabled or self.nc is None:
            return
        try:
            self.nc.talk(message, self.channel)
        except NextcloudError as e:
            self._display.warning('markuman.nextcloud.talk callback: {0}'.format(e))

    def log(self, result, category):
        data = result._result
        taskname = result._task.get_name()
        task_action = result._task.action
        host = result._host.get_name()
        changed = data.get('changed')

        self.send(f"TASK[{taskname}] {host}: {task_action} - {category}\n\tchanged: {changed}")

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
        self.send(f"________________________________________\nPlaybook: {playbook._file_name}")
