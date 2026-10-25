# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


class ModuleDocFragment:

    CONNECTIVITY = r'''
options:
  api_token:
    description:
      - Nextcloud App Password.
      - Can also be set with the E(NEXTCLOUD_TOKEN) environment variable.
    required: false
    type: str
    aliases: ['access_token']
  user:
    description:
      - Nextcloud user who (will) owns the file.
      - Can also be set with the E(NEXTCLOUD_USER) environment variable.
    required: false
    type: str
  host:
    description:
      - Nextcloud host, for example V(cloud.example.com) or V(localhost:8443).
      - A full base url like V(https://example.com/nextcloud) is also accepted.
        In this case the scheme of the url wins over O(ssl_mode=http).
      - Can also be set with the E(NEXTCLOUD_HOST) environment variable.
    required: false
    type: str
  ssl_mode:
    description:
      - V(https) uses https with certificate validation.
      - V(http) uses plain http, for example for integration tests.
      - V(skip) uses https but skips the certificate validation.
      - Can also be set with the E(NEXTCLOUD_SSL_MODE) environment variable.
    required: false
    type: str
    default: https
    choices: ['https', 'http', 'skip']
    version_added: 4.0.0
requirements:
  - requests
'''

    PLUGIN_CONNECTIVITY = r'''
options:
  host:
    description:
      - Nextcloud host, for example V(cloud.example.com) or V(localhost:8443).
      - A full base url like V(https://example.com/nextcloud) is also accepted.
    type: str
    env:
      - name: NEXTCLOUD_HOST
  user:
    description: Nextcloud user.
    type: str
    env:
      - name: NEXTCLOUD_USER
  api_token:
    description: Nextcloud App Password of O(user).
    type: str
    aliases: ['access_token']
    env:
      - name: NEXTCLOUD_TOKEN
  ssl_mode:
    description:
      - V(https) uses https with certificate validation.
      - V(http) uses plain http.
      - V(skip) uses https but skips the certificate validation.
    type: str
    default: https
    choices: ['https', 'http', 'skip']
    env:
      - name: NEXTCLOUD_SSL_MODE
requirements:
  - requests
'''
