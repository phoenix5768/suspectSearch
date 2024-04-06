import numpy as np
import cv2
import matplotlib as plt
# import cv2_imshow
import mediapipe as mp


global left_eye, right_eye, nose_size, nose_height, left_brow, right_brow, mouth
left_eye = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
right_eye = [362, 398, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
nose_size = [240, 99, 328, 460, 294, 278, 360, 363, 281, 5, 51, 134, 131, 48, 64]
nose_height = [19, 1, 4, 5, 195, 197, 6]
left_brow = []
right_brow = []
mouth = [0, 27, 39, 40, 185, 61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267]
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)


def Normalize(x, y):
  return int(x * 2444), int(y * 1718)


def Resize(img):
  return cv2.resize(img, (1024, 720))


def dist(point_1, point_2):
  x_1, y_1 = Normalize(point_1.x, point_1.y)
  x_2, y_2 = Normalize(point_2.x, point_2.y)
  p_1 = np.array([x_1, y_1])
  p_2 = np.array([x_2, y_2])
  res = np.linalg.norm(p_1 - p_2)
  return res


def shoelace(x_y):
    x_y = np.array(x_y)
    x_y = x_y.reshape(-1,2)

    x = x_y[:,0]
    y = x_y[:,1]

    S1 = np.sum(x*np.roll(y,-1))
    S2 = np.sum(y*np.roll(x,-1))

    area = .5*np.absolute(S1 - S2)

    return area


def calc_area(face_part, mesh_res):
    res = []
    for i in range(len(face_part)):
      x, y = Normalize(mesh_res.multi_face_landmarks[0].landmark[face_part[i]].x, mesh_res.multi_face_landmarks[0].landmark[face_part[i]].y)
      temp = (x, y)
      res.append(temp)
    return shoelace(res)


# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh


def Mesh(img) -> dict:
    # Load image
    image = cv2.imread(img)
    #image = Resize(image)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Initialize MediaPipe Face Mesh
    with mp_face_mesh.FaceMesh(min_detection_confidence=0.9, min_tracking_confidence=0.2, refine_landmarks=True) as face_mesh:
        # Process image
        results = face_mesh.process(image_rgb)

        # Draw landmarks on the face
        if results.multi_face_landmarks:
            # print(results.multi_face_landmarks[0].landmark[33])
            # print(dist(results.multi_face_landmarks[0].landmark[107], results.multi_face_landmarks[0].landmark[55]))
            # print(dist(results.multi_face_landmarks[0].landmark[159], results.multi_face_landmarks[0].landmark[145]))
            for landmarks in results.multi_face_landmarks:
                mp_drawing.draw_landmarks(image, landmarks, mp_face_mesh.FACEMESH_CONTOURS)
                #print(landmarks)
            ans = []

            #Nose
            temp_nose_l = float("{:.2f}".format(dist(results.multi_face_landmarks[0].landmark[19], results.multi_face_landmarks[0].landmark[168])/10))
            #ans.append(float(dist(results.multi_face_landmarks[0].landmark[19], results.multi_face_landmarks[0].landmark[168])))
            ans.append(temp_nose_l)
            temp_right_br = float("{:.2f}".format(dist(results.multi_face_landmarks[0].landmark[285], results.multi_face_landmarks[0].landmark[136])/100))
            ans.append(temp_right_br)
            temp_left_br = float("{:.2f}".format(dist(results.multi_face_landmarks[0].landmark[55], results.multi_face_landmarks[0].landmark[107])/100))
            ans.append(temp_left_br)
            ans.append(calc_area(left_eye, results)/100)
            ans.append(calc_area(right_eye, results)/100)
            ans.append(calc_area(nose_size, results)/100)
            ans.append(calc_area(mouth, results)/100)

            return {
                'nose_length': ans[0],
                'right_brow_size': ans[1],
                'left_brow_size': ans[2],
                'left_eye_size': calc_area(left_eye, results) / 100,
                'right_eye_size': calc_area(right_eye, results) / 100,
                'nose_size': calc_area(nose_size, results) / 100,
                'lips_size': calc_area(mouth, results) / 100
            }

        return {
            'nose_length': 0,
            'right_brow_size': 0,
            'left_brow_size': 0,
            'left_eye_size': 0,
            'right_eye_size': 0,
            'nose_size': 0,
            'lips_size': 0
        }
    # Display the result
    # cv2_imshow(image)


def getFaceBox(net, frame, conf_threshold=0.7):
    frameOpencvDnn = frame.copy()
    frameHeight = frameOpencvDnn.shape[0]
    frameWidth = frameOpencvDnn.shape[1]
    blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    bboxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frameWidth)
            y1 = int(detections[0, 0, i, 4] * frameHeight)
            x2 = int(detections[0, 0, i, 5] * frameWidth)
            y2 = int(detections[0, 0, i, 6] * frameHeight)
            bboxes.append([x1, y1, x2, y2])
            cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
    return frameOpencvDnn, bboxes

# def genderPred(face):
#   genderProto = "gender_deploy.prototxt"
#   genderModel = "gender_net.caffemodel"                                                 Ne nuzhno
#   genderNet = cv2.dnn.readNet(genderModel, genderProto)

#   genderList = ['Male', 'Female']

#   blob = cv2.dnn.blobFromImage(face, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
#   genderNet.setInput(blob)
#   genderPreds = genderNet.forward()
#   gender = genderList[genderPreds[0].argmax()]
#   print("Gender Output : {}".format(genderPreds))
#   print("Gender : {}".format(gender))

# def agePred(face):
#   ageProto = "age_deploy.prototxt"
#   ageModel = "age_net.caffemodel"
#   ageNet = cv2.dnn.readNet(ageModel, ageProto)

#   ageList = ['(0 - 2)', '(4 - 6)', '(8 - 12)', '(15 - 20)', '(25 - 32)', '(38 - 43)', '(48 - 53)', '(60 - 100)']

#   blob = cv2.dnn.blobFromImage(face, 1, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
#   ageNet.setInput(blob)
#   agePreds = ageNet.forward()
#   age = ageList[agePreds[0].argmax()]
#   print("Age Output : {}".format(agePreds))
#   print("Age : {}".format(age))

# if __name__ == "__main__":
#     Mesh('Test.jpg')
#     Mesh('test2.jpg')
#     # pic = cv2.imread('Test.jpg')
#     #pic1 = cv2.imread('Test1.jpg')
#     # genderPred(pic)
#     # genderPred(pic1)
#     # agePred(pic)
#     # agePred(pic1)
#




# new section