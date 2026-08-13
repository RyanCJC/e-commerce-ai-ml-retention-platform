$ErrorActionPreference = "Stop"

Write-Host "========================================"
Write-Host "Exporting model from MLflow"
Write-Host "========================================"

python scripts/export_model.py

if ($LASTEXITCODE -ne 0) {
    throw "Model export failed."
}

Write-Host ""
Write-Host "========================================"
Write-Host "Verifying model"
Write-Host "========================================"

python scripts/verify_model.py

if ($LASTEXITCODE -ne 0) {
    throw "Model verification failed."
}

Write-Host ""
Write-Host "========================================"
Write-Host "Building Docker image"
Write-Host "========================================"

docker build -t ecommerce-churn-api:latest .

if ($LASTEXITCODE -ne 0) {
    throw "Docker build failed."
}

Write-Host ""
Write-Host "Docker image built successfully."