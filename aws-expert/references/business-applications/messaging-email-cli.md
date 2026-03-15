# AWS Messaging & Email — CLI Reference

For service concepts, see [messaging-email-capabilities.md](messaging-email-capabilities.md).

## Amazon SES v2

```bash
# --- Email identities ---
# Create domain identity
aws sesv2 create-email-identity --email-identity example.com

# Create email address identity
aws sesv2 create-email-identity --email-identity noreply@example.com

# Get identity details (check verification status, DKIM records)
aws sesv2 get-email-identity --email-identity example.com

# List identities
aws sesv2 list-email-identities

# Enable DKIM signing for a domain identity
aws sesv2 put-email-identity-dkim-signing-attributes \
  --email-identity example.com \
  --signing-attributes-origin AWS_SES

# BYODKIM configuration
aws sesv2 put-email-identity-dkim-signing-attributes \
  --email-identity example.com \
  --signing-attributes-origin EXTERNAL \
  --signing-attributes '{
    "DomainSigningSelector": "selector1",
    "DomainSigningPrivateKey": "-----BEGIN RSA PRIVATE KEY-----\n..."
  }'

# Set custom MAIL FROM domain
aws sesv2 put-email-identity-mail-from-attributes \
  --email-identity example.com \
  --mail-from-domain bounce.example.com \
  --behavior-on-mx-failure USE_DEFAULT_VALUE

# Delete identity
aws sesv2 delete-email-identity --email-identity example.com

# --- Configuration sets ---
aws sesv2 create-configuration-set \
  --configuration-set-name my-transactional \
  --tracking-options '{"CustomRedirectDomain": "click.example.com"}' \
  --sending-options '{"SendingEnabled": true}' \
  --suppression-options '{"SuppressedReasons": ["BOUNCE", "COMPLAINT"]}'

aws sesv2 get-configuration-set --configuration-set-name my-transactional

aws sesv2 list-configuration-sets

# Add event destination to configuration set
aws sesv2 create-configuration-set-event-destination \
  --configuration-set-name my-transactional \
  --event-destination-name send-to-sns \
  --event-destination '{
    "Enabled": true,
    "MatchingEventTypes": ["SEND", "DELIVERY", "BOUNCE", "COMPLAINT", "OPEN", "CLICK"],
    "SnsDestination": {
      "TopicArn": "arn:aws:sns:us-east-1:123456789012:ses-events"
    }
  }'

# Kinesis Firehose event destination
aws sesv2 create-configuration-set-event-destination \
  --configuration-set-name my-transactional \
  --event-destination-name send-to-firehose \
  --event-destination '{
    "Enabled": true,
    "MatchingEventTypes": ["SEND", "DELIVERY", "BOUNCE"],
    "KinesisFirehoseDestination": {
      "IamRoleArn": "arn:aws:iam::123456789012:role/SESFirehoseRole",
      "DeliveryStreamArn": "arn:aws:firehose:us-east-1:123456789012:deliverystream/ses-events"
    }
  }'

aws sesv2 delete-configuration-set --configuration-set-name my-transactional

# --- Sending email ---
# Simple send
aws sesv2 send-email \
  --from-email-address "sender@example.com" \
  --destination '{"ToAddresses": ["recipient@example.com"]}' \
  --content '{
    "Simple": {
      "Subject": {"Data": "Hello from SES"},
      "Body": {
        "Text": {"Data": "Plain text body"},
        "Html": {"Data": "<h1>HTML body</h1>"}
      }
    }
  }' \
  --configuration-set-name my-transactional

# Send with template
aws sesv2 send-email \
  --from-email-address "sender@example.com" \
  --destination '{"ToAddresses": ["customer@example.com"]}' \
  --content '{
    "Template": {
      "TemplateName": "OrderConfirmation",
      "TemplateData": "{\"order_id\": \"12345\", \"customer_name\": \"Alice\"}"
    }
  }'

# Bulk send with template
aws sesv2 send-bulk-email \
  --from-email-address "sender@example.com" \
  --default-content '{
    "Template": {
      "TemplateName": "OrderConfirmation",
      "TemplateData": "{}"
    }
  }' \
  --bulk-email-entries '[
    {
      "Destination": {"ToAddresses": ["alice@example.com"]},
      "ReplacementEmailContent": {
        "ReplacementTemplate": {
          "ReplacementTemplateData": "{\"customer_name\": \"Alice\", \"order_id\": \"123\"}"
        }
      }
    },
    {
      "Destination": {"ToAddresses": ["bob@example.com"]},
      "ReplacementEmailContent": {
        "ReplacementTemplate": {
          "ReplacementTemplateData": "{\"customer_name\": \"Bob\", \"order_id\": \"456\"}"
        }
      }
    }
  ]'

# --- Templates ---
aws sesv2 create-email-template \
  --template-name OrderConfirmation \
  --template-content '{
    "Subject": "Your order {{order_id}} is confirmed",
    "Text": "Hi {{customer_name}}, your order is confirmed.",
    "Html": "<h1>Hi {{customer_name}}</h1><p>Order {{order_id}} confirmed.</p>"
  }'

aws sesv2 get-email-template --template-name OrderConfirmation

aws sesv2 list-email-templates

aws sesv2 update-email-template \
  --template-name OrderConfirmation \
  --template-content '{
    "Subject": "Order {{order_id}} confirmed - Thank you!",
    "Html": "<h1>Thank you {{customer_name}}!</h1>"
  }'

aws sesv2 delete-email-template --template-name OrderConfirmation

# --- Suppression list ---
aws sesv2 put-suppressed-destination \
  --email-address bounced@example.com \
  --reason BOUNCE

aws sesv2 get-suppressed-destination --email-address bounced@example.com

aws sesv2 list-suppressed-destinations \
  --reasons BOUNCE COMPLAINT \
  --start-date 2024-01-01T00:00:00Z

aws sesv2 delete-suppressed-destination --email-address bounced@example.com

# --- Dedicated IPs ---
aws sesv2 list-dedicated-ip-addresses \
  --pool-name my-dedicated-pool

aws sesv2 create-dedicated-ip-pool \
  --pool-name my-dedicated-pool \
  --scaling-mode STANDARD

aws sesv2 put-dedicated-ip-in-pool \
  --ip 203.0.113.45 \
  --destination-pool-name my-dedicated-pool

# --- Account-level settings ---
aws sesv2 get-account

aws sesv2 put-account-sending-attributes \
  --sending-enabled

aws sesv2 put-account-suppression-attributes \
  --suppressed-reasons BOUNCE COMPLAINT

# --- Contact lists (subscription management) ---
aws sesv2 create-contact-list \
  --contact-list-name newsletter \
  --topics '[
    {
      "TopicName": "product-updates",
      "DisplayName": "Product Updates",
      "Description": "News about our product",
      "DefaultSubscriptionStatus": "OPT_IN"
    }
  ]'

aws sesv2 create-contact \
  --contact-list-name newsletter \
  --email-address subscriber@example.com \
  --topic-preferences '[{"TopicName": "product-updates", "SubscriptionStatus": "OPT_IN"}]'

aws sesv2 list-contacts --contact-list-name newsletter

aws sesv2 get-contact \
  --contact-list-name newsletter \
  --email-address subscriber@example.com

# --- Sending statistics ---
aws sesv2 get-send-statistics
aws sesv2 get-sending-quota
```

