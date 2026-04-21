# Roadmap: malpanez.security — Compliance Role Expansion

**Created:** 2026-04-14
**Milestone:** v1.2.0 — Compliance Role Expansion
**Status:** Planning

## Overview

This milestone adds 6 new Ansible roles to the malpanez.security collection, each targeting
a specific audit gap in NIS2, SOC2, HIPAA, and PCI-DSS. Each role follows the existing
review/enforce pattern: review mode exposes the deficiency visibly so the operator can
show it to an auditor; enforce mode closes it. The 6 roles are independent of each other
and can be executed in any order, though the sequence below follows natural grouping
from infrastructure fundamentals (time, users, logging) to controls (AV, TLS, USB).
The milestone closes with a version bump from 1.1.0 to 1.2.0.

## Phases

- [x] **Phase 1: ntp_hardening** - NTP/chrony hardening with review and enforce mode (PCI-DSS 10.6.1, NIS2, SOC2 CC6.1) (completed 2026-04-20)
- [x] **Phase 2: user_audit** - Local user account audit and lockout enforcement (SOC2 CC6.2, HIPAA, PCI-DSS 8.x) (completed 2026-04-18)
- [x] **Phase 3: rsyslog_forwarding** - Centralised log forwarding via rsyslog drop-in with optional TLS (NIS2, SOC2 CC7.2, PCI-DSS 10.5) (completed 2026-04-18)
- [x] **Phase 4: antivirus** - ClamAV installation, freshclam updates, and scheduled scan timer (PCI-DSS 5.2, NIS2, SOC2 CC6.8) (completed 2026-04-18)
- [x] **Phase 5: tls_hardening** - System-wide TLS version and cipher enforcement (PCI-DSS 4.2.1, HIPAA, NIS2) (completed 2026-04-19)
- [x] **Phase 6: usbguard** - USB device control with block-by-default policy (PCI-DSS 12.3.4, HIPAA, NIS2) (completed 2026-04-20)
- [x] **Phase 06.1: security-audit-remediations** - AUDIT-CRIT-01, HIGH-01, HIGH-03, MED-02 remediations in sssd_ad_integration and antivirus (completed 2026-04-20)
- [ ] **Phase 7: tech-debt** - Role READMEs, Molecule SHA pins, prepare.yml sed→lineinfile, argument_specs gaps, venv rebuild, CI permissions

## Phase Details

### Phase 1: ntp_hardening

**Goal**: Implement NTP/chrony hardening role that reviews time synchronisation posture and enforces a secure chrony configuration across Debian, RHEL, and SUSE.
**Depends on**: Nothing (first phase)
**Requirements**: NTP-01, NTP-02, NTP-03, NTP-04, NTP-05, NTP-06, STD-01, STD-02, STD-03, STD-04, STD-05, STD-06, STD-07, STD-08, STD-09, STD-10, STD-11, STD-12, STD-13, STD-14
**Success Criteria** (what must be TRUE):
  1. review.yml reports chrony/ntpd status, time drift, NTP servers, and flags CVE-2013-5211 risk (monitor directive) — no system changes occur
  2. enforce.yml installs chrony, disables systemd-timesyncd (Debian) or legacy ntpd (RHEL), deploys chrony.conf drop-in with configurable servers, enables and starts the service
  3. Container-aware: adjtimex/service assertions are skipped inside Docker/Podman containers; template is still deployed and verified
  4. yamllint and ansible-lint --profile production pass with 0 errors on all role files
  5. Molecule scenario converges and verify.yml passes on ubuntu2204 and rockylinux9

**Plans**: 5 plans

