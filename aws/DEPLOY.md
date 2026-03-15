## AWS Deployment

Use AWS-managed MySQL via RDS and run the app containers separately from the database.

### Recommended layout

- Push the API and dashboard images to Amazon ECR.
- Run the `api` and `dashboard` containers on ECS Fargate.
- Run MySQL on Amazon RDS.
- Run `bootstrap_db.py` once as a one-off ECS task after the RDS database is reachable.
- Expose the dashboard publicly through an Application Load Balancer.
- Expose the API publicly only if you need direct access. Otherwise keep it internal and point the dashboard at the internal API URL.

### Required environment variables

Use the values from [`.env.aws.example`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/.env.aws.example) as the template.

- `DB_HOST`
- `DB_USER`
- `DB_PASSWORD`
- `DB_NAME`
- `DB_PORT`
- `API_URL`
- `INITIAL_ARTWORK_SEED_COUNT`
- `INITIAL_ARTWORK_MINIMUM_COUNT`
- `INITIAL_ARTWORK_MAX_ATTEMPTS`
- `INITIAL_ARTWORK_RETRIES_PER_ARTWORK`
- `INITIAL_ARTWORK_RETRY_BACKOFF_SECONDS`
- `FAIL_ON_SEED_SHORTFALL`

### Runtime behavior

- [`scripts/start_api.py`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/scripts/start_api.py) waits for the database and creates tables when `RUN_DB_INIT_ON_STARTUP=true`.
- [`scripts/bootstrap_db.py`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/scripts/bootstrap_db.py) initializes tables and seeds data as a one-off task.
- `CREATE_DB_IF_MISSING` should stay `false` on RDS unless your DB user has permission to create databases and that is part of your rollout.
- The bootstrap task now treats `408`, `429`, and `5xx` responses as transient, retries them with backoff, and fails the task if it cannot reach `INITIAL_ARTWORK_MINIMUM_COUNT`.
- The bootstrap task also starts with a curated fallback list from [`app/seed_ids.py`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/app/seed_ids.py), so seed runs are not fully dependent on a fresh `/objects` scan.

### ECS task templates

Use the templates in [`aws/ecs/api-task-definition.json`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/aws/ecs/api-task-definition.json), [`aws/ecs/dashboard-task-definition.json`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/aws/ecs/dashboard-task-definition.json), and [`aws/ecs/bootstrap-task-definition.json`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/aws/ecs/bootstrap-task-definition.json).

See [`aws/ecs/README.md`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/aws/ecs/README.md) for the placeholder values you need to replace.

### Deployment order

1. Create the ECR repositories.
2. Build and push the API and dashboard images.
3. Create the RDS MySQL instance and allow inbound traffic from the ECS service security group.
4. Register and run the bootstrap ECS task once.
5. Deploy the API ECS service.
6. Deploy the dashboard ECS service.
7. Attach an ALB target group to the dashboard service.
8. Optionally attach an internal ALB target group to the API service.

### Build and push

```bash
docker build -f Dockerfile.api -t museum-art-api .
docker build -f Dockerfile.dashboard -t museum-art-dashboard .
```

Then tag and push to your ECR repositories.

### Example bootstrap task command

```bash
python -m scripts.bootstrap_db
```

### Example API task command

```bash
python -m scripts.start_api
```

### Suggested ECS health checks

- API health path: `GET /health`
- Dashboard health path: `GET /`

### Local production-like test

```bash
docker compose -f docker-compose.aws.yml --env-file .env.aws.example up --build
```

That compose file intentionally excludes MySQL so you can point it at an external database, mirroring AWS more closely.
