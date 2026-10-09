# Hosting RepoInsight live for $0 (Oracle Cloud Always Free)

This puts the whole app (frontend, API, worker, Postgres, Redis and ChromaDB)
on one free Oracle Cloud server with HTTPS, at a link like
`https://yourname-repoinsight.duckdns.org` that you can put on your portfolio.

**What it costs:** $0. Oracle's *Always Free* tier, free Gemini and Groq AI keys,
and a free DuckDNS domain. Oracle asks for a card at sign-up to verify identity;
Always Free resources aren't charged.

**Time:** about an hour the first time, mostly waiting for builds.

---

## 1. Create the Oracle Cloud account

1. Sign up at <https://signup.cloud.oracle.com>.
2. **Pick your home region carefully.** You can't change it later, and free
   servers can only be created there. A region near you is fine. If free
   servers turn out to be "out of capacity" there, the fix is retrying later,
   not changing region.

## 2. Create the server

In the Oracle Console: **Compute → Instances → Create instance**.

| Setting | Value |
| --- | --- |
| Name | `repoinsight` |
| Image | **Canonical Ubuntu 24.04** (click *Change image*) |
| Shape | *Change shape* → **Ampere** → **VM.Standard.A1.Flex**, **2 OCPUs**, **12 GB memory** (the full Always Free allowance; look for the *Always Free-eligible* label) |
| Networking | Keep the defaults (new virtual cloud network, public subnet, **assign a public IPv4 address**) |
| SSH keys | **Generate a key pair for me** → download **both** keys and keep them safe |
| Boot volume | Default size (about 50 GB) is plenty |

Click **Create**. When it shows **Running**, copy the **Public IP address**.

> **"Out of capacity for shape VM.Standard.A1.Flex"** is common. Wait and try
> again later, or try a different *availability domain* in the Placement section.
> It's a capacity problem on Oracle's side, not a mistake on yours.

## 3. Open ports 80 and 443 in Oracle's network firewall

Instance page → **Subnet** link → **Security Lists** → *Default Security List* →
**Add Ingress Rules**, then add two rules:

| Source CIDR | IP Protocol | Destination port |
| --- | --- | --- |
| `0.0.0.0/0` | TCP | `80` |
| `0.0.0.0/0` | TCP | `443` |

(Port 80 is needed for the HTTPS certificate check. Visitors get redirected to 443.)

## 4. Get a free domain (DuckDNS)

HTTPS needs a domain name, not a bare IP.

1. Go to <https://www.duckdns.org> and sign in (GitHub or Google works).
2. Create a subdomain, e.g. `darel-repoinsight` → `darel-repoinsight.duckdns.org`.
3. Paste your server's public IP into **current ip** and click **update ip**.

> Have your own domain already? Add an **A record** (e.g. `repoinsight.yourdomain.com`)
> pointing at the server's IP and use that instead.

## 5. Get the free AI keys

- **Gemini:** <https://aistudio.google.com/apikey> → *Create API key*
- **Groq:** <https://console.groq.com/keys> → *Create API Key*

Get both. The app uses Gemini first and switches to Groq if Gemini fails or
hits its daily limit.

## 6. Connect to the server

From PowerShell (Windows) or Terminal (Mac):

```bash
ssh -i path/to/ssh-key.key ubuntu@YOUR_PUBLIC_IP
```

> **Windows "bad permissions" error on the key?** Run this once in PowerShell, then retry:
> ```powershell
> icacls path\to\ssh-key.key /inheritance:r /grant:r "$($env:USERNAME):R"
> ```

## 7. Put the code on the server

**If your GitHub repo is public:**

```bash
git clone https://github.com/Darel1997/RepoInsight.git
cd RepoInsight
```

**If it's private,** copy the zip from your computer instead. In a *second*
PowerShell window, on your computer:

```powershell
scp -i path\to\ssh-key.key RepoInsight.zip ubuntu@YOUR_PUBLIC_IP:~
```

Then on the server:

```bash
sudo apt-get update && sudo apt-get install -y unzip
unzip RepoInsight.zip && cd RepoInsight
```

## 8. Run the setup script

```bash
bash deploy/setup-server.sh
```

It installs Docker, opens the server's own firewall, asks for your domain and
AI keys, generates every password and secret, and starts the app. The first
build takes **10–20 minutes**. When it prints:

```
✓ RepoInsight is live
    https://darel-repoinsight.duckdns.org
```

open that link and register an account to confirm everything works.

## 9. Link it from your portfolio

Point the RepoInsight logo or button on your portfolio at your new URL. A short
line next to it helps recruiters: *"Live demo: create a free account and
analyze any public GitHub repo."*

---

## Optional: GitHub sign-in

Without this, visitors register with email and can analyze any **public** repo.
To add *Sign in with GitHub*:

1. <https://github.com/settings/developers> → **New OAuth App**
2. Homepage URL: `https://YOUR_DOMAIN`
3. Authorization callback URL: `https://YOUR_DOMAIN/auth/github/callback`
4. Put the Client ID and Secret in `.env` on the server (`nano .env`), then restart:
   ```bash
   docker compose -f docker-compose.prod.yml up -d
   ```

## Updating the live app

After pushing changes to GitHub:

```bash
cd ~/RepoInsight
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Everyday commands

```bash
docker compose -f docker-compose.prod.yml ps               # is everything healthy?
docker compose -f docker-compose.prod.yml logs -f api      # API logs (Ctrl+C to exit)
docker compose -f docker-compose.prod.yml logs caddy       # HTTPS / certificate logs
docker compose -f docker-compose.prod.yml restart api      # restart one service
```

Everything restarts automatically after a server reboot.

## Troubleshooting

| Symptom | Likely cause and fix |
| --- | --- |
| Site doesn't load at all | Ports 80/443 missing from the Oracle **security list** (step 3), or DuckDNS still has an old IP. |
| Browser shows a certificate warning | Caddy couldn't get the certificate yet, usually for the same reasons as above. Check `logs caddy`, fix, then `restart caddy`. |
| Site loads but AI features fail | Check the keys in `.env`, then run the diagnostics command below to see which AI providers the API detected. Free daily limits reset each day. |
| `api` shows `unhealthy` | `logs api --tail 50`. In production it refuses to start if a required secret is missing, and the log names which one. |
| `permission denied` running `docker` | Log out and back in once (the setup script added you to the `docker` group), or prefix commands with `sudo`. |

**Full diagnostics** (kept off the public internet on purpose):

```bash
docker compose -f docker-compose.prod.yml exec api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health/detail').read().decode())"
```

## Staying at $0

- Only create **Always Free-eligible** resources (one A1 server at 2 OCPUs / 12 GB, about 50 GB boot volume).
- Set a budget alert as a safety net: **Billing → Budgets → Create Budget** with a $1 limit.
- Oracle says it *may* reclaim Always Free servers that are idle for 7 days.
  It counts as idle only if CPU, network **and** memory use all stay under 20%.
  This app keeps several GB of memory in use, which should keep it above that
  line. Still, check your link every few weeks.
- Never put real API keys in `.env.example` or commit `.env`. `.gitignore` already excludes it.
