import streamlit as st
import requests
from xml_utils import sign_xml
from datetime import datetime, timezone

st.set_page_config(page_title="Secure XML Sender", layout="centered", page_icon="🔒")

st.markdown(
    """
    <h1 style='text-align: center; color: #4F8BF9;'>🔒 Secure XML Sender</h1>
    <p style='text-align: center; color: #666;'>Send sensitive XML documents securely with digital signatures.</p>
    <hr>
    """,
    unsafe_allow_html=True,
)

with st.form("xml_form"):
    col1, col2 = st.columns(2)
    with col1:
        sender_id = st.text_input("👤 Sender ID", "MINISTRY 1_SEG01")
    with col2:
        receiver_id = st.text_input("🏢 Receiver ID", "MINISTRY 2_SEG01")
    sensitive_data = st.text_area("🔑 Sensitive Data", "Lunch party at Saturday", height=100)
    instructions = st.text_area("📋 Instructions", "Deliver by 0300.", height=80)
    submitted = st.form_submit_button("🚀 Generate & Send XML")

if submitted:
    timestamp = datetime.now(timezone.utc).isoformat() + "Z"
    xml = f"""<CriticalDocument id="doc123">
  <SenderID>{sender_id}</SenderID>
  <ReceiverID>{receiver_id}</ReceiverID>
  <TimestampForSignature>{timestamp}</TimestampForSignature>
  <Payload>
    <SensitiveData>{sensitive_data}</SensitiveData>
    <Instructions>{instructions}</Instructions>
  </Payload>
</CriticalDocument>"""

    with st.expander("📄 Show Generated XML"):
        st.code(xml, language="xml")

    try:
        signature = sign_xml(xml, 'certs/sender.key')
        signature_hex = signature.hex()
        st.success("🔐 XML signed successfully!")

        url = "https://localhost:5001/receive"
        response = requests.post(
            url,
            json={"xml": xml, "signature": signature_hex},
            cert=('certs/sender.crt', 'certs/sender.key'),
            verify='certs/rootCA.pem'
        )
        st.info("📡 Sent to receiver endpoint.")
        st.markdown(f"**Response status code:** `{response.status_code}`")
        with st.expander("📬 Show Response"):
            try:
                st.json(response.json())
            except Exception:
                st.write(response.text)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("📝 Fill the form and click **Generate & Send XML** to sign and send your document securely.")

st.markdown(
    """
    <hr>
    <div style='text-align: center; color: #aaa; font-size: 0.9em;'>
        Made with ❤️ using Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
