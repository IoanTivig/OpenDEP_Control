import cv2


def crop_image(image, scale=0):
    center_x, center_y = image.shape[1] / 2, image.shape[0] / 2
    width_scaled, height_scaled = image.shape[1] * scale, image.shape[0] * scale
    left_x, right_x = center_x - width_scaled / 2, center_x + width_scaled / 2
    top_y, bottom_y = center_y - height_scaled / 2, center_y + height_scaled / 2
    img_cropped = image[int(top_y):int(bottom_y), int(left_x):int(right_x)]
    return img_cropped


def rotate_image(image, rotation):
    if str(rotation) == "90":
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif str(rotation) == "180":
        rotated_image = cv2.rotate(image, cv2.ROTATE_180)
    elif str(rotation) == "270":
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        rotated_image = image
    return rotated_image


def mark_image(image, size, center, resolution):
    size_x = int(resolution[0]/1000*size)
    size_y = int(resolution[1]/1000*size)

    local_image = image

    start_rect = (int(center[0]) - size_x*6, int(center[1]) - size_y*4)
    end_rect = (int(center[0]) + size_x*6, int(center[1]) + size_y*4)

    start_line = (int(center[0]), int(center[1]) - size_x)
    end_line = (int(center[0]), int(center[1]) + size_x)

    local_image = cv2.rectangle(local_image, start_rect, end_rect, (255, 255, 0), 2)
    local_image = cv2.line(local_image, start_line, end_line, (255, 255, 0), 2)

    return local_image


def convert_location_percentage_to_cv(location, image):
    location_x = int((100 - location[0]) * image.shape[1] / 100)
    location_y = int(location[1] * image.shape[0] / 100)
    local_location = (location_x, location_y)
    return local_location
