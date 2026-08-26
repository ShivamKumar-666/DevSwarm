$ErrorActionPreference = "Stop"

$BIN_DIR = "$PSScriptRoot\.bin"
$KIND_EXE = "$BIN_DIR\kind.exe"
$KUBECTL_EXE = "$BIN_DIR\kubectl.exe"
$IMAGE_NAME = "devswarm-app:latest"

# 1. Ensure Binaries Exist
if (!(Test-Path -Path $BIN_DIR)) {
    New-Item -ItemType Directory -Force -Path $BIN_DIR | Out-Null
}

if (!(Test-Path -Path $KIND_EXE)) {
    Write-Host " Downloading kind.exe..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "https://kind.sigs.k8s.io/dl/v0.20.0/kind-windows-amd64" -OutFile $KIND_EXE
}

if (!(Test-Path -Path $KUBECTL_EXE)) {
    Write-Host " Downloading kubectl.exe..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "https://dl.k8s.io/release/v1.28.0/bin/windows/amd64/kubectl.exe" -OutFile $KUBECTL_EXE
}

Write-Host " STARTING CI/CD PIPELINE" -ForegroundColor Green
Write-Host "===========================" -ForegroundColor Green

# 2. Build Docker Image
Write-Host "`n Building Docker image: $IMAGE_NAME" -ForegroundColor Cyan
docker build -t $IMAGE_NAME ./sample-app
if ($LASTEXITCODE -ne 0) {
    Write-Host " Docker build failed." -ForegroundColor Red
    exit 1
}

# 3. Trigger DevSwarm Verification
Write-Host "`n Triggering DevSwarm AI Evaluation..." -ForegroundColor Cyan
$runPayload = @{
    image_tag = "nginx:1.14.2"
    deployment_name = "devswarm-demo"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/swarm/run" -Method Post -Body $runPayload -ContentType "application/json"
    $runId = $response.run_id
    Write-Host " Swarm Triggered. Run ID: $runId" -ForegroundColor Green
} catch {
    Write-Host " Failed to reach DevSwarm API. Is the FastAPI server running on port 8000?" -ForegroundColor Red
    exit 1
}

# 4. Poll Status
Write-Host " Waiting for Swarm Decision..." -ForegroundColor Yellow
$status = "running"
$finalDecision = ""

while ($status -eq "running" -or $status -eq "needs_approval") {
    Start-Sleep -Seconds 3
    $statusResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/swarm/status/$runId"
    $status = $statusResponse.status
    
    if ($status -eq "needs_approval") {
        Write-Host " CONFLICT DETECTED. Human approval required!" -ForegroundColor Yellow
        Write-Host " Open http://localhost:3000 to manually approve." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}

$finalDecision = $statusResponse.state.final_decision

if ($finalDecision -ne "proceed") {
    Write-Host "`n DEPLOYMENT BLOCKED by DevSwarm: Decision was $finalDecision" -ForegroundColor Red
    exit 1
}

Write-Host "`n DEPLOYMENT APPROVED by DevSwarm!" -ForegroundColor Green

# 5. Deploy to Kind
Write-Host "`n Deploying to local Kind cluster..." -ForegroundColor Cyan

# Check if cluster exists
$clusters = & $KIND_EXE get clusters
if ($clusters -notcontains "devswarm") {
    Write-Host "Creating Kind cluster devswarm..."
    & $KIND_EXE create cluster --name devswarm
}

Write-Host "Loading Docker image into Kind..."
& $KIND_EXE load docker-image $IMAGE_NAME --name devswarm

Write-Host "Applying Kubernetes manifests..."
& $KUBECTL_EXE apply -f ./sample-app/k8s/deployment.yaml

Write-Host "`n PIPELINE SUCCESSFUL!" -ForegroundColor Green
Write-Host "Your app is now running securely in Kubernetes." -ForegroundColor Green