---

## Amazon Pinpoint

```bash
# --- Projects (apps) ---
aws pinpoint create-app \
  --create-application-request '{"Name": "MyCustomerEngagement"}'

aws pinpoint get-app --application-id abc123def456

aws pinpoint get-apps

aws pinpoint delete-app --application-id abc123def456

# --- Segments ---
# Create dynamic segment
aws pinpoint create-segment \
  --application-id abc123def456 \
  --write-segment-request '{
    "Name": "High Value Customers",
    "Dimensions": {
      "Attributes": {
        "CustomerTier": {
          "AttributeType": "INCLUSIVE",
          "Values": ["Gold", "Platinum"]
        }
      },
      "UserAttributes": {},
      "Demographic": {
        "Channel": {
          "DimensionType": "INCLUSIVE",
          "Values": ["EMAIL"]
        }
      }
    }
  }'

aws pinpoint get-segment \
  --application-id abc123def456 \
  --segment-id seg-id-12345

aws pinpoint get-segments --application-id abc123def456

# Import a segment from S3
aws pinpoint create-import-job \
  --application-id abc123def456 \
  --import-job-request '{
    "Format": "CSV",
    "RoleArn": "arn:aws:iam::123456789012:role/PinpointImportRole",
    "S3Url": "s3://my-bucket/segments/customers.csv",
    "RegisterEndpoints": true,
    "DefineSegment": true,
    "SegmentName": "ImportedCustomers"
  }'

# --- Campaigns ---
aws pinpoint create-campaign \
  --application-id abc123def456 \
  --write-campaign-request '{
    "Name": "Spring Sale Email",
    "SegmentId": "seg-id-12345",
    "MessageConfiguration": {
      "EmailMessage": {
        "FromAddress": "promos@example.com",
        "HtmlBody": "<h1>Spring Sale! 20% off everything.</h1>",
        "Title": "Spring Sale"
      }
    },
    "Schedule": {
      "StartTime": "2024-03-01T10:00:00Z",
      "Timezone": "America/New_York",
      "Frequency": "ONCE"
    }
  }'

aws pinpoint get-campaign \
  --application-id abc123def456 \
  --campaign-id cmp-id-12345

aws pinpoint get-campaigns --application-id abc123def456

aws pinpoint update-campaign \
  --application-id abc123def456 \
  --campaign-id cmp-id-12345 \
  --write-campaign-request '{"Name": "Spring Sale Email v2"}'

aws pinpoint delete-campaign \
  --application-id abc123def456 \
  --campaign-id cmp-id-12345

# --- Journeys ---
aws pinpoint create-journey \
  --application-id abc123def456 \
  --write-journey-request '{
    "Name": "Onboarding Journey",
    "StartActivity": "activity-start",
    "Activities": {
      "activity-start": {
        "Description": "Welcome email",
        "EMAIL": {
          "MessageConfig": {"FromAddress": "welcome@example.com"},
          "NextActivity": "activity-wait",
          "TemplateName": "WelcomeEmail"
        }
      },
      "activity-wait": {
        "Wait": {"WaitTime": {"WaitFor": "P3D"}, "NextActivity": "activity-followup"}
      }
    },
    "State": "DRAFT"
  }'

aws pinpoint get-journey \
  --application-id abc123def456 \
  --journey-id jrn-id-12345

aws pinpoint list-journeys --application-id abc123def456

# Update journey state
aws pinpoint update-journey-state \
  --application-id abc123def456 \
  --journey-id jrn-id-12345 \
  --journey-state-request '{"State": "ACTIVE"}'

# --- Endpoints ---
# Create/update an endpoint
aws pinpoint update-endpoint \
  --application-id abc123def456 \
  --endpoint-id endpoint-user123-email \
  --endpoint-request '{
    "Address": "user@example.com",
    "ChannelType": "EMAIL",
    "User": {"UserId": "user-123"},
    "Attributes": {
      "CustomerTier": ["Gold"],
      "LastPurchasedCategory": ["Electronics"]
    },
    "Demographic": {
      "AppVersion": "2.1.0",
      "Locale": "en_US",
      "Timezone": "America/New_York"
    },
    "OptOut": "NONE"
  }'

aws pinpoint get-endpoint \
  --application-id abc123def456 \
  --endpoint-id endpoint-user123-email

# Batch update endpoints
aws pinpoint update-endpoints-batch \
  --application-id abc123def456 \
  --endpoint-batch-request '{
    "Item": [
      {"Id": "ep1", "Address": "a@example.com", "ChannelType": "EMAIL"},
      {"Id": "ep2", "Address": "+15551234567", "ChannelType": "SMS"}
    ]
  }'

# --- Send messages (transactional) ---
aws pinpoint send-messages \
  --application-id abc123def456 \
  --message-request '{
    "Addresses": {
      "user@example.com": {"ChannelType": "EMAIL"}
    },
    "MessageConfiguration": {
      "EmailMessage": {
        "FromAddress": "noreply@example.com",
        "SimpleEmail": {
          "Subject": {"Data": "Your receipt"},
          "HtmlPart": {"Data": "<p>Thank you for your order.</p>"},
          "TextPart": {"Data": "Thank you for your order."}
        }
      }
    }
  }'

# Transactional SMS
aws pinpoint send-messages \
  --application-id abc123def456 \
  --message-request '{
    "Addresses": {
      "+15551234567": {"ChannelType": "SMS"}
    },
    "MessageConfiguration": {
      "SMSMessage": {
        "Body": "Your OTP is 123456. Valid for 10 minutes.",
        "MessageType": "TRANSACTIONAL",
        "OriginationNumber": "+18005551234"
      }
    }
  }'

# Send OTP
aws pinpoint send-otp-message \
  --application-id abc123def456 \
  --send-otp-message-request-parameters '{
    "BrandName": "MyApp",
    "Channel": "SMS",
    "DestinationIdentity": "+15551234567",
    "OriginationIdentity": "+18005551234",
    "ReferenceId": "session-abc123",
    "ValidityPeriod": 10
  }'

aws pinpoint verify-otp-message \
  --application-id abc123def456 \
  --verify-otp-message-request-parameters '{
    "DestinationIdentity": "+15551234567",
    "Otp": "123456",
    "ReferenceId": "session-abc123"
  }'

# --- Templates ---
aws pinpoint create-email-template \
  --template-name WelcomeEmail \
  --email-template-request '{
    "Subject": "Welcome to {{BrandName}}!",
    "HtmlPart": "<h1>Welcome {{User.UserAttributes.FirstName}}!</h1>",
    "TextPart": "Welcome to {{BrandName}}!"
  }'

aws pinpoint get-email-template --template-name WelcomeEmail

aws pinpoint list-templates

# --- Analytics ---
aws pinpoint get-campaign-activities \
  --application-id abc123def456 \
  --campaign-id cmp-id-12345

aws pinpoint get-campaign-date-range-kpi \
  --application-id abc123def456 \
  --campaign-id cmp-id-12345 \
  --kpi-name email-open-rate \
  --start-time 2024-03-01T00:00:00Z \
  --end-time 2024-03-31T23:59:59Z

aws pinpoint get-journey-execution-metrics \
  --application-id abc123def456 \
  --journey-id jrn-id-12345
```

