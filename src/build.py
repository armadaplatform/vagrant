import json
import os
import random

import remote


def _get_this_directory():
    return os.path.abspath(os.path.dirname(__file__))


def _get_build_server_config_path():
    return os.path.join(_get_this_directory(), '../config/build-server.json')


def _get_build_server_config():
    build_server_config_path = _get_build_server_config_path()
    with open(build_server_config_path) as f:
        return json.loads(f.read())


def _get_ssh_key_path(ssh_key):
    return os.path.join(os.path.dirname(_get_build_server_config_path()), ssh_key)


def main():
    config = _get_build_server_config()
    workspace = '/tmp/armada-vagrant-' + str(random.randrange(10**7))
    remote_address = {
        'host': config['host'],
        'port': config['port'],
        'user': config['user'],
        'ssh_key': _get_ssh_key_path(config['ssh_key']),
    }
    http_proxy = config.get('http_proxy')
    remote_scripts_path = os.path.join(_get_this_directory(), 'remote_scripts/.')
    os.system('chmod +x ' + os.path.join(remote_scripts_path, '*.sh'))
    code, out, err = remote.rsync(remote_scripts_path, workspace, remote_address, 'push')
    remote.print_err('PUSH:\ncode:\n{code}\nout:\n{out}\nerr:\n{err}'.format(**locals()))
    assert code == 0
    command = os.path.join(workspace, 'build-armada-box.sh')
    env_http_proxy = 'http_proxy=' + http_proxy if http_proxy else ''
    full_command = 'WORKSPACE={workspace} {env_http_proxy} {command}'.format(**locals())
    code, out, err = remote.execute_remote_command(full_command, remote_address, stream_output=True)
    assert code == 0

    code, out, err = remote.rsync(
        os.path.join(_get_this_directory(), 'static/.'),
        os.path.join(workspace, 'armada.box'),
        remote_address,
        'pull'
    )
    remote.print_err('PULL:\ncode:\n{code}\nout:\n{out}\nerr:\n{err}'.format(**locals()))
    assert code == 0
    code, out, err = remote.execute_remote_command('rm -rf {workspace}'.format(**locals()),
                                                   remote_address,
                                                   stream_output=True)
    assert code == 0


if __name__ == '__main__':
    main()
