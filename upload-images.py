import pandas as pd
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry, Region
import os

data = pd.read_fwf('data/manlabel.txt', infer_nrows=1000, sep=" ", header=None) \
         .set_axis(["filename", "y1", "x1", "y2", "x2", "defect"], axis=1, inplace=False) \
         .query('defect != "UNKNOWN" & defect != "moustache_knot" & defect != "sound"')

ENDPOINT = "https://eastus.api.cognitive.microsoft.com"
training_key = "<your api key>"

trainer = CustomVisionTrainingClient(training_key, endpoint=ENDPOINT)

# Find the object detection domain
obj_detection_domain = next(domain for domain in trainer.get_domains() if domain.type == "ObjectDetection" and domain.name == "General")

print ("Creating project...")
project = trainer.create_project("wood-1", domain_id=obj_detection_domain.id)

defects = data['defect'].drop_duplicates().to_list()
tags = ({k: trainer.create_tag(project.id, k) for k in defects})

print("processing files...")

for name, group in data.groupby('filename'):
    image_width = 488
    image_height = 512
    regions = []
    tagged_images_with_regions = []

    for index, row in group.iterrows():

        width = row['x2']-row['x1']
        height = row['y2']-row['y1']

        x_scaled = row['x1'] / image_width
        y_scaled = row['y1'] / image_height
        width_scaled = width / image_width
        height_scaled = height / image_height

        regions.append(Region(tag_id=tags[row['defect']].id, left=x_scaled,top=y_scaled,width=width_scaled,height=height_scaled))

    with open(os.path.join('./data', "{0}.png".format(name)), mode="rb") as image_contents:
        tagged_images_with_regions.append(ImageFileCreateEntry(name=name, contents=image_contents.read(), regions=regions))

    upload_result = trainer.create_images_from_files(project.id, images=tagged_images_with_regions)
    if not upload_result.is_batch_successful:
        print("Image batch upload failed.")
        for image in upload_result.images:
            print("Image status: ", image.status)
