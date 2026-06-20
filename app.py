from flask import Flask, render_template, request, send_file
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)

# Store latest summary
latest_summary = ""


@app.route("/", methods=["GET", "POST"])
def home():
    global latest_summary

    summary = ""

    if request.method == "POST":
        text = request.form.get("text", "")
        pdf = request.files.get("pdf")

        # Read uploaded PDF
        if pdf and pdf.filename != "":
            reader = PdfReader(pdf)
            text = ""

            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"

        # Generate summary
        if text.strip():
            parser = PlaintextParser.from_string(
                text,
                Tokenizer("english")
            )

            summarizer = LsaSummarizer()

            summary = " ".join(
                str(sentence)
                for sentence in summarizer(parser.document, 3)
            )

            latest_summary = summary

    return render_template(
        "index.html",
        summary=summary
    )


@app.route("/download")
def download():
    global latest_summary

    if latest_summary == "":
        return "No summary available."

    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer)
    pdf.setTitle("Summary")

    y = 800

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, y, "Notes Summary")

    y -= 40

    pdf.setFont("Helvetica", 12)

    lines = latest_summary.split(". ")

    for line in lines:
        if y < 50:
            pdf.showPage()
            pdf.setFont("Helvetica", 12)
            y = 800

        pdf.drawString(50, y, line.strip())
        y -= 20

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Summary.pdf",
        mimetype="application/pdf"
    )


if __name__ == "__main__":
    app.run(debug=True)