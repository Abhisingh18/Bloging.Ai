import streamlit as st
import google.generativeai as genai
import openai
from apikey import google_gemini_api_key, openai_api_key
from PIL import Image
import requests
from io import BytesIO
import time

# Configure the Gemini API with your API key
genai.configure(api_key=google_gemini_api_key)

# Configure the OpenAI API with your API key
openai.api_key = openai_api_key

# Define generation configuration settings for Gemini
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# Define safety settings to filter out harmful content
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the GenerativeModel with the specified settings
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Set the Streamlit app layout to wide mode
st.set_page_config(layout="wide")

# Adding emojis to the title
st.title("✍️🤖 BlogCraft: Your AI Writing Companion")

# Adding emojis to the subheader
st.subheader("Now you can craft perfect blogs with the help of AI—BlogCraft is your new AI Blog Companion. 📝✨")

# Sidebar for user inputs
with st.sidebar:
    st.title("Input Your Blog Details")
    st.subheader("Enter Details of the Blog you want to generate")

    # Blog title input
    blog_title = st.text_input("Blog Title")

    # Keywords input
    keywords = st.text_area("Keywords (comma-separated)")

    # Number of words slider
    num_words = st.slider("Number of words", min_value=250, max_value=2500, step=250)

    # Number of images input
    num_images = st.number_input("Number of Images", min_value=0, max_value=10, step=1)

    # Generate Blog button
    submit_button = st.button("Generate Blog")

# Function to generate images with retry mechanism
def generate_image_with_retry(prompt, max_retries=3, delay=5):
    for attempt in range(max_retries):
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024",
            )
            return response['data'][0]['url']
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                st.error(f"An error occurred while generating the image: {e}")
                return None

# When the user clicks the "Generate Blog" button
if submit_button:
    # Ensure that the blog title and keywords are provided
    if not blog_title:
        st.error("Please enter a blog title.")
    elif not keywords:
        st.error("Please enter at least one keyword.")
    else:
        # Create the prompt for the Gemini model
        prompt = (
            f"Generate a comprehensive, engaging blog post relevant to the given title \"{blog_title}\" "
            f"and keywords \"{keywords}\". Make sure to incorporate these keywords in the blog post. "
            f"The blog should be approximately {num_words} words in length, suitable for an online audience. "
            f"Ensure the content is original, informative, and maintains a consistent tone throughout."
        )

        # Generate the content using the Gemini model
        response = model.generate_content(prompt)

        # Display the generated blog content
        st.title("Your Blog Post:")
        st.write(response.text)

        # Generate images using OpenAI's DALL·E 3 model
        for i in range(num_images):
            image_prompt = f"{blog_title} - {keywords} - Image {i+1}"
            image_url = generate_image_with_retry(image_prompt)
            if image_url:
                response = requests.get(image_url)
                image = Image.open(BytesIO(response.content))
                st.image(image, caption=f"Generated Image {i+1}")
