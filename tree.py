import json

# Load the JSON file
with open('tree.json') as f:
    data = json.load(f)

print(' ')
print('Initial results for input city:')
print(' ')
for i, r in enumerate(data['initial results']):
    print(i, r)
print(' ')
for i in range(7):
    print('              |               ')
print('              V               ')
print(' ')
if len(data['type results']) == 1:
    print('User did not choose to filter by type')
    print(' ')
    print('              |               ')
    print('              V               ')
    print(' ')
else:
    print(' ')
    print('Would you like to filter by restaurant type?:')
    print(' ')
    print('              |               ')
    print('              V               ')
    print(' ')
    for i, r in enumerate(data['type results']):
        print(i, r)
    print(' ')
    for i in range(7):
        print('              |               ')
print('              V               ')
print(' ')
if len(data['rating results']) == 1:
    print('User did not choose to filter by type')
    print(' ')
    print('              |               ')
    print('              V               ')
    print(' ')
else:
    print(' ')
    print('Would you like to filter by rating?:')
    print(' ')
    print('              |               ')
    print('              V               ')
    print(' ')
    for i, r in enumerate(data['rating results']):
        print(i, r)
    print(' ')
    for i in range(7):
        print('              |               ')
print('              V               ')
print(' ')
if len(data['price results']) == 1:
    print('User did not choose to filter by price')
    print(' ')
    print('              |               ')
    print('              V               ')
    print(' ')
else:
    print(' ')
    print('Would you like to filter by restaurant price?:')
    print(' ')
    print('              |               ')
    print('              V               ')
    print(' ')
    for i, r in enumerate(data['price results']):
        print(i, r)
    print('Done, user would pick one of these restaurants')
# dict_keys(['initial results', 'type results', 'rating results', 'price results'])