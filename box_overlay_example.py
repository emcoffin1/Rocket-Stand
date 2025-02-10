x = {'yes': 1, "no": 0, "test": 3}
for y in x.keys():
    if "no" in y:
        print(y)
        continue

    print(y,"false")