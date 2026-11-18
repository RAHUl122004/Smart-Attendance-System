import streamlit as st
import segno
import io

@st.dialog("Share Subject")
def share_subject_dialog(subject_name, subject_code):
    st.subheader(subject_name)
    st.write("Share this code or QR code with students to let them auto-enroll:")
    
    st.code(subject_code, language="text")
    
    join_url = f"?join-code={subject_code}"
    qr = segno.make_qr(join_url)
    buf = io.BytesIO()
    qr.save(buf, kind='png', scale=8)
    
    st.image(buf.getvalue(), caption=f"Scan to join {subject_name}", use_container_width=True)
    st.info(f"Students can enter code **{subject_code}** or scan the QR code above.")