Plans:
- [x] 01-01: Scaffold ntp_hardening — `ansible-galaxy role init`, defaults/main.yml (ntp_hardening_enabled, servers, makestep, rtcsync, maxdistance, minsources, allow, deny_all, leapsectz, logdir, logchange), vars/RedHat.yml (chrony_package, chrony_config /etc/chrony.conf, chrony_service chronyd, conf_d /etc/chrony.d), vars/Debian.yml (config /etc/chrony/chrony.conf, service chrony, conf_d /etc/chrony/conf.d), vars/Suse.yml (same paths as RedHat), meta/main.yml (platforms: Debian buster/bullseye/bookworm, Ubuntu bionic/focal/jammy, EL versions: [all]; galaxy_tags, min_ansible_version 2.16), meta/argument_specs.yml (all defaults documented with type/description), tests/test.yml (play name + FQCN malpanez.security.ntp_hardening), handlers/main.yml (Restart chronyd with changed_when: true, when: not _ntp_in_container)
- [x] 01-02: Tasks — tasks/main.yml (setup gather_subset:[min], OS assert for Debian/RedHat/Suse, include_vars "{{ ansible_os_family }}.yml", set_fact _ntp_in_container from virtualization_type in [docker,podman,container,lxc], include review.yml tags:[ntp_hardening,review], include enforce.yml when ntp_hardening_enabled+security_mode==enforce tags:[ntp_hardening,enforce]); tasks/review.yml (package check via rpm-q or dpkg-query changed_when:false failed_when:false, systemctl is-active changed_when:false failed_when:false, chronyc tracking + sources -v skipped when _ntp_in_container, grep for monitor/cmdallow directive CVE-2013-5211 check, debug report with service state/tracking/sources/CVE risk); tasks/enforce.yml (dnf/apt/zypper install chrony with OS guards, systemd stop systemd-timesyncd failed_when:false when Debian, systemd stop ntpd failed_when:false when RedHat, file logdir 0750, template chrony.conf.j2 → config_file backup:true notify:Restart chronyd, systemd enable+start service when not _ntp_in_container daemon_reload:true, command chronyc tracking verify when not _ntp_in_container changed_when:false)
- [x] 01-03: Templates — templates/chrony.conf.j2 (Ansible-managed header, server loop with ntp_hardening_servers, allow loop if ntp_hardening_allow non-empty, deny all if ntp_hardening_deny_all, makestep directive, rtcsync if true, maxdistance, minsources, leapsectz, logdir, log tracking measurements statistics, logchange; CRITICAL: no monitor directive anywhere — omission is the secure state for CVE-2013-5211; no nomonitor — that is an older pattern)
- [x] 01-04: Molecule — molecule/default/molecule.yml (driver docker, platforms: geerlingguy/docker-ubuntu2204-ansible latest + geerlingguy/docker-rockylinux9-ansible latest, privileged:true, volumes:/sys/fs/cgroup:/sys/fs/cgroup:rw, cgroupns_mode:host); molecule/default/prepare.yml (Rocky 9 only: sed -i 's/ sss//g' /etc/nsswitch.conf); molecule/default/converge.yml (play name, include_role malpanez.security.ntp_hardening with vars ntp_hardening_enabled:true, security_mode:enforce, ntp_hardening_servers:[0.pool.ntp.org iburst]); molecule/default/verify.yml (assert chrony package installed, assert config file exists at OS-appropriate path, when not container assert service enabled, assert no monitor directive in config file)
- [x] 01-05: CI integration — add ntp_hardening to ci-uv.yml test-roles matrix and ci-cd-enterprise.yml test-molecule matrix; run `ansible-galaxy collection install . --force -p .ansible/collections`; run `yamllint roles/ntp_hardening/` and `ansible-lint --profile production roles/ntp_hardening/` confirming 0 errors

---

### Phase 2: user_audit

**Goal**: Implement user account audit role that reports local account compliance deficiencies and enforces password expiry and inactive account lockout without touching root or system accounts.
**Depends on**: Phase 1 (collection install pattern established)
**Requirements**: USR-01, USR-02, USR-03, USR-04, USR-05, USR-06, STD-01, STD-02, STD-03, STD-04, STD-05, STD-06, STD-07, STD-08, STD-09, STD-10, STD-11, STD-12, STD-13, STD-14
**Success Criteria** (what must be TRUE):
  1. review.yml reports accounts with no password expiry, UID 0 non-root accounts, accounts inactive beyond threshold, service accounts with interactive shells, and passwd/shadow consistency — no system changes occur
  2. enforce.yml locks inactive accounts using ansible.builtin.user password_lock:true (idempotent) and sets password expiry via the two-step chage pattern (collect current maxdays, only fire when -1 or 99999)
  3. Root (UID 0) and system accounts (UID < 1000) are never touched by enforce tasks; triple guard in place: UID filter, user_audit_skip_users list, explicit item != 'root' condition
  4. Repeated enforce runs produce no changes on already-compliant accounts (genuine idempotence)
  5. yamllint and ansible-lint --profile production pass with 0 errors; Molecule passes on ubuntu2204 and rockylinux9

**Plans**: 5 plans

