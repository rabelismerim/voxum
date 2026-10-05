"""
Module: excel_utilities

This module provides utility functions for working with Excel files, including creating styled sheets and converting
Excel files to PDF.

Classes:
    - SheetStyle: Class defining styles for Excel sheet cells.
    - ExcelWriter: Class defining methods for writer Excel sheet value and formatting.
    - ExcelToPDFConverter: Convert an Excel file to a PDF file.

Usage:
1. Define cell styles using the SheetStyle class.
2. Use the ExcelWriter class to create and customize Excel files.
3. Optionally, convert Excel files to PDF using the excel_to_pdf function.

Example:
```python
from excel_utilities import SheetStyle, ExcelWriter, excel_to_pdf

# Create a styled sheet
style = SheetStyle()
cell_style = style.gray_fill
font_style = style.bold_white_font

# Create an ExcelWriter instance
excel_writer = ExcelWriter()

# Set center-aligned headers
excel_writer.set_center_headers("Center Header")

# Set left-aligned headers
excel_writer.set_left_headers("Left Header")

# Set right-aligned headers
excel_writer.set_right_headers("Right Header")

# Set the active sheet
excel_writer.set_sheet("Sheet1")

# Set cell values with styling
excel_writer.set_value(1, "A", "Data", font=font_style, fill=cell_style)
excel_writer.set_value(2, ["B", "C"], "Merged Cells", font=font_style, fill=cell_style)

# Save as XLSX
xlsx_file = excel_writer.save_as_xlsx()

# Save as PDF
pdf_file = excel_writer.save_as_pdf()

# Convert Excel to PDF
converter = ExcelToPDFConverter(xlsx_file, output_pdf_file)
converter.set_center_header('Title in header')
converter.convert()
"""
import logging
import os
import tempfile
import textwrap
import uuid

import psutil

import openpyxl
import pythoncom
from openpyxl.styles import Alignment, PatternFill, Font
from openpyxl.worksheet.pagebreak import Break, RowBreak
from xlsx2html import xlsx2html
from win32com import client


def close_all_excel_instances():
    return
    for process in psutil.process_iter(['pid', 'name']):
        if 'excel' in process.info['name'].lower():
            try:
                os.kill(process.info['pid'], 9)
                logging.error('Excel Process stopped')
            except Exception as e:
                logging.error(f"Erro ao finalizar o processo {process.info['name']}: {e}")


