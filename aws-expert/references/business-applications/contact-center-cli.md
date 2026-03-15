# AWS Contact Center — CLI Reference

For service concepts, see [contact-center-capabilities.md](contact-center-capabilities.md).

## Amazon Connect

```bash
# --- Instance management ---
aws connect create-instance \
  --identity-management-type CONNECT_MANAGED \
  --inbound-calls-enabled \
  --outbound-calls-enabled \
  --instance-alias my-contact-center

aws connect describe-instance --instance-id abc12345-1234-1234-1234-abc123456789
aws connect list-instances
aws connect delete-instance --instance-id abc12345-1234-1234-1234-abc123456789

# Associate approved origin for the CCP widget
aws connect associate-approved-origin \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --origin https://myapp.example.com

aws connect list-approved-origins --instance-id abc12345-1234-1234-1234-abc123456789

# --- Contact flows ---
aws connect create-contact-flow \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --name "Main IVR Flow" \
  --type CONTACT_FLOW \
  --content file://flow-content.json

aws connect describe-contact-flow \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --contact-flow-id flow-id-12345

aws connect list-contact-flows \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --contact-flow-types CONTACT_FLOW CUSTOMER_QUEUE

aws connect update-contact-flow-content \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --contact-flow-id flow-id-12345 \
  --content file://updated-flow.json

aws connect update-contact-flow-name \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --contact-flow-id flow-id-12345 \
  --name "Updated IVR Flow" \
  --description "Updated main IVR"

# --- Queues ---
aws connect create-queue \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --name "Support Queue" \
  --hours-of-operation-id hoo-id-12345 \
  --max-contacts 100

aws connect describe-queue \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --queue-id queue-id-12345

aws connect list-queues \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --queue-types STANDARD

aws connect update-queue-name \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --queue-id queue-id-12345 \
  --name "Tier 1 Support Queue"

aws connect update-queue-max-contacts \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --queue-id queue-id-12345 \
  --max-contacts 200

aws connect update-queue-hours-of-operation \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --queue-id queue-id-12345 \
  --hours-of-operation-id hoo-id-67890

# --- Routing profiles ---
aws connect create-routing-profile \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --name "Tier1 Agents" \
  --description "Routing profile for tier 1 support agents" \
  --default-outbound-queue-id queue-id-12345 \
  --media-concurrencies '[
    {"Channel": "VOICE", "Concurrency": 1},
    {"Channel": "CHAT", "Concurrency": 3},
    {"Channel": "TASK", "Concurrency": 5}
  ]' \
  --queue-configs '[
    {
      "QueueReference": {"QueueId": "queue-id-12345", "Channel": "VOICE"},
      "Priority": 1,
      "Delay": 0
    }
  ]'

aws connect describe-routing-profile \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --routing-profile-id rp-id-12345

aws connect list-routing-profiles \
  --instance-id abc12345-1234-1234-1234-abc123456789

aws connect update-routing-profile-queues \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --routing-profile-id rp-id-12345 \
  --queue-configs '[
    {"QueueReference": {"QueueId": "queue-id-67890", "Channel": "CHAT"}, "Priority": 2, "Delay": 30}
  ]'

# --- Users (agents) ---
aws connect create-user \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --username jsmith \
  --password 'TempP@ssw0rd!' \
  --identity-info '{"FirstName": "John", "LastName": "Smith", "Email": "jsmith@example.com"}' \
  --phone-config '{"PhoneType": "SOFT_PHONE", "AutoAccept": false, "AfterContactWorkTimeLimit": 30}' \
  --routing-profile-id rp-id-12345 \
  --security-profile-ids sp-id-12345

aws connect describe-user \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --user-id user-id-12345

aws connect list-users --instance-id abc12345-1234-1234-1234-abc123456789

aws connect update-user-routing-profile \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --user-id user-id-12345 \
  --routing-profile-id rp-id-67890

aws connect update-user-phone-config \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --user-id user-id-12345 \
  --phone-config '{"PhoneType": "DESK_PHONE", "DeskPhoneNumber": "+15551234567", "AutoAccept": true, "AfterContactWorkTimeLimit": 60}'

aws connect delete-user \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --user-id user-id-12345

# --- User hierarchy (org chart for reporting) ---
aws connect create-user-hierarchy-group \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --name "Americas Support" \
  --parent-group-id group-id-root

aws connect describe-user-hierarchy-group \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --hierarchy-group-id group-id-12345

aws connect list-user-hierarchy-groups \
  --instance-id abc12345-1234-1234-1234-abc123456789

aws connect update-user-hierarchy \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --user-id user-id-12345 \
  --hierarchy-group-id group-id-12345

# --- Hours of operation ---
aws connect create-hours-of-operation \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --name "Business Hours 9-5 ET" \
  --time-zone "America/New_York" \
  --config '[
    {"Day": "MONDAY", "StartTime": {"Hours": 9, "Minutes": 0}, "EndTime": {"Hours": 17, "Minutes": 0}},
    {"Day": "TUESDAY", "StartTime": {"Hours": 9, "Minutes": 0}, "EndTime": {"Hours": 17, "Minutes": 0}},
    {"Day": "WEDNESDAY", "StartTime": {"Hours": 9, "Minutes": 0}, "EndTime": {"Hours": 17, "Minutes": 0}},
    {"Day": "THURSDAY", "StartTime": {"Hours": 9, "Minutes": 0}, "EndTime": {"Hours": 17, "Minutes": 0}},
    {"Day": "FRIDAY", "StartTime": {"Hours": 9, "Minutes": 0}, "EndTime": {"Hours": 17, "Minutes": 0}}
  ]'

aws connect list-hours-of-operations \
  --instance-id abc12345-1234-1234-1234-abc123456789

# --- Phone numbers ---
aws connect search-available-phone-numbers \
  --target-arn arn:aws:connect:us-east-1:123456789012:instance/abc12345 \
  --phone-number-country-code US \
  --phone-number-type TOLL_FREE

aws connect claim-phone-number \
  --target-arn arn:aws:connect:us-east-1:123456789012:instance/abc12345 \
  --phone-number "+18005551234" \
  --phone-number-description "Main support line"

aws connect associate-phone-number-contact-flow \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --phone-number-id pn-id-12345 \
  --contact-flow-id flow-id-12345

aws connect list-phone-numbers-v2 \
  --target-arn arn:aws:connect:us-east-1:123456789012:instance/abc12345

aws connect release-phone-number --phone-number-id pn-id-12345

# --- Contact attributes ---
aws connect update-contact-attributes \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --initial-contact-id contact-id-12345 \
  --attributes '{"CustomerTier": "Gold", "OrderId": "ORD-987654"}'

aws connect get-contact-attributes \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --initial-contact-id contact-id-12345

# --- Contact Lens rules ---
aws connect create-rule \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --name "Escalation Keywords" \
  --trigger-event-source '{"EventSourceName": "OnPostCallAnalysisAvailable"}' \
  --function 'expression using Contact Lens rule language' \
  --actions '[{"ActionType": "CREATE_TASK", "TaskAction": {"Name": "Escalation task", "ContactFlowId": "flow-id"}}]' \
  --publish-status PUBLISHED

aws connect list-rules \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --event-source-name OnPostCallAnalysisAvailable

aws connect describe-rule \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --rule-id rule-id-12345

aws connect update-rule \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --rule-id rule-id-12345 \
  --name "Updated Escalation Rule" \
  --function 'updated expression' \
  --actions '[]' \
  --publish-status PUBLISHED

aws connect delete-rule \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --rule-id rule-id-12345

# --- Integration associations (Lambda, Lex, etc.) ---
aws connect create-integration-association \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --integration-type LAMBDA_FUNCTION \
  --integration-arn arn:aws:lambda:us-east-1:123456789012:function:my-connect-function

aws connect list-integration-associations \
  --instance-id abc12345-1234-1234-1234-abc123456789

aws connect delete-integration-association \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --integration-association-id assoc-id-12345

# Associate a Lex bot
aws connect associate-lex-bot \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --lex-bot '{"Name": "MyOrderBot", "LexRegion": "us-east-1"}'

# --- Vocabularies (custom terminology for transcription) ---
aws connect create-vocabulary \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --vocabulary-name "ProductTerms" \
  --language-code en-US \
  --content "Phrase\nMyProductName\nAnotherTerm"

aws connect list-default-vocabularies \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --language-code en-US

aws connect associate-default-vocabulary \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --language-code en-US \
  --vocabulary-id vocab-id-12345

# --- Security profiles ---
aws connect create-security-profile \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --security-profile-name "Agent Basic" \
  --permissions '["BasicAgentAccess", "OutboundCallAccess"]'

aws connect list-security-profiles \
  --instance-id abc12345-1234-1234-1234-abc123456789

# --- Metrics ---
aws connect get-current-metric-data \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --filters '{"Queues": ["queue-id-12345"], "Channels": ["VOICE"]}' \
  --current-metrics '[
    {"Name": "CONTACTS_IN_QUEUE", "Unit": "COUNT"},
    {"Name": "AGENTS_AVAILABLE", "Unit": "COUNT"},
    {"Name": "AGENTS_ON_CALL", "Unit": "COUNT"}
  ]'

aws connect get-metric-data \
  --instance-id abc12345-1234-1234-1234-abc123456789 \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --filters '{"Queues": ["queue-id-12345"], "Channels": ["VOICE"]}' \
  --groupings QUEUE \
  --historical-metrics '[
    {"Name": "CONTACTS_HANDLED", "Unit": "COUNT", "Statistic": "SUM"},
    {"Name": "HANDLE_TIME", "Unit": "SECONDS", "Statistic": "AVG"}
  ]'

# --- Tagging ---
aws connect tag-resource \
  --resource-arn arn:aws:connect:us-east-1:123456789012:instance/abc12345 \
  --tags Environment=prod Team=cx
```