Plans:
- [x] 02-01: Scaffold user_audit — `ansible-galaxy role init`, defaults/main.yml (user_audit_enabled, inactive_days:90, max_password_age:90, min_password_age:1, warn_days:14, lock_inactive:true, set_password_expiry:true, fix_service_shells:false, skip_users:[root,halt,sync,shutdown], login_shells list), vars/RedHat.yml (shadow_utils:shadow-utils, nologin_shell:/sbin/nologin), vars/Debian.yml (shadow_utils:login, nologin_shell:/usr/sbin/nologin), vars/Suse.yml (shadow_utils:shadow, nologin_shell:/sbin/nologin), meta/main.yml (platforms same pattern as Phase 1, tags:user-audit/account-management/compliance), meta/argument_specs.yml (all vars documented), tests/test.yml (FQCN malpanez.security.user_audit), handlers/main.yml (empty — no service restarts needed)
- [x] 02-02: Tasks review.yml — shell+awk collect human accounts (UID >= 1000, not nologin/false shell, executable:/bin/bash, set -o pipefail, changed_when:false); set_fact _ua_human_account_list; command chage -l loop over account list (changed_when:false failed_when:false); set_fact _ua_no_expiry filtering on 'Password expires.*never'; shell+awk UID 0 non-root accounts from /etc/passwd; command lastlog -u loop (changed_when:false); set_fact _ua_inactive_accounts (Never logged in); shell lastlog --time {{ user_audit_inactive_days }} pipe awk (note: --time N shows logins OLDER than N days — correct direction); shell+awk service accounts (UID > 0 and < 1000) with bash/sh/zsh shell; command pwck -r -q (changed_when:false failed_when:false); debug report with all findings
- [x] 02-03: Tasks enforce.yml — all enforce tasks gated with `when: not ansible_check_mode` for check_mode safety; ansible.builtin.user password_lock:true loop over _ua_inactive_by_days.stdout_lines when user_audit_lock_inactive and item not in skip_users and item != 'root'; two-step chage idempotence: command chage -l loop over _ua_no_expiry (changed_when:false), then command chage --maxdays/--mindays/--warndays loop only when stdout matches 'Maximum number of days.*(-1|99999)' and item not in skip_users and item != 'root' (changed_when:true failed_when:rc!=0); ansible.builtin.user shell:nologin loop over service accounts when user_audit_fix_service_shells and item not in skip_users; tasks/main.yml follows standard pattern with OS assert and include_vars
- [x] 02-04: Molecule — molecule.yml (ubuntu2204 + rockylinux9, privileged:true); prepare.yml (Rocky 9 nsswitch sss fix, also create test user with no password expiry: useradd testuser + chage -M -1 testuser); converge.yml (user_audit_enabled:true, security_mode:enforce, user_audit_inactive_days:90); verify.yml (assert chage -l testuser shows Password expires is not 'never' after enforce, assert shadow-utils/login package present, assert pwck -r -q exits 0 or output is inspectable, container-aware service assertions)
- [x] 02-05: CI integration — add user_audit to ci-uv.yml and ci-cd-enterprise.yml matrices; reinstall collection; run yamllint and ansible-lint --profile production confirming 0 errors; verify no_log not required (no secrets handled — pwck/chage/lastlog are non-secret operations)

---

### Phase 3: rsyslog_forwarding

**Goal**: Implement centralised log forwarding role that reports rsyslog configuration state and deploys a drop-in forwarding config to /etc/rsyslog.d/99-forwarding.conf with optional TLS, never touching /etc/rsyslog.conf.
**Depends on**: Phase 2
**Requirements**: LOG-01, LOG-02, LOG-03, LOG-04, LOG-05, LOG-06, STD-01, STD-02, STD-03, STD-04, STD-05, STD-06, STD-07, STD-08, STD-09, STD-10, STD-11, STD-12, STD-13, STD-14
**Success Criteria** (what must be TRUE):
  1. review.yml reports rsyslog installation status, whether a forwarding drop-in exists, destination hostname, TLS state — no files are modified
  2. enforce.yml deploys /etc/rsyslog.d/99-forwarding.conf using RainerScript action() syntax with disk-assisted queue; validate: rsyslogd -N1 -f %s is applied in the template task
  3. Optional TLS mode deploys GnuTLS global() stanza with CA cert path; asserts CA cert file exists on target before deploying TLS config; fails early if rsyslog_forwarding_tls_enabled=true but protocol=udp
  4. Post-deploy rsyslogd -N1 full syntax check exits 0 and rsyslog service is active
  5. yamllint and ansible-lint --profile production pass with 0 errors; Molecule passes on ubuntu2204 and rockylinux9

**Plans**: 5 plans