---

## Amazon Chime SDK

```bash
# --- Meetings ---
aws chime-sdk-meetings create-meeting \
  --client-request-token "$(uuidgen)" \
  --media-region us-east-1 \
  --external-meeting-id "meeting-2024-conf-1"

aws chime-sdk-meetings get-meeting --meeting-id meet-id-12345

aws chime-sdk-meetings list-meetings

# Add attendees
aws chime-sdk-meetings create-attendee \
  --meeting-id meet-id-12345 \
  --external-user-id user-123

# Batch create attendees
aws chime-sdk-meetings batch-create-attendee \
  --meeting-id meet-id-12345 \
  --attendees '[
    {"ExternalUserId": "user-123"},
    {"ExternalUserId": "user-456"}
  ]'

aws chime-sdk-meetings list-attendees --meeting-id meet-id-12345

aws chime-sdk-meetings delete-meeting --meeting-id meet-id-12345

# --- Media pipelines ---
aws chime-sdk-media-pipelines create-media-capture-pipeline \
  --source-type ChimeSdkMeeting \
  --source-arn arn:aws:chime::123456789012:meeting/meet-id-12345 \
  --sink-type S3Bucket \
  --sink-arn arn:aws:s3:::my-recordings-bucket \
  --client-request-token "$(uuidgen)"

aws chime-sdk-media-pipelines get-media-capture-pipeline \
  --media-pipeline-id pipeline-id-12345

aws chime-sdk-media-pipelines list-media-capture-pipelines

aws chime-sdk-media-pipelines delete-media-capture-pipeline \
  --media-pipeline-id pipeline-id-12345

# --- Messaging ---
# Create app instance
aws chime-sdk-messaging create-app-instance \
  --name MyMessagingApp \
  --client-request-token "$(uuidgen)"

aws chime-sdk-messaging describe-app-instance \
  --app-instance-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345

# Create user in app instance
aws chime-sdk-messaging create-app-instance-user \
  --app-instance-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345 \
  --app-instance-user-id user-123 \
  --name "Alice" \
  --client-request-token "$(uuidgen)"

# Create a channel
aws chime-sdk-messaging create-channel \
  --app-instance-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345 \
  --name "Support Chat" \
  --mode UNRESTRICTED \
  --privacy PUBLIC \
  --chime-bearer arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/user/user-123 \
  --client-request-token "$(uuidgen)"

# Send a message
aws chime-sdk-messaging send-channel-message \
  --channel-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/channel/ch-id-12345 \
  --content "Hello, how can I help you?" \
  --type STANDARD \
  --persistence PERSISTENT \
  --chime-bearer arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/user/user-123 \
  --client-request-token "$(uuidgen)"

aws chime-sdk-messaging list-channel-messages \
  --channel-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/channel/ch-id-12345 \
  --chime-bearer arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/user/user-123

# --- Voice (Chime SDK Voice) ---
# Create voice connector
aws chime-sdk-voice create-voice-connector \
  --name MyVoiceConnector \
  --aws-region us-east-1 \
  --require-encryption

aws chime-sdk-voice get-voice-connector \
  --voice-connector-id vc-id-12345

aws chime-sdk-voice list-voice-connectors

# Create SIP media application
aws chime-sdk-voice create-sip-media-application \
  --aws-region us-east-1 \
  --name MyCallControlApp \
  --endpoints '[{"LambdaArn": "arn:aws:lambda:us-east-1:123456789012:function:my-sip-handler"}]'

# Create SIP rule
aws chime-sdk-voice create-sip-rule \
  --name "Route inbound calls" \
  --trigger-type ToPhoneNumber \
  --trigger-value "+18005551234" \
  --target-applications '[
    {
      "SipMediaApplicationId": "sma-id-12345",
      "Priority": 1,
      "AwsRegion": "us-east-1"
    }
  ]'

aws chime-sdk-voice list-sip-media-applications
aws chime-sdk-voice list-sip-rules
```

