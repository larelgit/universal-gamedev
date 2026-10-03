# Link skills\ into the folders each agent scans in a clone (.claude\skills, .agents\skills, .gemini\skills,
# .github\skills) as directory junctions: no admin rights or Developer Mode needed. Run once after cloning;
# the links are gitignored.
$root = Split-Path -Parent $PSScriptRoot
foreach ($d in '.claude', '.agents', '.gemini', '.github') {
    $dir = Join-Path $root $d
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $link = Join-Path $dir 'skills'
    if (Test-Path $link) { Write-Output "exists: $d\skills"; continue }
    New-Item -ItemType Junction -Path $link -Target (Join-Path $root 'skills') | Out-Null
    Write-Output "linked: $d\skills -> skills"
}
