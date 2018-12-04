# (c) 2018, Gaudenz Steinlin <gaudenz.steinlin@cloudscale.ch>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
    name: cloudscale
    plugin_type: inventory
    author: "Gaudenz Steinlin (@gaudenz) <gaudenz.steinlin@cloudscale.ch>"
    short_description: cloudscale.ch inventory source
    description:
        - Get inventory hosts from cloudscale.ch API
    options:
        plugin:
            description: |
                Token that ensures this is a source file for the 'cloudscale'
                plugin.
            required: True
            choices: ['cloudscale']
        inventory_hostname:
            description: |
                What to register as the inventory hostname.
                If set to 'uuid' the uuid of the server will be used and a
                group will be created for the server name.
                If set to 'name' the name of the server will be used unless
                there are more than one server with the same name in which
                case the 'uuid' logic will be used.
            type: string
            choices:
                - name
                - uuid
            default: "name"
        ansible_host:
            description: |
                Which IP address to register as the ansible_host. If the
                requested value does not exist or this is set to 'none', no
                ansible_host will be set.
            type: string
            choices:
                - public_v4
                - public_v6
                - private
                - none
            default: public_v4
        api_token:
          description: cloudscale.ch API token
          env:
            - name: CLOUDSCALE_API_TOKEN
        api_timeout:
          description: Timeout in seconds for calls to the cloudscale.ch API.
          default: 30
'''

EXAMPLES = r'''
# cloudscale_inventory.yml file in YAML format
# Example command line: ansible-inventory --list -i cloudscale_inventory.yml

plugin: cloudscale
'''

from collections import defaultdict
from json import loads
from os import environ

from ansible.errors import AnsibleError
from ansible.module_utils.cloudscale import API_URL
from ansible.module_utils.urls import open_url
from ansible.plugins.inventory import BaseInventoryPlugin

iface_type_map = {
    'public_v4': ('public', 4),
    'public_v6': ('public', 6),
    'private': ('private', 4),
}

class InventoryModule(BaseInventoryPlugin):

    NAME = 'cloudscale'

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)

        self._read_config_data(path)

        token = self.get_option('api_token')
        if not token:
            raise AnsibleError('Could not find an API token. Set the '
                               'CLOUDSCALE_API_TOKEN environment variable.')

        inventory_hostname = self.get_option('inventory_hostname')
        if inventory_hostname not in ('name', 'uuid'):
            raise AnsibleError('Invalid value for option inventory_hostname: %s'
                               % inventory_hostname)

        ansible_host = self.get_option('ansible_host')
        if ansible_host not in iface_type_map:
            raise AnsibleError('Invalid value for option ansible_host: %s'
                               % ansible_host)

        response = open_url(
            API_URL + '/servers',
            headers = {'Authorization': 'Bearer %s' % token}
        )
        response_text = response.read()
        firstpass = defaultdict(list)
        for server in loads(response_text):
            firstpass[server['name']].append(server)

        for name, servers in firstpass.items():
            if len(servers) == 1 and inventory_hostname == 'name':
                self.inventory.add_host(name)
                servers[0]['inventory_hostname'] = name
            else:
                if not name in self.inventory.groups:
                    self.inventory.add_group(name)
                for server in servers:
                    self.inventory.add_host(server['uuid'], name)
                    server['inventory_hostname'] = server['uuid']

            iface_type, iface_version = iface_type_map[ansible_host]
            for server in servers:

                addresses = [address['address']
                             for interface in server['interfaces']
                             for address in interface['addresses']
                             if interface['type'] == iface_type
                             and address['version'] == iface_version]

                if len(addresses) > 0:
                    self.inventory.set_variable(
                        server['inventory_hostname'],
                        'ansible_host',
                        addresses[0],
                    )
                self.inventory.set_variable(
                    server['inventory_hostname'],
                    'cloudscale',
                    {k: v for k,v in server.items()
                     if k != 'inventory_hostname'},
                )
