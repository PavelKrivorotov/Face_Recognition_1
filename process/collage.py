from pathlib import Path
from PIL import Image


class PhotoCollage:
    _path = None
    _collage = None

    _reverse = None

    def __init__(self, path_to_photos, width=1024, count_in_row=4, reverse=False):
        self._path = Path(path_to_photos)
        self._reverse = reverse
        self._collage = self._make_collage(width, count_in_row)

    def _list_photos(self):
        photos = [photo for photo in self._path.glob('*') if photo.is_file()]
        return sorted(photos, reverse=self._reverse)

    def _make_collage(self, width, count_in_row):
        photos = self._list_photos()

        width_photo = int(width / count_in_row)
        height_photo = width_photo

        row_cout = len(photos) // count_in_row
        if len(photos) % count_in_row:
            row_cout += 1

        height = height_photo * row_cout
        img = Image.new('RGB', (width, height))

        for ind, photo in enumerate(photos):
            width_coff = ind % count_in_row
            height_coff = ind // count_in_row

            tmp = Image.open(photo)
            tmp = tmp.resize((width_photo, height_photo))

            x = width_photo * width_coff
            y = height_photo * height_coff
            img.paste(tmp, (x, y))

        return img

    def get(self):
        return self._collage

    def show(self):
        self._collage.show()
