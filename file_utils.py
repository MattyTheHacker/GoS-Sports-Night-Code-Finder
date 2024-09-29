import json

def save_dictionary_to_file(codes) -> None:
    print(codes)
    with open('codes.json', 'w') as fp:
        json.dump(codes, fp)






