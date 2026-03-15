# Chrome Enterprise — Capabilities

## Chrome Browser Cloud Management (CBCM)

**Chrome Browser Cloud Management** allows organizations to manage the Google Chrome browser across Windows, macOS, and Linux endpoints from a centralized Google Admin Console, without requiring enrollment in a full MDM solution.

### Key Capabilities

**Policy enforcement:**
- Block or allow extensions (allowlist/blocklist by extension ID or from Chrome Web Store)
- Force-install extensions (deployed to all managed browsers automatically)
- Configure security settings (safe browsing, password manager, certificate policies, proxy)
- Restrict access to specific websites (URL allowlist/blocklist)
- Disable incognito mode, developer tools, print to PDF
- Enforce Chrome version updates (minimum version, auto-update schedule)

**Visibility and reporting:**
- Inventory of enrolled browsers: OS version, Chrome version, installed extensions, hardware details
- Browser activity reports: usage statistics, visited sites (with appropriate admin setup)
- Risk insights: browsers with outdated versions, potentially dangerous extensions
- Extension requests: users can request extensions; admin approves or denies

**Deployment methods:**
- Windows: deploy via Group Policy (GPO) or Microsoft Intune with Chrome ADMX templates
- macOS: deploy via MDM (JAMF, Workspace ONE) with Chrome configuration profiles
- Linux: deploy via chrome-enterprise.conf or MDM
- Cloud policy enrollment token: enroll browsers by setting the `CloudManagementEnrollmentToken` policy

### CBCM vs Intune/JAMF

CBCM manages Chrome-specific settings and policies. It complements (does not replace) traditional MDM for OS-level management. Many organizations use both:
- MDM (Intune/JAMF): OS patches, disk encryption, device compliance
- CBCM: Chrome browser policies, extension management, Chrome insights

---

## ChromeOS Device Management (Chrome Enterprise Upgrade)

**Chrome Enterprise Upgrade** is the license that enables advanced management of ChromeOS devices (Chromebooks, Chromeboxes, Chromebases) through the Google Admin Console.

### License Types

| License | Use Case |
|---|---|
| Chrome Enterprise Upgrade | Enterprise; full policy control; SSO, advanced networking |
| Chrome Education Upgrade | Schools and universities; student-specific features |
| Chrome Kiosk & Signage Upgrade | Single-app kiosk or digital signage mode |

### Device Enrollment

**Zero-touch enrollment**: pre-enroll devices before shipping to users
- Work with authorized resellers to associate device serial numbers with your domain
- Device automatically enrolls during OOBE (out-of-box experience)
- No manual enrollment needed

**Manual enrollment**: user presses Ctrl+Alt+E during OOBE or from sign-in screen

**Forced re-enrollment**: prevent users from unenrolling by setting device policy; device requires admin enrollment even after factory reset

### Device Policies

- **User account policies**: restrict which Google accounts can sign in (managed domain only)
- **Session policies**: session length, screen lock timeout, allowed URLs, developer mode
- **App and extension policies**: force-install apps and extensions, block specific apps
- **Network policies**: Wi-Fi configurations (SSID, EAP/802.1X certificates) deployed to devices
- **Printing policies**: configure printers, restrict color printing
- **Update policies**: pin ChromeOS version, auto-update window

### Kiosk Mode

Deploy ChromeOS devices as dedicated single-purpose kiosks:
- **Single app kiosk**: one app runs full-screen after device boot; no user login
- **Managed guest session**: no user profile; any app can be used; session cleared on sign-out
- **Use cases**: digital signage, POS terminals, customer check-in kiosks, shared workstations
- **App deployment**: deploy web apps (PWAs), Android apps, or Chrome apps in kiosk mode

### User Policies

Policies applied to Workspace users signing into managed ChromeOS devices:
- Force-install extensions, disable developer tools, configure proxy
- Restrict which apps and websites can be accessed
- Apply different policies to different Organizational Units (OUs)

### Android App Support

- ChromeOS supports Android apps via Google Play Store
- Enable managed Google Play in Admin Console to push Android apps to Chromebooks
- Control which Android apps are available (allowlist from Play Store)
- Android app policies via Android Management API

---

## BeyondCorp Enterprise (Chrome-Based Zero Trust)

> Primary documentation: see `security-iam/identity-access-capabilities.md`

BeyondCorp Enterprise enforces zero-trust access at the Chrome browser level:
- **Chrome Verified Access**: cryptographically verify device trustworthiness from the browser
- **Access Context Manager policies**: evaluate device posture (managed device, OS version, screen lock status) before granting access to applications
- **Browser-enforced DLP**: data loss prevention rules enforced in Chrome (block copy, print, screenshot for sensitive apps)
- **Real-time device signals**: Chrome continuously reports device health to BeyondCorp; access revoked if device falls out of compliance

---

## ChromeOS Flex

**ChromeOS Flex** is a free version of ChromeOS that can be installed on older Windows PCs and Macs, converting them into managed ChromeOS devices.

### Key Facts

- **Download**: available from chromeenterprise.google/os/chromeosflex
- **Certified models list**: Google maintains a certified device list for best compatibility; non-certified devices may have limited functionality
- **Installation**: boot from USB drive; installs alongside or replaces existing OS
- **Management**: once enrolled with Chrome Enterprise Upgrade, managed identically to hardware Chromebooks
- **Limitations vs ChromeOS**:
  - No Android app support (only on certified hardware Chromebooks)
  - No Linux development environment (Project Crostini) on some devices
  - Limited Parallels Desktop integration

### Use Cases

- **Refresh aging PC fleet**: convert 5-7 year old Windows PCs into managed ChromeOS devices for another 3-5 years
- **Cost reduction**: avoid hardware refresh costs; $0 for ChromeOS Flex vs $300-500/device for new hardware
- **Security upgrade**: move from unmanaged Windows to fully managed ChromeOS

---

## Virtual Desktop Solutions on GCP (Third-Party)

GCP does not have a native VDI product equivalent to AWS WorkSpaces. Enterprise VDI on GCP uses:

| Solution | Description |
|---|---|
| **Citrix DaaS on GCP** | Deploy Citrix Cloud with GCP as resource location; VDA (virtual delivery agent) on GCE VMs; management via Citrix Cloud console |
| **VMware Horizon on GCVE** | VMware Horizon desktop virtualization on Google Cloud VMware Engine; familiar VMware management; lift-and-shift of on-prem Horizon |
| **Itopia** | GCP-native DaaS solution built specifically on GCP; deploys Windows VMs on GCE; integrates with Google Workspace SSO |
| **Workspot** | Cloud VDI on GCP; enterprise Windows desktops on GCE; multi-cloud support |
| **Cloud Workstations** | For developer workstations specifically; see developer-tools domain |

**For non-developer end users requiring Windows desktop access**, Citrix DaaS or VMware Horizon are the most enterprise-grade options on GCP.
