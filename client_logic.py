from phe import paillier
import json

# geneate both public key and private key
public_key, private_key = paillier.generate_paillier_keypair()

def encrypt_plain_array(plaintext_array,public_key):
    encrypted_array=[]
    for element in plaintext_array:
        enc = public_key.encrypt(element)
        encrypted_array.append(enc)
    return encrypted_array

def decrypt_plain_array(cipher_text_array,private_key):
    decrypted_array=[]
    for element in cipher_text_array:
        enc = private_key.decrypt(element)
        decrypted_array.append(enc)
    return decrypted_array

def register(roll_number,finger_print_inverse):
    user_dict = {"roll_number":roll_number,"fingerprint_inverse":finger_print_inverse}
    json_data = json.dumps(user_dict,indent=2)
    return json_data

# print(register("b170212cs","1,2,3,4,5,6"))