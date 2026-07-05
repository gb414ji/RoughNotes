================================================================================
                     JOHN THE RIPPER (JTR) - LAB MANUAL
              Password Hash Auditing with Wordlists & Rules
================================================================================

  Topic     : Password hash auditing using wordlists and rule mutations
  Audience  : Beginners learning offensive security / password auditing
  Tool      : John the Ripper (JTR)


--------------------------------------------------------------------------------
  TABLE OF CONTENTS
--------------------------------------------------------------------------------

  1.  What Is John the Ripper?
  2.  Core Concept: Wordlists vs Rules
  3.  Deep Dive: How Rules & Mutation Work
  4.  Lab Environment Setup
  5.  Hands-On Scenarios (A, B, C)
  6.  Debugging: Watching Rules Generate Candidates
  7.  Extracting Hashes From Real Files
  8.  Session & Cache Management
  9.  Quick Reference Cheat Sheet
  10. Glossary


--------------------------------------------------------------------------------
  1. WHAT IS JOHN THE RIPPER?
--------------------------------------------------------------------------------

  John the Ripper is a password-cracking tool used to test the strength of
  password hashes. It does not "hack" a password directly. Instead, it:

    1. Guesses a candidate password
    2. Hashes that guess using the same algorithm as the original
    3. Checks if the result matches the target hash
    4. Repeats until it finds a match or runs out of guesses

  ETHICS REMINDER:
    Only run John against hashes you own, or systems/data you have explicit
    written authorization to test. This manual uses self-created test hashes.

  ATTACK MODES (the two below are used in this lab):

    Wordlist mode         -> Tries every word in a dictionary, one at a time
    Wordlist + Rules mode -> Mutates each word into many variations first

  Not covered in this lab (more advanced):

    Incremental mode -> Brute-forces every possible character combination
    Mask mode         -> Brute-forces a pattern you define, e.g. ?u?l?l?l?d?d


--------------------------------------------------------------------------------
  2. CORE CONCEPT: WORDLISTS VS RULES
--------------------------------------------------------------------------------

  PURE WORDLIST ATTACK
  ---------------------
    John reads a wordlist file and checks each entry EXACTLY as written.
    No changes. No guessing variations.

    + Fast
    - Only works if the real password appears in your list word-for-word

    Example: if the real password is "P@ssword123" but your wordlist only
    has "password", this attack will NEVER find it.


  RULE-BASED MUTATION ATTACK  (--rules)
  ---------------------------------------
    Instead of trying each word as-is, John runs every word through a set
    of transformation rules and tests each mutated result.

    This mimics real human password habits, such as:

      - Capitalizing the first letter      password  -> Password
      - Leet-speak substitution             password  -> p4ssw0rd
      - Adding a number/year suffix         password  -> password123
      - Combining several habits at once    password  -> P4ssword123!


  COMPARISON

    Attack Type        Speed     Coverage                  Best For
    -----------------  --------  ------------------------  ------------------------
    Pure wordlist       Fast      Narrow (exact match only)  Quick pass, common creds
    Wordlist + rules     Slower    Broad (realistic variants) Real-world audits


--------------------------------------------------------------------------------
  3. DEEP DIVE: HOW RULES & MUTATION WORK
