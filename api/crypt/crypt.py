import ipfsapi
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP as ecrypt
from Crypto import Random
import ast
import json

# example keystore; replace with redis or equivalent
keystore = {}
user = ''

# CORE FUNCTIONS ============================================================

# FUNCTION: 	encrypt a message with public key
# ARGS:         message: bytestream; pubkey: RSA public key
# RETURN:		encrypted message (bytes)


def encrypt(message, pubkey):
    encryptor = ecrypt.new(pubkey)
    if (type(message) == str):
        bm = bytes(message, 'utf-8')
    elif (type(message) == bytes):
        bm = bytes(message)
    return encryptor.encrypt(bm)


# FUNCTION: 	decrypt a message with private key
# RETURN:		decrypted message (string)
def decrypt(encMessage, prvkey):
    decryptor = ecrypt.new(prvkey)
    return decryptor.decrypt(ast.literal_eval(str(encMessage)))


# FUNCTION:		generate a random keypair
# RETURN:		RSA key
def newKey():
    rando_gen = Random.new().read
    key = RSA.generate(2048, rando_gen)
    return key


# TEST FUNCTIONS ============================================================
# FUNCTION:		sample keystore ("pre-runtime") (global vars)
# RETURN:		none
def testInit():
    # sample user ID
    user = 'unique_user_id'

    # generate new keypair
    key = newKey()

    # store user's key in database -- this is probably a terrible practice
    keystore[user] = key


# FUNCTION: 	sample runtime usage
# RETURN:		none
def test():
    # encrypt some data with user in keystore
    user = 'unique_user_id'
    message = "this is some secret data"
    key = keystore[user]
    data = encrypt(message, key.publickey())
    print("encrypted data: " + str(data))

    # decrypt data with user in keystore
    output = decrypt(data, key)
    print("decrypted data: " + str(output))

    # generate new keypair
    key = newKey()

    # encrypt some data with new key
    message = "this is some new secret data"
    data = encrypt(message, key.publickey())
    print("encrypted data: " + str(data))
    print("decrypted data: " + str(decrypt(data, key)))


testInit()
test()
