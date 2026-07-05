================================================================================
                       HYDRA (THC-HYDRA) - LAB MANUAL
            Network Login Brute-Forcing & Credential Auditing
================================================================================

  Topic     : Auditing network service authentication using Hydra
  Audience  : Beginners learning offensive security / credential auditing
  Tool      : Hydra (THC-Hydra)


--------------------------------------------------------------------------------
  TABLE OF CONTENTS
--------------------------------------------------------------------------------

  1.  What Is Hydra?
  2.  Core Concept: How Hydra Attacks Work
  3.  Command Syntax Anatomy
  4.  Credential Input Options (Users & Passwords)
  5.  Supported Protocols / Modules
  6.  Hands-On Scenarios (SSH, FTP, HTTP Form, RDP)
  7.  Tuning Speed, Threads & Timing
  8.  Reading Hydra Output
  9.  Session Resume & Output Logging
  10. Common Errors & Troubleshooting
  11. Quick Reference Cheat Sheet
  12. Glossary


--------------------------------------------------------------------------------
  1. WHAT IS HYDRA?
--------------------------------------------------------------------------------

  Hydra is a fast, parallelized network login cracker. Unlike John the
  Ripper (which cracks OFFLINE password hashes you already have), Hydra
  attacks LIVE, ONLINE services directly over the network - it actually
  sends login attempts to a real service (SSH, FTP, a web login form,
  RDP, databases, etc.) and checks whether each attempt succeeds.

  KEY DIFFERENCE FROM JOHN THE RIPPER:

    John the Ripper   -> Cracks a hash you already have, OFFLINE, no
                         network traffic, no lockout risk.
    Hydra             -> Sends real login attempts to a live target,
                         ONLINE, generates network traffic, CAN trigger
                         account lockouts / IDS alerts / rate limiting.

  ETHICS + SAFETY REMINDER:

    Only run Hydra against systems you own or are explicitly authorized
    to test in writing. Online brute-forcing is noisy, can lock out real
    accounts, and can crash fragile services if run too aggressively.
    Since this manual assumes you have no target yet, treat every example
    below as syntax reference - swap in an authorized target IP before
    actually running anything.


--------------------------------------------------------------------------------
  2. CORE CONCEPT: HOW HYDRA ATTACKS WORK
--------------------------------------------------------------------------------

  Hydra needs 4 pieces of information to run an attack:

    1. TARGET       - the IP/hostname of the service to attack
    2. SERVICE      - which protocol module to use (ssh, ftp, http-post-form, etc.)
    3. USERNAME(S)  - a single username, or a list of usernames to try
    4. PASSWORD(S)  - a single password, or a wordlist of passwords to try

  Hydra then tries EVERY combination of username x password against the
  target service, in parallel (multiple attempts at once via threads),
  until it finds a match or exhausts the list.

  THE ATTACK LOOP (SIMPLE VIEW)

    STEP 1 - Load username list and password list
    STEP 2 - Pick a username + password pair
    STEP 3 - Send that pair as a real login attempt to the target service
    STEP 4 - Check the service's response

        Login accepted  -> Save credentials as valid  -> report success
        Login rejected  -> Discard pair, try next combination

    STEP 5 - Repeat steps 2-4 for every combination, using multiple
             parallel threads to speed things up


--------------------------------------------------------------------------------
  3. COMMAND SYNTAX ANATOMY
--------------------------------------------------------------------------------

  General structure:

    hydra [ USER OPTIONS ] [ PASSWORD OPTIONS ] [ TUNING OPTIONS ] TARGET SERVICE

  Example broken down:

    hydra -l admin -P rockyou.txt -t 4 192.168.1.10 ssh
           |         |             |    |            |
           |         |             |    |            +-- service/module (ssh)
           |         |             |    +-- target IP/hostname
           |         |             +-- 4 parallel threads
           |         +-- password wordlist to try
           +-- single username to try

  Reading it in plain English:
    "Try the username 'admin' against every password in rockyou.txt,
     using 4 parallel connections, targeting SSH on 192.168.1.10."


--------------------------------------------------------------------------------
  4. CREDENTIAL INPUT OPTIONS (USERS & PASSWORDS)
