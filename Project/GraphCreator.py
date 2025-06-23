import subprocess
import os
import io
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
import pandas as pd
import matplotlib.pyplot as plt
import json
import matplotlib.pyplot as plt
from tempfile import TemporaryDirectory
import re
from reportlab.lib.enums import TA_LEFT

extra_feature_selection=False

def to_cammel_case(s):
    s = s.strip()
    if not s:
        return ''
    
    # If first character is already uppercase, return as-is
    if s[0].isupper():
        return s

    # Otherwise, convert to PascalCase
    words = s.split()
    return ''.join(word.capitalize() for word in words)



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


def GraphCreator(output_folder,key,file_path):
    output_folder="ReportData/"+output_folder
    os.makedirs(output_folder, exist_ok=True)

    if is_json_file(file_path)==False:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                svg_string = f.read()
            print(f"File '{file_path}' (key: {key}) read as text successfully.")
            svg_output = os.path.join(output_folder, f"{key}.svg")
            png_output = os.path.join(output_folder, f"{key}.png")

            with open(svg_output, "w", encoding="utf-8") as f:
                f.write(svg_string)

            convert_svg_to_png(svg_output, png_output)
        except UnicodeDecodeError:
            print(f"File '{file_path}' (key: {key}) is not plain UTF-8 text.")
        except Exception as e:
            print(f"Error reading file '{file_path}' (key: {key}): {e}")

        


def add_title_overlay(page, title_text):
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    # Clean and format title
    cleaned_title = title_text.strip().replace("_", " ")

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0, 0, 0)

    # Measure text width and calculate centered x
    text_width = c.stringWidth(cleaned_title, "Helvetica-Bold", 24)
    x = (width - text_width) / 2
    y = height - 36  # Adjust vertical position if needed

    c.drawString(x, y, cleaned_title)
    c.save()
    packet.seek(0)

    overlay_reader = PdfReader(packet)
    overlay_page = overlay_reader.pages[0]
    page.merge_page(overlay_page)
    return page


def PDFCreator2(folder, output_pdf):
    # Temporary in-memory PDF to hold new pages
    first=True
    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter

    title = folder

    folder="ReportData/"+folder

    # Sort images (you can add your logic to define sections here)
    images = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    images.sort()

    if images:
        if first==True:
            c.setFont("Helvetica-Bold", 24)
            c.drawCentredString(width / 2, height - 30, title)
            first=False

        for img_file in images:
            img_path = os.path.join(folder, img_file)

            # Draw a title based on the file name (without extension)
            title = os.path.splitext(img_file)[0].split("__")[0].replace("_", " ")
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(width*0.2, height-130, to_cammel_case(title))

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

        first_pdf = True
        if first==False:
            first_pdf=False

        # Add pages from other PDFs in the folder
        for pdf_file in pdfs:
            full_path = os.path.join(folder, pdf_file)
            if os.path.abspath(full_path) == os.path.abspath(output_pdf):
                continue  # skip Report.pdf itself

            print(f"Adding {pdf_file}")
            reader = PdfReader(full_path)

            for i, page in enumerate(reader.pages):
                # Add title overlay only on the first page of the first PDF
                if first_pdf and i == 0:
                    print(f"Adding title to {pdf_file}'s first page")
                    page = add_title_overlay(page, title)

                writer.add_page(page)

            first_pdf = False  # Only first PDF gets title on first page

        # Save to output PDF
        with open(output_pdf, "wb") as f_out:
            writer.write(f_out)

    print(f"Report generated at {output_pdf}")





def csv_to_pdf_table(folder, output_pdf, csv_file):
    folder="ReportData/"+folder
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 7
    styleN.leading = 9

    subtitle_style = styles["Heading2"]

    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists


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

            # Title
            file_title = os.path.splitext(base_name)[0].split("__")[0].replace("_", " ")
            subtitle_para = Paragraph(to_cammel_case(file_title), subtitle_style)

            # Assemble PDF content
            elements = [ Spacer(1, 6), subtitle_para, Spacer(1, 12), table]

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
                bad_csv_to_pdf(folder, output_pdf, csv_file)


def bad_csv_to_pdf(folder,output_pdf,csv_file ):
    styles = getSampleStyleSheet()
    styleN = styles["BodyText"]
    styleN.fontSize = 7
    styleN.leading = 9

    subtitle_style = styles["Heading2"]

    spacer = Spacer(1, 12) 

    elements=[spacer]

    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists

    table_para_title = Paragraph(to_cammel_case(output_pdf.split("__")[0]), subtitle_style)
    elements.append(table_para_title)

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
    pdf_path = os.path.join(folder, output_pdf)
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]

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

    elements.append(table)

    # Build PDF
    doc.build(elements)


