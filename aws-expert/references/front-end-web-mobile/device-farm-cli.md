# AWS Device Farm — CLI Reference

For service concepts, see [device-farm-capabilities.md](device-farm-capabilities.md).

> **Region note**: Device Farm is only available in `us-west-2`. Always pass `--region us-west-2` or set `AWS_DEFAULT_REGION=us-west-2`.

## Mobile Device Testing — `aws devicefarm`

```bash
# --- Projects ---
aws devicefarm create-project \
  --name "My Mobile App Tests" \
  --default-job-timeout-minutes 60 \
  --region us-west-2

aws devicefarm list-projects --region us-west-2
aws devicefarm get-project \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --region us-west-2

aws devicefarm update-project \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name "Updated Project Name" \
  --default-job-timeout-minutes 90 \
  --region us-west-2

aws devicefarm delete-project \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --region us-west-2

# --- Devices ---
# List all available devices
aws devicefarm list-devices --region us-west-2

# Filter by platform
aws devicefarm list-devices \
  --filters '[{"attribute":"PLATFORM","operator":"EQUALS","values":["ANDROID"]}]' \
  --region us-west-2

# Filter by OS version
aws devicefarm list-devices \
  --filters '[
    {"attribute":"PLATFORM","operator":"EQUALS","values":["IOS"]},
    {"attribute":"OS_VERSION","operator":"GREATER_THAN","values":["16"]}
  ]' \
  --region us-west-2

aws devicefarm get-device \
  --arn arn:aws:devicefarm:us-west-2::device:DEVICE_ARN \
  --region us-west-2

# --- Device Pools ---
# Create a custom device pool
aws devicefarm create-device-pool \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name "Top Android Phones" \
  --rules '[
    {"attribute":"PLATFORM","operator":"EQUALS","values":["ANDROID"]},
    {"attribute":"FORM_FACTOR","operator":"EQUALS","values":["PHONE"]},
    {"attribute":"AVAILABILITY","operator":"EQUALS","values":["HIGHLY_AVAILABLE"]}
  ]' \
  --max-devices 5 \
  --region us-west-2

# Create a device pool with specific device ARNs
aws devicefarm create-device-pool \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name "Specific Devices" \
  --rules '[
    {"attribute":"ARN","operator":"IN","values":[
      "arn:aws:devicefarm:us-west-2::device:DEVICE_ARN_1",
      "arn:aws:devicefarm:us-west-2::device:DEVICE_ARN_2"
    ]}
  ]' \
  --region us-west-2

aws devicefarm list-device-pools \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --type PRIVATE \
  --region us-west-2

# Also list curated (AWS-managed) pools
aws devicefarm list-device-pools \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --type CURATED \
  --region us-west-2

aws devicefarm get-device-pool \
  --arn arn:aws:devicefarm:us-west-2:123456789012:devicepool:POOL_ARN \
  --region us-west-2

aws devicefarm update-device-pool \
  --arn arn:aws:devicefarm:us-west-2:123456789012:devicepool:POOL_ARN \
  --max-devices 10 \
  --region us-west-2

aws devicefarm delete-device-pool \
  --arn arn:aws:devicefarm:us-west-2:123456789012:devicepool:POOL_ARN \
  --region us-west-2

# Check device pool compatibility with an upload
aws devicefarm get-device-pool-compatibility \
  --device-pool-arn arn:aws:devicefarm:us-west-2:123456789012:devicepool:POOL_ARN \
  --app-arn arn:aws:devicefarm:us-west-2:123456789012:upload:UPLOAD_ARN \
  --test-type APPIUM_PYTHON \
  --region us-west-2

# --- Uploads (app binaries, test packages, test specs) ---
# Step 1: Create upload (returns pre-signed S3 URL)
aws devicefarm create-upload \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name my-app.apk \
  --type ANDROID_APP \
  --region us-west-2
# Returns: arn, url (pre-signed S3 URL), status=INITIALIZED

# Step 2: Upload the file to the returned URL
curl -T my-app.apk "PRESIGNED_S3_URL"

# Step 3: Check upload status (poll until SUCCEEDED)
aws devicefarm get-upload \
  --arn arn:aws:devicefarm:us-west-2:123456789012:upload:UPLOAD_ARN \
  --region us-west-2

# Upload iOS app
aws devicefarm create-upload \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name my-app.ipa \
  --type IOS_APP \
  --region us-west-2

# Upload Appium Python test package (ZIP)
aws devicefarm create-upload \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name tests.zip \
  --type APPIUM_PYTHON_TEST_PACKAGE \
  --region us-west-2

# Upload test spec (YAML)
aws devicefarm create-upload \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name testspec.yml \
  --type APPIUM_PYTHON_TEST_SPEC \
  --region us-west-2

# Upload XCUITest bundle
aws devicefarm create-upload \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name MyApp-Runner.zip \
  --type XCTEST_UI_TEST_PACKAGE \
  --region us-west-2

# Upload Espresso APK
aws devicefarm create-upload \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name app-debug-androidTest.apk \
  --type INSTRUMENTATION_TEST_PACKAGE \
  --region us-west-2

# Upload extra data (fixtures, certs, data files)
aws devicefarm create-upload \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name testdata.zip \
  --type EXTERNAL_DATA \
  --region us-west-2

aws devicefarm list-uploads \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --region us-west-2

aws devicefarm delete-upload \
  --arn arn:aws:devicefarm:us-west-2:123456789012:upload:UPLOAD_ARN \
  --region us-west-2

# --- Network Profiles ---
aws devicefarm list-network-profiles \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --region us-west-2

# Create custom network profile (throttle to EDGE)
aws devicefarm create-network-profile \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name "Simulated EDGE" \
  --downlink-bandwidth-bits 240000 \
  --uplink-bandwidth-bits 200000 \
  --downlink-delay-ms 400 \
  --uplink-delay-ms 400 \
  --downlink-jitter-ms 50 \
  --uplink-jitter-ms 50 \
  --downlink-loss-percent 1 \
  --uplink-loss-percent 1 \
  --region us-west-2

aws devicefarm get-network-profile \
  --arn arn:aws:devicefarm:us-west-2:123456789012:networkprofile:PROFILE_ARN \
  --region us-west-2

aws devicefarm delete-network-profile \
  --arn arn:aws:devicefarm:us-west-2:123456789012:networkprofile:PROFILE_ARN \
  --region us-west-2

# --- Runs (schedule and monitor test execution) ---
# Schedule Appium Python run (custom test spec)
aws devicefarm schedule-run \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name "Sprint 42 Regression" \
  --app-arn arn:aws:devicefarm:us-west-2:123456789012:upload:APP_UPLOAD_ARN \
  --device-pool-arn arn:aws:devicefarm:us-west-2:123456789012:devicepool:POOL_ARN \
  --test '{
    "type": "APPIUM_PYTHON",
    "testPackageArn": "arn:aws:devicefarm:us-west-2:123456789012:upload:TEST_PACKAGE_ARN",
    "testSpecArn": "arn:aws:devicefarm:us-west-2:123456789012:upload:TEST_SPEC_ARN"
  }' \
  --configuration '{
    "networkProfileArn": "arn:aws:devicefarm:us-west-2:123456789012:networkprofile:PROFILE_ARN",
    "extraDataPackageArn": "arn:aws:devicefarm:us-west-2:123456789012:upload:EXTRA_DATA_ARN",
    "jobTimeoutMinutes": 60,
    "auxiliaryApps": [],
    "billingMethod": "METERED"
  }' \
  --execution-configuration '{
    "jobTimeoutMinutes": 60,
    "accountsCleanup": true,
    "appPackagesCleanup": true,
    "videoCapture": true,
    "skipAppResign": false
  }' \
  --region us-west-2

# Schedule XCUITest run
aws devicefarm schedule-run \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name "iOS UI Tests" \
  --app-arn arn:aws:devicefarm:us-west-2:123456789012:upload:IOS_APP_ARN \
  --device-pool-arn arn:aws:devicefarm:us-west-2:123456789012:devicepool:IOS_POOL_ARN \
  --test '{"type":"XCTEST_UI","testPackageArn":"arn:aws:devicefarm:us-west-2:123456789012:upload:XCTEST_ARN"}' \
  --region us-west-2

# Schedule built-in Fuzz test (no test package needed)
aws devicefarm schedule-run \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --name "Fuzz Test" \
  --app-arn arn:aws:devicefarm:us-west-2:123456789012:upload:APP_UPLOAD_ARN \
  --device-pool-arn arn:aws:devicefarm:us-west-2:123456789012:devicepool:POOL_ARN \
  --test '{"type":"BUILTIN_FUZZ","parameters":{"event_count":"6000","throttle":"50","seed":"12345"}}' \
  --region us-west-2

# Get run status (poll until status != RUNNING)
aws devicefarm get-run \
  --arn arn:aws:devicefarm:us-west-2:123456789012:run:RUN_ARN \
  --region us-west-2

# List runs for a project
aws devicefarm list-runs \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --region us-west-2

# Stop a run in progress
aws devicefarm stop-run \
  --arn arn:aws:devicefarm:us-west-2:123456789012:run:RUN_ARN \
  --region us-west-2

# Delete a run and its results
aws devicefarm delete-run \
  --arn arn:aws:devicefarm:us-west-2:123456789012:run:RUN_ARN \
  --region us-west-2

# --- Jobs, Suites, Tests (drill into results) ---
aws devicefarm list-jobs \
  --arn arn:aws:devicefarm:us-west-2:123456789012:run:RUN_ARN \
  --region us-west-2

aws devicefarm get-job \
  --arn arn:aws:devicefarm:us-west-2:123456789012:job:JOB_ARN \
  --region us-west-2

aws devicefarm list-suites \
  --arn arn:aws:devicefarm:us-west-2:123456789012:job:JOB_ARN \
  --region us-west-2

aws devicefarm list-tests \
  --arn arn:aws:devicefarm:us-west-2:123456789012:suite:SUITE_ARN \
  --region us-west-2

# --- Artifacts (logs, videos, screenshots) ---
# List artifacts for a run (all jobs)
aws devicefarm list-artifacts \
  --arn arn:aws:devicefarm:us-west-2:123456789012:run:RUN_ARN \
  --type FILE \
  --region us-west-2

# List video artifacts for a specific job
aws devicefarm list-artifacts \
  --arn arn:aws:devicefarm:us-west-2:123456789012:job:JOB_ARN \
  --type VIDEO \
  --region us-west-2

# List logs for a specific job
aws devicefarm list-artifacts \
  --arn arn:aws:devicefarm:us-west-2:123456789012:job:JOB_ARN \
  --type LOG \
  --region us-west-2

# List screenshots
aws devicefarm list-artifacts \
  --arn arn:aws:devicefarm:us-west-2:123456789012:suite:SUITE_ARN \
  --type SCREENSHOT \
  --region us-west-2

# Artifacts contain a pre-signed URL in the "url" field — download directly:
# aws devicefarm list-artifacts ... | jq -r '.artifacts[].url' | xargs -I{} curl -O {}

# --- Remote Access Sessions (interactive) ---
# Create interactive session on a specific device
aws devicefarm create-remote-access-session \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --device-arn arn:aws:devicefarm:us-west-2::device:DEVICE_ARN \
  --name "Debug session" \
  --configuration '{
    "billingMethod": "METERED",
    "vpceConfigurationArns": []
  }' \
  --remote-debug-enabled \
  --region us-west-2

# Install an app into the session
aws devicefarm install-to-remote-access-session \
  --remote-access-session-arn arn:aws:devicefarm:us-west-2:123456789012:session:SESSION_ARN \
  --app-arn arn:aws:devicefarm:us-west-2:123456789012:upload:APP_UPLOAD_ARN \
  --region us-west-2

aws devicefarm get-remote-access-session \
  --arn arn:aws:devicefarm:us-west-2:123456789012:session:SESSION_ARN \
  --region us-west-2

aws devicefarm list-remote-access-sessions \
  --arn arn:aws:devicefarm:us-west-2:123456789012:project:PROJECT_UUID \
  --region us-west-2

aws devicefarm stop-remote-access-session \
  --arn arn:aws:devicefarm:us-west-2:123456789012:session:SESSION_ARN \
  --region us-west-2

aws devicefarm delete-remote-access-session \
  --arn arn:aws:devicefarm:us-west-2:123456789012:session:SESSION_ARN \
  --region us-west-2

# --- Private Device Instances ---
aws devicefarm list-device-instances --region us-west-2
aws devicefarm get-device-instance \
  --arn arn:aws:devicefarm:us-west-2:123456789012:deviceinstance:INSTANCE_ARN \
  --region us-west-2

aws devicefarm update-device-instance \
  --arn arn:aws:devicefarm:us-west-2:123456789012:deviceinstance:INSTANCE_ARN \
  --labels iOS16 regression-suite \
  --profile-arn arn:aws:devicefarm:us-west-2:123456789012:instanceprofile:PROFILE_ARN \
  --region us-west-2

# --- Instance Profiles (configure private device behavior) ---
aws devicefarm create-instance-profile \
  --name "Clean State Profile" \
  --description "Clear all data between runs" \
  --package-cleanup \
  --reboot-after-use \
  --exclude-app-packages-from-cleanup com.example.myapp \
  --region us-west-2

aws devicefarm list-instance-profiles --region us-west-2
aws devicefarm get-instance-profile \
  --arn arn:aws:devicefarm:us-west-2:123456789012:instanceprofile:PROFILE_ARN \
  --region us-west-2
aws devicefarm delete-instance-profile \
  --arn arn:aws:devicefarm:us-west-2:123456789012:instanceprofile:PROFILE_ARN \
  --region us-west-2

# --- Device Slots (private device subscriptions) ---
aws devicefarm list-offering-transactions --region us-west-2
aws devicefarm list-offerings --region us-west-2
aws devicefarm get-offering-status --region us-west-2

# Purchase a device slot
aws devicefarm purchase-offering \
  --offering-id OFFERING_ID \
  --quantity 1 \
  --region us-west-2

# Renew a device slot
aws devicefarm renew-offering \
  --offering-id OFFERING_ID \
  --quantity 1 \
  --region us-west-2
```