--------------------------------------------------------------------------------

  USERNAME OPTIONS

    -l <username>     Try a single, specific username
    -L <file>         Try every username listed in a file (one per line)

  PASSWORD OPTIONS

    -p <password>     Try a single, specific password
    -P <file>         Try every password listed in a file (one per line)

  COMBINED CREDENTIAL FILE

    -C <file>         Use a single file containing username:password
                       pairs directly, instead of separate user/pass lists.
                       Format inside the file:  admin:password123

  EXAMPLES

    -l admin -P rockyou.txt         one username, full password list
    -L users.txt -P rockyou.txt     full username list x full password list
    -L users.txt -p Summer2026!     full username list, one password
                                     (useful for "password spraying")
    -C creds.txt                     pre-paired username:password combos


--------------------------------------------------------------------------------
  5. SUPPORTED PROTOCOLS / MODULES
--------------------------------------------------------------------------------

  Hydra supports many service modules. Some of the most commonly used:

    ssh                  SSH login
    ftp                  FTP login
    telnet               Telnet login
    smb                  Windows SMB / file sharing login
    rdp                  Remote Desktop Protocol login
    mysql                MySQL database login
    postgres             PostgreSQL database login
    http-get             HTTP Basic Auth over GET
    http-post-form       HTML login forms (POST request)
    https-post-form      HTML login forms over HTTPS
    smtp                 Email (SMTP) login
    pop3 / imap          Email retrieval protocol login
    vnc                  VNC remote desktop login

  See the full list any time with:

    hydra -U


--------------------------------------------------------------------------------
  6. HANDS-ON SCENARIOS
--------------------------------------------------------------------------------

  Replace <TARGET_IP> with an authorized lab target before running any
  of these. Since no target is set up yet, treat these as syntax templates.


  SCENARIO A - SSH Brute Force

    hydra -l admin -P /usr/share/wordlists/rockyou.txt <TARGET_IP> ssh

  What it does: tries the username "admin" against every password in
  rockyou.txt over SSH (default port 22).


  SCENARIO B - FTP Brute Force with Username List

    hydra -L users.txt -P /usr/share/wordlists/rockyou.txt <TARGET_IP> ftp

  What it does: tries every username in users.txt against every password
  in rockyou.txt over FTP (default port 21).


  SCENARIO C - HTTP POST Login Form

    hydra -l admin -P rockyou.txt <TARGET_IP> http-post-form \
      "/login.php:username=^USER^&password=^PASS^:Invalid login"

  Breaking down the http-post-form argument (it has 3 colon-separated parts):

    Part 1: /login.php
            -> the path to the login endpoint

    Part 2: username=^USER^&password=^PASS^
            -> the POST body template. ^USER^ and ^PASS^ are placeholders
               Hydra substitutes with each username/password attempt.

    Part 3: Invalid login
            -> a string that appears on the page ONLY when login FAILS.
               Hydra uses this to tell a failed attempt from a successful one.

  TIP: You can also specify a success-condition instead by prefixing the
  third part with "S=" instead of "F=", e.g. S=Welcome  matches on success
  text rather than failure text.


  SCENARIO D - RDP Brute Force

    hydra -l administrator -P rockyou.txt <TARGET_IP> rdp

  What it does: tries RDP login (Windows Remote Desktop, default port 3389).
  Note: RDP attacks are slow and prone to lockouts - keep thread count low.


--------------------------------------------------------------------------------
  7. TUNING SPEED, THREADS & TIMING
--------------------------------------------------------------------------------

    -t <N>       Number of parallel tasks/threads (default 16 for most
                 modules). Higher = faster, but noisier and more likely
                 to trigger lockouts or crash a fragile service.

    -w <sec>     Max wait time for a response before giving up on a try

    -W <sec>     Wait time between connection attempts

    -f           Stop as soon as ONE valid username/password pair is found
                 (useful once you just need to prove a credential works)

    -F           Stop as soon as a valid pair is found, for every host
                 being tested (useful with multiple targets)

    -s <port>    Specify a non-default port for the service

    -v / -V      Verbose mode - show each attempt as it happens

  GUIDANCE FOR STUDENTS:

    Start with a LOW thread count (e.g. -t 4) on any real test, especially
    against services like RDP, SMB, or anything with account lockout
    policies. High thread counts are fine for local practice labs but can
    cause real account lockouts or denial-of-service on production systems.


