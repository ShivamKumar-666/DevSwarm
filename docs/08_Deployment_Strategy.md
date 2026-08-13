# Deployment Strategy and Environment Guardrails

## 1. Staging Environment First
- **Never push untested code straight to production** where real users can see it.
- **Staging Environment**: A private staging deployment must be maintained that mirrors the application architecture for pre-production testing. To prevent accidental impact on production resources or exposure of production PII, the staging environment must be strictly isolated: it must use separate secrets, credentials, data stores, third-party accounts, and domains, and it must be limited to sanitized test data.
- All new features, bug fixes, and updates must be deployed and tested in the staging environment first.

## 2. Git Workflow
- **`main` branch**: This is the strict production branch. It must always be stable and deployable. To enforce this, branch protection rules must be applied: require pull requests, prohibit direct and force pushes, and require successful build, security, preview, and staging-QA checks before merging.
- **`staging` branch**: This acts as our persistent pre-production branch. It must also have branch protection enabled: require pull requests, prohibit direct and force pushes, and require successful checks before merging.
- **Feature Branches**: All active work should be done in feature branches (e.g., `feat/...`, `fix/...`).
- **Merge Flow**: 
  1. Open a Pull Request from your `feature` branch to `staging`.
  2. Verify the ephemeral PR preview deployment.
  3. Once tested and approved (and reviewed by CodeRabbit), merge into `staging`.
  4. Perform final QA on the persistent `staging` environment.
  5. Open a Pull Request from `staging` to `main` to promote changes to production.
  6. **Promotion Gates:** The staging-to-main promotion requires the `docker-mcp` image build and parallel `security-mcp` scan to pass, followed by rollout verification via `k8s-mcp`. 
  7. **Failure & Rollback:** If the build, scan, or rollout checks fail, promotion is blocked. If the production rollout fails after merge, an automated rollback is executed as documented.

## 3. Deployment Infrastructure & Configuration
- **Primary Deployment Path**: DevSwarm operates primarily via a local `kind` cluster orchestrated by Docker Compose. The `docker-mcp`, `security-mcp`, and `k8s-mcp` agents natively handle image builds, security gates, deployments, and rollbacks against this cluster.
- **Alternative / Frontend Path (e.g., Vercel/Netlify)**: If utilizing a platform like Vercel or Netlify for hosting frontend assets (like the SRE Dashboard), set the Production Branch to `main`.
- **Preview Deployments**: If configured in the provider settings, the platform can generate ephemeral **PR Previews** for pull requests and branches. These are temporary and distinct from persistent staging.
- **Persistent Staging**: Assign the persistent `staging` branch a dedicated preview domain. Final QA must occur against this persistent staging deployment, not just an ephemeral PR preview.
