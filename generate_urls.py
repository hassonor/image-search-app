# Python script to generate 50,000 image URLs and save them to a file
base_url = "http://images.cocodataset.org/train2017/"
file_name = "image_urls.txt"

with open(file_name, "a") as file:
    for i in range(1, 50001):
        # Assuming image filenames follow a pattern like "000000000001.jpg", "000000000002.jpg", etc.
        image_url = f"{base_url}{str(i).zfill(12)}.jpg"
        file.write(image_url + "\n")

print(f"50,000 image URLs have been added to {file_name}.")