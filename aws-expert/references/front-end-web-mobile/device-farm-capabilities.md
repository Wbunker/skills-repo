# AWS Device Farm — Capabilities Reference

For CLI commands, see [device-farm-cli.md](device-farm-cli.md).

## AWS Device Farm

**Purpose**: Fully managed application testing service. Run automated tests on real physical mobile devices and desktop browsers hosted in AWS data centers. Also supports live interactive remote access for manual testing and debugging.

> **Region note**: AWS Device Farm is only available in `us-west-2` (US West - Oregon). All API calls must target this region.

---

## Mobile Device Testing

### Core Concepts

| Concept | Description |
|---|---|
| **Project** | Top-level container; groups device pools, uploads, runs, and artifacts |
| **Device pool** | Named set of devices selected for test runs; reusable across runs |
| **Upload** | App binary (APK/IPA), test package, test spec, or extra data file stored in Device Farm |
| **Run** | Execution of a test suite against a device pool; contains one job per device |
| **Job** | Single device execution within a run; contains one or more suites and test results |
| **Suite** | Logical grouping of tests within a job |
| **Test** | Individual test case result (pass/fail/skipped/errored) |
| **Artifact** | Output file from a run: device logs, video recording, screenshots, test result XML |

### Device Pools

- **Curated device pools**: AWS-managed pools (e.g., "Top Devices", "Top Android Devices", "Top iOS Devices")
- **Custom device pools**: select specific devices by model, OS version, manufacturer, form factor, availability
- Device selection rules (filter operators): `EQUALS`, `LESS_THAN`, `GREATER_THAN`, `IN`, `NOT_IN`, `CONTAINS`
- Filterable attributes: `ARN`, `PLATFORM` (Android/iOS), `FORM_FACTOR` (phone/tablet), `MANUFACTURER`, `REMOTE_ACCESS_ENABLED`, `REMOTE_DEBUG_ENABLED`, `APPIUM_VERSION`, `INSTANCE_ARN`, `INSTANCE_LABELS`, `FLEET_TYPE`

### Supported Test Frameworks (Mobile)

| Framework | Platform | Description |
|---|---|---|
| **Appium (Python)** | Android, iOS | Appium 2.x; write tests in Python using `pytest` |
| **Appium (Java JUnit)** | Android, iOS | Appium 2.x; JUnit 4/5 test runner |
| **Appium (Java TestNG)** | Android, iOS | Appium 2.x; TestNG runner |
| **Appium (Node.js)** | Android, iOS | Appium 2.x; Mocha, Jasmine, or custom runner |
| **Appium (Ruby)** | Android, iOS | Appium 2.x; RSpec |
| **XCUITest** | iOS only | Native Apple UI testing framework; built with Xcode |
| **Espresso** | Android only | Google's native Android UI testing framework |
| **Built-in: Fuzz** | Android, iOS | Randomized UI interaction test; no test code required |
| **Built-in: Explorer** | Android only | Automated app crawl; discovers UI paths; no test code required |

### Test Environments

| Environment | Description |
|---|---|
| **Standard environment** | Managed by AWS; Appium and dependencies pre-installed; no custom packages |
| **Custom environment (test spec)** | Use a YAML test spec to install custom packages, configure the environment, and run arbitrary commands |

### Test Spec (Custom Environment)

A YAML file that controls the device test environment setup and execution:

```yaml
version: 0.1
phases:
  install:
    commands:
      - export PYTHON_VERSION=3
      - export APPIUM_VERSION=2.0
      - pip3 install pytest Appium-Python-Client==2.3.0 requests
  pre_test:
    commands:
      - echo "Starting tests"
      - cd $DEVICEFARM_TEST_PACKAGE_PATH
  test:
    commands:
      - python3 -m pytest tests/ -v --junitxml=$DEVICEFARM_LOG_DIR/results.xml
  post_test:
    commands:
      - echo "Tests complete"
artifacts:
  - $DEVICEFARM_LOG_DIR
```

Test spec environment variables available during execution:

| Variable | Value |
|---|---|
| `DEVICEFARM_APP_PATH` | Path to installed app package |
| `DEVICEFARM_TEST_PACKAGE_PATH` | Extracted test package directory |
| `DEVICEFARM_EXTRA_DATA_PATH` | Extracted extra data ZIP directory |
| `DEVICEFARM_LOG_DIR` | Directory where logs and artifacts should be written |
| `DEVICEFARM_DEVICE_UDID` | Device UDID (iOS) or serial number (Android) |
| `DEVICEFARM_DEVICE_OS` | `IOS` or `ANDROID` |
| `DEVICEFARM_DEVICE_NAME` | Human-readable device name |

### Upload Types

| Type constant | Description |
|---|---|
| `ANDROID_APP` | Android APK or AAB |
| `IOS_APP` | iOS IPA file |
| `APPIUM_PYTHON_TEST_PACKAGE` | ZIP of Python test files + requirements.txt |
| `APPIUM_JAVA_JUNIT_TEST_PACKAGE` | JAR containing JUnit tests |
| `APPIUM_JAVA_TESTNG_TEST_PACKAGE` | JAR containing TestNG tests |
| `APPIUM_NODE_TEST_PACKAGE` | ZIP of Node.js test files + package.json |
| `APPIUM_RUBY_TEST_PACKAGE` | ZIP of Ruby test files + Gemfile |
| `XCTEST_UI_TEST_PACKAGE` | XCUITest ZIP bundle |
| `INSTRUMENTATION_TEST_PACKAGE` | Espresso APK |
| `APPIUM_PYTHON_TEST_SPEC` | YAML test spec for Appium Python |
| `APPIUM_JAVA_JUNIT_TEST_SPEC` | YAML test spec for Appium Java JUnit |
| `APPIUM_JAVA_TESTNG_TEST_SPEC` | YAML test spec for Appium Java TestNG |
| `APPIUM_NODE_TEST_SPEC` | YAML test spec for Appium Node |
| `APPIUM_RUBY_TEST_SPEC` | YAML test spec for Appium Ruby |
| `XCTEST_UI_TEST_SPEC` | YAML test spec for XCUITest |
| `INSTRUMENTATION_TEST_SPEC` | YAML test spec for Espresso |
| `EXTERNAL_DATA` | ZIP of data files (fixtures, certs, config) pushed to device |

