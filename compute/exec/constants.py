"""
Hyper-V / Windows related constants.
"""


# Path: compute\exec\constants.py
class Constants:
    # Hyper-V VM states
    HYPERV_VM_STATE_OTHER = 1
    HYPERV_VM_STATE_ENABLED = 2
    HYPERV_VM_STATE_DISABLED = 3
    HYPERV_VM_STATE_SHUTTING_DOWN = 4
    HYPERV_VM_STATE_REBOOT = 10
    HYPERV_VM_STATE_PAUSED = 32768
    HYPERV_VM_STATE_SUSPENDED = 32769

    HYPERV_VM_STATE_MAP = {
        HYPERV_VM_STATE_OTHER: 'Other',
        HYPERV_VM_STATE_ENABLED: 'Enabled',
        HYPERV_VM_STATE_DISABLED: 'Disabled',
        HYPERV_VM_STATE_SHUTTING_DOWN: 'Shutting Down',
        HYPERV_VM_STATE_REBOOT: 'Reboot',
        HYPERV_VM_STATE_PAUSED: 'Paused',
        HYPERV_VM_STATE_SUSPENDED: 'Suspended'
    }

    VM_POWER_ACTION = ['start', 'stop', 'force-stop', 'restart', 'force-restart', 'force-restart', 'pause', 'resume', 'save']

    # VM versions
    VM_VERSION_5_0 = '5.0'
    VM_VERSION_6_2 = '6.2'
    VM_VERSION_8_0 = '8.0'
    VM_VERSION_254_0 = '254.0'

    # VM generations
    VM_GEN_1 = 1
    VM_GEN_2 = 2
    VM_GEN = ['1', '2']

    # Controller types
    CTRL_TYPE_MAP = {
        'CTRL_TYPE_IDE': 'IDE',
        'CTRL_TYPE_SCSI': 'SCSI'
    }

    SIZE_UNIT = ['GB', 'MB']
    VM_MEMORY_TYPE = ['dynamic', 'static']
    VM_BOOT_DEVICE_MAP = {
        'hdd': 'HardDisk',
        'cd': 'CD',
        'network': 'Network',
        'uefi': 'UEFI'
    }
    VM_BOOT_DEVICE = ['hdd', 'cd', 'network', 'uefi']

    # VM TPM
    VTPM_SUPPORTED_OS = ['windows']
