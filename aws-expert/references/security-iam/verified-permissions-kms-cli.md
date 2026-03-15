# AWS Verified Permissions & KMS — CLI Reference
For service concepts, see [verified-permissions-kms-capabilities.md](verified-permissions-kms-capabilities.md).

## Amazon Verified Permissions

```bash
# --- Policy stores ---
aws verifiedpermissions create-policy-store \
  --validation-settings Mode=STRICT
aws verifiedpermissions list-policy-stores
aws verifiedpermissions get-policy-store --policy-store-id psEXAMPLEid
aws verifiedpermissions update-policy-store \
  --policy-store-id psEXAMPLEid \
  --validation-settings Mode=OFF
aws verifiedpermissions delete-policy-store --policy-store-id psEXAMPLEid

# --- Schema ---
aws verifiedpermissions put-schema \
  --policy-store-id psEXAMPLEid \
  --definition file://schema.json  # Cedar schema JSON
aws verifiedpermissions get-schema --policy-store-id psEXAMPLEid

# --- Policies ---
aws verifiedpermissions create-policy \
  --policy-store-id psEXAMPLEid \
  --definition Static="{Description=\"Allow premium users\",Statement=\"permit(principal in Group::premium-users, action == Action::ViewPhoto, resource);\"}"
aws verifiedpermissions list-policies --policy-store-id psEXAMPLEid
aws verifiedpermissions get-policy --policy-store-id psEXAMPLEid --policy-id policyId
aws verifiedpermissions update-policy \
  --policy-store-id psEXAMPLEid \
  --policy-id policyId \
  --definition Static="{Statement=\"permit(principal in Group::premium-users, action, resource);\"}"
aws verifiedpermissions delete-policy --policy-store-id psEXAMPLEid --policy-id policyId

# --- Policy templates ---
aws verifiedpermissions create-policy-template \
  --policy-store-id psEXAMPLEid \
  --description "Share with specific user" \
  --statement "permit(principal == ?principal, action == Action::ViewPhoto, resource == ?resource);"
aws verifiedpermissions list-policy-templates --policy-store-id psEXAMPLEid
aws verifiedpermissions get-policy-template --policy-store-id psEXAMPLEid --policy-template-id templateId
aws verifiedpermissions create-policy \
  --policy-store-id psEXAMPLEid \
  --definition TemplateLinked="{PolicyTemplateId=templateId,Principal={EntityType=User,EntityId=alice},Resource={EntityType=Photo,EntityId=photo123}}"
aws verifiedpermissions delete-policy-template --policy-store-id psEXAMPLEid --policy-template-id templateId

# --- Authorization ---
aws verifiedpermissions is-authorized \
  --policy-store-id psEXAMPLEid \
  --principal EntityType=User,EntityId=alice \
  --action ActionType=Action,ActionId=ViewPhoto \
  --resource EntityType=Photo,EntityId=photo123
# Response: {"Decision": "ALLOW", "Errors": []}

aws verifiedpermissions is-authorized-with-token \
  --policy-store-id psEXAMPLEid \
  --access-token "$ACCESS_TOKEN" \
  --action ActionType=Action,ActionId=ViewPhoto \
  --resource EntityType=Photo,EntityId=photo123
```

---

## AWS KMS

```bash
# --- Key management ---
aws kms create-key \
  --description "My application encryption key" \
  --key-usage ENCRYPT_DECRYPT \
  --origin AWS_KMS \
  --policy file://key-policy.json \
  --tags TagKey=Environment,TagValue=Production
aws kms list-keys
aws kms describe-key --key-id alias/my-key  # can use alias, key ID, or ARN
aws kms get-key-policy --key-id alias/my-key --policy-name default
aws kms put-key-policy --key-id alias/my-key --policy-name default --policy file://updated-policy.json

# Key rotation
aws kms enable-key-rotation --key-id alias/my-key
aws kms disable-key-rotation --key-id alias/my-key
aws kms get-key-rotation-status --key-id alias/my-key
aws kms rotate-key-on-demand --key-id alias/my-key  # immediate manual rotation

# Enable/disable/schedule deletion
aws kms enable-key --key-id key-id
aws kms disable-key --key-id key-id
aws kms schedule-key-deletion --key-id key-id --pending-window-in-days 30  # 7-30 days
aws kms cancel-key-deletion --key-id key-id

# --- Aliases ---
aws kms create-alias --alias-name alias/my-key --target-key-id key-id
aws kms list-aliases
aws kms list-aliases --key-id key-id
aws kms update-alias --alias-name alias/my-key --target-key-id new-key-id
aws kms delete-alias --alias-name alias/my-key

# --- Encrypt / Decrypt ---
aws kms encrypt \
  --key-id alias/my-key \
  --plaintext fileb://secret.txt \
  --output text --query CiphertextBlob | base64 -d > secret.enc

aws kms decrypt \
  --ciphertext-blob fileb://secret.enc \
  --output text --query Plaintext | base64 -d

aws kms re-encrypt \
  --ciphertext-blob fileb://old.enc \
  --destination-key-id alias/new-key \
  --output text --query CiphertextBlob | base64 -d > new.enc

# --- Data keys (envelope encryption) ---
aws kms generate-data-key \
  --key-id alias/my-key \
  --key-spec AES_256
  # Returns: {CiphertextBlob, Plaintext, KeyId}
  # Use Plaintext to encrypt data, store CiphertextBlob alongside encrypted data
  # Discard Plaintext from memory after encrypting

aws kms generate-data-key-without-plaintext \
  --key-id alias/my-key \
  --key-spec AES_256
  # For pre-generating encrypted data keys without decrypting them yet

# --- Grants ---
aws kms create-grant \
  --key-id alias/my-key \
  --grantee-principal arn:aws:iam::123456789012:role/MyServiceRole \
  --operations Decrypt GenerateDataKey
aws kms list-grants --key-id alias/my-key
aws kms retire-grant --key-id alias/my-key --grant-id grant-id
aws kms revoke-grant --key-id alias/my-key --grant-id grant-id

# --- Multi-region keys ---
aws kms replicate-key \
  --key-id arn:aws:kms:us-east-1:123456789012:key/mrk-xxx \
  --replica-region us-west-2
aws kms update-primary-region \
  --key-id arn:aws:kms:us-east-1:123456789012:key/mrk-xxx \
  --primary-region us-west-2

# --- Asymmetric keys ---
aws kms create-key --key-usage SIGN_VERIFY --key-spec RSA_2048
aws kms sign \
  --key-id key-id \
  --message fileb://message.txt \
  --message-type RAW \
  --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 \
  --output text --query Signature | base64 -d > signature.bin
aws kms verify \
  --key-id key-id \
  --message fileb://message.txt \
  --message-type RAW \
  --signing-algorithm RSASSA_PKCS1_V1_5_SHA_256 \
  --signature fileb://signature.bin
aws kms get-public-key --key-id key-id  # export public key for verification outside AWS
```
