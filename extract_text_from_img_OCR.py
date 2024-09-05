import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
from datetime import datetime

# Set the path for Tesseract if it's not in your system's PATH
# For example, on Windows you might need something like:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# TODO:
# delete files once picked out of IN
# format extracted text into valid paragraphs once extracted out. batch it based off token limit to gemini API, etc.
#


def fetch_files():
    input_directory = 'IN'
    valid_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
    valid_files = []

    for filename in os.listdir(input_directory):
        if any(filename.lower().endswith(ext) for ext in valid_extensions):
            full_path = os.path.join(input_directory, filename)
            valid_files.append(full_path)

    print("file list:" + str(valid_files))
    return valid_files


def file_orchestrator(file_list):
    pdf_png_files = []
    successfully_processed = []
    output_directory = "OUT"

    # for file_path in file_list:
    #     # if IMAGE
    #     if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
    #         print("processing IMAGE: " + file_path)
    #         convert_image_to_text(file_path)

    #     # if PDF
    #     elif file_path.lower().endswith('.pdf'):
    #         print("processing PDF: " + file_path)
    #         # Convert PDF to PNG, then process the image
    #         png_file = pdf_to_img(file_path)
    #         if png_file:
    #             convert_image_to_text(png_file)
    #             # Remove the PNG file after processing
    #             os.remove(png_file)

    # if PDFs are found, convert each page to PNG and return file paths for newly created PNGs (this is only triggering for PDFs, so big(O) is constant.. looks more inefficient than it is)
    # for file_path in file_list:
    #     if file_path.lower().endswith('.pdf'):
    #         print("processing PDF: " + file_path)
    #         # Convert PDF to PNG, then process the image
    #         pdf_img_file_paths = pdf_to_img(file_path)
    #         pdf_png_files.extend(pdf_img_file_paths)

    # # Append newly found PDF PNG files to the file list
    # file_list.extend(pdf_png_files)

    # # Now process all valid image files:
    # for file_path in file_list:
    #     if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
    #         print("processing IMAGE: " + file_path)
    #         convert_image_to_text(file_path)
    #         successfully_processed.append(file_path)

    # # Delete all successfully processed img files from IN
    # delete_files_by_basename(successfully_processed)

    # def file_orchestrator(file_list, out_directory, file_name="output"):
    # pdf_png_files = []
    # successfully_processed = []

    # Get the current date time for filename
    current_date_time = datetime.now().strftime("%Y.%m.%d %H.%M")

    # Construct the output file path with the current date appended
    output_file_path = os.path.join(
        output_directory, f"{current_date_time}.txt")

    # Open the file for writing and append as we process each image
    with open(output_file_path, 'a', encoding='utf-8') as output_file:

        # Process all PDF files (convert to image and add to processing list)
        for file_path in file_list:
            if file_path.lower().endswith('.pdf'):
                print(f"Processing PDF: {file_path}")
                # Convert PDF to PNG, then process the image
                pdf_img_file_paths = pdf_to_img(file_path)
                pdf_png_files.extend(pdf_img_file_paths)

        # Append newly found PDF PNG files to the file list
        file_list.extend(pdf_png_files)

        # Now process all valid image files (PNG, JPEG, etc.)
        for file_path in file_list:
            if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                print(f"Processing IMAGE: {file_path}")

                # Call the function to convert the image to text
                image_text = convert_image_to_text(file_path)

                # Write the image text to the file (appending)
                if image_text:
                    output_file.write(f"Processed file: {file_path}\n")
                    output_file.write(image_text + "\n\n")

                successfully_processed.append(file_path)

    # Delete all successfully processed image files (and original file)
    delete_files_by_basename(file_list.extend(successfully_processed))

    print(f"Processing complete. Output saved to: {output_file_path}")


def pdf_to_img(pdf_path):
    try:
        print("Converting PDF to image...")
        output_dir = "IN"
        created_files = []

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Get the base name of the PDF file without extension
        pdf_base_name = os.path.splitext(os.path.basename(pdf_path))[0]

        # Convert PDF to images
        images = convert_from_path(pdf_path)

        # Process each page
        for i, image in enumerate(images):
            # Create the image filename
            image_filename = f"{pdf_base_name}_{i+1}.png"
            image_path = os.path.join(output_dir, image_filename)

            # Save the image
            image.save(image_path, "PNG")

            # Process the image
            # page_processor(image_path)

            # Add the file path to the list of created files
            created_files.append(image_path)

            print(f"Processed page {i+1}")

        print(f"PDF converted to {len(created_files)} images")
        return created_files

    except Exception as e:
        print(f"An error occurred while converting PDF to image: {e}")
        return ""


def convert_image_to_text(image_path):
    print("Converting image to text...")
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        print(f"Text extracted from {image_path}:\n{text}")
        return text
    except Exception as e:
        print(f"An error occurred while processing {image_path}: {e}")
        return ""


def pdf_to_text(pdf_path, output_txt_path='output.txt', dpi=300):
    try:
        # Convert PDF to images
        pages = convert_from_path(pdf_path, dpi)

        # Initialize an empty string to hold the extracted text
        extracted_text = ""

        for page_number, page in enumerate(pages):
            # Save the page as a temporary image file
            temp_image_path = f"temp_page_{page_number}.png"
            page.save(temp_image_path, 'PNG')

            # Use pytesseract to do OCR on the saved image
            text = pytesseract.image_to_string(Image.open(temp_image_path))

            # Append the text from this page to the overall text
            extracted_text += text + "\n\n"

            # Remove the temporary image file
            os.remove(temp_image_path)

        # Save the extracted text to a text file
        with open(output_txt_path, 'w', encoding='utf-8') as output_file:
            output_file.write(extracted_text)

        print(f"Text extracted and saved to {output_txt_path}")

    except Exception as e:
        print(f"An error occurred: {e}")


def delete_files_by_basename(file_list):
    print("deleting the files from the IN directory...")
    # directories = ["IN"]
    # deleted_files = []
    # for directory in directories:
    #     directory_path = os.path.join(os.getcwd(), directory)
    #     if os.path.exists(directory_path):
    #         for file_name in os.listdir(directory_path):
    #             if os.path.splitext(file_name)[0] == filename:
    #                 file_path = os.path.join(directory_path, file_name)
    #                 os.remove(file_path)
    #                 deleted_files.append(file_name)
    # if len(deleted_files) > 0:
    #     print("Deleted files:", deleted_files)
    # else:
    #     print("No files matching the basename were found.")
    # return deleted_files

    results = {"deleted": [], "skipped": [], "errors": []}

    for file in file_list:
        if not os.path.exists(file):
            results["skipped"].append(file)
            continue

        try:
            os.remove(file)
            results["deleted"].append(file)
        except PermissionError:
            results["errors"].append(f"Permission denied: {file}")
        except Exception as e:
            results["errors"].append(f"Error deleting {file}: {str(e)}")

    print(results)


def main():
    print("Starting...")
    # Get a list of valid files
    file_list = fetch_files()
    # Process the file list
    file_orchestrator(file_list)


main()
