from flask import Flask, render_template, request, send_file
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
import os
from io import BytesIO
from reportlab.pdfgen import canvas

app = Flask(__name__)

# =========================
# FIX NLTK FOR RENDER
# =========================
def setup_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

setup_nltk()


# =========================
# SUMMARIZER FUNCTION
# =========================
def summarize_text(text, sentences_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()

    summary = summarizer(parser.document, sentences_count)

    result = ""
    for sentence in summary:
        result += str(sentence) + " "

    return result.strip()


# =========================
# HOME ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    summary = ""

    if request.method == "POST":
        text = request.form.get("text")

        if text:
            summary = summarize_text(text)

    return render_template("index.html", summary=summary)


# =========================
# DOWNLOAD PDF
# =========================
@app.route("/download", methods=["POST"])
def download():
    text = request.form.get("summary")

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(50, 800, "Summarized Notes:")

    y = 780
    for line in text.split("."):
        if y < 50:
            p.showPage()
            y = 800
        p.drawString(50, y, line.strip())
        y -= 20

    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="summary.pdf", mimetype="application/pdf")


# =========================
# RUN APP (RENDER SAFE)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)