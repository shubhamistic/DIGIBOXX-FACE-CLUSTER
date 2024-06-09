import os
import cv2
import requests


def get_file_from_server(url, jwt_token, user_id, file_id):
    # check if the requested file already exists in the cache or not
    cached_image_file_path = f"cache/{user_id}/{file_id}.png"
    if os.path.exists(cached_image_file_path):
        # now the load the image from directory in the form of cv2 image
        load_image = cv2.imread(cached_image_file_path)
        return load_image

    response = requests.post(
        url=f"{url}/daemon/get",
        headers={
            'Authorization': jwt_token,
            'Content-Type': 'application/json'
        },
        json={
            'userId': user_id,
            'fileId': file_id
        }
    )

    # cache the image file received from the request
    user_directory = f"cache/{user_id}"
    if response.status_code == 200:
        if not os.path.isdir(user_directory):
            os.makedirs(user_directory)

        # write the file to the user cached directory
        with open(f"{user_directory}/{file_id}.png", 'wb') as f:
            f.write(response.content)

        # now the load the image from directory in the form of cv2 image
        load_image = cv2.imread(f"{user_directory}/{file_id}.png")

        return load_image

    return None
