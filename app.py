import streamlit as st
import openai
from openai import OpenAI
from fpdf import FPDF
from PIL import Image
import requests
from io import BytesIO
import os

# Streamlit App
st.set_page_config(page_title="KDP-Studio", layout="centered")
st.title("🚗 KDP-Studio – Ausmalbuch-Seitengenerator")

# Eingabefelder
fahrzeug = st.text_input("🚙 Fahrzeug", "Traktor")
ort = st.text_input("🌍 Ort", "auf dem Feld")
stil = st.text_input("🎨 Stil", "reimend, kindgerecht")
alter = st.text_input("👧 Altersempfehlung", "4–6 Jahre")
if st.button("🎨 Seite generieren"):
    openai.api_key = st.secrets["OPENAI_API_KEY"]



    # Prompt für GPT-4o
    prompt_text = (
        f"Schreibe eine kurze Kindergeschichte (ca. 300–400 Wörter) "
        f"für Kinder im Alter von {alter}. Die Hauptfigur ist ein Fahrzeug: {fahrzeug}. "
        f"Die Geschichte spielt {ort} und soll {stil} geschrieben sein. "
        f"Bitte mit Titel. Kindgerecht, einfach, liebevoll."
    )

from openai import OpenAI

client = OpenAI(api_key=openai.api_key)

with st.spinner("✍️ Schreibe Geschichte..."):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Du bist ein Kinderbuchautor."},
            {"role": "user", "content": prompt_text}
        ],
        temperature=0.8
    )
    story = response.choices[0].message.content


    # Prompt für DALL·E
    dalle_prompt = (
        f"A black and white cartoon-style coloring page of a {fahrzeug} {ort}, "
        f"with clear outlines, no background clutter, no text, no color. Kid-friendly."
    )

    with st.spinner("🖼️ Erzeuge Ausmalbild..."):
        image_response = openai.Image.create(
            prompt=dalle_prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )
        image_url = image_response["data"][0]["url"]
        image = Image.open(BytesIO(requests.get(image_url).content))
        st.image(image, caption="Dein Ausmalbild", use_column_width=True)

    # PDF-Erstellung
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.multi_cell(0, 10, story)
    
    # Bild zwischenspeichern
    image_path = "temp_image.png"
    image.save(image_path)

    # Bild in PDF einfügen
    pdf.image(image_path, x=30, y=None, w=150)
    pdf.output("kdp_page.pdf")
    os.remove(image_path)

    with open("kdp_page.pdf", "rb") as f:
        st.download_button(
            label="📄 PDF herunterladen",
            data=f,
            file_name="kdp_ausmalseite.pdf",
            mime="application/pdf"
        )
