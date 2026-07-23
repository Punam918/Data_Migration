param(
    [switch]$Dev
)

python -m venv .venv
.\.venv\Scripts\Activate.ps1

if ($Dev) {
    pip install -e .[dev]
} else {
    pip install -e .
}

Write-Host "Bootstrap complete. Activate with .\\.venv\\Scripts\\Activate.ps1"
