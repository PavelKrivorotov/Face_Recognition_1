from pathlib import Path
import json

import numpy as np
import cv2
import face_recognition


class PhotoEncoding:
    _path = Path.cwd()

    def __init__(self, path=None):
        if path:
            self._path = Path(path)

        self._initial_photos_dir = Path(self._path, 'initial-photos')
        self._initial_photos_json = Path(self._path, 'face-encodings.json')
        self._initial_photos_encodigs = {}

        self._modify_photos_dir = Path(self._path, 'modify-photos')

        self._check_photos_dir = Path(self._path, 'check-photos')

    def _initial_photos_path(self):
        return self._initial_photos_dir
    
    def _copy_directories(self, people):
            dir_path = Path(self._modify_photos_dir, people.name)
            dir_path.mkdir(exist_ok=True)
            return dir_path

    def create_encodings(self):
        # Get list of directoryes then name eqal pople-name:
        list_people_dirs = self._initial_photos_path().glob('*')

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

        # Write face encodings '_initial_photos_encodigs':
        self._write_face_encodings(self._initial_photos_json)

    def load_encodings(self):
        self._read_face_encodings(self._initial_photos_json)

    def _compare_face(self, unknown_encodings):
        for key, values_list in self._initial_photos_encodigs.items():
            check_list = face_recognition.compare_faces(
                values_list,
                unknown_encodings
            )

            if True in check_list:
                return (True, key)

        return (False, 'Noname')

    def check_images(self):
        # Select all photos in '_check_photos_dir':
        for photo in self._check_photos_dir.glob('*'):
            if not photo.is_file():
                continue
                
            # Get name and extension of the photo:
            photo_name, photo_extension = photo.name.split('.')

            # Make directory with name in (photo.name):
            dir_path = Path(self._check_photos_dir, photo_name)
            dir_path.mkdir(exist_ok=True)

            # Move check photo to self check directory:
            # initial_photo_name = f'initial-{photo_name}.{photo_extension}'
            initial_photo_name = f'initial.{photo_extension}'
            initial_photo_path = Path(dir_path, initial_photo_name)
            photo.rename(initial_photo_path)

            # Open image:
            img = cv2.imread(initial_photo_path.as_posix(), cv2.COLOR_BGR2RGB)

            # Get face locations (rectangle_coords):
            rectangle_coords = self._get_rectangle_coords(img)

            # Make face encodings:
            encodings = face_recognition.face_encodings(img, rectangle_coords)

            for coord, encoding in zip(rectangle_coords, encodings):
                # Compare unknown encodings with wnowns encodings:
                state, name = self._compare_face(encoding)
                print(
                    '\n',
                    '\nState = ', state,
                    '\nName = ', name,
                    '\n'
                )

                # Draw face rectangle:
                color = (0, 0, 255)
                if state:
                    color = (0, 255, 0)

                # img = self._draw_rectangle(img, rectangle_coords, name, color)
                img = self._draw_rectangle(img, coord, name, color)

            # Save check photo:
            check_photo_name = f'check.{photo_extension}'
            check_photo_path = Path(dir_path, check_photo_name)
            cv2.imwrite(check_photo_path.as_posix(), img)

    def _get_rectangle_coords(self, img):
        face_location = face_recognition.face_locations(img)
        return face_location

    def _draw_rectangle(self, img, coord, text=None, color=(0, 0, 255)):
        top, right, bottom, left = coord

        start_point = (left, top)
        stop_point = (right, bottom)

        img = cv2.rectangle(img, start_point, stop_point, color, 2)

        # ...
        if text:
            cv2.putText(
                img,
                text,
                (start_point[0], start_point[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                # (0, 0, 255)
                color,
                2,
                cv2.LINE_AA
            )

        return img

    def _resize_photo(selfm, img, scale_percent = 60):
        # Calc widht and height of new image:
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)

        img = cv2.resize(img, dim)
        return img

    def _logic(self, dir_path, photo):
        # print('Process the photo: ', photo.as_posix())
        print('Process the photo: ', photo.name)

        # Create save photo-path:
        photo_name = f'{dir_path.name}-{photo.name}'
        # save_path = Path(dir_path, photo.name)
        save_path = Path(dir_path, photo_name)

        # Open initial image:
        img = cv2.imread(photo.as_posix(), cv2.COLOR_BGR2RGB)

        # Search face rectangles:
        rectangle_coords = self._get_rectangle_coords(img)

        # Calc encodings:
        encodings = face_recognition.face_encodings(img, rectangle_coords)
        self._initial_photos_encodigs.setdefault(photo_name, encodings)

        # Draw rectangles by photo:
        for coord in rectangle_coords:
            img = self._draw_rectangle(img, coord)

        # Resize image:
        # img_resize = self._resize_photo()

        # Save modif image:
        cv2.imwrite(save_path.as_posix(), img)

    def _write_face_encodings(self, file_path):
        doc = {}
        for key, list_values in self._initial_photos_encodigs.items():
            values = [value.tolist() for value in list_values]
            doc.setdefault(key, values)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(
                doc,
                file,
                indent = 4,
            )

    def _read_face_encodings(self, file_path):
        with open(file_path, encoding='utf-8') as file:
            obj = json.load(file)

        self._initial_photos_encodigs.clear()
        for key, list_values in obj.items():
            values = [np.array(value) for value in list_values]
            self._initial_photos_encodigs.setdefault(key, values)
