from pathlib import Path

import cv2


class BaseProcessing:
    _path = Path.cwd()

    _initial_photos_dir = Path(_path, 'initial-photos')
    _modify_photos_dir = Path(_path, 'modify-photos')

    _check_photos_dir = Path(_path, 'check-photos')

    def __init__(self, *args, **kyargs):
        pass

    def processing(self):
        # Get list of directoryes then name eqal pople-name:
        list_people_dirs = self._initial_photos_dir.glob('*')

        for people in list_people_dirs:
            # Check the people it is a directory:
            if not people.is_dir:
                continue

            # Create copy directories equal _initial_photos_dir:
            dir_path = self._copy_directories(people)

            # Get list of people photos:
            list_people_photos = people.glob('*')

            for photo in list_people_photos:
                # Check the photo is a file:
                if not photo.is_file:
                    continue

                # Logic ...
                self._logic(dir_path, photo)

    def _copy_directories(self, people):
        pass

    def _logic(self, dir_path, photo):
        pass


class PhotoProcessing(BaseProcessing):
    def _copy_directories(self, people):
            dir_path = Path(self._modify_photos_dir, people.name)
            dir_path.mkdir(exist_ok=True)
            return dir_path

    def _logic(self, dir_path, photo):
        print('Process the photo: ', photo.as_posix())

        #  Create save photo-path:
        save_path = Path(dir_path, photo.name)

        # Open initial image:
        img = cv2.imread(photo.as_posix(), cv2.IMREAD_GRAYSCALE)
        resize_photo = self._resize_photo(img)

        # Save modif image:
        cv2.imwrite(save_path.as_posix(), resize_photo)

    def _resize_photo(selfm, img, scale_percent = 60):
        # Calc widht and height of new image:
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        
        # Resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        return resized


if __name__ == '__main__':
    p = PhotoProcessing()
    p.processing()