--------------------------------------------------------------------------------

  WHAT IS A "RULE," TECHNICALLY?

    A rule is a short instruction telling John how to transform a word.
    Rules live inside john.conf under sections like [List.Rules:Wordlist].
    Passing --rules loads that section and applies EVERY rule in it to
    EVERY word in your wordlist.

    Example: 4 words in your wordlist x 50 rules in your ruleset
             = up to 200 candidate passwords generated and tested.


  COMMON RULE SYMBOLS  (word used: "password")

    Symbol     Meaning                          Result
    ---------  -------------------------------  -------------------
    c          Capitalize first letter          Password
    u          Make entirely uppercase          PASSWORD
    l          Make entirely lowercase          password
    r          Reverse the word                 drowssap
    d          Duplicate the word                passwordpassword
    $1         Append "1" to the end             password1
    $!         Append "!" to the end             password!
    ^1         Prepend "1" to the front          1password
    sa@        Replace every "a" with "@"        p@ssword
    so0        Replace every "o" with "0"        passw0rd


  CHAINING RULES TOGETHER

    Rules can be combined on a single line to stack transformations.
    This is how you get:  password  ->  P@ssword123

        c so0 sa@ $1 $2 $3

    Read left to right:
      c     -> capitalize
      so0   -> swap o with 0
      sa@   -> swap a with @
      $1$2$3 -> append 1, 2, 3


  THE MUTATION PIPELINE (SIMPLE STEP-BY-STEP)

    Think of it as an assembly line with 4 stations. Here is what happens
    to one word, "password", as it moves through:

    STEP 1 - Start with the raw word

        password

    STEP 2 - The rule engine generates several mutated versions

        password  ->  Password        (capitalized)
        password  ->  p4ssw0rd        (leet-speak substitution)
        password  ->  password123     (suffix appended)
        password  ->  P@ssword123     (all of the above, combined)

    STEP 3 - Each mutated version is hashed and compared to the target

        hash(Password)     == target hash ?   ->  No
        hash(p4ssw0rd)     == target hash ?   ->  No
        hash(password123)  == target hash ?   ->  No
        hash(P@ssword123)  == target hash ?   ->  Yes  [MATCH]

    STEP 4 - Outcome

        Match found  ->  Save "P@ssword123" to potfile  ->  CRACKED
        No match     ->  Discard candidate, try the next one

    IN SHORT:
      one word in  ->  many mutated guesses out  ->  each guess hashed
      and checked  ->  first match wins


  WHY A RULE ATTACK CAN STILL FAIL

    The default ruleset only contains a finite, predefined list of
    transformations. If a real password uses a combination that is not
    in that list (e.g. mutating only the 2nd letter, or putting a symbol
    before the numbers instead of after), the exact candidate is never
    generated - so John reports 0 cracked, even though the password looks
    "simple" to a human.

    KEY TAKEAWAY: rule-based cracking is only as good as the ruleset you
    use. Larger community rule packs (Jumbo rules, OneRuleToRuleThemAll)
    cover far more realistic patterns, at the cost of speed.


--------------------------------------------------------------------------------
  4. LAB ENVIRONMENT SETUP
--------------------------------------------------------------------------------

  Run this block to create your lab folder, generate a test hash for a
  password you chose yourself, and build a small starter wordlist.

    mkdir -p ~/lab2 && cd ~/lab2

    # 1. Generate a salted SHA-512 Linux-style hash ($6$) for a test password
    echo "victim_user:$(openssl passwd -6 P@ssword123)" > my_test_hash.txt

    # 2. Build a small starter wordlist of common weak passwords
    echo -e "password\nadmin\nqwerty\nwelcome" > small_dict.txt

  WHAT JUST HAPPENED:

    - openssl passwd -6 generates a real salted SHA-512 crypt hash, the
      same format used in /etc/shadow on Linux.
    - small_dict.txt is your dictionary - kept small and weak on purpose
      to keep the lab fast.


--------------------------------------------------------------------------------
  5. HANDS-ON SCENARIOS
--------------------------------------------------------------------------------

  SCENARIO A - Pure Wordlist Attack (Baseline)
  ----------------------------------------------
  Goal: see what happens when the wordlist does not match the password.

    john --format=sha512crypt --wordlist=small_dict.txt my_test_hash.txt

  Expected result: 0g DONE (0 guesses cracked). Proves plain dictionary
  words tried as-is cannot match a password with mixed case + symbol + digits.


  SCENARIO B - Wordlist + Rule-Based Mutation Attack
  ----------------------------------------------------
  Goal: let John mutate each word using its built-in rules, then re-test.

    john --format=sha512crypt --wordlist=small_dict.txt --rules my_test_hash.txt

  Possible outcome: still 0g. The default ruleset applies common
  transformations, but if none of them produce the EXACT combination needed
  (capital P + @ for a + 123 suffix, together), the candidate never gets
  generated. Lesson: rules only work if the ruleset covers that exact pattern.


  SCENARIO C - Exact Payload Proof of Concept
  -----------------------------------------------
  Goal: confirm your whole pipeline works, by giving John the literal answer.

    # Add the exact real password directly into the wordlist
    echo "P@ssword123" >> small_dict.txt

    # Re-run the same baseline command from Scenario A
    john --format=sha512crypt --wordlist=small_dict.txt my_test_hash.txt

  Expected result: CRACKED. "P@ssword123" is reported as cracked. This
  confirms your command syntax and hash format were correct all along -
  the earlier 0g results were about wordlist/rule coverage, not a mistake.


