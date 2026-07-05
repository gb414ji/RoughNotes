# Generate the targeted Linux SHA-512 crypt hash
echo "victim_user:$(openssl passwd -6 P@ssword123)" > my_test_hash.txt

# Add the explicit password payload to your dictionary
echo "P@ssword123" >> small_dict.txt

# Run the direct dictionary attack
john --format=sha512crypt --wordlist=small_dict.txt my_test_hash.txt

# Run the dictionary attack with mutation rules enabled
john --format=sha512crypt --wordlist=small_dict.txt --rules my_test_hash.txt

# Display any cracked passwords for this target
john --show my_test_hash.txt

# View John's persistent cracked password storage
cat ~/.john/john.pot
