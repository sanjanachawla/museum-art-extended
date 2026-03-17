## AWS Deployment

This repo is set up to deploy cleanly on a single EC2 instance with Docker Compose.

There are two supported paths:

- EC2 only: one Ubuntu instance runs MySQL, API, dashboard, and the one-time bootstrap job
- EC2 + RDS: the EC2 instance runs API and dashboard, while MySQL lives in Amazon RDS

For a class project or small demo, EC2 only is the shortest path. For a more durable setup, use EC2 + RDS.

## Architecture

EC2 only:

- MySQL runs in Docker on the EC2 instance
- FastAPI runs in Docker on port `8000`
- Streamlit runs in Docker on port `8501`
- the dashboard reaches the API over the internal Compose network at `http://api:8000`

EC2 + RDS:

- MySQL runs in Amazon RDS
- FastAPI and Streamlit still run together on the EC2 instance
- the bootstrap job runs once against RDS from the EC2 host

## Files used

- [`docker-compose.ec2.yml`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/docker-compose.ec2.yml)
- [`docker-compose.aws.yml`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/docker-compose.aws.yml)
- [`.env.ec2.example`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/.env.ec2.example)
- [`.env.aws.example`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/.env.aws.example)
- [`aws/ec2/deploy.sh`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/aws/ec2/deploy.sh)
- [`scripts/start_api.py`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/scripts/start_api.py)
- [`scripts/bootstrap_db.py`](/c:/Users/Rahul%20Chawla/dev/museum-art-extended/scripts/bootstrap_db.py)

## Step 1: Launch the EC2 instance

Create an Ubuntu EC2 instance.

Recommended minimum:

- instance type: `t3.small`
- storage: `20 GB`
- OS: Ubuntu 24.04 LTS or Ubuntu 22.04 LTS

Security group rules:

- inbound `22` from your IP only
- inbound `8501` from the public internet if you want direct access to Streamlit
- inbound `8000` only if you intentionally want the API public
- inbound `3306` only if you are using RDS and need a temporary direct admin path

If you later add Nginx and TLS, expose `80` and `443` instead of `8501`.

## Step 2: Install Docker on the instance

SSH into the instance and run:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
newgrp docker
```

Verify:

```bash
docker --version
docker compose version
```

## Step 3: Copy the repo to the instance

From the EC2 shell:

```bash
git clone <your-repo-url>
cd museum-art-extended
```

If the repo is already on the box, just `git pull`.

## Step 4: Choose your deployment mode

### Option A: EC2 only

Copy the example env file:

```bash
cp .env.ec2.example .env.ec2
```

Edit `.env.ec2` and set at least:

- `MYSQL_ROOT_PASSWORD`
- `DB_PASSWORD`

Keep `DB_HOST=mysql` and `API_URL=http://api:8000` as-is.

### Option B: EC2 + RDS

Create an RDS MySQL database first, then:

```bash
cp .env.aws.example .env.aws
```

Edit `.env.aws` and set:

- `DB_HOST=<your-rds-endpoint>`
- `DB_USER=<your-db-user>`
- `DB_PASSWORD=<your-db-password>`
- `DB_NAME=met_art`
- `DB_PORT=3306`

Keep `API_URL=http://api:8000` when API and dashboard run in the same Compose project on EC2.

For RDS security groups:

- allow MySQL `3306` from the EC2 instance security group
- do not open MySQL to the public internet unless you have a temporary admin need

## Step 5: Start the stack

EC2 only:

```bash
bash aws/ec2/deploy.sh
```

EC2 + RDS:

```bash
COMPOSE_FILE=docker-compose.aws.yml ENV_FILE=.env.aws bash aws/ec2/deploy.sh
```

What this does:

- builds the API and dashboard images
- starts the long-running services
- runs the one-time `bootstrap` job to create tables and seed initial artwork
- prints the service status

If you need to skip bootstrap on a later deploy:

```bash
RUN_BOOTSTRAP=false bash aws/ec2/deploy.sh
```

## Step 6: Verify the deployment

From the EC2 shell:

```bash
docker compose -f docker-compose.ec2.yml --env-file .env.ec2 ps
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/docs
```

For the RDS mode, replace the compose and env file names:

```bash
docker compose -f docker-compose.aws.yml --env-file .env.aws ps
```

From your browser:

- `http://<ec2-public-ip>:8501`

## Step 7: View logs and manage the app

EC2 only:

```bash
docker compose -f docker-compose.ec2.yml --env-file .env.ec2 logs -f
docker compose -f docker-compose.ec2.yml --env-file .env.ec2 ps
docker compose -f docker-compose.ec2.yml --env-file .env.ec2 restart
docker compose -f docker-compose.ec2.yml --env-file .env.ec2 down
```

EC2 + RDS:

```bash
docker compose -f docker-compose.aws.yml --env-file .env.aws logs -f
```

## Updating later

When you change the code on the instance:

```bash
git pull
RUN_BOOTSTRAP=false bash aws/ec2/deploy.sh
```

If you need to re-run the database seed intentionally:

```bash
docker compose --env-file .env.ec2 -f docker-compose.ec2.yml run --rm bootstrap
```

## Notes

- Streamlit on `8501` is fine for a first deployment, but it is not a polished public-facing setup
- for a cleaner public endpoint, place Nginx or Caddy in front of the dashboard and terminate TLS there
- if you outgrow one EC2 host, move to ECS or another managed container platform
