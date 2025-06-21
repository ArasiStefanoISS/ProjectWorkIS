import subprocess
import os
import io
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Preformatted, Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
import pandas as pd
import matplotlib.pyplot as plt
import ast
from collections import Counter
import json
import matplotlib.pyplot as plt




def get_custom_packets(folder):
    packets_dict = {}

    for filename in os.listdir(folder):
        if "Custom" in filename:
            full_path = os.path.join(folder, filename)
            packets_dict[filename] = full_path

    return packets_dict


def is_csv(file_path):
    try:
        pd.read_csv(file_path)
        return True
    except Exception:
        return False

def is_bad_csv(file_path):
    isBad=is_csv(file_path)
    isHeader=True
    try:
        pd.read_csv(file_path, nrows=1)
        isHeader=True
    except Exception:
        isHeader=False
    if isHeader==False:
        return False
    if isHeader==True and isBad==False:
        return True

def is_image(file_path):
    from PIL import Image
    try:
        with Image.open(file_path) as img:
            return True
    except Exception:
        return False
    
def is_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, FileNotFoundError, PermissionError):
        return False


def convert_svg_to_png(svg_path, png_path):
    inkscape_path = r"C:\\Program Files\\Inkscape\\bin\\inkscape.exe" 
    subprocess.run([
        inkscape_path, svg_path,
        "--export-type=png",
        "--export-filename", png_path
    ], check=True)


def GraphCreator(output_folder,dictionary):
    os.makedirs(output_folder, exist_ok=True)

    for key, file_path in dictionary.items():
        if is_json_file(file_path)==False:
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


def PDFCreator2(folder, output_pdf):
    # Temporary in-memory PDF to hold new pages
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter

    # Sort images (you can add your logic to define sections here)
    images = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    images.sort()

    title = folder
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 30, title)

    if images:
        for img_file in images:
            img_path = os.path.join(folder, img_file)

            # Draw a title based on the file name (without extension)
            title = os.path.splitext(img_file)[0].replace('_', ' ').title()
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width / 2,height - 50, title)#height - 50,

            # Draw the image
            c.drawImage(img_path, 0, 0, width=width, height=height, preserveAspectRatio=True, anchor='c')

            c.showPage()

        c.save()
        packet.seek(0)
        # Read the in-memory PDF
        new_pdf = PdfReader(packet)

        # If output PDF already exists, read it and append new pages
        if os.path.exists(output_pdf):
            existing_pdf = PdfReader(output_pdf)
            writer = PdfWriter()

            for page in existing_pdf.pages:
                writer.add_page(page)

            for page in new_pdf.pages:
                writer.add_page(page)

            with open(output_pdf, "wb") as f_out:
                writer.write(f_out)
            print(f"Appended to existing PDF at {output_pdf}")
        else:
            # Save as new PDF
            writer = PdfWriter()
            for page in new_pdf.pages:
                writer.add_page(page)

            with open(output_pdf, "wb") as f_out:
                writer.write(f_out)
            print(f"PDF created at {output_pdf}")
    
    pdfs=[f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    pdfs.sort()  # optional: sort alphabetically
    
    if pdfs:
        writer = PdfWriter()

        # If Report.pdf already exists, add its pages first
        if os.path.exists(output_pdf):
            print(f"Appending to existing {output_pdf}")
            with open(output_pdf, "rb") as existing:
                reader = PdfReader(existing)
                for page in reader.pages:
                    writer.add_page(page)

        # Add pages from other PDFs in the folder
        for pdf_file in pdfs:
            full_path = os.path.join(folder, pdf_file)
            if os.path.abspath(full_path) == os.path.abspath(output_pdf):
                continue  # skip Report.pdf itself to avoid infinite loop

            print(f"Adding {pdf_file}")
            reader = PdfReader(full_path)
            for page in reader.pages:
                writer.add_page(page)

        # Save to output PDF
        with open(output_pdf, "wb") as f_out:
            writer.write(f_out)

    print(f"Report generated at {output_pdf}")





def csv_to_pdf_table(folder, dictionary):
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 7
    styleN.leading = 9

    title_style = styles["Title"]
    subtitle_style = styles["Heading2"]

    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists


    for output_pdf, csv_file in dictionary.items():
        if is_json_file(csv_file)==False:
            output_pdf += ".pdf"
            try:
                df = pd.read_csv(csv_file)

                # Prepare table data with wrapped cells
                data = [[Paragraph(str(cell), styleN) for cell in row] for row in [df.columns.tolist()] + df.values.tolist()]

                # Column widths
                page_width, _ = landscape(letter)
                usable_width = page_width - 60  # left + right margin (30 each)
                num_columns = len(df.columns)
                col_widths = [usable_width / num_columns] * num_columns

                # Create table
                table = Table(data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                ]))

                # Build output path
                base_name = os.path.basename(output_pdf)
                output_path = os.path.join(folder, base_name)

                # Titles
                folder_title = os.path.basename(folder).title()
                file_title = os.path.splitext(base_name)[0].replace("_", " ").title()
                title_para = Paragraph(folder_title, title_style)
                subtitle_para = Paragraph(file_title, subtitle_style)

                # Assemble PDF content
                elements = [title_para, Spacer(1, 6), subtitle_para, Spacer(1, 12), table]

                # Build PDF
                doc = SimpleDocTemplate(
                    output_path,
                    pagesize=landscape(letter),
                    leftMargin=30, rightMargin=30,
                    topMargin=30, bottomMargin=30
                )
                doc.build(elements)

                print(f"Created PDF: {output_path}")
            except Exception as badFile:
                print(f"Failed to process {csv_file}: {badFile}")
                if is_bad_csv(csv_file):
                    bad_csv_to_pdf(folder, {output_pdf: csv_file})
                else:
                    GraphCreator(folder, {output_pdf: csv_file})


