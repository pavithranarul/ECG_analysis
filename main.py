from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import google.generativeai as genai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change this to a secure key in production
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config['WTF_CSRF_ENABLED'] = True  # Enable CSRF protection

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure Gemini API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Set up model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# Define Flask-WTF Form
class UploadForm(FlaskForm):
    file = FileField("Upload ECG Image", validators=[InputRequired()])
    submit = SubmitField("Analyze")

# Route for file upload and ECG analysis
@app.route("/", methods=["GET", "POST"])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save the uploaded file

        # Send the image for analysis (assuming Gemini supports image input)
        response = model.generate_content(["Analyze this ECG image.", file_path])
        
        return render_template("result.html", response=response.text, file_path=file_path)

    return render_template("upload.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)
