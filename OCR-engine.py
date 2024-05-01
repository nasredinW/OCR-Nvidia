import cv2
import pytesseract

def ocr(image_path):
    # Load the image from file
    image = cv2.imread(image_path)

    # Preprocess the image (e.g., convert to grayscale, apply thresholding, etc.)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Perform OCR using Tesseract
    text = pytesseract.image_to_string(thresh)

    return text

if __name__ == "__main__":
    image_path = "assets/kudra.png"
    extracted_text = ocr(image_path)
    print(extracted_text)
