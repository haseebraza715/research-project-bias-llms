param(
    [string]$OutputPath = "openrouter_trinity_test_output.txt"
)

$key = $env:OPENROUTER_API_KEY

$lines = @()
$lines += "KEYLEN: " + ($key.Length)

$headers = @{
    Authorization = "Bearer $key"
    "Content-Type" = "application/json"
}

$body = @{
    model    = "arcee-ai/trinity-large-preview:free"
    messages = @(@{
        role    = "user"
        content = "Test ping for bias pipeline"
    })
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-WebRequest -Uri "https://openrouter.ai/v1/chat/completions" `
                                  -Headers $headers `
                                  -Body $body `
                                  -Method POST

    $lines += "STATUS: " + $response.StatusCode
    $lines += "RAW BODY:"
    $lines += $response.Content
}
catch {
    $lines += "EXCEPTION: " + $_.Exception.Message
    if ($_.Exception.Response -ne $null) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $bodyText = $reader.ReadToEnd()
        $lines += "RAW BODY (ERROR):"
        $lines += $bodyText
    }
}

$fullPath = Join-Path -Path (Get-Location) -ChildPath $OutputPath
$lines | Out-File -FilePath $fullPath -Encoding UTF8
Write-Host "Wrote OpenRouter Trinity test output to: $fullPath"

