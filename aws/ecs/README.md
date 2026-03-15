## ECS Templates

These task definitions are templates, not drop-in finished values.

Replace:

- `<account-id>`
- `<region>`
- `<rds-endpoint>`
- `<db-user>`
- `<db-password-secret>`
- `<internal-api-dns>`

Recommended usage:

1. Register `bootstrap-task-definition.json`
2. Run it once as an ECS task
3. Register `api-task-definition.json` and deploy the API service
4. Register `dashboard-task-definition.json` and deploy the dashboard service

Use the same VPC and security groups so:

- dashboard can reach API on `8000`
- API can reach RDS on `3306`
