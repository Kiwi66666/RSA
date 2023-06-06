from pytube import YouTube
import matplotlib.pyplot as plt
from pydub import AudioSegment
from moviepy.video.io.VideoFileClip import VideoFileClip
import numpy as np
import scipy
import math
import base64
import ast

LINK = "https://www.youtube.com/watch?v=8WKDTU8_790"
AUDIO_FILE = "audio_clip.mp3"
WYNIK = "wynik.txt"
PIERWSZA_RAMKA = 300000
LICZBA_RAMEK = 200000

#POBIERANIE FILMU I KONWERSJA DO PLIKU MP3
def generator(link, outputfile):
    yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
    stream = yt.streams.get_highest_resolution()
    filename = stream.download()
    clip = VideoFileClip(filename)
    clip.audio.write_audiofile(outputfile)
    clip.close()

#MIESZANIE BITÓW WEDŁUG WZORU
"""
x1, x2
x1, x3, x2
x1, x4, x3, x5, x2
x1, x6, x4, x7, x3, x8, x5, x9, x2 
etc
"""
def mix_bits(input_bits):
    if(len(input_bits)<3):
        return input_bits
    
    mixed_bits = [input_bits[0],input_bits[1]]
    curentstep=2
    while(len(mixed_bits)<len(input_bits)):
        a=len(mixed_bits)-1
        b=0
        if(curentstep+a>len(input_bits)):
            a=len(input_bits)-curentstep
        for i in range(a):
            mixed_bits.insert(b*2+1, input_bits[curentstep])
            b=b+1
            curentstep=curentstep+1

    return mixed_bits

#WYKONYWANIE FUNKCJI XOR NA KAŻDYCH KOLEJNYCH 2 BITACH(TABLICA NA WYJŚCIU JEST 2 RAZY KRÓTSZA OD TABLICY NA WEJŚCIU)
def xor_operation(input_bits):
    result = []
    for i in range(0, len(input_bits), 2):
        result.append(input_bits[i] ^ input_bits[i+1])
    return result

#WPISANIE 4 NAJMNIEJ ZNACZĄCYCH BITÓW LICZBY DO TABLICY
def int_to_bits(n):
    n = n & 0xF
    bit_array = [int(bit) for bit in bin(n)[2:]]
    while len(bit_array) < 4:
        bit_array.insert(0, 0)
    return bit_array

#KONWERSJA TABLICY BITÓW NA TABLICE 8-BITOWYCH LICZB CAŁKOWITYCH
def bits_to_ints(bit_array):
    num_bits = len(bit_array)
    num_ints = num_bits // 8
    int_array = []

    for i in range(num_ints):
        start_index = i * 8
        end_index = start_index + 8
        segment = bit_array[start_index:end_index]
        segment_value = int("".join(map(str, segment)), 2)
        int_array.append(segment_value)
    return int_array

#KONWERSJA TABLICY BITÓW NA LICZBĘ CAŁKOWITĄ
def bits_to_int(bit_array):
    bit_string = ''.join(str(bit) for bit in bit_array)
    value = int(bit_string, 2)
    return value

#MIESZANIE I WYKONYWANIE FUNKCJI XOR NA WSZYSTKICH RAMKACH RAZEM
def long_postprocessing(num_of_values, input_values, start_value):
    result = []
    for i in range(num_of_values):
        bit_tab = int_to_bits(input_values[start_value+i])
        result.extend(bit_tab)
    mixed_segment = mix_bits(result)
    xored_segment = xor_operation(mixed_segment)
    return xored_segment

#SPRAWDZANIE, CZY LICZBA JEST PIERWSZA
def is_prime(n):
  for i in range(2,int(n/2)):
    if (n%i) == 0:
      return False
  return True

#SZYFORWANIE WIADOMOŚCI
def encrypt(msg_plaintext, e, n):
    arr = [pow(ord(char), e, n) for char in msg_plaintext]

    return base64.b64encode(bytes(str(arr), 'ascii')).decode()

#DESZYFROWANIE WIADOMOŚCI
def decrypt(msg_ciphertext, d, n):
    try:
        
        message_decoded = base64.b64decode(msg_ciphertext).decode()
        arr = ast.literal_eval(message_decoded)

        message_dencrypted = ""
        text = [chr(pow(char, d, n)) for char in arr]
        
        return message_dencrypted.join(text)
    except TypeError as e:
        raise e
    

def _generate_RSA_modulus(p: int, q: int):
    '''selection of two prime numbers namely p and q, and then 
    calculating their product N'''

    return p * q

def _calculate_eulers_totient_function(p: int, q: int):
    '''counts the positive integers up to a given integer n that
    are relatively prime to n.'''
    return (p-1) * (q-1) 

def _gcd(a, b):
    '''
    calculates the gcd of two ints
    '''
    while b != 0:
        a, b = b, a % b
    return a
    
def _egcd(a, b):
    '''
    calculates the modular inverse from e and phi
    '''
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = _egcd(b % a, a)
        return (g, x - (b // a) * y, y)

generator(LINK,AUDIO_FILE)
audio = AudioSegment.from_file(AUDIO_FILE, format="mp3")
frames = audio.get_array_of_samples()

num_of_values = LICZBA_RAMEK
start = PIERWSZA_RAMKA
p = 1
q = 0
while True:
    long_result = bits_to_ints(long_postprocessing(num_of_values, frames, start))

    ostateczna_lista_bitów = long_postprocessing(num_of_values, frames, start)


    for i in range(len(long_result) - 3):
        #test = long_result[i] << 24
        #test += long_result[i+1] << 16
        #test += long_result[i+2] << 8
        #test += long_result[i+3]
        test = long_result[i] << 8
        test += long_result[i+1]
        if(is_prime(test)):
            if(test>p):
                q = p
                p = test
            elif(test>q):
                q = test
    print(p, " ", q)
    start+=num_of_values
    if (q !=0):
        break


# step 2
n = _generate_RSA_modulus(p, q)

phi = _calculate_eulers_totient_function(p, q)
g = 1
e = long_result[i] << 24
e += long_result[i+1] << 16
e += long_result[i+2] << 8
e += long_result[i+3]
if (test<phi and test>1):
    g = _gcd(e,phi)
i = 0
while g != 1:
    e = long_result[i] << 24
    e += long_result[i+1] << 16
    e += long_result[i+2] << 8
    e += long_result[i+3]
    if (test<phi and test>1):
        g = _gcd(e,phi)
    i+=1

d = _egcd(e, phi)[1]
    
d = d % phi
if(d < 0):
    d += phi
print("d =", d)
print(f'Klucz publiczny: {e, n}')
print(f'Klucz prywatny: {d, n}')
 
# plain text
msg = input("Napisz wiadomość ")
print(f'Wiadomość oryginalna: {msg}')
 
# encryption
encrypted_msg = encrypt(msg, e, n)
print("Zaszyforwana wiadomość: ")
print(''.join(map(lambda x: str(x), encrypted_msg)))
 
# decryption

print("Zdeszyfrowana wiadomość: ")
print(decrypt(encrypted_msg, d, n))
