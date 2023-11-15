import json

a = {"style": "36",
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "bedrockavatarcreatorstac-bedrockavatarimagestore7-14hmtn4fhp02r"
        },
        "object": {
          "key": "FL1.jpeg"
        }
      }
    }
  ]
}
r_json = list()
images = ['FL6.jpeg']
for image in images:
    for i in range(1,32):
        r_json.append({"style": str(i), "Records": [{"s3": {"bucket": {"name": "bedrockavatarcreatorstac-bedrockavatarimagestore7-14hmtn4fhp02r"}, "object": {"key": image}}}]})
# write the json in a file
with open('data.json', 'w') as outfile:
    json.dump(r_json, outfile)
    outfile.close()