Plans:
- [x] 03-01: Scaffold rsyslog_forwarding — `ansible-galaxy role init`, defaults/main.yml (rsyslog_forwarding_enabled, host:"", port:514, protocol:tcp, tls_enabled:false, tls_ca_cert:"", tls_client_cert:"", tls_client_key:"", tls_auth_mode:x509/name, selector:*.*, queue_size:10000, queue_type:LinkedList, action_resume_retry:-1, log_dir:/var/log, file_create_mode:0640, logrotate_enabled:true, logrotate_rotate:4, logrotate_size:50M), vars/Debian.yml (rsyslog_package:rsyslog, rsyslog_tls_package:rsyslog-gnutls, rsyslog_service:rsyslog, rsyslog_dropin_dir:/etc/rsyslog.d), vars/RedHat.yml (same packages, same paths), vars/Suse.yml (rsyslog_tls_package:rsyslog-module-gtls — DIFFERENT from Debian/RHEL), meta/main.yml, meta/argument_specs.yml, tests/test.yml, handlers/main.yml (Restart rsyslog with ansible.builtin.systemd state:restarted changed_when:true)
- [x] 03-02: Tasks — tasks/main.yml (standard pattern with set_fact _rsyslog_in_container, include review.yml, include enforce.yml when enabled+enforce mode); tasks/review.yml (stat /usr/sbin/rsyslogd, systemctl is-active rsyslog changed_when:false failed_when:false, stat /etc/rsyslog.d/99-forwarding.conf, slurp if exists, set_fact _rsyslog_configured_dest from b64decoded content, set_fact _rsyslog_tls_present via 'StreamDriverMode' in content, debug report with all findings); tasks/enforce.yml (assert rsyslog_forwarding_host length > 0, assert TLS CA cert path set when TLS enabled, stat CA cert on target assert exists when TLS enabled, assert protocol==tcp when TLS enabled, package install rsyslog, conditional TLS package install, file ensure dropin_dir 0755, template 99-forwarding.conf.j2 validate:'rsyslogd -N1 -f %s' notify:Restart rsyslog, template rsyslog-logrotate.j2 when logrotate_enabled, systemd enable+start rsyslog when not _rsyslog_in_container, command rsyslogd -N1 changed_when:false failed_when:rc!=0, command systemctl is-active rsyslog changed_when:false failed_when:stdout!='active')
- [x] 03-03: Templates — templates/99-forwarding.conf.j2 (Ansible-managed header; conditional GnuTLS module(load="imtls") + global() block with CA cert and optional mTLS certs when tls_enabled; $FileCreateMode directive; action() block using omfwd with target/port/protocol, TLS StreamDriver/Mode/AuthMode when enabled, queue.type/size, action.resumeRetryCount; use RainerScript action() syntax — NOT legacy @@host:port which cannot express queues or TLS inline); templates/rsyslog-logrotate.j2 (logrotate stanza for log_dir/*.log with rotate/size/missingok/compress/delaycompress/sharedscripts/postrotate systemctl kill -s HUP rsyslog.service)
- [x] 03-04: Molecule — molecule.yml (ubuntu2204 + rockylinux9, privileged:true); prepare.yml (Rocky 9 nsswitch fix); converge.yml (rsyslog_forwarding_enabled:true, security_mode:enforce, rsyslog_forwarding_host:"127.0.0.1", rsyslog_forwarding_tls_enabled:false — no TLS in CI to avoid cert chain requirement); verify.yml (assert /etc/rsyslog.d/99-forwarding.conf exists and mode 0640, assert rsyslogd binary present, assert rsyslogd -N1 exits 0 when not container, assert rsyslog active when not container using systemd-detect-virt or _rsyslog_in_container fact)
- [x] 03-05: CI integration — add rsyslog_forwarding to ci-uv.yml and ci-cd-enterprise.yml matrices; reinstall collection; run yamllint and ansible-lint --profile production confirming 0 errors

---

### Phase 4: antivirus

**Goal**: Implement ClamAV antivirus role that reports AV installation status, database age, and scan history, then installs ClamAV, configures freshclam for signature updates, and deploys a systemd scan timer — with EPEL handling for RHEL and container-aware skipping.
**Depends on**: Phase 3
**Requirements**: AV-01, AV-02, AV-03, AV-04, AV-05, AV-06, AV-07, STD-01, STD-02, STD-03, STD-04, STD-05, STD-06, STD-07, STD-08, STD-09, STD-10, STD-11, STD-12, STD-13, STD-14
**Success Criteria** (what must be TRUE):
  1. review.yml reports clamscan binary presence, ClamAV version, signature DB age (main.cvd/daily.cld stat), clamd service state, last scan log existence — no changes made
  2. enforce.yml installs ClamAV packages (EPEL enabled first on RHEL via dnf RPM URL), deploys clamd.conf and freshclam.conf drop-ins, enables freshclam and clamd services when not in container
  3. Systemd scan service and timer are deployed; timer is enabled when not in container (antivirus_scan_enabled:true default)
  4. antivirus_update_db:false skips freshclam invocation and DB presence assertion — safe for CI molecule runs
  5. yamllint and ansible-lint --profile production pass with 0 errors; Molecule passes on ubuntu2204 and rockylinux9

**Plans**: 5 plans

Plans:
- [x] 04-01: Scaffold antivirus — `ansible-galaxy role init`, defaults/main.yml (antivirus_enabled, antivirus_update_db:true, antivirus_scan_enabled:true, antivirus_scan_dirs:[/home,/tmp,/var/tmp], antivirus_scan_schedule:daily, antivirus_scan_log:/var/log/clamav/scan.log, antivirus_freshclam_checks:12, antivirus_max_file_size:25M, antivirus_max_scan_size:100M, antivirus_selinux_contexts:true), vars/Debian.yml (packages:[clamav,clamav-daemon,clamav-freshclam], clamd_service:clamav-daemon, freshclam_service:clamav-freshclam, clamd_config:/etc/clamav/clamd.conf, freshclam_config:/etc/clamav/freshclam.conf, clamd_user:clamav, clamd_group:clamav, log_dir:/var/log/clamav, db_dir:/var/lib/clamav, epel_required:false), vars/RedHat.yml (packages:[clamav,clamav-update,clamd], clamd_service:clamd@scan, freshclam_service:clamav-freshclam, clamd_config:/etc/clamd.d/scan.conf, freshclam_config:/etc/freshclam.conf, clamd_user:clamscan, clamd_group:clamscan, log_dir:/var/log/clamd.scan, epel_required:true), vars/Suse.yml (packages:[clamav,clamav-daemon], clamd_service:clamd, freshclam_service:freshclam, clamd_config:/etc/clamd.conf, freshclam_config:/etc/freshclam.conf, clamd_user:vscan, clamd_group:vscan, epel_required:false), meta/main.yml, meta/argument_specs.yml, tests/test.yml, handlers/main.yml (Restart clamd, Restart freshclam, Reload systemd — each changed_when:true)
- [x] 04-02: Tasks — tasks/main.yml (standard pattern, include_vars, set_fact _antivirus_in_container, include review/enforce); tasks/review.yml (stat /usr/bin/clamscan, command clamscan --version changed_when:false failed_when:false when binary exists, stat antivirus_db_dir/main.cvd, stat antivirus_db_dir/daily.cld, command systemctl is-active clamd_service changed_when:false failed_when:false, stat scan_log, slurp scan_log if exists, debug report); tasks/enforce.yml (set_fact _antivirus_in_container, dnf install EPEL RPM URL when RedHat+epel_required using ansible_distribution_major_version, apt install Debian, dnf install RedHat, zypper install Suse, file log_dir 0750 owner clamd_user, template clamd.conf.j2 notify:Restart clamd, template freshclam.conf.j2 notify:Restart freshclam, command restorecon -Rv scan_dirs loop when RedHat+selinux_contexts changed_when:'Relabeled' in stdout failed_when:false, command freshclam register changed_when:'Database updated' in stdout failed_when:rc not in [0,1] when antivirus_update_db, systemd enable+start freshclam when not container, systemd enable+start clamd when not container, template clamav-scan.service.j2 notify:Reload systemd when scan_enabled, template clamav-scan.timer.j2 notify:Reload systemd when scan_enabled, systemd enable+start clamav-scan.timer daemon_reload:true when scan_enabled+not container, stat clamd_config assert exists, warn debug if db absent+update_db false)
- [x] 04-03: Templates — templates/clamd.conf.j2 (LogFile, LogTime yes, LogRotate yes, PidFile /run/clamd.scan/clamd.pid, TemporaryDirectory /var/tmp, DatabaseDirectory, LocalSocket /run/clamd.scan/clamd.sock, User clamd_user, MaxFileSize/MaxScanSize, ScanPE/ELF/OLE2/Mail/Archive yes, DetectPUA yes, FollowFileSymlinks/FollowDirectorySymlinks false); templates/freshclam.conf.j2 (DatabaseOwner, UpdateLogFile, LogRotate yes, LogTime yes, DatabaseDirectory, DatabaseMirror database.clamav.net, Checks freshclam_checks, NotifyClamd pointing to clamd_config); templates/clamav-scan.service.j2 ([Unit] After clamd services ConditionPathExists=/usr/bin/clamscan; [Service] Type=oneshot User=root ExecStart=/usr/bin/clamscan --recursive --infected --log=scan_log scan_dirs); templates/clamav-scan.timer.j2 ([Timer] OnCalendar scan_schedule Persistent=true; [Install] WantedBy=timers.target)
- [x] 04-04: Molecule — molecule.yml (ubuntu2204 + rockylinux9, privileged:true); prepare.yml (Rocky 9 nsswitch fix); converge.yml (antivirus_enabled:true, security_mode:enforce, antivirus_update_db:false — skips 200MB download in CI, antivirus_scan_enabled:true); verify.yml (assert clamav package installed via package_facts, assert clamd.conf deployed, assert freshclam.conf deployed, assert clamav-scan.service and .timer deployed when scan_enabled, skip service state assertions when _antivirus_in_container, skip db presence assertion when antivirus_update_db false)
- [x] 04-05: CI integration — add antivirus to ci-uv.yml and ci-cd-enterprise.yml matrices; reinstall collection; run yamllint and ansible-lint --profile production confirming 0 errors; verify EPEL URL pattern uses ansible_distribution_major_version (not hardcoded 9)

---

### Phase 5: tls_hardening

**Goal**: Implement system-wide TLS hardening role that reports current TLS policy posture and enforces minimum TLS version and cipher strength — using update-crypto-policies on RHEL and openssl.cnf lineinfile/blockinfile on Debian/SUSE.
**Depends on**: Phase 4
**Requirements**: TLS-01, TLS-02, TLS-03, TLS-04, TLS-05, TLS-06, STD-01, STD-02, STD-03, STD-04, STD-05, STD-06, STD-07, STD-08, STD-09, STD-10, STD-11, STD-12, STD-13, STD-14
**Success Criteria** (what must be TRUE):
  1. review.yml reports current crypto-policy on RHEL (update-crypto-policies --show) and MinProtocol/CipherString on Debian/SUSE, including whether a policy change is needed
  2. enforce.yml on RHEL calls update-crypto-policies --set only when current policy differs from target; skips with debug message when FIPS is active (/proc/sys/crypto/fips_enabled == 1)
  3. enforce.yml on Debian/SUSE uses slurp to detect whether [system_default_sect] exists in openssl.cnf, inserts full block via blockinfile if absent, then lineinfile to set MinProtocol and CipherString — idempotent on repeated runs
  4. No service restarts are triggered by this role — policy changes apply to new connections; README documents that callers must reload daemons
  5. yamllint and ansible-lint --profile production pass with 0 errors; Molecule passes on ubuntu2204 and rockylinux9

**Plans**: 5 plans

Plans:
- [x] 05-01: Scaffold tls_hardening — `ansible-galaxy role init`, defaults/main.yml (tls_hardening_enabled, tls_hardening_min_version:TLSv1.2, tls_hardening_policy_rhel:DEFAULT:NO-SHA1, tls_hardening_openssl_seclevel:2, tls_hardening_disable_tls10:true, tls_hardening_disable_tls11:true, tls_hardening_check_services:[]), vars/RedHat.yml (_tls_policy_tool:update-crypto-policies, _tls_policy_tool_package:crypto-policies-scripts, _tls_openssl_cnf:/etc/pki/tls/openssl.cnf — RHEL path differs from Debian), vars/Debian.yml (_tls_policy_tool:openssl_cnf, _tls_openssl_cnf:/etc/ssl/openssl.cnf), vars/Suse.yml (same as Debian), meta/main.yml, meta/argument_specs.yml (choices for tls_hardening_min_version:[TLSv1.2,TLSv1.3] and tls_hardening_policy_rhel:[DEFAULT,DEFAULT:NO-SHA1,FUTURE,FIPS]), tests/test.yml, handlers/main.yml (intentionally minimal — no service restarts; comment explains design decision)
- [x] 05-02: Tasks review.yml — command update-crypto-policies --show changed_when:false failed_when:false when RedHat; shell+pipefail grep MinProtocol from _tls_openssl_cnf || echo NOT_SET when Debian/Suse; shell+pipefail grep CipherString same pattern; shell connectivity tests loop over tls_hardening_check_services if non-empty (echo '' | openssl s_client -connect item -tls1 2>&1 | grep -qE 'unsupported protocol|handshake failure', changed_when:false failed_when:false); debug report block with OS-conditional sections showing current vs target policy, change-needed flag, and TLS 1.0/1.1 target state
- [x] 05-03: Tasks enforce.yml — RHEL path: package crypto-policies-scripts state:present; slurp /proc/sys/crypto/fips_enabled register _tls_fips_enabled failed_when:false; debug skip message when fips==1; command update-crypto-policies --set policy changed_when:'Setting system policy to' in stdout when not fips AND _tls_current_policy.stdout != target (idempotent: only fires when policy differs); Debian/SUSE path: slurp _tls_openssl_cnf register _tls_cnf_content; blockinfile insertafter:EOF block:"[system_default_sect]\nMinProtocol = ...\nCipherString = ..." when 'system_default_sect' not in content b64decoded (use registered slurp result, NOT lookup('file') which reads controller not managed host); lineinfile regexp:'^\\s*MinProtocol\\s*=' line:"MinProtocol = {{ tls_hardening_min_version }}" insertafter:'^\[system_default_sect\]' backup:true; lineinfile for CipherString; shell connectivity test loop when check_services non-empty; debug completion report
- [x] 05-04: Molecule — molecule.yml (ubuntu2204 + rockylinux9, privileged:true); prepare.yml (Rocky 9 nsswitch fix); converge.yml (tls_hardening_enabled:true, security_mode:enforce, tls_hardening_check_services:[] — no connectivity check in containers); verify.yml (RHEL: command update-crypto-policies --show assert stdout == DEFAULT:NO-SHA1; Debian: shell grep MinProtocol /etc/ssl/openssl.cnf assert TLSv1.2 present; assert no change on second converge run — idempotence check via molecule idempotency sequence)
- [x] 05-05: CI integration — add tls_hardening to ci-uv.yml and ci-cd-enterprise.yml matrices; reinstall collection; run yamllint and ansible-lint --profile production; verify single-quoted strings in fail_msg/description (colons in strings require single-quotes per YAML conventions in this collection)

---

### Phase 05.1: SSH Access VM Test — commit workflow, playbook, and user_audit inventory for VM-based sssd_ad_integration validation (real sshd, sudoers, pam_access; no AD DC required) (INSERTED)

**Goal:** Commit and validate VM-based SSH access control test workflow, playbook, and user_audit test inventory for sssd_ad_integration structural validation (real sshd, sudoers, pam_access; no AD DC required).
**Requirements**: VMTEST-01, VMTEST-02, VMTEST-03, VMTEST-04
**Depends on:** Phase 5
**Plans:** 5/5 plans complete

Plans:
- [x] 05.1-01-PLAN.md -- Validate, lint, commit 3 untracked files and update ROADMAP

### Phase 6: usbguard

**Goal**: Implement USB device control role that reports USBGuard installation state and enforces block-by-default policy — generating an initial device whitelist from currently-attached hardware before starting the daemon to prevent lockout.
**Depends on**: Phase 5
**Requirements**: USB-01, USB-02, USB-03, USB-04, USB-05, USB-06, USB-07, STD-01, STD-02, STD-03, STD-04, STD-05, STD-06, STD-07, STD-08, STD-09, STD-10, STD-11, STD-12, STD-13, STD-14
**Success Criteria** (what must be TRUE):
  1. review.yml reports usbguard installation status, service state, current ImplicitPolicyTarget, and initial rules file presence — warns when USB bus is absent (container environment)
  2. enforce.yml follows correct task order: install → generate-policy (write-once) → deploy rules.d/00-initial-policy.conf → deploy daemon.conf → start service; generate-policy is skipped on subsequent runs if rules file already exists
  3. Container-aware: stat /sys/bus/usb/devices is used for detection (more reliable than virtualization_type); enforce tasks call meta:end_host gracefully when USB bus is absent
  4. usbguard-daemon.conf has mode 0600 (daemon refuses to start otherwise); IPCAllowedGroups uses wheel (RHEL/SUSE) or sudo (Debian) from OS-specific vars
  5. yamllint and ansible-lint --profile production pass with 0 errors; Molecule verify.yml asserts graceful skip behaviour on containers (review report present, no enforcement errors)

**Plans**: 5 plans

Plans:
- [x] 06-01: Scaffold usbguard — `ansible-galaxy role init`, defaults/main.yml (usbguard_enabled, usbguard_implicit_policy:block, usbguard_allow_existing_devices:true, usbguard_present_device_policy:apply-policy, usbguard_present_controller_policy:apply-policy, usbguard_restore_controller_state:false, usbguard_audit_backend:LinuxAudit, usbguard_audit_file_path:/var/log/usbguard/usbguard-audit.log, usbguard_extra_rules:[]), vars/RedHat.yml (_usbguard_package:usbguard, _usbguard_service:usbguard, _usbguard_conf_dir:/etc/usbguard, _usbguard_rules_dir:/etc/usbguard/rules.d, _usbguard_daemon_conf:/etc/usbguard/usbguard-daemon.conf, _usbguard_initial_rules:/etc/usbguard/rules.d/00-initial-policy.conf, _usbguard_needs_epel:"{{ ansible_distribution_major_version|int == 8 }}", _usbguard_ipc_group:wheel), vars/Debian.yml (same paths, _usbguard_needs_epel:false, _usbguard_ipc_group:sudo), vars/Suse.yml (same paths, _usbguard_needs_epel:false, _usbguard_ipc_group:wheel), meta/main.yml, meta/argument_specs.yml (choices for implicit_policy:[allow,block,reject] and present_device_policy:[allow,block,reject,apply-policy,keep]), tests/test.yml, handlers/main.yml (Restart usbguard with ansible.builtin.service changed_when:true)
- [x] 06-02: Tasks — tasks/main.yml (gather_subset:[min,virtual] to populate virtualization_type, OS assert, include_vars with first_found, stat /sys/bus/usb/devices register _usbguard_usb_bus tags:[always], set_fact _usbguard_usb_available from stat.exists tags:[always], package_facts manager:auto tags:[always], include review.yml, include enforce.yml when enabled+enforce); tasks/review.yml (package_facts + service_facts; shell grep ImplicitPolicyTarget from daemon_conf failed_when:false; stat initial_rules file; debug report block with all findings including USB bus availability warning and RHEL 8 EPEL warning when applicable)
- [x] 06-03: Tasks enforce.yml (full implementation) — debug+meta:end_host when not _usbguard_usb_available (graceful container skip); package_facts for EPEL assert when RHEL 8; package install usbguard; file rules_dir 0750; stat initial_rules register _usbguard_rules_existing; shell usbguard generate-policy register _usbguard_generated_policy changed_when:false when allow_existing_devices+not rules_existing; copy content:generated_policy+newline to initial_rules 0640 when allow_existing_devices+not rules_existing+policy non-empty; copy usbguard_extra_rules joined content to rules.d/10-extra-rules.conf when extra_rules non-empty notify:Restart usbguard; template usbguard-daemon.conf.j2 dest:daemon_conf mode:"0600" notify:Restart usbguard; service enable+start usbguard; service_facts post; assert service running; debug completion report; templates/usbguard-daemon.conf.j2 (RuleFile + RuleFolder pointing to rules_dir, ImplicitPolicyTarget, PresentDevicePolicy, PresentControllerPolicy, RestoreControllerDeviceState ternary true/false, InsertDRID:false, AuthorizedDefault:none, IPCAllowedUsers:root, IPCAllowedGroups:_usbguard_ipc_group, AuditBackend, conditional AuditFilePath when FileAudit)
- [x] 06-04: Molecule — molecule.yml (ubuntu2204 + rockylinux9, privileged:true); prepare.yml (Rocky 9 nsswitch fix; note: RHEL 8 EPEL not needed for RHEL 9); converge.yml (usbguard_enabled:true, security_mode:enforce — will hit end_host in containers due to no USB bus); verify.yml (assert _usbguard_usb_available is false in container context; assert review debug output was produced; assert no enforcement errors occurred; assert package_facts were gathered; do NOT assert usbguard is running — containers have no USB bus and enforce gracefully skips)
- [x] 06-05: CI integration + milestone close — add usbguard to ci-uv.yml and ci-cd-enterprise.yml matrices; reinstall collection; run yamllint and ansible-lint --profile production confirming 0 errors; bump galaxy.yml version 1.1.0 → 1.2.0; update CHANGELOG.md promoting [Unreleased] section to [1.2.0] - 2026-04-14 listing all 6 new roles with their compliance framework tags; run `ansible-galaxy collection build --force` to verify build succeeds

---

## Dependencies

- Phases 1-6 are independent of each other at the role level (roles do not call each other)
- Each phase depends on the collection install patterns established in the previous phase
- Phase 4 (antivirus) requires EPEL on RHEL 8/9 — documented in role defaults and README; not a blocker for CI since Molecule tests set antivirus_update_db:false
- Phase 6 (usbguard) requires physical USB bus for full enforcement — Molecule tests verify graceful container skip only; VM-level testing deferred to kernel-vm-test workflow

## Version Bump

After all 6 phases complete: bump galaxy.yml version 1.1.0 → 1.2.0, update CHANGELOG.md.
This is included in Phase 6 plan 06-05.

## Traceability Update

See REQUIREMENTS.md Traceability section for full requirement-to-phase mapping.

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. ntp_hardening | 1/5 | Complete    | 2026-04-20 |
| 2. user_audit | 7/7 | Complete   | 2026-04-18 |
| 3. rsyslog_forwarding | 5/5 | Complete   | 2026-04-18 |
| 4. antivirus | 5/5 | Complete   | 2026-04-18 |
| 5. tls_hardening | 5/5 | Complete   | 2026-04-19 |
| 6. usbguard | 5/5 | Complete    | 2026-04-20 |

### Phase 7: tech-debt

**Goal:** Close pre-Galaxy-publish technical debt: replace all 7 role README placeholders with real documentation, pin all Molecule images to SHA digests, replace `command: sed` with `ansible.builtin.lineinfile` in all prepare.yml files, fill argument_specs gaps in sssd_ad_integration, rebuild the `.venv` to fix broken pre-commit shebangs, and tighten CI permissions.
**Requirements**: TECH-01 through TECH-06
**Depends on:** Phase 06.1
**Success Criteria** (what must be TRUE):
  1. All 7 role READMEs have role-specific content (no ansible-galaxy scaffold placeholders)
  2. All Molecule platform images use SHA digest pins (no `:latest` floating tags)
  3. All prepare.yml files use `ansible.builtin.replace` instead of `command: sed`
  4. sssd_ad_integration argument_specs covers IPA vars and ssh_identity_backend
  5. `.venv/bin/pre-commit` shebang works (normal `git commit` runs hooks without wrapper)
  6. CI workflows have minimal permissions (no unnecessary `contents: write`)
**Plans:** 2/4 plans executed

Plans:
- [ ] 07-01-PLAN.md -- Role READMEs (7 roles)
- [x] 07-02-PLAN.md -- Molecule SHA digest pins (all roles)
- [x] 07-03-PLAN.md -- prepare.yml sed→lineinfile + argument_specs gaps + CI permissions
- [x] 07-04-PLAN.md -- venv rebuild

---

### Phase 06.1: Security audit remediations — CRITICAL-01, HIGH-01, HIGH-03, MEDIUM-02 (HIGH) (INSERTED)

**Goal:** Remediate 4 security audit findings: corp LAN MFA downgrade (CRIT-01), offline credential expiration never expires (HIGH-01), verify_groups_strict unsafe default (HIGH-03), ClamAV scan runs as root (MED-02). All fixes use secure-by-default values with opt-out for backward compatibility.
**Requirements**: AUDIT-CRIT-01, AUDIT-HIGH-01, AUDIT-HIGH-03, AUDIT-MED-02
**Depends on:** Phase 6
**Success Criteria** (what must be TRUE):
  1. ssh_corp_require_mfa variable controls MFA in corp Match Address block; when true, AuthenticationMethods = publickey,keyboard-interactive
  2. sssd_offline_credentials_expiration defaults to 7 (not 0); argument_specs documents the risk
  3. ssh_verify_groups_strict defaults to true (not false); argument_specs documents lockout risk
  4. clamav-scan.service runs as antivirus_clamd_user (not root); no User=root in template
  5. yamllint + ansible-lint pass on all modified files
**Plans:** 2/2 plans complete

Plans:
- [x] 06.1-01-PLAN.md -- sssd_ad_integration remediations: AUDIT-CRIT-01 (corp MFA toggle), AUDIT-HIGH-01 (offline cred expiry 0->7), AUDIT-HIGH-03 (verify_groups_strict false->true)
- [x] 06.1-02-PLAN.md -- antivirus remediation: AUDIT-MED-02 (clamav-scan.service User=root -> antivirus_clamd_user)
