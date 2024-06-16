import cv2
import face_recognition


# compares the input_image with all the images of person_images
# return matched_score if input_image matches with more than 50% images of person_images
def compare_face_with_multiple_images(input_image, person_images, threshold=0.6):
    # Load the input image and compute its face encoding
    input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    input_face_encodings = face_recognition.face_encodings(input_image)

    if not input_face_encodings:
        return {"success": False}

    input_face_encoding = input_face_encodings[0]

    # Load and compute face encodings for each image of the same person
    person_face_encodings = []
    for person_image in person_images:
        person_image = cv2.cvtColor(person_image, cv2.COLOR_BGR2RGB)
        person_face_encoding = face_recognition.face_encodings(person_image)
        if person_face_encoding:
            person_face_encodings.append(person_face_encoding[0])

    # Compare the input face encoding with each person's face encoding
    match_results = []
    for person_face_encoding in person_face_encodings:
        match = face_recognition.compare_faces([person_face_encoding], input_face_encoding, tolerance=threshold)
        match_results.append(match[0])

    # Calculate the similarity score for each comparison
    face_distances = face_recognition.face_distance(person_face_encodings, input_face_encoding)
    similarity_scores = [(1 - distance) * 100 for distance in face_distances]

    # Determine if there's a match with the specified accuracy rate
    matches = [score >= (1 - threshold) * 100 for score in similarity_scores]

    # Check if more than 50% of the images match
    if matches.count(True) > len(person_images) / 2:
        matched_score = max(similarity_scores)
        return {
            "success": True,
            "matched_score": matched_score
        }
    else:
        return {
            "success": True,
            "matched_score": 0
        }
