path = "../../WEBPAGES_RAW/"
new_path = f"{path}0/0"

with open(new_path, "r") as file:
    a = file.read()

print(a)