---

## Amazon Chime

```bash
# --- Meetings ---
aws chime create-meeting \
  --client-request-token "$(uuidgen)" \
  --media-region us-east-1 \
  --external-meeting-id "meeting-2024-conf-1"

aws chime delete-meeting --meeting-id meet-id-12345

# Add an attendee
aws chime create-attendee \
  --meeting-id meet-id-12345 \
  --external-user-id user-123

aws chime list-attendees --meeting-id meet-id-12345

# --- Messaging ---
# Create an app instance (messaging container)
aws chime create-app-instance \
  --name MyMessagingApp \
  --client-request-token "$(uuidgen)"

# Create a user within the app instance
aws chime create-app-instance-user \
  --app-instance-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345 \
  --app-instance-user-id user-123 \
  --name "Alice" \
  --client-request-token "$(uuidgen)"

# Create a channel
aws chime create-channel \
  --app-instance-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345 \
  --name "Support Chat" \
  --mode UNRESTRICTED \
  --privacy PUBLIC \
  --chime-bearer arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/user/user-123 \
  --client-request-token "$(uuidgen)"

aws chime list-channels \
  --app-instance-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345 \
  --chime-bearer arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/user/user-123

# Send a channel message
aws chime send-channel-message \
  --channel-arn arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/channel/ch-id-12345 \
  --content "Hello, how can I help you?" \
  --type STANDARD \
  --persistence PERSISTENT \
  --chime-bearer arn:aws:chime:us-east-1:123456789012:app-instance/ai-id-12345/user/user-123 \
  --client-request-token "$(uuidgen)"

# --- Voice Connector ---
# Create a Voice Connector for SIP trunking
aws chime create-voice-connector \
  --name MyVoiceConnector \
  --aws-region us-east-1 \
  --require-encryption

# Configure PSTN origination (inbound SIP trunks)
aws chime put-voice-connector-origination \
  --voice-connector-id vc-id-12345 \
  --origination '{
    "Routes": [
      {
        "Host": "203.0.113.10",
        "Port": 5060,
        "Protocol": "UDP",
        "Priority": 1,
        "Weight": 1
      }
    ],
    "Disabled": false
  }'

# Configure PSTN termination (outbound SIP trunks)
aws chime put-voice-connector-termination \
  --voice-connector-id vc-id-12345 \
  --termination '{
    "CpsLimit": 1,
    "CallingRegions": ["US"],
    "CidrAllowedList": ["203.0.113.0/24"],
    "Disabled": false
  }'
```

