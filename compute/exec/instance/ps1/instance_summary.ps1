param($vm_name)


function Get-VMSummary
{
    param($vm_name)

    $vm_state = (Get-VM -Name $vm_name).State

    $vm_createdate = Get-VM -Name $vm_name | Select-Object -ExpandProperty CreationTime

    $vm_snapshot = Get-VMSnapshot -VMName $vm_name | Measure-Object | Select-Object -ExpandProperty Count

    $vm_ipaddress = Get-VMNetworkAdapter -VMName $vm_name | Select-Object -ExpandProperty IPAddresses

    $wmi_vm = Get-WmiObject -Namespace 'root\virtualization\v2' -Class 'Msvm_ComputerSystem' | Where-Object { $_.ElementName -eq $vm_name }
    $summary = $wmi_vm.GetRelated('Msvm_SummaryInformation')
    New-Object PSObject -Property @{
        "Host" = [String]$summary.HostComputerSystemName;
        "Name" = [String]$summary.elementname;
        "VMId" = [String]$summary.name;
        "CreationTime" = [String]$vm_createdate;
        "EnabledState" = [String]$vm_state;
        "Notes" = [String]$summary.Notes;
        "CPUCount" = [String]$summary.NumberOfProcessors;
        "CPULoad" = [String]$summary.ProcessorLoad;
        "MemoryCount" = [String]$summary.MemoryUsage;
        "GuestOS" = [String]$summary.GuestOperatingSystem;
        "Snapshots" = [String]$vm_snapshot;
        "IPAddress" = [String]$vm_ipaddress;
        "Uptime" = [String]$summary.UpTime;
        "UptimeFormatted" = $( if ($summary.uptime -gt 0)
        {
            ([datetime]0).addmilliseconds($summary.UpTime).tostring("hh:mm:ss")
        }
        else
        {
            0
        } )
    }
}
# $key: Host, Name, VMId, CreationTime, EnabledState, Notes, CPUCount, CPULoad, MemoryCount, GuestOS, Snapshots, IPAddress, Uptime, UptimeFormatted
Get-VMSummary $vm_name