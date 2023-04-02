import json
from os import makedirs, path
from glob import iglob
from sys import argv, exit
from PIL import ExifTags, Image, ImageDraw, ImageFont
#from pillow_heif import register_heif_opener

#register_heif_opener()

EXIF_TAG_ORIENTATION = 274

def add_caption(infile, title, subtitle):
  head, ext = path.splitext(infile)
  folder, filename = path.split(head)

  with Image.open(infile, mode='r', formats=None) as img:
    exif_meta = img.getexif()
    alpha = img.convert("RGBA")

    if EXIF_TAG_ORIENTATION in exif_meta:
      orientation = exif_meta[EXIF_TAG_ORIENTATION]

      print(f'Fixing image orientation; {orientation}')

      if orientation == 2:
        alpha = alpha.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
      elif orientation == 3:
        alpha = alpha.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
      elif orientation == 4:
        alpha = alpha.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
        alpha = alpha.transpose(method=Image.Transpose.FLIP_TOP_BOTTOM)
      elif orientation == 5:
        alpha = alpha.transpose(method=Image.Transpose.ROTATE_270)
        alpha = alpha.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
      elif orientation == 6:
        alpha = alpha.transpose(method=Image.Transpose.ROTATE_270)
      elif orientation == 7:
        alpha = alpha.transpose(method=Image.Transpose.ROTATE_90)
        alpha = alpha.transpose(method=Image.Transpose.FLIP_LEFT_RIGHT)
      elif orientation == 8:
        alpha = alpha.transpose(method=Image.Transpose.ROTATE_270)

    overlay = Image.new('RGBA', alpha.size, (255, 255, 255, 0))

    # calculate caption offset
    image_width, image_height = alpha.size
    caption_width, caption_height = image_width, 310
    caption_x, caption_y = 0, image_height - caption_height - 230

    title_x = caption_x + 149
    title_y = caption_y + 72
    title_font = ImageFont.truetype(font='DejaVuSerif-Bold.ttf', size=75)

    subtitle_x = title_x + 0
    subtitle_y = title_y + 89
    subtitle_font = ImageFont.truetype(font='DejaVuSerif.ttf', size=66)

    draw = ImageDraw.Draw(overlay)

    draw.rectangle(((caption_x, caption_y), (caption_width, caption_y + caption_height)), fill=(0, 0, 0, 128))
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255, 255))
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(255, 255, 255, 255))

    final = Image.alpha_composite(alpha, overlay)
    final = final.convert('RGB')

    final.save(f'{folder}/imager/{filename}.jpeg', format='JPEG')

if __name__ == '__main__':
  if len(argv) != 2:
    print(f'Usage {argv[0]} FOLDER')
    exit(1)

  folder = argv[1]
  destination = path.join(folder, 'imager')

  makedirs(destination, exist_ok=True)

  with open('config.json', 'r') as fd:
    config = json.load(fd)

  for filepath in iglob(f'{folder}/*'):
    if path.isdir(filepath):
      continue

    print(f'Processing image {filepath}')
    add_caption(filepath, config['title'], config['subtitle'])