def truncate_text(text, max_len=150):
    text = str(text)
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def json_to_pdf2(folder,section_title,json_path):
    folder="ReportData/"+folder
    os.makedirs(folder, exist_ok=True)  # Ensure output folder exists

    styles = getSampleStyleSheet()
    section_title_style = styles['Heading2']

    pdf_filename=folder+"/"+section_title+".pdf"

    elements = []

    elements.append(Spacer(1, 24))

    elements.append(Paragraph(to_cammel_case(section_title.split("__")[0]),section_title_style))
    elements.append(Spacer(1, 12))  # Add space between title and table

    print(section_title)
    with open(json_path, 'r') as f:
        data = json.load(f)

    

    cleaned_data = {
        key.strip('" '): value
        for key, value in data.items()
    }


    def contains_when(data):
        if not isinstance(data, dict):
            return False
        for key, val in data.items():
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, dict) and "when" in item:
                        return True
        return False
    
    def search_key(obj, key="suggested_proxy"):
        if isinstance(obj, dict):
            if key in obj:
                return True
            return any(search_key(v, key) for v in obj.values())
        elif isinstance(obj, list):
            return any(search_key(item, key) for item in obj)
        return False
    
    if(contains_when(cleaned_data)):
        histogram_json_to_pdf(folder,section_title,json_path)
    elif(search_key(cleaned_data)):
        suggested_json_to_pdf(folder,section_title,json_path)
    elif(search_key(cleaned_data,"$algorithm")):
        preprocessing_json_to_pdf(folder,section_title,json_path)
    else:
        # Auto-infer all unique inner keys
        columns = set()
        for props in cleaned_data.values():
            columns.update(props.keys())
        
        # Sort columns to keep them consistent
        columns = sorted(columns)
        # Value formatting
        def format_value(val):
            if isinstance(val, bool):
                return "✔" if val else "✘"
            elif isinstance(val, float):
                return f"{val * 100:.0f}%"  # convert to percentage
            return str(val)

        # Build table rows
        table_data = [["Field Name"] + columns]  # Add headers
        for field_name, properties in cleaned_data.items():
            row = [field_name] + [format_value(properties.get(col)) for col in columns]
            table_data.append(row)


        # Create PDF
        if (search_key(cleaned_data,"target")) and (search_key(cleaned_data,"sensitive")) and (search_key(cleaned_data,"drop")):
            os.makedirs("ReportData/FeatureSelection", exist_ok=True)  # Ensure output folder exists
            pdf_filename="ReportData/FeatureSelection/"+section_title+".pdf"
            global extra_feature_selection
            extra_feature_selection=True
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)

        # Create and style the table
        table = Table(table_data, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ]))

        elements.append(table)
        doc.build(elements)

        print(f"PDF saved as: {pdf_filename}")


def create_histogram_image(labels, values, img_path, title=None):
    plt.figure(figsize=(2,1.5))
    plt.bar(labels, values, color='skyblue')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    if title:
        plt.title(title, fontsize=8)
    plt.savefig(img_path)
    plt.close()



def sanitize_filename(text):
    return re.sub(r'[^\w\-_.]', '_', str(text))


def histogram_json_to_pdf(folder, pdf_name, json_path):
    os.makedirs(folder, exist_ok=True)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pdf_path = os.path.join(folder, f"{pdf_name}.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4))
    elements = []
    styles = getSampleStyleSheet()

    left_heading2 = ParagraphStyle('LeftHeading2', parent=styles['Heading2'], alignment=TA_LEFT)
    elements.append(Paragraph(to_cammel_case(pdf_name.split("__")[0].replace("_"," ")), left_heading2))

    elements.append(Spacer(1, 24))

    with TemporaryDirectory() as tmpdir:
        for metric_name, records in data.items():
            if not records:
                continue

            when_keys = list(records[0].get('when', {}).keys())
            if len(when_keys) < 2:
                continue
            first_attr, second_attr = when_keys[0], when_keys[1]

            first_vals = sorted(set(r['when'][first_attr] for r in records if first_attr in r['when']))
            second_vals = sorted(set(r['when'][second_attr] for r in records if second_attr in r['when']))

            data_map = {col_val: {row_val: None for row_val in first_vals} for col_val in second_vals}

            for rec in records:
                w = rec['when']
                val = rec.get('value', None)
                if val is None:
                    continue
                f_val = w.get(first_attr)
                s_val = w.get(second_attr)
                if f_val in first_vals and s_val in second_vals:
                    data_map[s_val][f_val] = val

            # Break second_vals into chunks of max 8 columns
            chunk_size = 6
            for i in range(0, len(second_vals), chunk_size):
                chunk = second_vals[i:i+chunk_size]

                # Create header row for this chunk
                header_row = [""] + chunk
                # Create image row for this chunk
                img_cells = []
                for col_val in chunk:
                    labels = []
                    values = []
                    for f_val in first_vals:
                        v = data_map[col_val][f_val]
                        if v is not None:
                            labels.append(str(f_val))
                            values.append(v)
                    img_path = os.path.join(tmpdir, f"{metric_name}_{sanitize_filename(col_val)}.png")
                    create_histogram_image(labels, values, img_path, title=col_val)
                    img = Image(img_path, width=100, height=80)
                    img_cells.append(img)

                data_rows = [["Values"] + img_cells]

                table_data = [header_row] + data_rows

                col_widths = [100] + [110] * len(chunk)
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('ALIGN', (1,1), (-1,-1), 'CENTER'),
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ]))

                elements.append(KeepTogether([
                    Paragraph(to_cammel_case(metric_name.split("__")[0]), styles['Heading2']),
                    Spacer(1, 12),
                    table
                ]))
                elements.append(Spacer(1, 24))

        doc.build(elements)
        print(f"PDF created at: {pdf_path}")


