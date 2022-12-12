param($vm_name,$bmp_path,$xResolution,$yResolution)


# 判断$vm_name是否存在于Get-VM的虚拟机列表中，如果存在则继续执行，否则报错，再加一个检测是否运行
if($vm_name -in (Get-VM).Name -and "Running" -in (Get-VM -VMName "$vm_name").State)
{
    Add-Type -AssemblyName "System.Drawing"
    $VMCS = Get-WmiObject -Namespace "root\virtualization\v2" -Class "Msvm_ComputerSystem" -Filter "ElementName='$($vm_name)'"

    # 获取缩略图分辨率
    $video = $VMCS.GetRelated("Msvm_VideoHead")

#    $x = $video.CurrentHorizontalResolution[0]
#    $y = $video.CurrentVerticalResolution[0]

    # 如果$xResolution和$yResolution为False，则使用下面的分辨率，否则使用传参分辨率
    if($xResolution -eq "False" -and $yResolution -eq "False")
    {
        $x = $video.CurrentHorizontalResolution[0]
        $y = $video.CurrentVerticalResolution[0]
    }
    else
    {
        $x = $xResolution
        $y = $yResolution
    }

    function getVMScreenBMP {
        param($VM, $x, $y)

        $VMMS = Get-WmiObject -Namespace "root\virtualization\v2" -Class "Msvm_VirtualSystemManagementService"

        # 尝试获取快照图
        $image = $VMMS.GetVirtualSystemThumbnailImage($VMCS, $x, $y).ImageData

        # 转换成bmp
        $BitMap = New-Object System.Drawing.Bitmap -Args $x,$y,Format16bppRgb565
        $Rect = New-Object System.Drawing.Rectangle 0,0,$x,$y
        $BmpData = $BitMap.LockBits($Rect,"ReadWrite","Format16bppRgb565")
        [System.Runtime.InteropServices.Marshal]::Copy($Image, 0, $BmpData.Scan0, $BmpData.Stride*$BmpData.Height)
        $BitMap.UnlockBits($BmpData)

        return $BitMap
    }
    (getVMScreenBMP $VMCS $x $y).Save($bmp_path)

}
else
{
    Write-Error "VM $vm_name does not exist or is not running"
}


#$VMName = "test_imported"
#$BMPName = "E:\test.bmp"


