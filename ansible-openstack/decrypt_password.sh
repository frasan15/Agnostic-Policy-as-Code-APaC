#!/bin/bash

openssl enc -d -aes-256-cbc -salt -pbkdf2 -in encrypted_password.enc -out decrypted_password.txt