class ExcelToPDFConverter:

    def get_excel_instance(self):
        """
        Retorna a instância do Excel, criando uma nova se necessário.
        """
        pythoncom.CoInitialize()

        try:
            excel_instance = client.GetActiveObject("Excel.Application")
            logging.debug("Usando instância existente do Excel.")
            # excel_instance.Visible = True  # Torna a instância visível
        except Exception as e:
            logging.debug(f'e: erro get excel application\n{e}\n\n')
            logging.debug("Nenhuma instância do Excel encontrada, criando nova instância.")
            excel_instance = client.Dispatch("Excel.Application")
            # excel_instance.Visible = True  # Torna a instância visível

        return excel_instance

    def __init__(self, excel_file, output_pdf_file):

        # close_all_excel_instances()
        self.excel_file = os.path.abspath(excel_file)
        self.output_pdf_file = output_pdf_file
        self.output_xlsx_file = output_pdf_file.replace('.pdf', '.xlsx')
        self.excel = self.get_excel_instance()

        self.workbook = self.excel.Workbooks.Open(self.excel_file)
        self.worksheet = self.workbook.Worksheets[0]
        self.filename = os.path.join(os.getcwd(), self.output_pdf_file)
        self.filename_xlsx = os.path.join(os.getcwd(), self.output_xlsx_file)
        self.file_pdf = 0  # 'xlTypePDF'
        self.file_xlsx = 1  # 'xlTypeXPS'
        # self.quality = 1 # 'xlQualityMinimum'
        self.quality = 0  # 'xlQualityStandard'
        self.include_doc_properties = True
        self.ignore_print_areas = True
        self.min_margin_top_default = 130
        self.min_margin_top_default = 90
        self.min_margin_left_default = 10
        self.min_margin_right_default = 5
        self.min_margin_top = self.min_margin_top_default
        self.set_top_margin(self.min_margin_top)

        self.min_margin_left = self.min_margin_left_default
        self.set_left_margin(self.min_margin_left)

        self.min_margin_right = self.min_margin_right_default
        self.set_right_margin(self.min_margin_right)

        self.worksheet.pageSetup.RightFooter = "Página &P/&N"

    def set_repeat_title(self, start_line, end_line):
        self.worksheet.PageSetup.PrintTitleRows = f"${start_line}:${end_line}"

    def set_center_header(self, text):
        """
        Sets the center header text for the PDF.

        Parameters:
            text (str): The text to be set in the center header.
        """
        self.worksheet.PageSetup.CenterHeader = text
        self.calcule_top_margin(text)

    def set_top_margin(self, top_margin):
        self.worksheet.PageSetup.TopMargin = top_margin

    def set_left_margin(self, left_margin):
        self.worksheet.PageSetup.LeftMargin = left_margin

    def set_right_margin(self, right_margin):
        self.worksheet.PageSetup.RightMargin = right_margin

    def calcule_top_margin(self, text):
        if not text:
            return
        return
        num_lines = text.count('\n') + 1  # Conta as quebras de linha
        estimated_height_per_line = 10  # Ajuste conforme necessário
        top_margin = self.min_margin_top_default + num_lines * estimated_height_per_line
        self.min_margin_top = max(top_margin, self.min_margin_top)
        self.set_top_margin(self.min_margin_top)

    def set_page_margin(self, top_margin):
        self.worksheet.PageSetup.TopMargin = top_margin

    def set_left_header(self, text):
        """
        Sets the left header text for the PDF.

        Parameters:
            text (str): The text to be set in the left header.
        """
        self.worksheet.PageSetup.LeftHeader = text
        self.calcule_top_margin(text)

    def set_right_header(self, text):
        """
        Sets the right header text or image for the PDF.

        Parameters:
            text (str): The text to be set in the right header.
        """
        self.worksheet.PageSetup.RightHeader = text
        self.calcule_top_margin(text)

    def set_img_center_header(self, image_path):
        """
        Sets an image in the center header of the PDF.

        Parameters:
            image_path (str): The path to the image file.
        """
        if image_path:
            image_path = os.path.abspath(image_path)
            self.worksheet.PageSetup.CenterHeaderPicture.Filename = image_path
            self.worksheet.PageSetup.CenterHeaderPicture.Width = 70  # Defina o valor desejado em pontos
            self.worksheet.PageSetup.CenterHeaderPicture.CropLeft = - 600  # Defina a margem esquerda desejada em pontos
            self.worksheet.PageSetup.CenterHeader = "&G"

    def set_img_left_header(self, image_path):
        """
        Sets an image in the left header of the PDF.

        Parameters:
            image_path (str): The path to the image file.
        """
        self.worksheet.PageSetup.LeftHeaderPicture.Filename = image_path
        self.worksheet.PageSetup.LeftHeader = "&G"

    def set_img_right_header(self, image_path):
        """
        Sets an image in the right header of the PDF.

        Parameters:
            image_path (str): The path to the image file.
        """
        if image_path:
            image_path = os.path.abspath(image_path)
            self.worksheet.PageSetup.RightHeaderPicture.Filename = image_path
            self.worksheet.PageSetup.RightHeaderPicture.Width = 107  # Defina o valor desejado em pontos
            self.worksheet.PageSetup.RightHeaderPicture.Height = 16  # Defina o valor desejado em pontos
            # self.worksheet.PageSetup.RightHeaderPicture.CropRight = - 28  # Defina a margem esquerda desejada em
            # pontos
            self.worksheet.PageSetup.RightHeader = "&G"

    def set_file_type(self, file_type):
        """
        Sets the type of file to be exported.

        Parameters:
            file_type (int): The type of file (e.g., PDF=0 or XPS=1).
        """
        self.file_pdf = file_type

    def set_quality(self, quality):
        """
        Sets the quality of the exported PDF.

        Parameters:
            quality (int): The quality value.
        """
        self.quality = quality

    def set_include_doc_properties(self, include_doc_properties):
        """
        Sets whether to include document properties in the exported PDF.

        Parameters:
            include_doc_properties (bool): True to include document properties, False otherwise.
        """
        self.include_doc_properties = include_doc_properties

    def set_ignore_print_areas(self, ignore_print_areas):
        """
        Sets whether to ignore print areas in the exported PDF.

        Parameters:
            ignore_print_areas (bool): True to ignore print areas, False otherwise.
        """
        self.ignore_print_areas = ignore_print_areas

    def save_and_close_excel(self):
        """
        Saves changes to the Excel workbook and closes the Excel application.
        """
        self.workbook.Saved = True
        self.workbook.Close(True)
        # self.excel.Quit()

    def export_to_pdf(self):
        """
        Exports the Excel workbook to PDF based on specified settings.
        """
        self.workbook.ExportAsFixedFormat(
            self.file_pdf, self.filename, self.quality, self.include_doc_properties, self.ignore_print_areas
        )

    def export_to_xlsx(self):
        """
        Exports the Excel workbook to XLSX based on specified settings.
        """
        self.workbook.ExportAsFixedFormat(
            self.file_xlsx, self.filename_xlsx, self.quality, self.include_doc_properties, self.ignore_print_areas
        )

    def convert(self):
        """
        Converts the Excel file to PDF.
        """
        self.export_to_pdf()
        self.export_to_xlsx()
        self.save_and_close_excel()


