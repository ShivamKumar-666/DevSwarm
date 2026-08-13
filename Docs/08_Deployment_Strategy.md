# Deployment Strategy and Environment Guardrails

## 1. Staging Environment First
- **Never push untested code straight to production** where real users can see it.
- **Staging Environment**: A persistent, isolated copy of the production application must be maintained for pre-production testing. Staging must be isolated from production: separate secrets/credentials, separate data stores, separate third-party accounts, and separate domains. Staging must use sanitized test data only (no real user/production data).
- All new features, bug fixes, and updates must be deployed and tested in the staging environment first.

## 2. Git Workflow
- **`main` branch**: This is the strict production branch. It must always be stable and deployable.
- **`staging` branch**: This acts as our persistent pre-production branch. 
- **Feature Branches**: All active work should be done in feature branches (e.g., `feat/...`, `fix/...`).
- **Merge Flow**:
  1. Open a Pull Request from your `feature` branch to `staging`.
  2. Verify the ephemeral PR preview deployment (if an optional provider like Vercel/Netlify is configured).
  3. Once tested and approved (and reviewed by CodeRabbit), merge into `staging`.
  4. Perform final QA on the persistent `staging` environment.
  5. Open a Pull Request from `staging` to `main` to promote changes to production. This promotion requires:
     - A docker-mcp image build
     - A security-mcp scan run (in parallel with or immediately after the build)
     - A rollout verification step
     - A failed build, failed scan, or failed rollout check blocks promotion to production
     - If production rollout fails, roll back automatically/immediately via k8s-mcp's rollback_deployment (or equivalent) to the previous known-good state

## 3. Deployment Infrastructure

### Primary Deployment Path (Local Docker Compose + kind Cluster)
The production and staging environments are deployed using the local Docker Compose + kind cluster setup:
- **docker-mcp**: Handles build_image, push_image (to local registry), and scan_image operations
- **security-mcp**: Runs security checks via Trivy (scan_image, scan_repo) and OWASP ZAP (zap_scan)
- **k8s-mcp**: Manages deployments on the local kind cluster via apply_manifest, rollout_status, rollback_deployment, and get_pods

The workflow for deploying to staging or production:
1. docker-mcp builds and pushes the container image to the local registry
2. security-mcp performs security scans (Trivy + ZAP) on the image and repository
3. k8s-mcp applies manifests to the local kind cluster and verifies rollout status
4. If rollout fails, k8s-mcp performs an automatic rollback to the previous known-good deployment

No cloud account is required for this core flow. The local orchestration is defined in `docker-compose.yml` and `kind-cluster.yaml`.

### Optional: Ephemeral PR Previews (Vercel / Netlify)
If you wish to generate ephemeral, per-PR preview deployments (not required for the core docker-mcp/security-mcp/k8s-mcp flow):
- Connect the GitHub repository to your chosen platform (Vercel/Netlify)
- Set the Production Branch to `main`
- The platform will automatically generate ephemeral preview deployments for every Pull Request and branch
- Note: These previews are temporary and per-PR, distinct from the persistent staging environment deployed via the primary path above
