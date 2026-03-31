from openai import OpenAI
import os
import fitz  # PyMuPDF

client = OpenAI(api_key="YOUR_API_KEY")

os.makedirs("extracted_images", exist_ok=True)
os.makedirs("output", exist_ok=True)

def extract_pdf_data(file_path, prefix):
    doc = fitz.open(file_path)
    text = ""
    image_paths = []

    for page_num, page in enumerate(doc):
        text += page.get_text()

        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image_name = f"{prefix}_page{page_num+1}_img{img_index+1}.png"
            image_path = os.path.join("extracted_images", image_name)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(image_path)

    return text, image_paths


inspection_file = input("Enter inspection PDF path: ")
thermal_file = input("Enter thermal PDF path: ")

inspection_text, inspection_images = extract_pdf_data(inspection_file, "inspection")
thermal_text, thermal_images = extract_pdf_data(thermal_file, "thermal")

all_images = inspection_images + thermal_images

image_list_text = "\n".join([f"- {img}" for img in all_images])

prompt = f"""
You are an AI system generating a Detailed Diagnostic Report (DDR).

Inspection Report:
{inspection_text}

Thermal Report:
{thermal_text}

Images:
{image_list_text}

Instructions:
- Extract observations
- Merge similar points
- Remove duplicates
- Assign only relevant images
- If no image → write "Image Not Available"
- Do not invent anything

Output format:
1. Property Issue Summary
2. Area-wise Observations
3. Root Cause
4. Severity
5. Actions
6. Notes
7. Missing Info
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}]
)

report = response.choices[0].message.content

with open("output/ddr_report.txt", "w") as f:
    f.write(report)

print("DONE")
