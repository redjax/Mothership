try {
    winget install jdx.mise
} catch {
    Write-Error "Failed installing Mise: $($_.Exception.Message)"
    exit(1)
}

Write-Output "Successfully installed Mise"
