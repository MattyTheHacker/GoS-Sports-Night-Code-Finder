import json

def save_dictionary_to_file(codes):
    with open('codes.json', 'w') as fp:
        json.dump(codes, fp)






