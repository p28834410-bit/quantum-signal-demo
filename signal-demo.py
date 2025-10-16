import streamlit as st
import pandas as pd
import numpy as np
import io
import zipfile
import json
from datetime import datetime

# ===== DEMO PROTECTION =====
DEMO_MODE = True
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB limit
MAX_ROWS = 500  # Small limit for demo
WATERMARK_TEXT = "QuantumSignal Demo | Not for Production | {}"

# ===== AUTHENTICATION =====
def check_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔒 Quantum Signal Processor - Investor Demo")
        st.markdown("**Secure Demo Access**")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Enter access code:", type="password")
            if st.button("Access Demo"):
                # Change this password per investor
                if password == "Demo2025":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid access code")
        with col2:
            st.info("""
            **Demo Features:**
            - Basic signal enhancement
            - Limited processing (500 rows)
            - Watermarked outputs
            - Real-time preview
            """)
        st.stop()
    
    return True

# ===== BASIC PROCESSING (NO SECRETS) =====
def basic_bandpass_filter(signal, lowcut=1.0, highcut=40.0, fs=256):
    """Basic filter - no quantum/ML secrets"""
    from scipy.signal import butter, filtfilt
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(4, [low, high], btype="band")
    return filtfilt(b, a, signal)

def demo_enhance_signals(df, boost_factor=1.5, lowcut=1.0, highcut=40.0):
    """Demo version - limited capabilities"""
    df_enhanced = df.copy()
    
    # Apply basic processing to signal columns
    signal_cols = [col for col in df.columns if col.lower() != "time"]
    
    for col in signal_cols:
        try:
            signal = df[col].values
            
            # DEMO LIMIT
            if len(signal) > MAX_ROWS:
                signal = signal[:MAX_ROWS]
            
            # BASIC processing only
            filtered = basic_bandpass_filter(signal, lowcut, highcut)
            boosted = filtered * boost_factor
            
            # Add some demo noise (not real algorithm)
            demo_noise = np.random.normal(0, 0.03 * np.std(boosted), len(boosted))
            df_enhanced[col] = boosted + demo_noise
            
        except Exception as e:
            st.error(f"Demo processing error for {col}")
            df_enhanced[col] = df[col]
    
    return df_enhanced

# ===== WATERMARKING =====
def add_watermark(df, investor="DemoUser"):
    """Add visible watermark to all data"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    watermark = WATERMARK_TEXT.format(timestamp)
    
    # Add watermark as first column
    df.insert(0, 'DEMO_WATERMARK', watermark)
    return df, watermark

# ===== MAIN DEMO APP =====
def main():
    # Check authentication
    if not check_auth():
        return
    
    st.title("🧠 Quantum Signal Processor - Secure Demo")
    st.warning("⚠️ **DEMO MODE**: Limited processing | Watermarked outputs | Not for production")
    
    # Demo limits display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Max File Size", "2MB")
    with col2:
        st.metric("Max Rows", "500")
    with col3:
        st.metric("Output", "Watermarked")
    
    # File upload with strict limits
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    
    if uploaded_file:
        # Size check
        if uploaded_file.size > MAX_FILE_SIZE:
            st.error(f"File too large for demo. Max: {MAX_FILE_SIZE/1024/1024}MB")
            return
        
        try:
            df = pd.read_csv(uploaded_file)
            
            # Row limit
            if len(df) > MAX_ROWS:
                df = df.head(MAX_ROWS)
                st.warning(f"Demo limited to first {MAX_ROWS} rows")
            
            # Demo processing parameters
            st.subheader("Demo Processing Settings")
            col1, col2, col3 = st.columns(3)
            with col1:
                boost = st.slider("Boost", 1.0, 2.0, 1.5)
            with col2:
                lowcut = st.slider("Low Cut (Hz)", 1.0, 20.0, 1.0)
            with col3:
                highcut = st.slider("High Cut (Hz)", 10.0, 50.0, 40.0)
            
            if st.button("🚀 Process in Demo Mode"):
                with st.spinner("Demo processing..."):
                    # Use basic demo processing
                    enhanced_df = demo_enhance_signals(df, boost, lowcut, highcut)
                    
                    # Add watermark
                    enhanced_df, watermark = add_watermark(enhanced_df)
                    
                    # Show results
                    st.success("Demo processing complete!")
                    st.info(f"**Watermark:** {watermark}")
                    
                    # Display comparison
                    st.subheader("Results Preview")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Original Data (first 5 rows)**")
                        st.dataframe(df.head())
                    with col2:
                        st.write("**Enhanced Data (first 5 rows)**")
                        st.dataframe(enhanced_df.head())
                    
                    # Download watermarked data
                    st.subheader("Download Watermarked Results")
                    csv = enhanced_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Demo CSV (Watermarked)",
                        data=csv,
                        file_name=f"demo_signal_enhancement_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        help="Contains demo watermark - not for production use"
                    )
                    
        except Exception as e:
            st.error(f"Demo error: {str(e)}")
    
    # Demo info
    with st.expander("About This Demo"):
        st.markdown("""
        **This is a limited demo showing:**
        - Basic signal enhancement capabilities
        - User interface and workflow
        - Real-time processing preview
        
        **Full version includes:**
        - Quantum-inspired processing algorithms
        - ML-powered noise prediction
        - Advanced signal analytics
        - Batch processing for large datasets
        - Production-ready performance
        
        **Contact for full version access.**
        """)

if __name__ == "__main__":
    main()

