# Install and Import Required Modules
try {
    # Ensure the PnP PowerShell module is installed and imported
    if (-not (Get-Module -ListAvailable -Name "PnP.PowerShell")) {
        Install-Module -Name "PnP.PowerShell" -Force -Scope CurrentUser
    }
    Import-Module PnP.PowerShell
} catch {
    Write-Host "Error installing or importing PnP.PowerShell module: $_"
    exit
}

# Define variables
$adminUrl = "https://safeloc-admin.sharepoint.com"
$userEmail = "eheins@electrificationcoalition.org"
$csvFilePath = "C:\users\antho\documents\RecycleBinItems.csv"  # Update this path as needed
$fileNameToRestore = "Emma Heins Transition Plan_July 2024.docx"  # Update this with the actual file name you want to restore

# Connect to SharePoint Online Admin Center using MFA
try {
    Connect-PnPOnline -Url $adminUrl -Interactive
} catch {
    Write-Host "Error connecting to SharePoint Online: $_"
    exit
}

# Get the OneDrive URL for the user
try {
    $oneDriveSite = Get-PnPTenantSite -IncludeOneDriveSites | Where-Object { $_.Owner -eq $userEmail }

    if ($oneDriveSite -eq $null) {
        Write-Host "Could not find OneDrive site for user: $userEmail"
        exit
    }
} catch {
    Write-Host "Error retrieving OneDrive URL: $_"
    exit
}

# Connect to the user's OneDrive using MFA
try {
    Connect-PnPOnline -Url $oneDriveSite.Url -Interactive
} catch {
    Write-Host "Error connecting to the user's OneDrive: $_"
    exit
}

# Retrieve Recycle Bin items in batches
$batchSize = 100  # Adjust batch size if necessary
$allRecycleBinItems = @()

try {
    $skip = 0
    $batch = $null
    do {
        $batch = Get-PnPRecycleBinItem -RowLimit $batchSize -StartRow $skip
        $allRecycleBinItems += $batch
        $skip += $batchSize
    } while ($batch.Count -eq $batchSize)

    # Display the Recycle Bin items
    $allRecycleBinItems | Format-Table -Property Title, DirName, Size, DeletedDate, ItemType, ID

    # Export Recycle Bin items to CSV
    $allRecycleBinItems | Export-Csv -Path $csvFilePath -NoTypeInformation -Force

    # Inform the user where the file has been saved
    Write-Host "Recycle Bin items have been exported to $csvFilePath"
} catch {
    Write-Host "Error retrieving or exporting Recycle Bin items: $_"
}

# Restore the specified file
try {
    $fileToRestore = $allRecycleBinItems | Where-Object { $_.Title -eq $fileNameToRestore }

    if ($fileToRestore -ne $null) {
        $recycleBinItemId = $fileToRestore.Id
        Restore-PnPRecycleBinItem -Identity (New-Object PnP.PowerShell.Commands.Base.PipeBinds.RecycleBinItemPipeBind($recycleBinItemId))
        Write-Host "Restored item: $($fileToRestore.Title)"
    } else {
        Write-Host "No file found with the name: $fileNameToRestore"
    }
} catch {
    Write-Host "Error restoring item: $_"
}
