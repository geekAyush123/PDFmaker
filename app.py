from flask import Flask, request, render_template, send_file
from fpdf import FPDF
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle PDF generation
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Retrieve files and text
        ticket_file = request.files['ticket']
        card_file = request.files['card']
        custom_message = request.form['message']

        # Save uploaded images
        ticket_path = os.path.join(UPLOAD_FOLDER, 'ticket.jpg')
        card_path = os.path.join(UPLOAD_FOLDER, 'card.jpg')
        ticket_file.save(ticket_path)
        card_file.save(card_path)

        # Generate PDF
        pdf_path = create_pdf(ticket_path, card_path, custom_message)

        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return str(e)

# Function to create PDF
def create_pdf(ticket_path, card_path, message):
    pdf = FPDF()
    pdf.add_page()

    # Add Ticket Image
    pdf.image(ticket_path, x=10, y=20, w=90, h=60)

    # Add ECHS Card Image
    pdf.image(card_path, x=110, y=20, w=90, h=60)

    # Add Custom Message
    pdf.set_xy(10, 100)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, message)

    # Save PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, 'final_ticket.pdf')
    pdf.output(pdf_path)
    return pdf_path

if __name__ == '__main__':
    app.run(debug=True)
