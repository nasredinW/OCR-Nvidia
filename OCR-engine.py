import os
import cv2
import pytesseract
from PIL import Image, ImageOps
from pytesseract import Output
import pdf2image

def ocr(file_path):
    """
    Perform OCR on the given image or PDF file and return tokens and extracted text.

    Args:
        file_path (str): The path to the image or PDF file.

    Returns:
        tuple: A tuple containing tokens and extracted text.
    """
    tokens = []
    extracted_text = ""

    # Check if the file is a PDF
    if file_path.lower().endswith(".pdf"):
        # Convert PDF pages to images
        pages = pdf2image.convert_from_path(file_path)

        for i, page in enumerate(pages):
            # Preprocess the image (e.g., convert to grayscale, apply thresholding, etc.)
            gray = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Get tokens and text using the get_tokens_from_tesseract function
            page_tokens, page_text = get_tokens_from_tesseract(Image.fromarray(thresh), extracted_text, i + 1, -1, 0)
            tokens.extend(page_tokens)
            extracted_text += page_text

    else:
        # Load the image from file
        image = cv2.imread(file_path)

        # Preprocess the image (e.g., convert to grayscale, apply thresholding, etc.)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Convert the OpenCV image to a PIL Image
        image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Get tokens and text using the get_tokens_from_tesseract function
        tokens, extracted_text = get_tokens_from_tesseract(image, extracted_text, 1, -1, 0)

    return tokens, extracted_text

# The rest of the code remains the same as before


def get_tokens_from_tesseract(
    image, text, pageNumber, last_token_id, last_token_position, exif_orientation=None, language=None
):
    """
    Get text and tokens/spans from an image using Tesseract and the pytesseract Python wrapper.

    Args:
        image (PIL Image): The image to perform OCR on.
        pageNumber (int): The page number.
        last_token_id (int): The ID of the last token.
        last_token_position (int): The end position of the last token in the text.
        exif_orientation (bool, optional): Whether to rotate the image based on EXIF orientation. Defaults to None.
        language (str, optional): The language code for Tesseract. Defaults to None.

    Returns:
        tuple: A tuple containing tokens and text.
    """
    # Get original text from image
    if language is None:
        text += pytesseract.image_to_string(image, lang="eng+mkd+deu")
        tesseract_output = pytesseract.image_to_data(image, output_type=Output.DICT, lang="eng+mkd+deu")
    else:
        text += pytesseract.image_to_string(image, lang=language)
        tesseract_output = pytesseract.image_to_data(image, output_type=Output.DICT, lang=language)

    # Make sure width/height are in correct order if the image is rotated
    if exif_orientation:
        image = ImageOps.exif_transpose(image)

    tokens = []  # To store tokens in the desired format
    counter = last_token_position  # To keep the position of the word in the document
    id_index = last_token_id + 1  # To increment the ID of tokens added

    # Format the result from the output to the desired JSON format
    for index, word in enumerate(tesseract_output["text"]):
        if tesseract_output["conf"][index] != "-1" and word != "" and word != " ":
            if not word in text:
                continue

            counter = get_index_word_from_text(word, text, counter)
            tokens.append(
                {
                    "id": id_index,
                    "end": counter + len(word) - 1,
                    "top": tesseract_output["top"][index],
                    "conf": tesseract_output["conf"][index],
                    "left": tesseract_output["left"][index],
                    "text": word,
                    "start": counter,
                    "width": tesseract_output["width"][index],
                    "height": tesseract_output["height"][index],
                    "length": len(word),
                    "pageNum": pageNumber,
                    "pageSize": {"width": image.size[0], "height": image.size[1]},
                    "selected": False,
                }
            )
            counter += len(word)
            id_index += 1

    # Return the formatted output
    return tokens, text

def get_index_word_from_text(word, text, index):
    """
    Find the start position of a word in the text, starting from the given index.

    Args:
        word (str): The word to search for.
        text (str): The text to search in.
        index (int): The index to start searching from.

    Returns:
        int: The start position of the word in the text.
    """
    while text[index : index + len(word)] != word:
        index += 1

    return index

if __name__ == "__main__":
    image_path = "assets/kudra.png"
    tokens, extracted_text = ocr(image_path)
    print("Tokens: ", tokens)
    print("Extracted Text: ", extracted_text)
