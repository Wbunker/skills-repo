# Cloud DNS — CLI Reference

---

## Managed Zones

```bash
# Create a public zone (internet-facing authoritative DNS)
gcloud dns managed-zones create example-com-zone \
  --dns-name=example.com. \
  --description="Public zone for example.com" \
  --visibility=public

# Create a private zone (VPC-internal)
gcloud dns managed-zones create internal-example-zone \
  --dns-name=internal.example.com. \
  --description="Private zone for internal services" \
  --visibility=private \
  --networks=my-vpc

# Create a private zone associated with multiple VPCs
gcloud dns managed-zones create shared-internal-zone \
  --dns-name=svc.internal. \
  --visibility=private \
  --networks=my-vpc,my-second-vpc

# Create a forwarding zone (forward queries to on-prem DNS)
gcloud dns managed-zones create corp-forwarding-zone \
  --dns-name=corp.example.com. \
  --description="Forward corp.example.com to on-prem DNS" \
  --visibility=private \
  --networks=my-vpc \
  --forwarding-targets=192.168.1.53,192.168.1.54

# Create a peering zone (delegate to another VPC's private zones)
gcloud dns managed-zones create peering-zone \
  --dns-name=services.internal. \
  --visibility=private \
  --networks=my-vpc \
  --target-network=projects/other-project/global/networks/other-vpc

# Create a private zone with DNSSEC enabled
gcloud dns managed-zones create dnssec-public-zone \
  --dns-name=example.com. \
  --visibility=public \
  --dnssec-state=on

# Describe a zone (shows nameservers, creation time, DNSSEC state)
gcloud dns managed-zones describe example-com-zone

# Get just the nameservers for a public zone (to add at registrar)
gcloud dns managed-zones describe example-com-zone \
  --format="value(nameServers)"

# List all managed zones
gcloud dns managed-zones list

# List private zones only
gcloud dns managed-zones list \
  --filter="visibility=private"

# Update a zone (add a VPC network to a private zone)
gcloud dns managed-zones update internal-example-zone \
  --networks=my-vpc,my-new-vpc

# Delete a zone (must have no record sets other than SOA and NS)
gcloud dns managed-zones delete example-com-zone
```

---

## Record Sets (Using Transactions)

The `gcloud dns record-sets transaction` workflow ensures atomic changes to DNS records.

```bash
# --- Basic Workflow ---
# 1. Start a transaction
gcloud dns record-sets transaction start --zone=example-com-zone

# 2. Add records
gcloud dns record-sets transaction add "34.120.1.2" \
  --zone=example-com-zone \
  --name=www.example.com. \
  --ttl=300 \
  --type=A

gcloud dns record-sets transaction add "34.120.1.3" \
  --zone=example-com-zone \
  --name=www.example.com. \
  --ttl=300 \
  --type=A

# 3. Execute (apply the transaction)
gcloud dns record-sets transaction execute --zone=example-com-zone

# --- Remove Records ---
gcloud dns record-sets transaction start --zone=example-com-zone

gcloud dns record-sets transaction remove "34.120.1.2" \
  --zone=example-com-zone \
  --name=www.example.com. \
  --ttl=300 \
  --type=A

gcloud dns record-sets transaction execute --zone=example-com-zone

# Abort a transaction (discard changes)
gcloud dns record-sets transaction abort --zone=example-com-zone

# --- Common Record Types ---

# A record
gcloud dns record-sets transaction add "34.120.5.10" \
  --zone=example-com-zone --name=api.example.com. --ttl=300 --type=A

# AAAA record
gcloud dns record-sets transaction add "2001:db8::1" \
  --zone=example-com-zone --name=www.example.com. --ttl=300 --type=AAAA

# CNAME record
gcloud dns record-sets transaction add "www.example.com." \
  --zone=example-com-zone --name=blog.example.com. --ttl=300 --type=CNAME

# MX records (priority + server)
gcloud dns record-sets transaction add "10 mail.example.com." \
  --zone=example-com-zone --name=example.com. --ttl=3600 --type=MX

gcloud dns record-sets transaction add "20 mail2.example.com." \
  --zone=example-com-zone --name=example.com. --ttl=3600 --type=MX

# TXT records (wrap in quotes; use space-separated for multiple values)
gcloud dns record-sets transaction add '"v=spf1 include:_spf.google.com ~all"' \
  --zone=example-com-zone --name=example.com. --ttl=3600 --type=TXT

# DKIM TXT record (split into 255-char chunks)
gcloud dns record-sets transaction add '"v=DKIM1; k=rsa; p=MIGfMA0GCSq..."' \
  --zone=example-com-zone \
  --name=google._domainkey.example.com. \
  --ttl=3600 \
  --type=TXT

# SRV record
gcloud dns record-sets transaction add "0 5 8080 myservice.example.com." \
  --zone=example-com-zone \
  --name=_http._tcp.example.com. \
  --ttl=300 \
  --type=SRV

# CAA record
gcloud dns record-sets transaction add '0 issue "letsencrypt.org"' \
  --zone=example-com-zone --name=example.com. --ttl=3600 --type=CAA

# NS delegation for subdomain
gcloud dns record-sets transaction add \
  "ns1.sub.example.com." "ns2.sub.example.com." \
  --zone=example-com-zone \
  --name=sub.example.com. \
  --ttl=3600 \
  --type=NS
```