### Network Shaping

Simulate real-world network conditions during tests:

| Profile | Download | Upload | Latency |
|---|---|---|---|
| Full — No Throttling | No limit | No limit | 0ms |
| LTE | 15 Mbps | 5 Mbps | 30ms |
| UMTS (3G) | 384 Kbps | 384 Kbps | 100ms |
| EDGE (2.75G) | 240 Kbps | 200 Kbps | 400ms |
| GPRS (2G) | 50 Kbps | 30 Kbps | 500ms |
| Custom | User-defined | User-defined | User-defined |

Network shaping is configured in `schedule-run` via the `--configuration networkProfileArn` parameter.

### Artifacts

Collected automatically for each test job:

| Artifact type | Description |
|---|---|
| `LOG` | Device syslog (Android logcat or iOS system log), Appium server log, test runner log |
| `SCREENSHOT` | Screenshots taken during the test run |
| `VIDEO` | MP4 video recording of the full test session |
| `RESULT` | JUnit XML result file, customer-provided logs |
| `FILE` | Extra files written to `DEVICEFARM_LOG_DIR` |

Artifacts are available via `list-artifacts` and expire after 30 days (downloadable via pre-signed S3 URL).

### Private Devices

- Reserve real physical devices exclusively for your account (no sharing with other AWS customers)
- Available via **device slots**: monthly subscription for a specific device model
- Private devices support remote debug (adb/Xcode Instruments) and custom device configurations
- Instance labels: tag private device instances for organized pool selection

---

## Desktop Browser Testing (Test Grid)

**Purpose**: Run Selenium WebDriver tests against real desktop browsers (Chrome, Firefox) on managed infrastructure. No device pool selection needed — specify browser and version.

### Supported Browsers

| Browser | Notes |
|---|---|
| **Google Chrome** | Specify major version or `latest` |
| **Mozilla Firefox** | Specify major version or `latest` |

### Test Grid Concepts

| Concept | Description |
|---|---|
| **Test grid project** | Container for browser test sessions |
| **Test grid session** | Active Selenium WebDriver session on a browser instance |
| **Test grid URL** | WebDriver endpoint URL; used in place of `http://localhost:4444/wd/hub` in Selenium code |

### Connecting Selenium Tests

```python
# Python example
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
driver = webdriver.Remote(
    command_executor="https://devicefarm.us-west-2.amazonaws.com/wd/hub",
    options=options,
    # AWS credentials injected via SigV4 — use boto3-based URL signing or Device Farm SDK
)
```

- Device Farm signs the WebDriver URL using SigV4; tests authenticate via IAM credentials
- Sessions expire after configurable timeout (default 30 minutes of inactivity)
- Artifacts: video, log available via `list-test-grid-session-artifacts`

---

## Remote Access (Interactive Sessions)

**Purpose**: Connect to a real device interactively in real time via a browser-based session for manual testing, debugging, and exploration.

### Remote Access Features

| Feature | Description |
|---|---|
| **Live device view** | See the device screen in a browser; interact with touch/tap/swipe gestures |
| **Install apps** | Push APK/IPA to the device during the session |
| **Remote adb (Android)** | Enable adb-over-USB forwarding; connect local Android Studio or CLI tools |
| **Remote Xcode Instruments (iOS)** | Connect Xcode instruments for profiling during the session |
| **Screenshot capture** | Take screenshots manually during session |
| **Push test files** | Upload data files to the device during session |

### Session Lifecycle

1. `create-upload` — upload the app binary
2. `create-remote-access-session` — start session on a chosen device with the app
3. `get-remote-access-session` — poll until `status = RUNNING`; retrieve `remoteAccessEnabled` URL
4. Open the URL in a browser to start interactive session
5. `stop-remote-access-session` — end the session when done
6. `list-artifacts` — download logs/screenshots from the session

---

## Run Execution and Status

### Run Result Values

| Result | Meaning |
|---|---|
| `PASSED` | All tests passed |
| `FAILED` | One or more tests failed |
| `ERRORED` | System error during run; infrastructure issue |
| `SKIPPED` | Tests were skipped |
| `STOPPED` | Run was manually stopped |
| `PENDING` | Waiting for devices to become available |

### Execution Strategy

| Strategy | Description |
|---|---|
| `WITHOUT_ERRORS` (default) | Stop testing on a device if it encounters a system error |
| `STOP_ON_FAILURE` | Stop testing on a device on first test failure |

---

## Pricing Model

| Type | Billing unit |
|---|---|
| **On-demand device minutes** | Per device-minute consumed across all jobs in a run |
| **Private device slot** | Monthly subscription per device slot |
| **Test grid** | Per browser-minute consumed |
| **Remote access** | Per device-minute of interactive session |

Device minutes billing starts when the device is allocated and stops when the job completes (including setup/teardown).