def suggested_json_to_pdf(folder, name, path):
    os.makedirs(folder, exist_ok=True)
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(os.path.join(folder, f"{name}.pdf"), pagesize=letter)
    elements = []

    left_heading2 = ParagraphStyle('LeftHeading2', parent=styles['Heading2'], alignment=TA_LEFT)
    elements.append(Paragraph(to_cammel_case(name.split("__")[0].replace("_"," ")), left_heading2))

    elements.append(Spacer(1, 24))

    max_cols=6

    

    for main_attr, nested_dict in data.items():
        header = main_attr.strip('\" ')

        columns = list(nested_dict.keys())
        clean_columns = [col.strip('\" ') for col in columns]

        # Get row labels from first nested dict value
        example_values = nested_dict[columns[0]]
        row_labels = list(example_values.keys())

        # Split columns in chunks of max_cols
        for i in range(0, len(columns), max_cols):
            chunk_cols = columns[i:i+max_cols]
            chunk_clean_cols = clean_columns[i:i+max_cols]

            table_data = [["", *chunk_clean_cols]]

            for row_label in row_labels:
                row = [row_label]
                for col in chunk_cols:
                    val = nested_dict[col].get(row_label)
                    if isinstance(val, float):
                        val_str = f"{val * 100:.2f}%"
                    elif isinstance(val, bool):
                        val_str = "✓" if val else "✗"
                    else:
                        val_str = str(val)
                    row.append(val_str)
                table_data.append(row)

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (1,0), (-1,0), colors.lightgrey),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('ALIGN', (1,1), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ]))

            elements.append(Paragraph(to_cammel_case(header.split("__")[0]), left_heading2))
            elements.append(Spacer(1, 12))
            elements.append(table)
            elements.append(Spacer(1, 24))

    doc.build(elements)
    print(f"PDF saved to {doc.filename}")

def preprocessing_json_to_pdf(folder, name, path):
    os.makedirs(folder, exist_ok=True)

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(os.path.join(folder, f"{name}.pdf"), pagesize=letter)
    elements = []

    # Prepare header (keys) and one row of values
    headers = list(data.keys())
    values = []
    for val in data.values():
        if isinstance(val, float):
            values.append(f"{val * 100:.2f}%")  # Format float as percentage
        else:
            values.append(str(val))

    # Build table data: one row for headers, one for values
    table_data = [headers, values]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    left_heading2  = ParagraphStyle('LeftHeading2', parent=styles['Heading2'], alignment=TA_LEFT)
    elements.append(Paragraph(to_cammel_case(name.split("__")[0]), left_heading2))
    elements.append(Spacer(1, 12))
    elements.append(table)
    elements.append(Spacer(1, 24))

    doc.build(elements)
    print(f"PDF saved to: {os.path.join(folder, f'{name}.pdf')}")

def CreateReportData(title,dictionary):
    for name,value in dictionary.items():
        try:
            json_to_pdf2(title,name,value)
        except:
            try:
                csv_to_pdf_table(title,name,value)
            except:
                try:
                    GraphCreator(title,name,value)
                except:
                    print("error")


CreateReportData("DatasetConfirmation",get_custom_packets("Packets/DatasetConfirmation"))
CreateReportData("FeatureSelection",get_custom_packets("Packets/FeatureSelection"))
CreateReportData("Proxies",get_custom_packets("Packets/Proxies"))
CreateReportData("Detection",get_custom_packets("Packets/Detection"))
CreateReportData("DataMitigation",get_custom_packets("Packets/DataMitigation"))
CreateReportData("DataMitigationSummary",get_custom_packets("Packets/DataMitigationSummary"))


def CreateReport(folder):
    if os.path.isdir(folder):
        folders = [
            f for f in os.listdir(folder)
            if os.path.isdir(os.path.join(folder, f))
        ]

        # Sort by creation time
        folders.sort(key=lambda f: os.path.getctime(os.path.join(folder, f)))

        for dir in folders:
            PDFCreator2(dir,"Report.pdf")
    else:
        print("ReportData does not exist")

CreateReport("ReportData")

