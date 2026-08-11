# Containerized development setup

A disposable Frappe v16 bench in Docker for developing Kamra, isolated from any
other bench on the machine (named volumes, ports 8100+).

**Requirements:** Docker Engine ≥ 24 with Compose v2. Nothing else — no local
Python, Node, MariaDB or Redis.

## 1. Start the stack

```bash
docker compose -p kamra-eval -f docker-compose.dev.yml up -d
```

Four containers come up: `frappe` (bench workspace), `mariadb`, `redis-cache`,
`redis-queue`.

## 2. Create the bench

```bash
docker exec -u root kamra-eval-frappe-1 chown -R frappe:frappe /workspace
docker exec kamra-eval-frappe-1 bash -c "cd /workspace && \
  bench init --skip-redis-config-generation --frappe-branch version-16 kamra-bench"
```

Kamra requires `frappe >=16.0.0-dev,<17.0.0` (see `pyproject.toml`), so the
bench must be initialised on **version-16**.

## 3. Point bench at the service containers

```bash
docker exec kamra-eval-frappe-1 bash -c "cd /workspace/kamra-bench && \
  bench set-config -g db_host mariadb && \
  bench set-config -g redis_cache redis://redis-cache:6379 && \
  bench set-config -g redis_queue redis://redis-queue:6379 && \
  bench set-config -g redis_socketio redis://redis-queue:6379"
```

## 4. Get the apps

`payments` is a required app (`required_apps` in `kamra/hooks.py`).

```bash
docker exec kamra-eval-frappe-1 bash -c "cd /workspace/kamra-bench && \
  bench get-app --branch version-16 payments && \
  bench get-app --branch develop https://github.com/Kamra-PMS/kamra-pms"
```

To work against a local checkout instead, `docker cp` it into the container and
`bench get-app /path/to/checkout --branch <branch>` — note `bench get-app` clones
from a local path, so the branch must exist **locally** in that checkout, not just
as a remote-tracking branch.

## 5. Create the site

```bash
docker exec kamra-eval-frappe-1 bash -c "cd /workspace/kamra-bench && \
  bench new-site kamra.localhost \
    --mariadb-root-password 123 --admin-password admin \
    --install-app payments --install-app kamra \
    --mariadb-user-host-login-scope='%' && \
  bench use kamra.localhost && \
  bench --site kamra.localhost set-config developer_mode 1"
```

## 6. Run it

```bash
docker exec -d kamra-eval-frappe-1 bash -c "cd /workspace/kamra-bench && bench start"
```

Open <http://localhost:8100> and log in as `Administrator` / `admin`.

For the SPA with hot reload, run `npm run dev` in `frontend/` inside the
container; Vite is reachable on port 8105 (container 5173 mapping may need
adjusting in the compose file).

## Housekeeping

```bash
docker compose -p kamra-eval -f docker-compose.dev.yml stop   # pause
docker compose -p kamra-eval -f docker-compose.dev.yml start  # resume
docker compose -p kamra-eval -f docker-compose.dev.yml down -v  # delete everything
```

`down -v` removes the volumes — bench, apps and database all go. Use it when you
want a genuinely clean slate.

## Note on ERPNext

Kamra defines DocTypes named `Company` and `Stock Ledger Entry`, which collide
with ERPNext's core DocTypes. **Kamra and ERPNext cannot be installed on the same
site.** They can coexist on the same bench as separate sites, with separate
databases.