class SheetStyle:
    """
    Class defining styles for Excel sheet cells.

    Attributes:
        gray_fill: PatternFill for gray solid background color.
            - start_color: Hex code for the starting color ("00C0C0C0").
            - end_color: Hex code for the ending color ("00C0C0C0").
            - fill_type: Type of fill, in this case, "solid".

        bold_white_font: Font style for bold white text.
            - bold: Indicates whether the text should be bold (True).
            - color: Hex code for the font color ("FFFFFF").

    Usage:
    style = SheetStyle()
    cell_style = style.gray_fill
    font_style = style.bold_white_font
    """
    gray_fill = PatternFill(start_color="00C0C0C0", end_color="00C0C0C0", fill_type="solid")
    bold_white_font = Font(bold=True, color="FFFFFF")
    bold_black_font = Font(bold=True, color='000000')
    underline = Font(b=True, i=True, u='single')


class ExcelWriter:
    """
    Class for creating and customizing Excel files, and converting them to PDF and HTML.

    Attributes:
        STILE: Reference to the SheetStyle class for cell styling.
        saved: Flag indicating whether the workbook has been saved (False initially).
        center_headers: Text for center-aligned headers.
        left_headers: Text for left-aligned headers.
        right_headers: Text for right-aligned headers.

    Methods:
        __init__: Initializes the ExcelWriter instance.
        set_center_headers: Sets the text for center-aligned headers.
        set_left_headers: Sets the text for left-aligned headers.
        set_right_headers: Sets the text for right-aligned headers.
        set_sheet: Sets the active sheet in the workbook.
        set_value: Sets the value of a cell in the sheet with optional formatting.
        save_as_xlsx: Saves the workbook as an XLSX file.
        save_as_pdf: Saves the workbook as a PDF file, optionally specifying header texts.
        save_as_html: Saves the workbook as an HTML file.

    """
    STILE = SheetStyle
    saved = False
    center_headers = None
    left_headers = None
    right_headers = None

    img_center_headers = None
    img_left_headers = None
    img_right_headers = None
    default_fill_width = None

    def __init__(self, folder=None, output_name_pdf=None, output_name_xlsx=None, output_name_html=None):
        """
        Initializes the ExcelWriter instance.

        Parameters:
            folder (str): The folder to save the files (default is the temporary directory).
            output_name_pdf (str): The name of the output PDF file (default is a UUID-based name).
            output_name_xlsx (str): The name of the output XLSX file (default is a UUID-based name).
            output_name_html (str): The name of the output HTML file (default is a UUID-based name).
        """
        # close_all_excel_instances()
        uuid_name = uuid.uuid4()
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.folder = folder or tempfile.gettempdir()
        self.output_name_pdf = output_name_pdf or f'{uuid_name}.pdf'
        self.output_name_pdf = os.path.join(self.folder, self.output_name_pdf)
        self.output_name_xlsx = output_name_xlsx or f'{uuid_name}.xlsx'
        self.output_name_xlsx = os.path.join(self.folder, self.output_name_xlsx)
        self.output_name_html = output_name_html or f'{uuid_name}.html'
        self.output_name_html = os.path.join(self.folder, self.output_name_html)
        self.repeat_title = []

    def add_break(self, row_num):
        row_break = RowBreak()
        row_break.append(Break(id=row_num))
        self.sheet.row_breaks.append(Break(id=row_num))  # insert page break

    def add_outline(self, line, column):

        # Configurar a linha de divisão na linha 10
        for col in range(1, 21):
            cell = self.sheet.cell(row=line, column=col)
            cell.outlineLevel = 1  # Nível de esboço (outline level)

        # if isinstance(column, list):
        #     self.sheet.merge_cells(f'{column[0]}{line}:{column[1]}{line}')
        #     column = column[0]
        #
        # column_line = f'{column}{line}'
        # sheet_line = self.sheet[column_line]
        # sheet_line.outlineLevel = 1

    def set_center_headers(self, text):
        """
        Sets the text for center-aligned headers.

        Parameters:
            text (str): The text for center-aligned headers.
        """
        self.center_headers = text

    def set_left_headers(self, text):
        """
        Sets the text for left-aligned headers.

        Parameters:
            text (str): The text for left-aligned headers.
        """
        self.left_headers = text

    def set_right_headers(self, text):
        """
        Sets the text for right-aligned headers.

        Parameters:
            text (str): The text for right-aligned headers.
        """
        self.right_headers = text

    def set_img_center_headers(self, img_path):
        """
        Sets the image for center-aligned headers.

        Parameters:
            img_path (str:path): The path image for center-aligned headers.
        """
        self.img_center_headers = img_path

    def set_img_left_headers(self, img_path):
        """
        Sets the image for left-aligned headers.

        Parameters:
            img_path str:pathstr): The path image for left-aligned headers.
        """
        self.left_headers = img_path

    def set_img_right_headers(self, img_path):
        """
        Sets the image for right-aligned headers.

        Parameters:
            img_path str:pathstr): The path image for right-aligned headers.
        """
        self.img_right_headers = img_path

    def set_sheet(self, sheet_name):
        """
        Sets the active sheet in the workbook.

        Parameters:
            sheet_name (str): The name of the sheet.
        """
        try:
            self.sheet = self.workbook[sheet_name]
        except KeyError as e:
            logging.error(e, exc_info=True)
            self.sheet = self.workbook.create_sheet(title=sheet_name)

    def parse_number(self, value):
        try:
            value = "{:,.2f}" \
                .format(value) \
                .replace(".", "|") \
                .replace(",", ".") \
                .replace("|", ",")
        except (ValueError, TypeError) as e:
            logging.debug(e)
        return value

    def set_number(self, line, column, value, force=False, alignment=None, font=None, fill=None, border=None):
        """
        Define um valor numérico formatado em uma célula na planilha.

        Args:
        - sheet_ (Sheet): Planilha onde será definido o valor.
        - line (int): Número da linha da célula.
        - column (str): Nome da coluna.
        - value: Valor numérico a ser definido na célula.
        - force (bool): Indica se a ação deve ser forçada (padrão é False).
        - alignment (str): Alinhamento do texto na célula.
        - font (Font): Fonte a ser aplicada na célula.
        - fill (PatternFill): Preenchimento da célula.

        Returns:
        - Sheet: Planilha com o valor numérico definido na célula.
        """
        value = self.parse_number(value)
        return self.set_value(line, column, value, force=force, alignment=alignment, font=font, fill=fill,
                              border=border)

    def set_repeat_title(self, start_line: int, end_line: int):
        self.repeat_title.append((start_line, end_line))

    def get_fill_width(self, fill_width):
        return fill_width or self.default_fill_width

    def set_value(self, line, column: str or list, value, force=False, alignment=None, font=None, fill=None,
                  border=None, wrap_text=False, fill_width=None):
        """
        Sets the value of a cell in the sheet with optional formatting.

        Parameters:
            line (int): The row number.
            column (str or list): The column letter or a list representing a merged range.
            value: The value to be set in the cell.
            force (bool): If True, forces insertion of a new row before setting the value.
            alignment (str): Horizontal alignment of the cell text.
            font: Font style for the cell text.
            fill: Fill style for the cell background.
            border: Border style for the cell border.

        """
        value = str(value)
        if force:
            merged_cells_range = self.sheet.merged_cells.ranges
            for merged_cell in merged_cells_range:
                if merged_cell.min_row >= line:
                    merged_cell.shift(0, 1)
            self.sheet.insert_rows(line, 1)

        if isinstance(column, list):
            self.sheet.merge_cells(f'{column[0]}{line}:{column[1]}{line}')
            column = column[0]

        column_line = f'{column}{line}'
        sheet_line = self.sheet[column_line]
        fill_width = self.get_fill_width(fill_width)
        fill_value = None
        if fill_width:
            fill_value = textwrap.fill(value, width=fill_width)

        sheet_line.value = value

        if alignment:
            sheet_line.alignment = Alignment(horizontal=alignment, vertical='top')
        if font:
            sheet_line.font = font
        if fill:
            sheet_line.fill = fill
        if border:
            sheet_line.border = border
        if wrap_text or (fill_value and fill_value.count("\n") > 0):
            value_count = (str(value).count("\n") + 1)
            if value.count("\n") == 0 and fill_value:
                sheet_line.value = fill_value
                value_count = (str(fill_value).count("\n") + 1)

            sheet_line.alignment = sheet_line.alignment.copy(wrap_text=True, vertical='top')
            default_line_height = 40
            old_height = self.sheet.row_dimensions[line].height or default_line_height
            required_height = value_count * 30

            self.sheet.row_dimensions[line].height = max(old_height, required_height)

            for coluna in self.sheet.iter_cols(min_col=1, max_col=self.sheet.max_column, min_row=line, max_row=line):
                for cell in coluna:
                    cell.alignment = cell.alignment.copy(wrap_text=True, vertical='top')

            # sheet_line.alignment.wrap_text = True

    def save_as_xlsx(self):
        """
        Saves the workbook as an XLSX file.

        Returns:
            str: The path to the saved XLSX file.
        """
        if not self.saved:
            self.workbook.save(self.output_name_xlsx)
            self.saved = True
        self.workbook.close()  # Fecha o arquivo (libera recursos)
        return self.output_name_xlsx

    def save_as_pdf(self):
        """
        Saves the workbook as a PDF file.

        Returns:
            str: The path to the saved PDF file.
        """
        self.save_as_xlsx()

        converter = ExcelToPDFConverter(self.output_name_xlsx, self.output_name_pdf)

        converter.set_right_header(self.right_headers)
        converter.set_left_header(self.left_headers)
        converter.set_center_header(self.center_headers)
        converter.set_img_center_header(self.img_center_headers)
        converter.set_img_right_header(self.img_right_headers)
        min_value = 1
        max_value = 1
        for repeat in self.repeat_title:
            # Obter o menor valor na posição 0 e o maior valor na posição 1
            min_value = min(min_value, repeat[0])
            max_value = max(min_value, repeat[1])

        converter.set_repeat_title(min_value, max_value)
        converter.convert()

        return self.output_name_pdf

    def save_as_html(self):
        """
        Saves the workbook as an HTML file.

        Returns:
            str: The path to the saved HTML file.
        """
        list_html = []
        self.save_as_xlsx()
        for sheet in self.workbook:
            if sheet.sheet_state == "hidden":
                continue
            out_stream = xlsx2html(self.output_name_xlsx, sheet=sheet.title, parse_formula=False)
            out_stream.seek(0)
            result_html = out_stream.read()
            start_body = result_html.find('<body>') + len('<body>')
            end_body = result_html.find('</body>')
            body_content = result_html[start_body:end_body].strip()

            list_html.append(body_content)

        final_html = '<!DOCTYPE html>\n<html>\n<head>\n<title></title>\n</head>\n<body>\n'
        final_html += '\n'.join(list_html)
        final_html += '\n</body>\n</html>'
        with open(self.output_name_html, 'w', encoding='utf-8') as html_file:
            html_file.write(final_html)
        return self.output_name_html
