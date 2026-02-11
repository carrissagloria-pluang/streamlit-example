import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.set_page_config(page_title="Codex Auto-Filler", layout="wide")

def process_pdf(input_pdf_bytes, data_mapping):
    # Open PDF from bytes
    doc = fitz.open(stream=input_pdf_bytes, filetype="pdf")
    
    for page in doc:
        for label, value in data_mapping.items():
            # Search for the label text in the PDF
            rects = page.search_for(label)
            for rect in rects:
                # Logic for Page 1 Blue Table: The label is in the blue box, 
                # we want to jump to the white box on the right.
                # Standard offset is usually rect.width + some padding.
                if rect.x0 < 200: # Typical for the sidebar labels on Page 1
                    insert_x = rect.x1 + 100 
                else:
                    insert_x = rect.x1 + 10
                
                insert_y = rect.y1 - 2
                page.insert_text((insert_x, insert_y), str(value), fontsize=11, color=(0, 0, 0.6))

    out_pdf = io.BytesIO()
    doc.save(out_pdf)
    doc.close()
    return out_pdf.getvalue()

st.title("🚀 Codex Interactive Form Filler")

# Sidebar Data Entry
st.sidebar.header("Master Data Reference")
c_name = st.sidebar.text_input("Company Name", "Cyberdyne Systems")
c_date = st.sidebar.text_input("Founded Date", "August 29, 1997")
c_addr = st.sidebar.text_input("Headquarters", "123 Tech Way, California")
c_ind  = st.sidebar.text_input("Industry", "Robotics & AI")
c_moto = st.sidebar.text_input("Motto", "The Future is Now")
c_ceo  = st.sidebar.text_input("CEO / Signatory", "Miles Dyson")

# Mapping keys specifically for the Codex Form labels
# Source [cite: 91, 93, 95, 97, 99, 187, 188, 198]
mapping = {
    "Company Name": c_name,
    "Date of Incorporation": c_date,
    "Registered Address/Principal Place": c_addr,
    "Line of Business": c_ind,
    "Company Motto": c_moto,
    "CEO Name:": c_ceo,
    "Industry:": c_ind,
    "Name and Surname:": c_ceo
}

uploaded_file = st.file_uploader("Upload 'Empty Codex - Company Profiling Form.pdf'", type="pdf")

if uploaded_file:
    pdf_bytes = uploaded_file.read()
    filled_pdf = process_pdf(pdf_bytes, mapping)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("Form Processed!")
        st.download_button("📥 Download Filled PDF", filled_pdf, "Filled_Codex.pdf", "application/pdf")
        
    with col2:
        # Preview first page
        preview_doc = fitz.open(stream=filled_pdf, filetype="pdf")
        pix = preview_doc[0].get_pixmap(dpi=100)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        st.image(img, caption="Page 1 Preview")
