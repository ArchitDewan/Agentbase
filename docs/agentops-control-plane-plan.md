# AgentOps Control Plane

## Summary

Build a resume-grade FastAPI + AWS SaaS platform for orchestrating AI agent jobs with hosted auth/UI and self-hosted Docker workers.

The project is an agent operations dashboard: users sign in, create workspaces, register local workers, submit jobs, watch live run logs, approve risky tool calls, and inspect outputs, costs, and audit history. AWS hosts the control plane; actual task execution happens on user-run workers that poll outbound over HTTPS.

Key references:

- AWS API Gateway/auth concepts: https://docs.aws.amazon.com/serverless/latest/devguide/starter-apigw.html
- Cognito JWT/auth behavior: https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-how-to-authenticate.html
- OpenAI Responses/tools quickstart: https://platform.openai.com/docs/quickstart/make-your-first-api-request
- Composio OpenAI provider docs: https://docs.composio.dev/docs/providers/openai

## Key Changes

- Backend: FastAPI control plane on AWS ECS Fargate behind ALB.
- Frontend: React/TypeScript SaaS dashboard hosted via S3 + CloudFront.
- Auth: Amazon Cognito user pool for login; FastAPI verifies JWTs and maps users to workspace roles.
- Data: PostgreSQL/RDS for tenants, users, workers, jobs, runs, approvals, logs, artifacts, and audit events.
- Worker model: local Docker worker CLI registers with the API, long-polls for leased jobs, executes jobs in isolated Docker containers, and streams status/logs back.
- Agent runtime: OpenAI integration for agent/tool execution, with Composio optional but supported for external tools like Gmail, Slack, GitHub, Linear, or Notion.
- Safety: approval gates for sensitive tool calls, per-job timeouts, worker allowlists, scoped environment variables, audit logs, and cancellation.
- Observability: CloudWatch logs/metrics, structured request IDs, job duration/cost tracking, worker heartbeat status, and admin dashboard filters.

## Public Interfaces

### User API

- `POST /jobs` creates an agent job with prompt, tool profile, workspace, and optional input files.
- `GET /jobs`, `GET /jobs/{id}`, `POST /jobs/{id}/cancel`.
- `GET /runs/{id}/logs` returns paginated logs/events.
- `POST /approvals/{id}/approve` and `POST /approvals/{id}/reject`.

### Worker API

- `POST /workers/register` exchanges a setup token for a worker credential.
- `POST /workers/heartbeat`.
- `POST /workers/lease` long-polls for available jobs.
- `POST /workers/jobs/{id}/events` streams status, logs, approval requests, artifacts, and final results.

### Core Statuses

- Job: `queued`, `leased`, `running`, `awaiting_approval`, `succeeded`, `failed`, `cancelled`, `expired`.
- Approval: `pending`, `approved`, `rejected`, `expired`.

### Tool Profiles

- `openai_local_tools`: custom Python tools only.
- `openai_composio`: Composio-backed external app tools, enabled only when API keys/session config exist.

## Implementation Plan

- Scaffold a monorepo with `apps/api`, `apps/web`, `apps/worker`, and `infra`.
- Implement FastAPI with SQLAlchemy/Alembic, Pydantic settings, JWT verification, workspace RBAC, and OpenAPI docs.
- Build the React dashboard with pages for login, workspace overview, jobs, job detail/log timeline, approval queue, workers, and settings.
- Implement the worker as a Python CLI:
  - Runs as `docker compose up worker`.
  - Registers once using a setup token.
  - Polls the API for leases.
  - Executes each job inside a short-lived Docker container.
  - Sends logs/events back to the API.
- Add OpenAI agent execution:
  - Start with custom function tools such as `summarize_text`, `create_ticket_mock`, and `send_message_mock`.
  - Add Composio integration behind config flags for real third-party actions.
  - Any mutating external action creates an approval request before execution.
- Add Terraform/CDK infrastructure for Cognito, ECS Fargate, RDS Postgres, S3, CloudFront, Secrets Manager, CloudWatch, IAM, and networking.

## Test Plan

- Unit tests for auth claims, RBAC, job state transitions, approval decisions, worker leasing, and timeout/expiry behavior.
- Integration tests for job lifecycle: create job -> worker leases -> job runs -> logs stream -> result stored.
- Approval tests: mutating tool pauses job -> user approves/rejects -> worker resumes or stops.
- Worker tests using Docker with fake tools and mocked OpenAI/Composio clients.
- API contract tests against generated OpenAPI schema.
- Deployment smoke test: hosted UI login, create workspace, register worker, run demo job, approve tool call, view final output.

## Assumptions

- Use React SPA instead of Next.js so the frontend can be cheaply hosted on S3 + CloudFront.
- Use ECS Fargate for the FastAPI API because it best demonstrates production container deployment.
- Use local Docker workers for execution because user tasks often need local context and should not require inbound access to the user machine.
- Use Composio as an optional integration, not a hard dependency, so the project still works without third-party account setup.
- Use PostgreSQL job leasing rather than exposing AWS queue credentials to local workers.
