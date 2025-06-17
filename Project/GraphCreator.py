import subprocess
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


folder = "Packets"  # your folder path
packets_dict = {}

for filename in os.listdir(folder):
    if "Custom-2" in filename:
        full_path = os.path.join(folder, filename)
        packets_dict[filename] = full_path



def convert_svg_to_png(svg_path, png_path):
    inkscape_path = r"C:\\Program Files\\Inkscape\\bin\\inkscape.exe" 
    subprocess.run([
        inkscape_path, svg_path,
        "--export-type=png",
        "--export-filename", png_path
    ], check=True)


def GraphCreator(dictionary):
    output_folder = "Graphs"
    os.makedirs(output_folder, exist_ok=True)

    for key, file_path in dictionary.items():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                svg_string = f.read()
            print(f"File '{file_path}' (key: {key}) read as text successfully.")
        except UnicodeDecodeError:
            print(f"File '{file_path}' (key: {key}) is not plain UTF-8 text.")
            continue
        except Exception as e:
            print(f"Error reading file '{file_path}' (key: {key}): {e}")
            continue

        svg_output = os.path.join(output_folder, f"{key}.svg")
        png_output = os.path.join(output_folder, f"{key}.png")

        with open(svg_output, "w", encoding="utf-8") as f:
            f.write(svg_string)

        convert_svg_to_png(svg_output, png_output)



def PDFCreator(image_folder, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    images = [f for f in os.listdir(image_folder) if f.lower().endswith(".png")]
    images.sort()
    for img_file in images:
        img_path = os.path.join(image_folder, img_file)
        c.drawImage(img_path, 0, 0, width=width, height=height, preserveAspectRatio=True, anchor='c')
        c.showPage()

    c.save()
    print(f"PDF created at {output_pdf}")





def CreateReport(dictionary):
    GraphCreator(dictionary)
    PDFCreator("Graphs", "Report.pdf")


CreateReport(packets_dict)