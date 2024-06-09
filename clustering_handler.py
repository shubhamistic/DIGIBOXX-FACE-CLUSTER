import uuid
from detect_face import detect_faces
from recognize_face import compare_face_with_multiple_images
import request_handler


def cluster_image(image, cluster_dict):
    # detect the number of faces in the image and get the coords of it
    faces_coords = detect_faces(image)
    # if no faces found then stop clustering
    if not faces_coords:
        return None

    # traverse through each the face
    clustered_info_list = []
    for face_coords in faces_coords:
        # get the height and width of the image
        image_height, image_width = image.shape[:2]
        if len(face_coords) == 1:
            x1, y1, x2, y2 = 0, 0, image_width, image_height
            face_image = image
        else:
            x, y, w, h = face_coords
            x1, y1, x2, y2 = x, y, x + w, y + h
            w_15_p = int((image_width / 100) * 15)  # width_15_percent
            h_15_p = int((image_height / 100) * 15)  # height_15_percent
            x1, y1, x2, y2 = max(0, x1 - w_15_p), max(0, y1 - h_15_p), min(x2 + w_15_p, image_width), min(y2 + h_15_p, image_height)
            # crop the face out of image to cluster
            face_image = image[y1:y2, x1:x2]

        for cluster_id, clustered_images in cluster_dict.items():
            result = compare_face_with_multiple_images(face_image, clustered_images)
            if result["matched_score"]:
                clustered_info_list.append({
                    "is_existing_cluster": True,
                    "cluster_id": cluster_id,
                    "coords": [x1, y1, x2, y2],
                    "matched_score": result["matched_score"]
                })
                break
        else:
            cluster_id = str(uuid.uuid4()).replace('-', '_')
            clustered_info_list.append({
                "is_existing_cluster": False,
                "cluster_id": cluster_id,
                "coords": [x1, y1, x2, y2],
                "matched_score": 0
            })

    return clustered_info_list


def handle_clustering(url, jwt_token, task_info, cluster_dict):
    clustering_result = []

    try:
        file_id = task_info["file_id"]
        user_id = task_info["user_id"]
        file_type = task_info["file_type"]
        print(f"file_id: {file_id} | user_id: {user_id}")
        # currently the algo works for an image file only
        if file_type == "image":
            # read the image using open cv
            image_to_cluster = request_handler.get_file_from_server(
                url=url,
                jwt_token=jwt_token,
                user_id=user_id,
                file_id=file_id
            )
            if image_to_cluster is not None and image_to_cluster.any():
                # replace the file_id in cluster_dict with the cv2 image
                empty_clustered_id_list = []
                for cluster_id, clustered_image_file_infos in cluster_dict.items():
                    clustered_image_list = []
                    for clustered_image_file_info in clustered_image_file_infos:
                        clustered_image_file_id = clustered_image_file_info["file_id"]
                        x1, y1, x2, y2 = clustered_image_file_info["coords"]
                        # define the path for image to cluster
                        clustered_image = request_handler.get_file_from_server(
                            url=url,
                            jwt_token=jwt_token,
                            user_id=user_id,
                            file_id=clustered_image_file_id
                        )
                        if clustered_image is not None and clustered_image.any():
                            clustered_image = clustered_image[y1:y2, x1:x2]
                            clustered_image_list.append(clustered_image)

                    if clustered_image_list:
                        cluster_dict[cluster_id] = clustered_image_list
                    else:
                        empty_clustered_id_list.append(cluster_id)

                # delete the cluster entities which are empty
                for cluster_id in empty_clustered_id_list:
                    del cluster_dict[cluster_id]

                # cluster the image_to_cluster based on cluster_dict
                clustered_info_list = cluster_image(image_to_cluster, cluster_dict)
                if clustered_info_list:
                    for clustered_info in clustered_info_list:
                        if clustered_info["is_existing_cluster"]:
                            clustering_result.append({
                                "cluster_id": clustered_info["cluster_id"],
                                "coords": clustered_info["coords"],
                                "matched_score": clustered_info["matched_score"],
                                "is_identity": False
                            })
                        else:
                            clustering_result.append({
                                "cluster_id": clustered_info["cluster_id"],
                                "coords": clustered_info["coords"],
                                "matched_score": clustered_info["matched_score"],
                                "is_identity": True
                            })

    except Exception as error:
        print("ERROR:", error)

    print("TASK COMPLETED")
    return clustering_result
