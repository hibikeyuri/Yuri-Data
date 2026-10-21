# Security checklist, Cloudflare and retiring GCP

## Historical findings
- Historical publicly tracked docker-compose.yml included a hardcoded phpMyAdmin password and host port publishing for MySQL 3306 and phpMyAdmin 8081. The secret might be retained in Git history even after removal on this new branch. If it was used, rotate credentials and review access logs; coordinate a history cleanup if necessary.
- Historical production Flask used app.debug=True with Flask built-in development server, an unsafe combination for public production.
- Old dependency pins (2022) include Flask 2.1, urllib3 1.26, Requests 2.27 and PyMySQL 1.0.
- Old default Nginx config had HTTP redirects, TLS 1.2/1.3, and security headers; its /static/ block used add_header, overriding inherited security header defaults on older Nginx configurations.
- No confirmed compromise or proof of actual external exposure was obtained from this inspection.

## Cloudflare Origin CA
The Origin CA certificate is ONLY intended for the Cloudflare-to-origin TLS hop, not direct public browser trust. Use Cloudflare SSL/TLS mode Full (strict), confirm the origin hostname matches the certificate and that the Cloudflare proxy is enabled.

Full (strict) validates the origin certificate but does not itself prevent visitors bypassing Cloudflare and hitting the origin IP. Restrict GCP ingress to needed sources, or consider correctly configured Cloudflare Tunnel / Authenticated Origin Pulls. These strategies are not interchangeable. Keep origin private keys outside Git and pass them only to trusted runtime mounts.

References:
- https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/full-strict/
- https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/

## Secrets and public repos
Never commit original full backup, certs/key.pem, SSH files, GCP configuration, Codex history, .env, service accounts, access tokens, raw database or private source-site credentials. Do not print secret values in logs. A Git ignore file only prevents new additions; it cannot erase prior commits.

## Before deleting GCP VM or its disk
1. Export the live MySQL database consistently into a protected backup, and test import/recovery in a separate instance. Do not mistake a tarball of home for a full database backup.
2. Snapshot persistent disks and separately inventory any Docker volumes, image-only code, DNS, Cloudflare settings, secrets and static IPs.
3. Verify site/data quality after migration, and decide what happens to the old hostname and Cloudflare DNS.
4. Confirm no other services depend on the VM. Do not delete until recovery has been tested.
5. Review billing for disk, IP and snapshots, which can remain chargeable when the VM is stopped.

## Safe code review
Check diff, inspect commit history and run a secret scanner before merging; automated scanners are not comprehensive. All new routes use local metadata and make zero upstream requests.
