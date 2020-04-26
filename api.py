import os
import sys
import datetime as dt
import subprocess
import shutil
import pandas as pd
from flask import Flask, render_template, flash, request, redirect, url_for, \
                  send_from_directory, send_file
from werkzeug.utils import secure_filename
from settings import app, ALLOWED_EXTENSIONS, OUTPUT_FOLDER, APP_LOG, CACHE_LOG
from execute import run

log = app.logger
app_log_ptr = open (APP_LOG, 'r')
app_log_ptr.readlines()

def reset_logs():
    log.info("Resetting APP log to recent entries")
    app_log_ptr.readlines()
    log.info("Resetting Cache")
    cache_log = open(CACHE_LOG, 'w')
    cache_log.close()

def get_cache():
    cache_log = open(CACHE_LOG, 'r')
    runtime_log = cache_log.readlines()
    cache_log.close()
    return runtime_log

def allowed_file(filename):
    log.info(f"Verifying Extension for file {filename}")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    log.info("homepage clicked")
    return render_template('main.html')

@app.route('/execute', methods=['GET','POST'])
def execute():
    log.info("Audit-1 Clicked")
    if request.method == 'GET':
        return render_template('execute.html', progress="-")
    elif request.method == 'POST':
        log.info(f"Audit-1 Invoked with files")
        reset_logs()
        files = {}
        for key in request.files:
            file = request.files[key]
            log.info(f"{file.filename}")
            if file and allowed_file(file.filename):
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
                files[file.filename] = os.path.join(app.config['UPLOAD_FOLDER'] + '\\' + file.filename)
                log.info(f'file : {file.filename} saved to {app.config["UPLOAD_FOLDER"]}')
            else:
                flash(f'Allowed file type : {ALLOWED_EXTENSIONS}')
                return redirect(request.url)
        if len(files) == 2:
            filenames = list(files.keys())
            log.info(f'Auditing files : {filenames[0]} & {filenames[1]}')
            output_file = run(files[filenames[0]], files[filenames[1]])
            runtime_log = get_cache()
            return render_template('audit.html', file_name=output_file['file_name'],\
                                    path=output_file['path'], progress="Done!!",\
                                    runtime_log=runtime_log)
        else:
            flash('Same file names')
            return redirect(request.url)

@app.route('/downloads', methods=['GET'])
def downloads():
    output_files = {}
    for dir in os.listdir(OUTPUT_FOLDER):
        for file in os.listdir(os.path.join(OUTPUT_FOLDER, dir)):
            if dir in output_files:
                output_files[dir].append([file,os.path.join(OUTPUT_FOLDER, dir)])
            else:
                output_files[dir] = [[file,os.path.join(OUTPUT_FOLDER, dir)]]
    return render_template('downloads.html', output=output_files)

@app.route('/download', methods=['GET','POST'])
def download():
    path = request.args.get('path')
    file_name = request.args.get('file_name')
    return send_from_directory(path, file_name, as_attachment=True)

@app.route('/delete')
def delete():
    path = request.args.get('path')
    file_name = request.args.get('file_name')
    os.remove(os.path.join(path, file_name))
    return redirect(request.referrer)

@app.route('/stream')
def stream():
    def generate():
        while True:
            cache = open(CACHE_LOG, 'a+')
            line = app_log_ptr.read()            
            cache.write(line)
            cache.close()
            yield line
    return app.response_class(generate(), mimetype='text/plain')

if __name__ == "__main__":
    app.run()
