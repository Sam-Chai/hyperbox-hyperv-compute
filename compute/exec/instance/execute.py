import os

class Execute:
    def __init__(self):
        self.startswith = 'powershell.exe -command '
        self.check_admin_perm = True

    def execute_command(self, command, select_param=None, convert_to_json=False):
        other_param = ''
        if self.check_admin_perm:
            from compute.exec.util.check_admin_perm import check_admin_perm
            if check_admin_perm() == 'False':
                return 'Execute PowerShell command need Administrators permission'
        if select_param is None:
            select_param = []
        if len(select_param) > 0:
            other_param = ' | Select-Object ' + ','.join(select_param)
        if convert_to_json:
            other_param += ' | ConvertTo-Json'
        if command:
            command = self.startswith + '"' + command + other_param + '"'
            # print(command)
            with os.popen(command) as f:
                f_encode = f.buffer.read()
            try:
                return f_encode.decode().strip()
            except UnicodeDecodeError:
                return f_encode.decode('gbk').strip()
        else:
            return 'Command is empty'

