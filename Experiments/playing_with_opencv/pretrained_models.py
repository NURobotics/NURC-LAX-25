import torch
import torchvision
from PIL import Image
from torchvision.transforms.functional import pil_to_tensor
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.utils import draw_bounding_boxes, draw_keypoints
from torchvision.transforms.functional import to_pil_image
from pycocotools.coco import COCO

annFile='annotations/instances_val2017.json'

coco=COCO(annFile)

object_detection_model = fasterrcnn_resnet50_fpn(pretrained=True, progress=False)

object_detection_model.eval(); ## Setting Model for Evaluation/Prediction



# open image in pythorch
img = Image.open("womenslacrosse.jpg")
img_tensor = pil_to_tensor(img)
img_tensor = img_tensor.unsqueeze(dim=0)
img_tensor = img_tensor / 255.0



# get some precitons
img_preds = object_detection_model(img_tensor)

# print(img_preds)



"""
label for sports balls seems to be 37


"""
BALL_LABEL = 37

# get the labels
labels = coco.loadCats(img_preds[0]["labels"].numpy())

# print(labels)


# find where ba
allpreds = img_preds[0]
boxes = allpreds['boxes']
raw_labels = allpreds['labels']

# only balls
onlyballsboxes = boxes[raw_labels == BALL_LABEL]
onlyballlables= raw_labels[raw_labels == BALL_LABEL]

onlyballlables = coco.loadCats(onlyballlables.numpy())


annots = ["{}-{:.2f}".format(label["name"], prob) for label, prob in zip(onlyballlables, img_preds[0]["scores"][raw_labels == BALL_LABEL].detach().numpy())]

out = draw_bounding_boxes(image=img_tensor[0],
                             boxes=onlyballsboxes,
                             labels=annots,
                             colors=["green" for label in onlyballlables],
                             width=2
                            )

"""
 try to figure centerpoints of balls

 tensor([[1382.1454,  303.1444, 1442.1348,  362.1280],
        [1386.2137,  255.1318, 1468.5118,  356.4641]],
       grad_fn=<IndexBackward0>)

boxes (FloatTensor[N, 4]): the predicted boxes in [x1, y1, x2, y2] 
"""

points = []
for i in onlyballsboxes:
    points.append( [(i[0] + i[2]) / 2.0, (i[1] + i[3]) / 2.0]   )

n = len(points)

points = torch.Tensor([points])

print(points)

# out2 = draw_keypoints(
#     img_tensor[0],
#     points
#     radius=100,
#     colors=
# )

# res_img = to_pil_image(out)
# res_img.show()
# res2 = to_pil_image(out2)
# res2.show()

print(onlyballsboxes)


# holiday_annot_labels = ["{}-{:.2f}".format(label["name"], prob) for label, prob in zip(labels, img_preds[0]["scores"].detach().numpy())]

# holiday_output = draw_bounding_boxes(image=img_tensor[0],
#                              boxes=img_preds[0]["boxes"],
#                              labels=holiday_annot_labels,
#                              colors=["red" if label["name"]=="person" else "green" for label in labels],
#                              width=2
#                             )

# res_img = to_pil_image(holiday_output)
# res_img.show()