--------------------------------------------------------------------------------
  8. READING HYDRA OUTPUT
--------------------------------------------------------------------------------

  A successful crack looks like this:

    [22][ssh] host: 192.168.1.10   login: admin   password: Summer2026!

  Breaking it down:

    [22][ssh]     -> port and service that was attacked
    host: ...     -> the target
    login: ...    -> the username that worked
    password: ...  -> the password that worked

  At the end of a run, Hydra also prints a summary line showing how many
  total login pairs were tried and how many valid pairs were found.


--------------------------------------------------------------------------------
  9. SESSION RESUME & OUTPUT LOGGING
--------------------------------------------------------------------------------

  SAVE RESULTS TO A FILE

    -o results.txt        Write found credentials to results.txt

  RESTORE AN INTERRUPTED SESSION

    Hydra can save its progress and resume later if interrupted:

    -R                    Resume the previous session (uses hydra.restore)

  Example: if a long scan gets killed (Ctrl+C) partway through, just re-run:

    hydra -R

  and Hydra will pick up where it left off using its restore file.


--------------------------------------------------------------------------------
  10. COMMON ERRORS & TROUBLESHOOTING
--------------------------------------------------------------------------------

  "Error: You must supply a login name or a login file"

    -> You forgot -l or -L. Every run needs at least one username source.

  Attack finishes instantly with 0 valid passwords found

    -> Check the service is actually reachable (try connecting manually
       first, e.g. ssh admin@<target> or curl the login page).
    -> For http-post-form, double check the failure/success string is
       EXACT - a mismatch means Hydra can never detect a real success.
    -> Confirm you're using the correct port with -s if it's non-default.

  Attack seems to hang or times out on every attempt

    -> Lower thread count with -t
    -> Increase wait time with -w
    -> The service may have lockout/rate-limiting kicking in after a few
       failed attempts, which will make everything after look like a fail.

  "Restoring backup" prompts unexpectedly

    -> Hydra found a leftover hydra.restore file from a previous run.
       Use -R to resume it, or delete hydra.restore to start fresh.


--------------------------------------------------------------------------------
  11. QUICK REFERENCE CHEAT SHEET
--------------------------------------------------------------------------------

  USERNAME / PASSWORD INPUT

    -l <user>          single username
    -L <file>          username list file
    -p <pass>          single password
    -P <file>          password list file
    -C <file>          combined user:pass file

  TUNING

    -t <N>             parallel threads (default varies by module)
    -w <sec>           response wait time
    -W <sec>           wait between attempts
    -f                 stop after first valid pair found (single host)
    -F                 stop after first valid pair found (all hosts)
    -s <port>          specify non-default port
    -v / -V            verbose output

  OUTPUT / SESSION

    -o <file>          save found credentials to file
    -R                 resume previous interrupted session

  MODULE LIST

    hydra -U            show every supported protocol/module

  COMMON MODULES

    ssh, ftp, telnet, smb, rdp, mysql, postgres, http-get,
    http-post-form, https-post-form, smtp, pop3, imap, vnc

  BASIC TEMPLATE

    hydra -l <user> -P <wordlist> <target_ip> <service>


--------------------------------------------------------------------------------
  12. GLOSSARY
--------------------------------------------------------------------------------

    Brute force        Trying many username/password combinations until
                        one works, rather than guessing intelligently.

    Password spraying   Trying ONE common password across MANY usernames,
                        to avoid triggering per-account lockouts.

    Module              The protocol-specific plugin Hydra uses to know
                        how to talk to a given service (ssh, ftp, etc.)

    Thread               A single parallel connection/attempt running
                        alongside others to speed up the attack.

    Lockout              A security control that disables/blocks an
                        account after too many failed login attempts.

    Restore file         hydra.restore - lets you resume an interrupted
                        Hydra session instead of starting over.

    Success/failure
    condition            The specific text or response Hydra looks for to
                        decide whether a login attempt worked, mainly
                        used in the http-post-form module.

================================================================================
                              END OF LAB MANUAL
================================================================================
