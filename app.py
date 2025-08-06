import streamlit as st
from openai import OpenAI
import openai
from fpdf import FPDF
from PIL import Image
import requests
from io import BytesIO

import unicodedata

def remove_non_latin(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')


st.set_page_config(page_title="KDP-Studio", layout="centered")

st.title("🎨 KDP-Studio – Ausmalbuch-Seitengenerator")
st.markdown("Erstelle in Sekunden deine individuelle Ausmalbuchseite für Amazon KDP.")

vehicle = st.text_input("🚗 Fahrzeugtyp", placeholder="z. B. Feuerwehr, Traktor...")
location = st.text_input("📍 Ort", placeholder="z. B. auf dem Bauernhof, in der Stadt...")
style = st.text_input("🎨 Stil / Ton", placeholder="z. B. reimend, witzig, lehrreich...")
age = st.text_input("👶 Zielalter", placeholder="z. B. 3–6 Jahre...")

if st.button("🎨 Seite generieren"):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=openai.api_key)

    # Prompt vorbereiten
    prompt_text = (
        f"Schreibe eine kurze, kindgerechte Geschichte über ein {vehicle} {location}, "
        f"im Stil: {style}. Zielgruppe: Kinder im Alter von {age} Jahren. "
        "Die Geschichte soll einfach verständlich, fantasievoll und pädagogisch wertvoll sein."
    )

    with st.spinner("✍️ Schreibe Geschichte..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Du bist ein erfahrener Kinderbuchautor."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.8
        )
        story = response.choices[0].message.content.strip()

    with st.spinner("🖼️ Generiere Ausmalbild..."):
        dalle_prompt = f"Ein {vehicle} {location} als Ausmalbild, einfache schwarze Linien, kindgerecht, zentriert"
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = image_response.data[0].url
        image = Image.open(BytesIO(requests.get(image_url).content))

    # PDF erzeugen
    with st.spinner("📄 Erstelle PDF..."):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 10, f"{vehicle} {location}", ln=True, align='C')
        
        # Bild
        image_path = "/tmp/image.png"
        image.save(image_path)
        pdf.image(image_path, x=30, y=30, w=150)

        # Text
        pdf.set_y(180)
        pdf.set_font("Arial", size=12)
clean_story = remove_non_latin(story)
for line in clean_story.split("\n"):
    pdf.multi_cell(0, 10, line)


        pdf_path = "/tmp/kdp_page.pdf"
        pdf.output(pdf_path)

    # Ausgabe
    st.success("✅ Seite erstellt!")
    st.image(image, caption="🖼️ Dein Ausmalbild")
    st.markdown("📘 **Kindergeschichte:**")
    st.write(story)
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ PDF herunterladen", f, file_name="kdp_ausmalbuchseite.pdf")

