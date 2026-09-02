# Flitt Bug Bounty #

## General Requirements ##

We assess the criticality of security issues with [Common Vulnerability Scoring System v4](https://www.first.org/cvss/calculator/4.0):

| Severity level| CVSS score |
|:-------------|:-----------|
|None| 0.0|
|Low| 0.1 – 3.9|
|Medium| 4.0 – 6.9|
|High| 7.0 – 8.9|
|Critical| 9.0 – 10.0|


As usual practice for rewards programs, we ask you to use common sense when looking for security bugs.

Expect us to eliminate the vulnerability within a reasonable time.

Avoid compromising data of other users and accounts, try to use only your personal or dummy data to search for vulnerabilities.

When reporting potential vulnerabilities, please consider realistic attack scenarios and the security impact of the behavior. The following issues will be rejected, except in rare circumstances demonstrating clear security impact.

1. Theoretical vulnerabilities that require unlikely user interaction or circumstances. For example:
    - Vulnerabilities only affecting users of unsupported or end-of-life browsers or operating systems
    - Broken link hijacking
    - Tabnabbing
    - Content spoofing and text injection issues
    - Self-exploitation, such as self-XSS or self-DoS (unless it can be used to attack a different account)
2. Theoretical vulnerabilities that do not demonstrate real-world security impact. For example:
    - Clickjacking on pages with no sensitive actions
    - Cross-Site Request Forgery (CSRF) on forms with no sensitive actions (e.g., Logout)
    - Permissive CORS configurations without demonstrated security impact
    - Software version disclosure / Banner identification issues / Descriptive error messages or headers (e.g., stack traces, application or server errors)
    - Open redirects (unless you can demonstrate additional security impact)
    - Wordpress user disclosure using REST API
3. Optional security hardening steps / Missing best practices. For example:
    - SSL/TLS Configurations
    - Lack of SSL Pinning
    - Cookie handling (e.g., missing HttpOnly/Secure flags)
    - Content-Security-Policy configuration opinions
    - Optional email security features (e.g., SPF/DKIM/DMARC configurations)
    - Most issues related to rate limiting
4. Vulnerabilities that may require hazardous testing. This type of testing must never be attempted unless explicitly authorized:
    - Issues relating to excessive traffic/requests (e.g., DoS, DDoS)
    - Any other issues where testing may affect the availability of systems
    - Social engineering attacks (e.g., phishing, opening support requests)
    - Attacks that are noisy to users or admins (e.g., spamming notifications or forms)
   

## Testing Requirements ##

The list of domains that are participating in the reward program:

```
    *.flitt.com
    *.flitt.dev
```
As with most security reward programs, there are some limitations:

  * we reward only the first person who informed us about the problem
  * publicly disclosed problems for which sufficient time has not waited for elimination are not rewarded
  * your safety research must not violate the law

[//]: # (## Possible Awards ##)

[//]: # (The approximate amount of reward for each of the levels of criticality is calculated as follows:)

[//]: # ()
[//]: # (| Severity level|Possible reward amount|)

[//]: # (|:--------------|:---------|)

[//]: # (| Low         |$50 – 200|)

[//]: # (| Medium    |$200 – 500|)

[//]: # (| High      |$500 – 1500|)

[//]: # (| Critical  |$1500 – individual|)

!!! note
    
    Flitt reserves the right to revise the amount of reward depending on the particular case or the circumstances.

## Notifications ##
If you think you have found a bug in Flitt security, contact us at email `YnVnYm91bnR5QGZsaXR0LmNvbQ==` and attach a detailed report on the problem found. 

We will respond as quickly as possible to your message. 

We ask you not to disclose the problem until it is fixed by Flitt specialists.