def bad_csv_to_pdf(folder,dictionary):
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 7
    styleN.leading = 9

    title_style = styles["Title"]
    subtitle_style = styles["Heading2"]

    # Create title and paragraph
    pdf_title = Paragraph(folder, title_style)

    # Optional spacer for some vertical space
    spacer = Spacer(1, 12)  # (width, height) — height is 12 points here

    elements=[pdf_title,spacer]

    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists


    for output_pdf, csv_file in dictionary.items():

        table_para_title = Paragraph(output_pdf, subtitle_style)
        elements.append(table_para_title)

        output_pdf += ".pdf"

        count=0
        col=[]
        rows=[]
        with open(csv_file, "r") as f:
            for line in f:
                count+=1
                parts=line.strip().split(",")
                isArray=False
                isJson=False
                array=[]
                json_string=""
                if count==1:
                    col = parts
                else:
                    fixed_line=[]
                    for word in parts:
                        if ("{" in word or isJson) and not isArray:
                            isJson=True
                            if "}" in word:
                                json_string+=word
                                isJson=False
                                json_string_fixed=json_string.replace("'","")
                                fixed_line.append(json.loads(json_string_fixed))
                                json_string=""
                            else:
                                json_string+=word+", "
                        elif ("[" in word or isArray) and not isJson:
                            isArray=True
                            if "]" in word:
                                array.append(word.replace("]", ""))
                                isArray=False
                                fixed_line.append(array)
                                array=[]
                            else:
                                array.append(word.replace("[", ""))
                        else:
                            fixed_line.append(word)

                    rows.append(fixed_line)


        df=pd.DataFrame(rows,columns=col)

        # Prepare PDF
        doc = SimpleDocTemplate(folder+"/table_with_histograms.pdf", pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        styleN = styles["Normal"]

        # Custom style for arrays with wrapping (optional)
        array_style = ParagraphStyle(
            name="ArrayStyle",
            fontSize=8,
            leading=10,
            wordWrap='CJK',
        )

        # Prepare header
        columns = df.columns.tolist()
        table_data = [columns]

        # Constants for image size
        MAX_IMAGE_WIDTH = 100
        MAX_IMAGE_HEIGHT = 70

        # Build each row dynamically
        for _, row in df.iterrows():
            row_cells = []

            for col in df.columns:
                value = row[col]

                # Handle array/list: convert to string and truncate
                if isinstance(value, list):
                    value_str = ", ".join(map(str, value))
                    value_str = truncate_text(value_str)
                    row_cells.append(Paragraph(value_str, styleN))

                # Handle JSON histogram
                elif isinstance(value, (dict, str)) and (
                    (isinstance(value, str) and value.strip().startswith("{") and "keys" in value)
                    or isinstance(value, dict)
                ):
                    try:
                        hist_data = json.loads(value) if isinstance(value, str) else value
                        fig, ax = plt.subplots(figsize=(2, 1.2))
                        ax.bar(hist_data['keys'], hist_data['values'])

                        # Hide x-axis tick labels and ticks, but keep the spine (line)
                        ax.set_xticks([])             # Remove tick marks
                        ax.set_xticklabels([])        # Remove tick labels
                        # Note: Do NOT hide the spine to keep the bottom line

                        plt.tight_layout()

                        img_buffer = io.BytesIO()
                        plt.savefig(img_buffer, format='PNG')
                        plt.close(fig)
                        img_buffer.seek(0)

                        img = Image(img_buffer, MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT)  # image size fixed here
                        row_cells.append(img)
                    except Exception:
                        row_cells.append(Paragraph("Invalid Histogram", styleN))

                # Handle long strings: truncate if needed
                elif isinstance(value, str):
                    value_str = truncate_text(value)
                    row_cells.append(Paragraph(value_str, styleN))

                # Other types: just convert and truncate if too long
                else:
                    value_str = truncate_text(value)
                    row_cells.append(Paragraph(value_str, styleN))

            table_data.append(row_cells)


        MAX_WIDTH = 150  # max width for text columns
        usable_width = landscape(letter)[0] - 60  # 30 margin on each side


        
        col_widths = []
        for col_name in df.columns:
            # Arrays get fixed width 80
            if df[col_name].apply(lambda x: isinstance(x, list)).any():
                col_widths.append(80)

            # Histograms (dict or JSON string) get double width
            elif df[col_name].apply(lambda x: (
                isinstance(x, dict) or 
                (isinstance(x, str) and x.strip().startswith("{") and "keys" in x)
            )).any():
                col_widths.append(1.2 * MAX_IMAGE_WIDTH)

            else:
                # Distribute remaining width evenly but max MAX_WIDTH
                col_widths.append(min(usable_width / len(df.columns), MAX_WIDTH))

        # Create and style table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table._argW = col_widths  # reinforce widths for layout
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))

        #elements.append(table_data)
        elements.append(table)

        # Build PDF
        doc.build(elements)


