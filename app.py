import streamlit as st
from markitdown import MarkItDown
import os
import tempfile
import pandas as pd

# --- Configuration ---
st.set_page_config(page_title="Universal Document Reader", page_icon="📄", layout="wide")

# Initialize the MarkItDown Engine
md_engine = MarkItDown()

def get_file_size_mb(file_bytes):
    """Returns size in MB."""
    return len(file_bytes) / (1024 * 1024)

def convert_file(uploaded_file):
    """Processes file and returns content and sizes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a path with the ORIGINAL extension so MarkItDown knows how to parse it
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        file_bytes = uploaded_file.getvalue()
        orig_size = get_file_size_mb(file_bytes)
        
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        try:
            # MarkItDown processes the file into Markdown content
            result = md_engine.convert(file_path)
            conv_content = result.text_content
            
            # Calculate sizes for different formats
            # Markdown size
            md_size = len(conv_content.encode('utf-8')) / (1024 * 1024)
            # Plain text size (often similar to MD but calculated separately for accuracy)
            txt_size = len(conv_content.encode('utf-8')) / (1024 * 1024)
            
            return conv_content, orig_size, md_size, txt_size
        except Exception as e:
            st.error(f"⚠️ Could not read {uploaded_file.name}. (Error: {str(e)})")
            return None, None, None, None

# --- UI Header ---
st.title("📄 Universal Document Reader")
st.markdown("Convert Office docs, PDFs, and HTML into lightweight Markdown.")

# --- [2] Upload Area ---
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=["docx", "xlsx", "pptx", "pdf", "html"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
            content, orig_s, md_s, txt_s = convert_file(uploaded_file)
            
            if content:
                status.update(label=f"✅ {uploaded_file.name} Processed!", state="complete")
                
                # Tabs for Content and Analytics
                tab1, tab2 = st.tabs(["📝 Content Preview", "📊 File Size Comparison"])
                
                with tab1:
                    st.text_area("Markdown Output", content, height=300, key=f"txt_area_{uploaded_file.name}")
                    
                    # [4] Download Logic (using original filename)
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    c1, c2 = st.columns(2)
                    c1.download_button("⬇️ Download .md", content, f"{base_name}_converted.md", "text/markdown")
                    c2.download_button("⬇️ Download .txt", content, f"{base_name}_converted.txt", "text/plain")

                with tab2:
                    st.subheader("Size Analysis")
                    
                    # Calculate percentage reduction
                    reduction_pct = ((orig_s - txt_s) / orig_s) * 100
                    
                    # Create the comparison table
                    comparison_data = {
                        "File Version": ["Original File", "Converted Markdown (.md)", "Converted Plain Text (.txt)"],
                        "Size (MB)": [
                            f"{orig_s:.2f} MB", 
                            f"{md_s:.4f} MB", 
                            f"{txt_s:.4f} MB"
                        ]
                    }
                    df = pd.DataFrame(comparison_data)
                    st.table(df)
                    
                    # Highlighting the savings
                    st.success(f"✨ **Result:** The text version is **{reduction_pct:.1f}% smaller** than the original file.")

            st.divider()

# --- Footer ---
st.caption("Universal File-to-Text Converter | Built with Microsoft MarkItDown")