--------------------------------------------------------------------------------
  6. DEBUGGING: WATCHING RULES GENERATE CANDIDATES
--------------------------------------------------------------------------------

  To see exactly what mutated words a ruleset produces, without attacking
  any hash, use --stdout:

    john --wordlist=small_dict.txt --rules --stdout

  This prints every generated candidate to your terminal. Best way to
  answer "why didn't this crack?" - scroll through and check whether your
  target password's exact form appears in the list.


--------------------------------------------------------------------------------
  7. EXTRACTING HASHES FROM REAL FILES
--------------------------------------------------------------------------------

  Many real-world targets don't hand you a hash directly. You extract it
  from the file format first using a helper tool, then feed it to John.

  SCENARIO D - Password-Protected ZIP Files

    zip2john secret.zip > zip_hash.txt
    john --wordlist=/usr/share/wordlists/rockyou.txt zip_hash.txt
    john --show zip_hash.txt

  SCENARIO E - Encrypted SSH Private Keys

    ssh2john ~/.ssh/id_rsa > ssh_hash.txt
    john --wordlist=/usr/share/wordlists/rockyou.txt ssh_hash.txt
    john --show ssh_hash.txt

  NOTE: similar *2john helper scripts exist for other formats too -
  office2john (Word/Excel), pdf2john (PDF), rar2john (RAR archives).
  Pattern is always the same: extract -> crack -> show.


--------------------------------------------------------------------------------
  8. SESSION & CACHE MANAGEMENT
--------------------------------------------------------------------------------

  RECOVER PREVIOUSLY CRACKED CREDENTIALS

    John remembers every cracked hash in a file called the "potfile". If
    you re-run an attack on an already-cracked hash, John instantly shows
    0g - not because it failed, but because it's already solved.

      john --show my_test_hash.txt

  INSPECT THE RAW POTFILE

      cat ~/.john/john.pot

    Stores every hash:plaintext pair John has ever cracked on this machine.

  RESET THE POTFILE (force a fresh crack, useful for re-demoing a lab)

      rm -f ~/.john/john.pot


--------------------------------------------------------------------------------
  9. QUICK REFERENCE CHEAT SHEET
--------------------------------------------------------------------------------

  COMMANDS / FLAGS

    --format=<type>        Tells John how to interpret the hash
                            (e.g. sha512crypt, nt, raw-md5)
    --wordlist=<file>       Supplies a dictionary of candidate passwords
    --rules                 Applies transformation rules to every word
    --stdout                 Prints generated candidates, does not crack
    --show <hashfile>        Displays previously cracked plaintexts
    zip2john <file.zip>      Converts a protected ZIP into a crackable hash
    ssh2john <keyfile>       Converts an encrypted SSH key into a crackable hash

  POTFILE LOCATION

    ~/.john/john.pot   ->  stores every cracked hash:plaintext pair

  COMMON RULE SYMBOLS

    c      Capitalize first letter
    u      Make entirely uppercase
    l      Make entirely lowercase
    r      Reverse the word
    d      Duplicate the word
    $X     Append character X
    ^X     Prepend character X
    saX    Substitute all "a" with X
    soX    Substitute all "o" with X


--------------------------------------------------------------------------------
  10. GLOSSARY
--------------------------------------------------------------------------------

    Hash               A one-way scrambled password representation; can't
                        be reversed directly, only guessed and re-hashed
                        for comparison.

    Wordlist           A text file of candidate passwords, one per line.

    Rule               An instruction that mutates a wordlist word into a
                        new candidate (e.g. capitalize, add symbols).

    Mutation           The result of applying one or more chained rules
                        to a word.

    Potfile            John's local database of previously cracked
                        hash:plaintext pairs.

    0g                 Shorthand for "0 guesses cracked" in a given run.

    Attack mode        The overall strategy John uses to generate
                        candidates: wordlist, wordlist+rules, mask, or
                        incremental.

================================================================================
                              END OF LAB MANUAL
================================================================================
