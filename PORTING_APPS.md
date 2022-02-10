# Porting a docker-compose.yml app to Citadel's app.yml

This guide should help you port your Umbrel app to Citadel's app.yml system.

We'll do that based on the BlueWallet app as an example.

Here's the current docker-compose.yml, this is what we're starting off with.

```yaml
version: "3.7"

services:
  redis:
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    volumes:
      - "${APP_DATA_DIR}/data/redis:/data"
    networks:
      default:
        ipv4_address: "${APP_BLUEWALLET_REDIS_IP}"

  lndhub:
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    ports:
      - "${APP_BLUEWALLET_LNDHUB_PORT}:${APP_BLUEWALLET_LNDHUB_PORT}"
    volumes:
      - "${LND_DATA_DIR}:/lnd:ro"
    environment:
      PORT: "${APP_BLUEWALLET_LNDHUB_PORT}"
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
    networks:
      default:
        ipv4_address: "${APP_BLUEWALLET_LNDHUB_IP}"
```

Porting to Citadel basically means cleaning up that file.

As a first step, we can remove the `networks` section from every container. This is added automatically in Citadel.

```yaml
version: "3.7"

services:
  redis:
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    volumes:
      - "${APP_DATA_DIR}/data/redis:/data"

  lndhub:
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    ports:
      - "${APP_BLUEWALLET_LNDHUB_PORT}:${APP_BLUEWALLET_LNDHUB_PORT}"
    volumes:
      - "${LND_DATA_DIR}:/lnd:ro"
    environment:
      PORT: "${APP_BLUEWALLET_LNDHUB_PORT}"
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
```

Now, we need to set the version to 2 and also turn services into an array. Instead of an object with containername: definition, we have an array of containers with a name property.

```yaml
version: "2"

services:
  - name: redis
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    volumes:
      - "${APP_DATA_DIR}/data/redis:/data"

  - name: lndhub
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    ports:
      - "${APP_BLUEWALLET_LNDHUB_PORT}:${APP_BLUEWALLET_LNDHUB_PORT}"
    volumes:
      - "${LND_DATA_DIR}:/lnd:ro"
    environment:
      PORT: "${APP_BLUEWALLET_LNDHUB_PORT}"
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
```

Now, we need to set permissions for every container. For every service (`bitcoind`, `electrum`, `lnd`) a container accesses, you need to add a permission:

```yaml
version: "2"

services:
  - name: redis
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    volumes:
      - "${APP_DATA_DIR}/data/redis:/data"

  - name: lndhub
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    ports:
      - "${APP_BLUEWALLET_LNDHUB_PORT}:${APP_BLUEWALLET_LNDHUB_PORT}"
    volumes:
      - "${LND_DATA_DIR}:/lnd:ro"
    environment:
      PORT: "${APP_BLUEWALLET_LNDHUB_PORT}"
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
    permissions:
      - lnd
```

If you are mounting the LND data dir on `/lnd`, you can remove the mount. This is automatically added on Citadel.
Mounts with `${APP_DATA_DIR}` can be removed too and added to `data:` without the `${APP_DATA_DIR}`

```yaml
version: "2"

services:
  - name: redis
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    data:
    - data/redis:/data

  - name: lndhub
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    ports:
      - "${APP_BLUEWALLET_LNDHUB_PORT}:${APP_BLUEWALLET_LNDHUB_PORT}"
    environment:
      PORT: "${APP_BLUEWALLET_LNDHUB_PORT}"
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
    permissions:
      - lnd
```

If your app has the port passed as the env var, you can remove the ports directive and make sure the port passed in is `${APP_|APP_NAME|_|CONTAINER|_PORT}` (like `${APP_BLUEWALLET_LNDHUB_PORT}`).

```yaml
version: "2"

services:
  - name: redis
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    data:
    - data/redis:/data

  - name: lndhub
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    environment:
      PORT: "${APP_BLUEWALLET_LNDHUB_PORT}"
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
    permissions:
      - lnd
```

If you app doesn't, you can simple specify `port: theportnumber`

```yaml
version: "2"

services:
  - name: redis
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    data:
    - data/redis:/data

  - name: lndhub
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    port: 3000
    environment:
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
    permissions:
      - lnd
```

But let's get back to the previous version for the next step. The next step is simply to add some metadata for your app and also rename `services` to `containers`.

```yaml
version: "2"

metadata:
  category: Wallet Servers
  name: BlueWallet Lightning
  version: 1.4.1
  tagline: Connect BlueWallet to your Lightning node
  description: >-
    Run BlueWallet in the most private and secure way possible by removing
    3rd parties and connecting it directly to your Citadel's Lightning node.


    You can pair multiple BlueWallet accounts, so your friends and family can pair
    their BlueWallet with your Citadel for a trust-minimized setup.
  developer: BlueWallet
  website: https://lndhub.io
  dependencies:
  - lnd
  repo: https://github.com/BlueWallet/LndHub
  support: https://t.me/bluewallet
  gallery:
  - 1.jpg
  - 2.jpg
  - 3.jpg

containers:
  - name: redis
    image: "redis:6.2.2-buster@sha256:e10f55f92478715698a2cef97c2bbdc48df2a05081edd884938903aa60df6396"
    user: "1000:1000"
    command: "redis-server --requirepass moneyprintergobrrr"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    data:
    - data/redis:/data

  - name: lndhub
    image: "bluewalletorganization/lndhub:v1.4.1@sha256:db673a8d360982984d05f97303e26dc0e5a3eea36ba54d0abdae5bbbeef31d3a"
    user: "1000:1000"
    depends_on: 
        - "redis"
    restart: "on-failure"
    stop_grace_period: "1m"
    init: true
    port: 3000
    environment:
      TOR_URL: "${APP_HIDDEN_SERVICE}"
      LND_CERT_FILE: "/lnd/tls.cert"
      LND_ADMIN_MACAROON_FILE: "/lnd/data/chain/bitcoin/${BITCOIN_NETWORK}/admin.macaroon"
      CONFIG: '{ "rateLimit": 10000, "postRateLimit": 10000, "redis": { "port": 6379, "host": "$APP_BLUEWALLET_REDIS_IP", "family": 4, "password": "moneyprintergobrrr", "db": 0 }, "lnd": { "url": "$LND_IP:$LND_GRPC_PORT", "password": ""}}'
    permissions:
      - lnd
```

Now, you got an app.yml ready. To get it addded to Citadel, submit a PR to this repo: https://github.com/runcitadel/apps