---

## Record Sets (Direct Create/Update)

For simpler operations without transactions:

```bash
# Create a record set directly
gcloud dns record-sets create api.example.com. \
  --zone=example-com-zone \
  --type=A \
  --ttl=300 \
  --rrdatas="34.120.5.10,34.120.5.11"

# Update a record set (replace existing)
gcloud dns record-sets update api.example.com. \
  --zone=example-com-zone \
  --type=A \
  --ttl=300 \
  --rrdatas="34.120.5.20"

# Delete a record set
gcloud dns record-sets delete api.example.com. \
  --zone=example-com-zone \
  --type=A

# List all record sets in a zone
gcloud dns record-sets list --zone=example-com-zone

# List with a specific name filter
gcloud dns record-sets list \
  --zone=example-com-zone \
  --filter="name=www.example.com."

# List with format
gcloud dns record-sets list \
  --zone=example-com-zone \
  --format="table(name,type,ttl,rrdatas)"
```

---

## Import and Export

```bash
# Import records from a BIND zone file
gcloud dns record-sets import zone-file.txt \
  --zone=example-com-zone \
  --zone-file-format

# Import from a YAML/CSV file
gcloud dns record-sets import records.yaml \
  --zone=example-com-zone

# Export all records to a BIND zone file
gcloud dns record-sets export zone-backup.txt \
  --zone=example-com-zone \
  --zone-file-format

# Export to YAML format
gcloud dns record-sets export records.yaml \
  --zone=example-com-zone
```

---

## DNSSEC

```bash
# Activate DNSSEC on a zone
gcloud dns managed-zones update example-com-zone \
  --dnssec-state=on

# Describe DNSSEC status
gcloud dns managed-zones describe example-com-zone \
  --format="yaml(dnssecConfig)"

# Get the DS record (to add to the parent zone/registrar)
gcloud dns dnskeys describe KEY_ID \
  --zone=example-com-zone \
  --format="value(dsRecord)"

# List DNS keys for a zone
gcloud dns dnskeys list --zone=example-com-zone

# Describe a specific DNS key
gcloud dns dnskeys describe KEY_ID --zone=example-com-zone

# Deactivate DNSSEC (remove DS record from registrar FIRST to avoid breakage)
gcloud dns managed-zones update example-com-zone \
  --dnssec-state=off
```

---

## DNS Policies

```bash
# Create an inbound DNS policy (allows on-prem to resolve Cloud DNS private zones)
gcloud dns policies create my-inbound-policy \
  --networks=my-vpc \
  --enable-inbound-forwarding \
  --description="Allow on-prem to query Cloud DNS"

# Create an outbound forwarding policy (forward specific queries to on-prem)
gcloud dns policies create my-outbound-policy \
  --networks=my-vpc \
  --alternative-name-servers=192.168.1.53,192.168.1.54 \
  --description="Forward to on-prem DNS"

# List DNS policies
gcloud dns policies list

# Describe a DNS policy
gcloud dns policies describe my-inbound-policy

# Update a policy
gcloud dns policies update my-inbound-policy \
  --networks=my-vpc,my-second-vpc

# Delete a DNS policy
gcloud dns policies delete my-inbound-policy
```

---

## Response Policy Zones (RPZ)

```bash
# Create a response policy
gcloud dns response-policies create my-response-policy \
  --networks=my-vpc \
  --description="Block malware domains, redirect internal services"

# Add a rule to block a domain (return NXDOMAIN)
gcloud dns response-policies rules create block-malware-domain \
  --response-policy=my-response-policy \
  --dns-name=malware.example.com. \
  --behavior=bypassResponsePolicy

# Note: The behavior flag controls the action:
# --behavior=bypassResponsePolicy  → do NOT apply this policy (pass through)
# For custom responses, use --local-data flag

# Add a rule to return custom A record (redirect)
gcloud dns response-policies rules create redirect-internal \
  --response-policy=my-response-policy \
  --dns-name=legacy-service.example.com. \
  --local-data=name="legacy-service.example.com.",type="A",ttl=60,rrdata="10.10.0.50"

# List response policies
gcloud dns response-policies list

# List rules in a response policy
gcloud dns response-policies rules list \
  --response-policy=my-response-policy

# Delete a response policy rule
gcloud dns response-policies rules delete block-malware-domain \
  --response-policy=my-response-policy

# Delete a response policy
gcloud dns response-policies delete my-response-policy
```

---

## Cloud Domains

```bash
# Search for available domains
gcloud domains registrations search-domains example

# Get pricing for a domain
gcloud domains registrations get-register-parameters example.com

# Register a domain
gcloud domains registrations register example.com \
  --contact-data-from-file=contact.yaml \
  --contact-privacy=private-contact-data \
  --cloud-dns-zone=my-cloud-dns-zone \
  --yearly-price="12.00 USD"

# List registered domains
gcloud domains registrations list

# Describe a domain registration
gcloud domains registrations describe example.com

# Configure DNS for a registered domain
gcloud domains registrations configure dns example.com \
  --cloud-dns-zone=example-com-zone

# Export authorization code (for domain transfer out)
gcloud domains registrations export-authorization-code example.com

# Delete a domain registration (only when expired or explicitly deleted)
gcloud domains registrations delete example.com
```
