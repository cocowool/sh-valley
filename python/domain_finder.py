import itertools
import whois

def generate_name(length = 6, alpha = 2, number = 4):
    chars = [chr(c) for c in range(97,123)]
    chars_tuple = itertools.permutations(chars, 4)

    for item in chars_tuple:
        cn_domain = ''.join(item) + '.com'
        com_domain = ''.join(item) + '.cn'



    print("Generate domain name")
    pass


generate_name()