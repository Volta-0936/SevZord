# Run the Jev comparison. The key is never printed.
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot
$log = Join-Path $PSScriptRoot "jev_run.log"
"start $(Get-Date -Format s)" | Out-File -Encoding utf8 $log
if (-not $env:TYPESAFE_API_KEY) {
  foreach ($scope in "User", "Machine") {
    $k = [Environment]::GetEnvironmentVariable("TYPESAFE_API_KEY", $scope)
    if ($k) { $env:TYPESAFE_API_KEY = $k; "key: TYPESAFE_API_KEY ($scope)" | Out-File -Append -Encoding utf8 $log; break }
  }
}
if (-not $env:TYPESAFE_API_KEY) {
  # Fallback: any variable whose name contains TYPESAFE (value never printed)
  foreach ($scope in "User", "Machine", "Process") {
    $vars = [Environment]::GetEnvironmentVariables($scope)
    foreach ($n in $vars.Keys) {
      if ($n -match "TYPESAFE" -and $vars[$n]) { $env:TYPESAFE_API_KEY = $vars[$n]; "key: $n ($scope)" | Out-File -Append -Encoding utf8 $log; break }
    }
    if ($env:TYPESAFE_API_KEY) { break }
  }
}
if (-not $env:TYPESAFE_API_KEY -and -not (Test-Path (Join-Path $PSScriptRoot "typesafe_key.txt"))) {
  "no key found in env (User/Machine/Process) nor typesafe_key.txt" | Out-File -Append -Encoding utf8 $log
}
$env:PYTHONUTF8 = "1"
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
"python: $($py.Source)" | Out-File -Append -Encoding utf8 $log
foreach ($lang in "ja", "en") {
  & $py.Source jev_compare.py $lang 2>&1 | ForEach-Object { $_; $_ | Out-File -Append -Encoding utf8 $log }
}
"end $(Get-Date -Format s)" | Out-File -Append -Encoding utf8 $log
