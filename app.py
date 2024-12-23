from flask import Flask, request, render_template, send_file
from fpdf import FPDF
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}

# Define layout themes
LAYOUT_THEMES = {
    "theme1": {
        "ticket": {"x": 10, "y": 20, "w": 90, "h": 150},  # Mobile phone screenshot
        "card": {"x": 110, "y": 20, "w": 80, "h": 60},   # ECHS card at top right
        "message": {"x": 110, "y": 100, "font_size": 12} # Custom message at bottom right
    },
    "theme2": {
        "ticket": {"x": 0, "y": 20, "w": 210, "h": 105},  # Laptop screenshot on top
        "card": {"x": 10, "y": 135, "w": 90, "h": 60},   # ECHS card at bottom left
        "message": {"x": 110, "y": 135, "font_size": 12} # Custom message at bottom right
    },
    # Add more themes as needed
}

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle PDF generation
@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        # Retrieve files and form data
        ticket_file = request.files['ticket']
        card_file = request.files['card']
        custom_message = request.form['message']
        selected_theme = request.form['theme']

        # Validate theme
        if selected_theme not in LAYOUT_THEMES:
            raise ValueError("Invalid theme selected.")

        # Get layout settings for the selected theme
        layout = LAYOUT_THEMES[selected_theme]

        # Validate and save uploaded images
        ticket_path = save_file(ticket_file, 'ticket')
        card_path = save_file(card_file, 'card')

        # Generate PDF
        pdf_path = create_pdf(
            ticket_path,
            card_path,
            custom_message,
            layout["ticket"],
            layout["card"],
            layout["message"]
        )

        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return str(e)

# Function to validate and save uploaded files
def save_file(file, name):
    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        ext = file.filename.rsplit('.', 1)[1].lower()
        save_path = os.path.join(UPLOAD_FOLDER, f"{name}.{ext}")
        file.save(save_path)
        return save_path
    else:
        raise ValueError("Unsupported file format. Allowed formats are: " + ', '.join(ALLOWED_EXTENSIONS))

# Function to create PDF
def create_pdf(ticket_path, card_path, message, ticket_layout, card_layout, message_layout):
    pdf = FPDF()
    pdf.add_page()

    # Add Ticket Image
    pdf.image(ticket_path, x=ticket_layout["x"], y=ticket_layout["y"],
              w=ticket_layout["w"], h=ticket_layout["h"])

    # Add ECHS Card Image
    pdf.image(card_path, x=card_layout["x"], y=card_layout["y"],
              w=card_layout["w"], h=card_layout["h"])

    # Add Custom Message
    pdf.set_xy(message_layout["x"], message_layout["y"])
    pdf.set_font('Arial', '', message_layout["font_size"])
    pdf.multi_cell(0, 10, message)

    # Save PDF
    pdf_path = os.path.join(UPLOAD_FOLDER, 'final_ticket.pdf')
    pdf.output(pdf_path)
    return pdf_path

if __name__ == '__main__':
    app.run(debug=True)
