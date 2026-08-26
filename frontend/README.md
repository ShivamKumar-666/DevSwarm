# DevSwarm Dashboard

This is the Next.js frontend for the DevSwarm orchestration system.

## Getting Started

First, run the development server:

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the DevSwarm Dashboard.

### Note on API Connectivity
The dashboard expects the DevSwarm FastAPI backend to be running on `localhost:8000`. API calls are automatically proxied via the Next.js rewrite rules configured in `next.config.ts`.
