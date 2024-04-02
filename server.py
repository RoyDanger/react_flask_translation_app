from flask import Flask,request
import openpyxl
from io import BytesIO
import base64
from flask import send_file
from pptx import Presentation
from docx import Document
from googletrans import Translator as trans
import time
from functools import lru_cache
from threading import Thread
stop_processing = False

app = Flask(__name__)
translator = trans()


@lru_cache(maxsize=None)  # Use caching to store translated results
def translate_text(translator, text, language, languageFrom):
    translated_text = translator.translate(text, src=languageFrom, dest=language).text
    return translated_text

def translate_ppt_slide(translator, slide, language, languageFrom,stop_processing):
    for shape in slide.shapes:
        if shape.has_table and stop_processing == False:
            for row in shape.table.rows:
                if stop_processing == False:
                    for cell in row.cells:
                        if stop_processing == False:
                            for paragraph in cell.text_frame.paragraphs:
                                for run in paragraph.runs:
                                    try:
                                        if run.text:
                                            if stop_processing == False:
                                                run.text = translate_text(translator, run.text, language, languageFrom)
                                    except Exception as e:
                                        print(f"Error translating text: {e}")

        if shape.has_text_frame and stop_processing == False:
            for paragraph in shape.text_frame.paragraphs:
                if stop_processing == False:
                    for run in paragraph.runs:
                        try:
                            run.text = translate_text(translator, run.text, language, languageFrom)
                        except Exception as e:
                            print(f"Error translating text: {e}")

def translate_ppts(result, translator, language, languageFrom,stop_processing):
    try:
        for slide in result.slides:
            translate_ppt_slide(translator, slide, language, languageFrom,stop_processing)

    except Exception as e:
        print(f"Error: {e}")
        return {'error': str(e)}, 500

            
@app.route('/convert',methods=['POST'])
def convert():
    file = request.files['file']
    language = request.form.get('languageTo', 'en')
    languageFrom = request.form.get('languageFrom','en')
    fileName = request.form.get("fileExtension",'en')
    translated_content = BytesIO()
    initial_time = time.time()
    mimetype = ''
    
    if file:
        if language == "":
            language = "en"
            
        file_content_base64 = request.form.get('fileContent')
        decoded_content = base64.b64decode(file_content_base64)

        fileExtension = fileName.split(".")[-1]
        if fileExtension == "xlsx":
            result = openpyxl.load_workbook(BytesIO(decoded_content))
            for sheet_name in result.sheetnames:
                sheet = result[sheet_name]
                if stop_processing == False:
                    for row in sheet.iter_rows():
                        if stop_processing == False:
                            for cell in row:
                                try:
                                    if cell.value is not None and stop_processing == False:
                                        translated_text = translator.translate(str(cell.value), src=languageFrom, dest=language).text
                                        cell.value = translated_text
                                except:
                                    continue
                        
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif fileExtension == "pptx":
            result = Presentation(BytesIO(decoded_content))      
            try:
                translate_ppts(result, translator, language, languageFrom,stop_processing)            
                mimetype='application/octet-stream'
                
            except Exception as e:
                return {'error': str(e)}, 500
            
        elif fileExtension == "docx":
            try:
                result = Document(BytesIO(decoded_content))
                for section in result.sections:
                    header = section.header
                    footer = section.footer
                    if header is not None and stop_processing == False:
                        for paragraph in header.paragraphs:
                            if stop_processing == False:
                                for run in paragraph.runs:
                                    try:
                                        run.text = translate_text(translator, run.text,language,languageFrom)
                                    except:
                                        continue

                    if footer is not None and stop_processing == False: 
                        for paragraph in footer.paragraphs:
                                for run in paragraph.runs:
                                    try:
                                        if stop_processing == False:
                                            run.text = translate_text(translator, run.text,language,languageFrom)
                                    except:
                                        continue
                # convert paragraph data               
                if result.paragraphs is not None and stop_processing == False:
                    for paragraph in result.paragraphs:
                            if paragraph.runs and stop_processing == False:
                                for run in paragraph.runs:
                                    try:
                                        if run.text is not None and stop_processing == False:
                                            run.text = translate_text(translator, run.text,language,languageFrom)
                                    except:
                                        continue
                                    
                # convert table data
                if result.tables is not None and stop_processing == False:
                    for table in result.tables:
                        for row in table.rows:
                            if stop_processing == False:
                                for cell in row.cells:
                                    for paragraph in cell.paragraphs:
                                        if stop_processing == False:
                                            for run in paragraph.runs:
                                                try:
                                                    if run.text:
                                                        run.text = translator.translate(run.text, src=languageFrom, dest=language).text
                                                except:
                                                    continue
                                        
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                                            
            except Exception as e:
                print("error12::"+str(e))     
                return {'error': str(e)}, 500   
            
        result.save(translated_content)
        translated_content.seek(0)
        print("file name:",fileName,", conversion time:",round(time.time()-initial_time),2)

    return send_file(
        translated_content,
        mimetype=mimetype,
        as_attachment=True,
        download_name=fileName
    )
    
@app.route('/stop_processing', methods=['POST'])
def stop_processing_endpoint():
    global stop_processing  # Use the global flag
    stop_processing = True
    return {'message': 'Processing stopped'}, 200


if __name__ == "__main__":
    app.run(debug=True)