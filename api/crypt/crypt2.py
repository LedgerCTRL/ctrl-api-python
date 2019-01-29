import pyAesCrypt
import io

buffsize = 64 * 2048

# # binary data to be encrypted
# pbdata = b"this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. this is binary plaintext. "

# # input plaintext binary stream
# fin = io.BytesIO(pbdata)

# # init cyphertext bin stream
# fciph = io.BytesIO()

# # init decrypted bin stream
# fdec = io.BytesIO()

# # encrypt stream
# pyAesCrypt.encryptStream(fin, fciph, password, buffsize)

# # print encrypted data
# print("encrypted data: " + str(fciph.getvalue()))

# # get ciphertext length
# ctlen = len(fciph.getvalue())

# # go back to start of ciphertext stream
# fciph.seek(0)

# # decrypt stream
# pyAesCrypt.decryptStream(fciph, fdec, password, buffsize, ctlen)

# # print decrypted data
# print("decrypted data: " + str(fdec.getvalue()))


# message: a string or bytestream or bytes
# pubkey: a string
# encrypts a message in memory
def encrypt(message, pubkey):
    if (type(message) == str):
        data = bytes(message, 'utf-8')
    elif (type(message) == bytes):
        data = message

    # input plaintext binary stream
    fin = io.BytesIO(data)

    # init cyphertext bin stream
    fciph = io.BytesIO()

    # encrypt stream
    pyAesCrypt.encryptStream(fin, fciph, data, buffsize)

    # print encrypted data
    print("encrypted data: " + str(fciph.getvalue()))
