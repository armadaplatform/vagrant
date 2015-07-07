from __future__ import print_function
import os
import subprocess
import time
import signal
import sys
import re


def print_err(*objs):
    print(*objs, file=sys.stderr)


class RemoteException(Exception):
    pass


class SSHTunnel(object):
    def __init__(self, ssh_tunnel_args):
        self.ssh_tunnel_args = ssh_tunnel_args
        self.process = None
        self.pid = None

    @staticmethod
    def execute_tunnel_command(host, port, user, ssh_key, bind_port, remote_host, remote_port):
        tunnel_command = ('ssh -i {ssh_key} -p {port} {user}@{host} -N -o StrictHostKeyChecking=no '
                          '-L *:{bind_port}:{remote_host}:{remote_port}').format(**locals())
        return async_execute_local_command(tunnel_command)

    def start(self):
        self.process = SSHTunnel.execute_tunnel_command(**self.ssh_tunnel_args)
        self.pid = self.process.pid

    def terminate(self):
        os.killpg(self.pid, signal.SIGTERM)


def async_execute_local_command(command):
    p = subprocess.Popen(
        command,
        shell=True,
        preexec_fn=os.setsid
    )
    return p


def execute_local_command(command):
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    out, err = p.communicate()
    return p.returncode, out, err


def rsync(local_path, remote_path, remote_address, method, tunnel_check_retries=5, tunnel_check_timeout=3,
          sleep_between_retries=1):
    command_format_params = {'local_path': local_path, 'remote_path': remote_path}
    command_format_params.update(remote_address)
    if remote_address.get('sudo'):
        command_format_params['sudo'] = "--rsync-path='sudo rsync'"
    else:
        command_format_params['sudo'] = ''

    if method == 'push':
        source_dest = '{local_path} {user}@{host}:{remote_path}'.format(**command_format_params)
    elif method == 'pull':
        source_dest = '{user}@{host}:{remote_path} {local_path}'.format(**command_format_params)
    else:
        raise AttributeError('Unknown method {method}'.format(**locals()))
    command_format_params['source_dest'] = source_dest

    ssh_tunnel_args = remote_address.get('tunnel')
    if ssh_tunnel_args:
        ssh_tunnel = SSHTunnel(ssh_tunnel_args)
        ssh_tunnel.start()
        check_tunnel_params = dict(command_format_params)
        check_tunnel_params['tunnel_check_timeout'] = tunnel_check_timeout
        check_tunnel_command = ('ssh -o StrictHostKeyChecking=no -o ConnectTimeout={tunnel_check_timeout} '
                                '-p {port} -i {ssh_key} {user}@{host} true').format(**check_tunnel_params)
        tunnel_ok = False
        for i in range(tunnel_check_retries + 1):
            check_tunnel_result = execute_local_command(check_tunnel_command)
            if check_tunnel_result[0] == 0:
                tunnel_ok = True
                break
            time.sleep(sleep_between_retries)
        if not tunnel_ok:
            raise RemoteException('Could not set up a tunnel, all retries failed.')
    rsync_command = ('rsync -cvrz --delete --exclude=".git*" '
                     '--rsh="ssh -o StrictHostKeyChecking=no -p {port} -i {ssh_key}" '
                     '{sudo} {source_dest} ').format(**command_format_params)
    result = execute_local_command(rsync_command)
    if ssh_tunnel_args:
        try:
            ssh_tunnel.terminate()
        except Exception as e:
            print_err('Termination of the tunnel failed. {e}'.format(**locals()))
    return result


def execute_remote_command(command, remote_address, stream_output=False):
    import paramiko

    class SilentPolicy(paramiko.WarningPolicy):
        def missing_host_key(self, client, hostname, key):
            pass

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(SilentPolicy())
    ssh_key = paramiko.RSAKey.from_private_key_file(remote_address['ssh_key'])
    ssh.connect(remote_address['host'], username=remote_address['user'], pkey=ssh_key, port=int(remote_address['port']),
                timeout=10)
    if stream_output:
        channel = ssh.get_transport().open_session()
        channel.set_combine_stderr(True)
        channel.exec_command(command)

        ansi_escape = re.compile(r'\x1b[^m]*m')
        line = ""
        while not channel.exit_status_ready():
            if channel.recv_ready():
                channel_byte = channel.recv(1)
                line += channel_byte
                if channel_byte == '\n':
                    line = ansi_escape.sub('', line)
                    sys.stderr.write(line)
                    line = ""
        if line:
            line = ansi_escape.sub('', line) + '\n'
            sys.stderr.write(line)

        ssh_return_code = channel.recv_exit_status()
        ssh_out = None
        ssh_err = None
    else:
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        ssh_out = ssh_stdout.read()
        ssh_err = ssh_stderr.read()
        ssh_return_code = ssh_stdout.channel.recv_exit_status()
        ssh.close()
    return ssh_return_code, ssh_out, ssh_err
