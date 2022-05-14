import imageio
import urllib.request
import cv2
from PIL import Image
from gamma_correct import convert_gamma
url = "https://c.tenor.com/LGI1Mo4rXdkAAAAC/this-is-fine-fire.gif"
fname = "fire.gif"

## Read the gif from the web, save to the disk
imdata = urllib.request.urlopen(url).read()
imbytes = bytearray(imdata)
open(fname,"wb+").write(imdata)

## Read the gif from disk to `RGB`s using `imageio.miread` 
gif = imageio.mimread(fname)
nums = len(gif)
print("Total {} frames in the gif!".format(nums))

# convert form RGB to BGR 
imgs = [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in gif]

## Display the gif
#out_images = np.zeros((64*len(imgs), 64, 3), dtype = "uint8")
result = Image.new('RGB', (64*(len(imgs)-20), 64))
print("LENGTH: ", len(imgs)-20)
for idx, img in enumerate(imgs[10:-10]):
	resized_img = cv2.resize(img, (64,64))
	convert_gamma1, convert_gamma2 = convert_gamma(resized_img)
	convert_gamma2 = cv2.cvtColor(convert_gamma2, cv2.COLOR_BGR2RGB)
	convert_gamma2_pil = Image.fromarray(convert_gamma2)
	result.paste(im=convert_gamma2_pil, box=(64*idx, 0))

result.save("fire.bmp")

# i = 0

# while True:
#     cv2.imshow("gif", imgs[i])
#     if cv2.waitKey(100)&0xFF == 27:
#         break
#     i = (i+1)%nums
# cv2.destroyAllWindows()