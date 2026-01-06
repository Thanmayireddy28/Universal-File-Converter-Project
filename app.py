import streamlit as st
from markitdown import MarkItDown
import os
import io

# --- Configuration ---
st.set_page_config(page_title="Universal Document Reader", page_icon="📄", layout="wide")

# Initialize the MarkItDown Engine
# Note: MarkItDown handles Word, Excel, PPT, PDF, and HTML natively.
md_engine = MarkItDown()

def convert_file(uploaded_file):
    """
    Processes the uploaded file using MarkItDown and returns the text content.
    """
    try:
        # We need to save the uploaded file to a temporary location 
        # because MarkItDown often expects a file path to detect extensions correctly
        temp_filename = f"temp_{uploaded_file.name}"
        with open(temp_filename, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Convert the file
        result = md_engine.convert(temp_filename)
        
        # Cleanup temp file
        os.remove(temp_filename)
        
        return result.text_content
    except Exception as e:
        # Graceful error handling for corrupted files or unsupported formats
        st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")
        return None

# --- UI Header ---
st.title("📄 Universal Document Reader")
st.markdown("""
    Upload MS Office files, PDFs, or HTML documents to instantly convert them into clean Markdown text.
    *Supports: .docx, .xlsx, .pptx, .pdf, .html*
""")

# --- [2] Upload Area ---
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=["docx", "xlsx", "pptx", "pdf", "html"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
            content = convert_file(uploaded_file)
            
            if content:
                status.update(label=f"✅ {uploaded_file.name} Processed!", state="complete")
                
                # --- [2] Instant Preview ---
                with st.expander(f"Preview: {uploaded_file.name}", expanded=True):
                    st.text_area(
                        label="Converted Content",
                        value=content,
                        height=300,
                        key=f"preview_{uploaded_file.name}"
                    )
                
                # --- [2] & [4] Download Options ---
                col1, col2 = st.columns(2)
                
                # Logic to keep original filename and append suffix
                base_name = os.path.splitext(uploaded_file.name)[0]
                
                with col1:
                    st.download_button(
                        label=f"⬇️ Download as .md",
                        data=content,
                        file_name=f"{base_name}_converted.md",
                        mime="text/markdown",
                        key=f"md_{uploaded_file.name}"
                    )
                
                with col2:
                    st.download_button(
                        label=f"⬇️ Download as .txt",
                        data=content,
                        file_name=f"{base_name}_converted.txt",
                        mime="text/plain",
                        key=f"txt_{uploaded_file.name}"
                    )
            st.divider()

# --- Footer ---
st.caption("Powered by Microsoft MarkItDown & Streamlit")