---

## AWS End User Messaging

```bash
# --- Phone pools ---
# Create a pool grouping origination identities
aws sms-voice create-pool \
  --origination-identity "+18005551234" \
  --iso-country-code US \
  --message-type TRANSACTIONAL

aws sms-voice describe-pools

# Associate an additional origination identity to an existing pool
aws sms-voice associate-origination-identity \
  --pool-id pool-id-12345 \
  --origination-identity "+18005555678" \
  --iso-country-code US

# --- Phone numbers ---
aws sms-voice describe-phone-numbers

# --- Sending messages ---
# Send an SMS
aws sms-voice send-text-message \
  --destination-phone-number "+15551234567" \
  --message-body "Your verification code is 123456. Valid for 10 minutes." \
  --message-type TRANSACTIONAL \
  --origination-identity "+18005551234"

# Send a voice message (text-to-speech)
aws sms-voice send-voice-message \
  --destination-phone-number "+15551234567" \
  --message-voice-body "Hello, your appointment is confirmed for tomorrow at 2 PM." \
  --origination-identity "+18005551234"

# Override spending limit for text messages
aws sms-voice set-text-message-spend-limit-override \
  --monthly-limit 500

# --- Registrations (10DLC) ---
# Create a brand and campaign registration for US 10DLC compliance
aws sms-voice create-registration \
  --registration-type TEN_DLC_REGISTRATION

aws sms-voice describe-registrations

# --- Keywords (two-way SMS) ---
aws sms-voice put-keyword \
  --origination-identity "+18005551234" \
  --keyword "HELP" \
  --keyword-message "Reply STOP to unsubscribe. For support visit example.com/help." \
  --keyword-action AUTOMATIC_RESPONSE

# --- Opt-out management ---
aws sms-voice delete-opt-out-list-name \
  --opt-out-list-name Default

# --- Protect configurations ---
# Create a protect configuration to restrict destinations
aws sms-voice create-protect-configuration

# Override a specific number's rule within a protect configuration
aws sms-voice put-protect-configuration-rule-set-number-override \
  --protect-configuration-id protect-id-12345 \
  --destination-phone-number "+15551234567" \
  --action BLOCK
```