---

## Desktop Browser Testing (Test Grid) — `aws devicefarm`

```bash
# --- Test Grid Projects ---
aws devicefarm create-test-grid-project \
  --name "Selenium Browser Tests" \
  --description "Cross-browser regression suite" \
  --region us-west-2

aws devicefarm list-test-grid-projects --region us-west-2
aws devicefarm get-test-grid-project \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID \
  --region us-west-2

aws devicefarm update-test-grid-project \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID \
  --name "Updated Grid Project" \
  --region us-west-2

aws devicefarm delete-test-grid-project \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID \
  --region us-west-2

# --- Test Grid Sessions ---
# Create a Selenium session URL (used as WebDriver remote URL)
aws devicefarm create-test-grid-url \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID \
  --expires-in-seconds 300 \
  --region us-west-2
# Returns: url — use as the `command_executor` in Selenium RemoteDriver

# List sessions for a test grid project
aws devicefarm list-test-grid-sessions \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID \
  --status CLOSED \
  --region us-west-2

aws devicefarm get-test-grid-session \
  --project-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID \
  --session-id SESSION_ID \
  --region us-west-2

# List actions (WebDriver commands) in a session
aws devicefarm list-test-grid-session-actions \
  --session-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID/testgrid-session:SESSION_ID \
  --region us-west-2

# List artifacts from a session (video, log)
aws devicefarm list-test-grid-session-artifacts \
  --session-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID/testgrid-session:SESSION_ID \
  --type VIDEO \
  --region us-west-2

aws devicefarm list-test-grid-session-artifacts \
  --session-arn arn:aws:devicefarm:us-west-2:123456789012:testgrid-project:GRID_PROJECT_UUID/testgrid-session:SESSION_ID \
  --type LOG \
  --region us-west-2

# --- VPC Connectivity (for Test Grid accessing private resources) ---
aws devicefarm create-test-grid-project \
  --name "Selenium Tests with VPC" \
  --vpc-config '{
    "subnetIds": ["subnet-abc123", "subnet-def456"],
    "securityGroupIds": ["sg-abc123"],
    "vpcId": "vpc-abc123"
  }' \
  --region us-west-2
```
