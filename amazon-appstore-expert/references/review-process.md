# Amazon Appstore: App Review Process

## What Amazon Reviews

During review, Amazon verifies that your app:
- Works as outlined in your product description
- Does not impair device functionality
- Does not compromise customer data security
- Complies with the Amazon Developer Services Agreement
- Complies with the Amazon Appstore Content Policy

---

## Review Timeline

Amazon does not publish a guaranteed review turnaround time. In practice:
- Most apps are reviewed within a few business days
- If your app is **still in review after 6 days**, you can use the Contact Us form to seek clarification: https://developer.amazon.com/support/cases/new

---

## App Status During Review

| Status | Meaning | Can You Edit? |
|--------|---------|---------------|
| **Submitted** | Awaiting review queue | No (but you can cancel) |
| **Under Review** | Actively being examined | No (but you can cancel) |
| **Pending** | Amazon paused review, emailed you about specific issue | No |
| **Approved** | Passed testing; queued for publication | No |
| **Live** | Available in the Appstore | No (submit update to change) |
| **Rejected** | Failed review | Submit a new version |

---

## Common Rejection Reasons

### Performance and Stability

- Force closes, crashes, hard locks, or error messages during normal use
- Frame rate drops below 25 fps sustained
- eMMC write rates exceeding 50 MB/hr (storage wear)
- Load screens without progress indicators lasting more than 15 seconds
- App taking more than 2 seconds to exit when the Home button is pressed
- Memory leaks or excessive battery drain during extended use
- Inability to handle conflicting inputs or rapid button presses

### UI and UX Issues

- Graphical distortions, pixelation, or misaligned UI elements
- For Fire TV: text illegible from 10 feet away
- For Fire TV: touch screen UI elements visible (Fire TV has no touchscreen)
- UI occupying less than 80% of screen area
- For Fire TV: inability to navigate using D-pad only
- For Fire TV: simultaneous button inputs required for core functionality
- Missing or incorrect soft key behavior on Fire tablets

### Technical Failures

- App exceeds 4 GB when fully installed
- Requires unsupported permissions without graceful degradation
- Data loss after updates or device hibernation
- HDMI disconnection not pausing media playback (Fire TV)
- Core features unavailable on targeted Fire devices
- Package name conflicts or invalid package name

### Content and Policy Violations

- Violation of Amazon Appstore Content Policy (see policies.md)
- App does not work as described in product listing
- App description, screenshots, or metadata misrepresent functionality
- Missing or inadequate IP documentation for third-party content

---

## Handling a Rejection

When an app is rejected:
1. Amazon sends an email with detailed, specific failure reasons
2. You must create a **new app version** — you cannot edit a rejected submission in place
3. Fix all identified issues
4. Re-upload the binary and resubmit from Step 1

There is no formal appeal mechanism described in Amazon's documentation. The standard path is to fix the issues identified in the rejection email and resubmit. If you believe a rejection was made in error, contact developer support: https://developer.amazon.com/support/cases/new

---

## Handling a "Pending" Status

If your app enters **Pending** status:
- Amazon has sent you an email specifying what action is needed
- This may involve fixing metadata, providing additional documentation, or addressing a specific technical concern
- Check the email associated with your developer account
- Take the requested action, then Amazon will resume review

---

## Tips for Faster, Cleaner Reviews

1. **Test on actual Amazon hardware** — Fire tablets and Fire TV behave differently from emulators and Android phones
2. **Complete all required IAP items** before submitting — Amazon won't review the app until IAP catalog is also submitted
3. **Check the test criteria checklist** before submitting: https://developer.amazon.com/docs/app-testing/test-criteria.html
4. **Ensure metadata accuracy** — descriptions must match actual app functionality
5. **Fire TV apps**: verify D-pad-only navigation works throughout the entire app
6. **Provide IP documentation** upfront if using licensed content — missing docs are a common Pending trigger
7. **Use Live App Testing** to catch issues before formal submission: https://developer.amazon.com/apps-and-games/test

---

## Documentation References

- Review and submit: https://developer.amazon.com/docs/app-submission/review-submit.html
- Test criteria: https://developer.amazon.com/docs/app-testing/test-criteria.html
- Pre-submission assessment for Fire TV: https://developer.amazon.com/docs/fire-tv/pre-submission-assessment-guide.html
- Contact support: https://developer.amazon.com/support/cases/new
