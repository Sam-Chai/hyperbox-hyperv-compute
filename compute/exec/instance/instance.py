from json import JSONDecodeError

from .execute import Execute
from compute.exec.util import check_location, translate_format
from compute.exec.constants import Constants


class Instance:
    def __init__(self):
        # print('Instance class initialized')
        self.ALLOW_SIZE_UNIT = Constants.SIZE_UNIT
        self.ALLOW_MEMORY_TYPE = Constants.VM_MEMORY_TYPE
        self.ALLOW_GENERATION = Constants.VM_GEN
        self.ALLOW_BOOT_DEVICE = Constants.VM_BOOT_DEVICE
        self.INSTANCE_STATES = Constants.VM_POWER_ACTION

        def _catch_abspath():
            import os
            return os.path.dirname(os.path.abspath(__file__))

        self._abspath = _catch_abspath()
        self._transform = translate_format

    def create_instance(self,
                        instance_name,
                        instance_gen,
                        instance_processor,
                        instance_memory,
                        instance_path):
        """
        :param instance_name: A name for vm
        :param instance_gen: Generation of vm (1 or 2)
        :param instance_processor: Number of processor
        :param instance_memory: Memory size (must be MB or GB)
        :param instance_path: Path of vm to storage
        :return: json context
        """

        """
        Check params part
        """
        if instance_name in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is existed in Hyper-V Manager database"}
        if instance_gen not in self.ALLOW_GENERATION:
            return {"result": "failed", "message": "Instance generation is not in ALLOW_GENERATION (default: 1 or 2)"}
        if check_location.check_dir(instance_path) is False:
            return {"result": "failed", "message": "Instance path is not existed or not writable"}
        # check instance_memory size unit
        if instance_memory[-2:].upper() not in self.ALLOW_SIZE_UNIT:
            return {"result": "failed",
                    "message": "Instance memory size unit is not in ALLOW_SIZE_UNIT (default: GB or MB)"}
        if instance_memory[-2:] == 'MB':
            # delete 'MB'
            instance_memory = instance_memory[:-2]
            # check instance_memory is number
            if instance_memory.isdigit():
                # check the number < 512
                if int(instance_memory) < 512:
                    return {"result": "failed", "message": "Instance memory is less than 512MB"}
                else:
                    instance_memory = str(instance_memory) + 'MB'
            else:
                return {"result": "failed", "message": "Instance memory is not valid"}
        elif instance_memory[-2:] == 'GB':
            # delete 'GB'
            instance_memory = instance_memory[:-2]
            # check instance_memory is number
            if instance_memory.isdigit():
                # check the number < 1
                if int(instance_memory) < 1:
                    return {"result": "failed", "message": "Instance memory is less than 1GB"}
                else:
                    instance_memory = str(instance_memory) + 'GB'
            else:
                return {"result": "failed", "message": "Instance memory is not valid"}

        """
        Execute command part
        """
        # create vm
        command_new_vm = "New-VM -Name '%s' -Generation '%s' -MemoryStartupBytes '%s' -Path '%s' -NoVHD" % (
            instance_name, instance_gen, instance_memory, instance_path)
        result_new_vm = Execute().execute_command(command_new_vm, convert_to_json=True)
        if 'ConfigurationLocation' in result_new_vm:
            result = self._transform.trans_json_to_dict(result_new_vm)
            pass
        else:
            return {"result": "failed", "message": result_new_vm}
        # change vm processor
        command_set_processor = "Set-VMProcessor -VMName '%s' -Count '%s'" % (instance_name, instance_processor)
        result_set_processor = Execute().execute_command(command_set_processor, convert_to_json=True)
        if result_set_processor == '':
            return {
                "result": "success",
                "message": "Instance '%s' is created" % instance_name,
                "instance_name": result['Name'],
                "instance_gen": str(result['Generation']),
                "instance_processor": str(result['ProcessorCount']),
                "instance_memory": str(int(result['MemoryStartup']) / 1024 / 1024).replace('.0', '') + 'MB',
                "instance_path": result['ConfigurationLocation']
            }
        else:
            return {"result": "failed", "message": result_set_processor}

    def delete_instance(self, instance_name, force=False):
        """
        :param instance_name: Name of instance
        :param force: Force delete instance (True or False)
        :return: json context
        """

        """
        Check params part
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}

        """
        Execute command part
        """
        check_vm_state = Execute().execute_command(
            "Get-VM -Name '%s' | Select-Object State | ConvertTo-Csv" % instance_name)
        vm_folder = Execute().execute_command(
            "Get-VM -Name '%s' | Select-Object ConfigurationLocation | ConvertTo-Json" % instance_name)
        vm_folder = self._transform.trans_json_to_dict(vm_folder)
        # vm_folder = json.loads(vm_folder)
        if 'Off' not in check_vm_state:
            if force:
                command_stop_vm = "Stop-VM -Name '%s' -TurnOff -Force" % instance_name
                command_remove_vm = "Remove-VM -Name '%s' -Force" % instance_name
                result_stop_vm = Execute().execute_command(command_stop_vm, convert_to_json=True)
                result_remove_vm = Execute().execute_command(command_remove_vm, convert_to_json=True)
                command_delete_vm_folder = "Remove-Item -Path '%s' -Recurse -Force" % vm_folder['ConfigurationLocation']
                result_delete_vm_folder = Execute().execute_command(command_delete_vm_folder, convert_to_json=True)
                if result_stop_vm == '' and result_remove_vm == '' and result_delete_vm_folder == '':
                    if check_location.check_dir(vm_folder['ConfigurationLocation']) is False:
                        return {"result": "success", "message": "Instance '%s' is deleted by forced" % instance_name}
                else:
                    return {"result": "failed",
                            "message": result_stop_vm + '\n\n' + result_remove_vm + '\n\n' + result_delete_vm_folder}
            else:
                return {"result": "failed", "message": "'Instance '%s' is not stopped'" % instance_name}
        else:
            command_remove_vm = "Remove-VM -Name '%s' -Force" % instance_name
            result_remove_vm = Execute().execute_command(command_remove_vm, convert_to_json=True)
            command_delete_vm_folder = "Remove-Item -Path '%s' -Recurse -Force" % vm_folder['ConfigurationLocation']
            result_delete_vm_folder = Execute().execute_command(command_delete_vm_folder, convert_to_json=True)
            if result_remove_vm == '' and result_delete_vm_folder == '':
                if check_location.check_dir(vm_folder['ConfigurationLocation']) is False:
                    return {"result": "success", "message": "Instance '%s' is deleted normally" % instance_name}
            else:
                return {"result": "failed", "message": result_remove_vm + '\n\n' + result_delete_vm_folder}

    def import_instance(self, instance_name, instance_path, template_name, template_path):
        """
        :param instance_name: instance name that be imported
        :param instance_path: imported instance path
        :param template_name: a template that we want to import
        :param template_path: template path
        :return: json context
        """

        """
        Check params part
        """

        if instance_name in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is existed in Hyper-V Manager database"}
        if check_location.check_dir(instance_path) is False:
            return {"result": "failed", "message": "Instance path is not existed or not writable"}
        if check_location.check_dir(template_path) is False:
            return {"result": "failed", "message": "Template path is not existed or not writable"}

        """
        Execute command part
        """
        template_vmcx_path = template_path + '\\' + template_name + '\\Virtual Machines\\'
        template_vmcx_file = template_vmcx_path + check_location.search_file(template_vmcx_path, '.vmcx')
        instance_vmcx_path = instance_path + '\\' + instance_name
        instance_vhdx_path = instance_path + '\\' + instance_name + '\\Virtual Hard Disks\\'
        command = "Import-VM -Path '%s' -VhdDestinationPath '%s' -VirtualMachinePath '%s' -Copy -GenerateNewId | Rename-VM -NewName '%s' -PassThru" % (
            template_vmcx_file, instance_vhdx_path, instance_vmcx_path, instance_name)
        result = Execute().execute_command(command, convert_to_json=True)
        if 'ConfigurationLocation' in result:
            result = self._transform.trans_json_to_dict(result)
            # result = json.loads(result)
            return {
                "result": "success",
                "message": "Instance '%s' is imported" % instance_name,
                "instance_name": result['Name'],
                "instance_gen": str(result['Generation']),
                "instance_processor": str(result['ProcessorCount']),
                "instance_memory": str(int(result['MemoryStartup']) / 1024 / 1024).replace('.0', '') + 'MB',
                "instance_path": result['ConfigurationLocation']
            }

        else:
            return {"result": "failed", "message": result}

    def export_instance(self, instance_name, template_path):
        """
        :param instance_name: Name of instance
        :param template_path: Path of template
        :return: json context
        """

        """
        Check params part
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}
        if check_location.check_dir(template_path) is False:
            return {"result": "failed", "message": "Template path is not existed or not writable"}

        """
        Execute command part
        """
        command = "Export-VM -Name '%s' -Path '%s'" % (instance_name, template_path)
        result = Execute().execute_command(command, convert_to_json=True)
        if result == '':
            return {"result": "success",
                    "message": "Instance '%s' is exported to '%s'" % (instance_name, template_path)}
        else:
            return {"result": "failed", "message": result}

    def set_instance_power(self, instance_name, action):
        """
        :param instance_name: A string of instance name
        :param action: A string of action (start, stop, restart), more in constants.py
        :return: json context
        """

        """
        Check params part
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}
        if action not in self.INSTANCE_STATES:
            return {"result": "failed", "message": "Action '%s' is not supported" % action}

        """
        Execute command part
        """
        instance_status = Execute().execute_command(
            "Get-VM -Name '%s' | Select-Object State | ConvertTo-Csv" % instance_name)

        if action == 'start':
            if 'Running' in instance_status:
                return {"result": 'warning', "message": "Instance '%s' is already running" % instance_name}
            elif 'Paused' in instance_status:
                command = "Resume-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is started (from resumed)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Saved' in instance_status:
                command = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is started (from saved)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Off' in instance_status:
                command = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is started" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            else:
                command = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success",
                            "message": "Instance '%s' is started (from '%s')" % (instance_name, instance_status)}
                else:
                    return {"result": "failed", "message": result}

        elif action == 'stop':
            if 'Running' in instance_status:
                command = "Stop-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is stopped" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Paused' in instance_status:
                command = "Stop-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is stopped (from paused)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Saved' in instance_status:
                command = "Stop-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "'Instance '%s' is stopped (from saved)'" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Off' in instance_status:
                return {"result": 'warning', "message": "Instance %s is already stopped" % instance_name}
            else:
                command = "Stop-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success",
                            "message": "Instance '%s' is stopped (from '%s')" % (instance_name, instance_status)}
                else:
                    return {"result": "failed", "message": result}

        elif action == 'force-stop':
            if 'Running' in instance_status:
                command = "Stop-VM -VMName '%s' -TurnOff -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is stopped by force" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Paused' in instance_status:
                command = "Stop-VM -VMName '%s' -TurnOff -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success",
                            "message": "Instance '%s' is stopped by force (from paused)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Saved' in instance_status:
                command = "Stop-VM -VMName '%s' -TurnOff -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success",
                            "message": "Instance '%s' is stopped by force (from saved)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Off' in instance_status:
                return {"result": 'warning', "message": "'Instance '%s' is already stopped'" % instance_name}
            else:
                command = "Stop-VM -VMName '%s' -TurnOff -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is stopped by force (from '%s')" % (
                        instance_name, instance_status)}
                else:
                    return {"result": "failed", "message": result}

        elif action == 'restart':
            if 'Running' in instance_status:
                command_stop_vm = "Stop-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command_stop_vm, convert_to_json=True)
                if result == '':
                    pass
                else:
                    return {"result": "failed", "message": result}
                command_start_vm = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command_start_vm, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Paused' in instance_status:
                command_resume_vm = "Resume-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command_resume_vm, convert_to_json=True)
                if result == '':
                    pass
                else:
                    return {"result": "failed", "message": result}
                command_stop_vm = "Stop-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command_stop_vm, convert_to_json=True)
                if result == '':
                    pass
                else:
                    return {"result": "failed", "message": result}
                command_start_vm = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command_start_vm, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Saved' in instance_status:
                command_start_vm = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command_start_vm, convert_to_json=True)
                if result == '':
                    pass
                else:
                    return {"result": "failed", "message": result}
                command_stop_vm = "Stop-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command_stop_vm, convert_to_json=True)
                if result == '':
                    pass
                else:
                    return {"result": "failed", "message": result}
                command_start_vm = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command_start_vm, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Off' in instance_status:
                command = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is started (not restarted)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            else:
                command = "Restart-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted by force (from '%s')" % (
                        instance_name, instance_status)}
                else:
                    return {"result": "failed", "message": result}

        elif action == 'force-restart':
            if 'Running' in instance_status:
                command = "Restart-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted by force" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Paused' in instance_status:
                command_stop_vm = "Stop-VM -VMName '%s' -TurnOff -Force" % instance_name
                result = Execute().execute_command(command_stop_vm, convert_to_json=True)
                if result == '':
                    pass
                else:
                    return {"result": "failed", "message": result}
                command_start_vm = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command_start_vm, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted by force" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Saved' in instance_status:
                command_stop_vm = "Stop-VM -VMName '%s' -TurnOff -Force" % instance_name
                result = Execute().execute_command(command_stop_vm, convert_to_json=True)
                if result == '':
                    pass
                else:
                    return {"result": "failed", "message": result}
                command_start_vm = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command_start_vm, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted by force" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Off' in instance_status:
                command = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is started (not restarted)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            else:
                command = "Restart-VM -VMName '%s' -Force" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is restarted by force (from '%s')" % (
                        instance_name, instance_status)}
                else:
                    return {"result": "failed", "message": result}

        elif action == 'pause':
            if 'Running' in instance_status:
                command = "Suspend-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is paused (suspended)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Paused' in instance_status:
                return {"result": "success", "message": "Instance '%s' is already paused (suspended)" % instance_name}
            else:
                return {"result": "failed", "message": "Instance '%s' is not allowed to pause (from '%s')" % (
                    instance_name, instance_status)}

        elif action == 'resume':
            if 'Paused' in instance_status:
                command = "Resume-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is resumed (from Paused)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            elif 'Saved' in instance_status:
                command = "Start-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is resumed (from Saved)" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            else:
                return {"result": "failed", "message": "Instance '%s' is not allowed to resume (from '%s')" % (
                    instance_name, instance_status)}

        elif action == 'save':
            if 'Running' in instance_status:
                command = "Save-VM -VMName '%s'" % instance_name
                result = Execute().execute_command(command, convert_to_json=True)
                if result == '':
                    return {"result": "success", "message": "Instance '%s' is saved" % instance_name}
                else:
                    return {"result": "failed", "message": result}
            else:
                return {"result": "failed", "message": "Instance '%s' is not allowed to save (from '%s')" % (
                    instance_name, instance_status)}

        else:
            return {"result": "failed", "message": "Action '%s' is not supported" % action}

    def create_instance_snap(self, instance_name, snap_name):
        """
        :param instance_name: A name for vm
        :param snap_name: instance snapshot name
        :return: json context
        """

        """
        Check params
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}
        if snap_name in str(Execute().execute_command(
                "Get-VMSnapshot -VMName '%s' | Select-Object Name | ConvertTo-Csv" % instance_name)):
            return {"result": "failed", "message": "Snapshot name is already existed in Hyper-V Manager database"}

        """
        Exec command
        """
        command = "Checkpoint-VM -VMName '%s' -SnapshotName '%s'" % (instance_name, snap_name)
        result = Execute().execute_command(command, convert_to_json=True)
        if result == '':
            return {"result": "success", "message": "Snapshot '%s' is created" % snap_name}
        else:
            return {"result": "failed", "message": result}

    def delete_instance_snap(self, instance_name, snap_name):
        """
        :param instance_name: A name for vm
        :param snap_name: instance snapshot name
        :return: json context
        """

        """
        Check params
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}
        if snap_name not in str(Execute().execute_command(
                "Get-VMSnapshot -VMName '%s' | Select-Object Name | ConvertTo-Csv" % instance_name)):
            return {"result": "failed", "message": "Snapshot name is not existed in Hyper-V Manager database"}

        """
        Exec command
        """
        command = "Remove-VMSnapshot -VMName '%s' -Name '%s'" % (instance_name, snap_name)
        result = Execute().execute_command(command, convert_to_json=True)
        if result == '':
            return {"result": "success", "message": "Snapshot '%s' is deleted" % snap_name}
        else:
            return {"result": "failed", "message": result}

    def restore_instance_snap(self, instance_name, snap_name):
        """
        :param instance_name: A name for vm
        :param snap_name: instance snapshot name
        :return: json context
        """

        """
        Check params
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}
        if snap_name not in str(Execute().execute_command(
                "Get-VMSnapshot -VMName '%s' | Select-Object Name | ConvertTo-Csv" % instance_name)):
            return {"result": "failed", "message": "Snapshot name is not existed in Hyper-V Manager database"}

        """
        Exec command
        """
        command = "Restore-VMSnapshot -VMName '%s' -Name '%s' -Confirm:$false" % (instance_name, snap_name)
        result = Execute().execute_command(command, convert_to_json=True)
        if result == '':
            return {"result": "success", "message": "Snapshot '%s' is restored" % snap_name}
        else:
            return {"result": "failed", "message": result}

    def set_instance_processor(self, instance_name, processor_num, maximum=None, reverse=None, weight=None, extra_params=None):
        """
        :param instance_name: A name for vm
        :param processor_num: Number of processors
        :param maximum: Maximum usage of processors
        :param reverse: Reverse keep of processors
        :param weight: Relative weight of the processor
        :param extra_params: another params for powershell command
        :return: json context
        """

        """
        Check params
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}
        if extra_params is None:
            extra_params = []
        """
        Exec command
        """
        command = "Set-VMProcessor -VMName '%s' -Count %s" % (instance_name, processor_num)
        if maximum is not None:
            command += " -Maximum %s" % maximum
        else:
            command += " -Maximum 100"
        if reverse is not None:
            command += " -Reserve %s" % reverse
        else:
            command += " -Reserve 0"
        if weight is not None:
            command += " -RelativeWeight %s" % weight
        else:
            command += " -RelativeWeight 100"
        if len(extra_params) > 0:
            for param in extra_params:
                command += " %s" % param

        result = Execute().execute_command(command, convert_to_json=True)
        if result == '':
            return {"result": "success", "message": "Instance '%s' processor is set" % instance_name}
        else:
            return {"result": "failed", "message": result}

    def set_instance_memory(self, instance_name, startup_bytes, dynamic=False, maximum=None, minimum=None, priority=80, buffer=20):
        """
        :param instance_name: A name for vm
        :param startup_bytes: Startup memory
        :param dynamic: Dynamic memory
        :param maximum: Maximum memory
        :param minimum: Minimum memory
        :param priority: Memory priority
        :param buffer: Memory buffer
        :return: json context
        """

        """
        Check params
        """
        import re
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}
        if not re.search(r'[0-9]+[M|G]B$', startup_bytes):
            return {"result": "failed", "message": "Startup memory must be a number with MB or GB"}
        if maximum is not None and not re.search(r'[0-9]+[M|G]B$', maximum):
            return {"result": "failed", "message": "Maximum memory must be a number with MB or GB"}
        if minimum is not None and not re.search(r'[0-9]+[M|G]B$', minimum):
            return {"result": "failed", "message": "Minimum memory must be a number with MB or GB"}

        """
        Exec command
        """
        command = "Set-VMMemory -VMName '%s' -StartupBytes %s" % (instance_name, startup_bytes)
        if dynamic:
            command += " -DynamicMemoryEnabled $true"
            if maximum is not None:
                command += " -MaximumBytes %s" % maximum
            else:
                command += " -MaximumBytes %s" % startup_bytes
            if minimum is not None:
                command += " -MinimumBytes %s" % minimum
            else:
                command += " -MinimumBytes 512MB"
            if priority is not None:
                command += " -Priority %s" % priority
            else:
                command += " -Priority 80"
            if buffer is not None:
                command += " -Buffer %s" % buffer
            else:
                command += " -Buffer 20"
        else:
            command += " -DynamicMemoryEnabled $false"

        result = Execute().execute_command(command, convert_to_json=True)
        if result == '':
            return {"result": "success", "message": "Instance '%s' memory is set" % instance_name}
        else:
            return {"result": "failed", "message": result}

    """
    INFO - Get instance info
    """

    def instance_summary(self, instance_name):
        """
        :param instance_name: A name for vm
        :return: json context
        """

        """
        Check params
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}

        """
        Execute command part
        """
        ps_script = "%s\\ps1\\instance_summary.ps1" % self._abspath
        command = ps_script + ' ' + instance_name
        result = Execute().execute_command(command, convert_to_json=True)
        try:
            result = self._transform.trans_json_to_dict(result)
            # result = json.loads(result)
        except JSONDecodeError:
            result = {"result": "failed", "message": result}
        return result

    def instance_list(self):
        """
        :return: json context
        """

        """
        Execute command part
        """
        command = "Get-VM -VMName *"
        # print json output, maybe kind of slowly
        result = Execute().execute_command(command, convert_to_json=True)
        try:
            result = self._transform.trans_json_to_dict(result)
            # result = json.loads(result)
        except JSONDecodeError:
            result = {"result": "failed", "message": result}
        return result

        # A method to search items from result
        # # 从result中索引所有虚拟机的Name
        # instance_list = []
        # for instance in result:
        #     instance_list.append(instance['Name'])
        #
        # return instance_list

    def instance_snap_list(self, instance_name):
        """
        :param instance_name: A name for vm
        :return: json context
        """

        """
        Check params
        """
        if instance_name not in str(Execute().execute_command("Get-VM | Select-Object Name | ConvertTo-Csv")):
            return {"result": "failed", "message": "Instance name is not existed in Hyper-V Manager database"}

        """
        Execute command part
        """
        command = "Get-VMSnapshot -VMName '%s'" % instance_name
        # similar as instance_list, but only have one instance info
        # kind of slowly if instance have many snapshots
        result = Execute().execute_command(command, convert_to_json=True)
        try:
            result = self._transform.trans_json_to_dict(result)
            # result = json.loads(result)
        except JSONDecodeError:
            result = {"result": "failed", "message": result}
        return result

        # A method that search items from result
        # instance_snap_list = []
        # for instance in result:
        #     instance_snap_list.append(instance['ComPort2']['VMSnapshotName'])
