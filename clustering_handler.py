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

    # get the height and width of the image
    image_height, image_width = image.shape[:2]

    # traverse through each the face
    clustered_info_list = []

    for face_coords in faces_coords:
        x, y, w, h = face_coords
        x1, y1, x2, y2 = x, y, x + w, y + h

        w_10_p = int((image_width / 100) * 10)  # width_10_percent
        h_10_p = int((image_height / 100) * 10)  # height_10_percent
        x1, y1, x2, y2 = max(0, x1 - w_10_p), max(0, y1 - h_10_p), min(x2 + w_10_p, image_width), min(y2 + h_10_p,
                                                                                                      image_height)

        face_image = image
        if len(face_coords) > 1:
            # crop the face out of image to cluster
            face_image = face_image[y1:y2, x1:x2]

        cur_best_cluster = {"matched_score": 0}
        error_flag = False  # flag to keep the note if any error occurs or not
        for cluster_id, clustered_images in cluster_dict.items():
            result = compare_face_with_multiple_images(face_image, clustered_images)

            # break the loop if the face_recognition algorithm fails to find the face in the image
            if not result["success"]:
                error_flag = True
                break

            # store the cluster with the max best matched score
            if result["matched_score"] > cur_best_cluster["matched_score"]:
                cur_best_cluster = {
                    "is_existing_cluster": True,
                    "cluster_id": cluster_id,
                    "matched_score": result["matched_score"]
                }

                # break the loop if maximum match score achieved
                if result["matched_score"] == 100:
                    break

        if not error_flag:
            # if the face matched no cluster with more than 50% accuracy, then create a new cluster
            if cur_best_cluster["matched_score"] < 50:
                cluster_id = str(uuid.uuid4()).replace('-', '_')
                cur_best_cluster = {
                    "is_existing_cluster": False,
                    "cluster_id": cluster_id,
                    "matched_score": 0
                }

            # check if one of the faces in the image is already clustered to clustered_info_list or not
            for cluster_info in clustered_info_list:
                if cluster_info["cluster_id"] == cur_best_cluster.get("cluster_id", None):
                    break
            else:
                # append the cluster info if the image with current face is not clustered in any of the
                # previous clustered folder
                # also add the coords of the face in the image
                cur_best_cluster["coords"] = [x1, y1, x2, y2]
                clustered_info_list.append(cur_best_cluster)

    return clustered_info_list


def handle_clustering(url, jwt_token, task_info, cluster_dict):
    clustering_result = []

    # try:
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

    # except Exception as error:
    #     print("ERROR:", error)

    print("TASK COMPLETED")
    return clustering_result
