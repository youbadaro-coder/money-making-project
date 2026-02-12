$shell = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath('Desktop')
# Find the batch file dynamically to avoid encoding issues in the script
$targetFile = Get-ChildItem "c:\ai작업\anti\수익화에이전트첫걸음" -Filter "*.bat" | Where-Object { $_.Name -match "바이럴" }

if ($targetFile) {
    # We still need a name for the shortcut. Let's try English first if Korean fails, 
    # but I'll try the full name from the file itself.
    $shortcut = $shell.CreateShortcut("$desktop\Shorts_Generator.lnk")
    $shortcut.TargetPath = $targetFile.FullName
    $shortcut.Save()
    Write-Host "Shortcut created: $($targetFile.Name) -> $desktop\Shorts_Generator.lnk"
} else {
    Write-Error "Target batch file not found."
}