def truncate_text(text, max_len=150):
    text = str(text)
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text



def json_to_pdf(folder,dictionary):
    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists

    

    styles = getSampleStyleSheet()
    main_title_style = styles['Title']
    section_title_style = styles['Heading2']
    code_style = styles['Code']

    elements = []

    # Add main title on first page
    elements.append(Paragraph(folder, main_title_style))
    elements.append(Spacer(1, 24))

    for section_title, json_path in dictionary.items():

        # Section title
        elements.append(Paragraph(section_title, section_title_style))
        elements.append(Spacer(1, 12))

        # Load and pretty print JSON
        with open(json_path, 'r') as f:
            data = json.load(f)
        pretty_json = json.dumps(data, indent=4)

        # JSON content as preformatted text
        elements.append(Preformatted(pretty_json, code_style))

        # Build output path
        output_pdf=json_path+".pdf"
        base_name = os.path.basename(output_pdf)
        output_path = os.path.join(folder, base_name)

        doc = SimpleDocTemplate(output_path, pagesize=letter,
                            leftMargin=30, rightMargin=30,
                            topMargin=30, bottomMargin=30)

        doc.build(elements)
    print(f"PDF created at {output_pdf}")





def CreateReport(title,dictionary):
    try:
        json_to_pdf(title,dictionary)
    except:
        try:
            csv_to_pdf_table(title,dictionary)
        except:
            try:
                GraphCreator(title,dictionary)
            except:
                print("error")
    PDFCreator2(title, "Report.pdf")


CreateReport("DataMitigationSummary",get_custom_packets("Packets/DataMitigationSummary"))
CreateReport("DatasetConfirmation",get_custom_packets("Packets/DatasetConfirmation"))
CreateReport("Proxies",get_custom_packets("Packets/Proxies"))
CreateReport("Detection",get_custom_packets("Packets/Detection"))
CreateReport("DataMitigation",get_custom_packets("Packets/DataMitigation"))
CreateReport("FeatureSelection",get_custom_packets("Packets/FeatureSelection"))