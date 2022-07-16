#!/usr/bin/env sh

export LND_MACAROON_HEX="$(xxd -p -c 1000 /lnd/data/chain/bitcoin/mainnet/admin.macaroon)"
export LND_CERT_HEX="$(xxd -p -c 1000 /lnd/tls.cert)"

/bin/lndhub
