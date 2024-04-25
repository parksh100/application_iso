import streamlit as st
import mysql.connector
import os
import time
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

def connect_db():
    load_dotenv()
    host=os.getenv('DB_HOST')
    user=os.getenv('DB_USER')
    password=os.getenv('DB_PASSWORD')
    database=os.getenv('DB_NAME')
    
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )


def get_applications(quote_id):
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM sh WHERE quote_id= %s', (quote_id,))
        applications = cursor.fetchall()
        cursor.close()
        conn.close()
        return applications
    except Exception as e:
        st.error(f'데이터베이스 조회 중 오류가 발생했습니다: {e}')


def insert_application(company_name, company_address, company_tel, company_email, company_ceo, company_employee, company_product, company_process, company_standard, company_certificate, company_date):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO application (company_name, company_address, company_tel, company_email, company_ceo, company_employee, company_product, company_process, company_standard, company_certificate, company_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (company_name, company_address, company_tel, company_email, company_ceo, company_employee, company_product, company_process, company_standard, company_certificate, company_date))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f'데이터베이스 저장 중 오류가 발생했습니다: {e}')


# 페이지 설정
st.set_page_config(
    page_title="ISO인증심사신청",
    page_icon=":sunglasses:",
)



st.title('ISO인증심사신청')
st.caption('ISO인증심사신청을 위한 정보를 입력해주세요.')
st.caption('인증심사와 관련한 자세한 사항은 인증심사원이 배정된 후 안내드리겠습니다.')

st.divider()

# 회사정보 입력
st.subheader('[기본정보]')
st.caption('견적산출 시 발급된 견적번호를 입력하시면 작성하신 정보를 불러옵니다.')

quote_id = st.text_input(
    '견적번호',
    help='견적계산 시 발급된 견적번호를 입력해주세요.',
)

# db_data = get_applications(quote_id) if quote_id is not None else None
# # st.write(db_data)

if quote_id:
   # 데이터베이스에서 정보 검색
    db_data = get_applications(quote_id)
    if db_data:
        # 정보를 기반으로 처리(예: 정보 표시)
        # st.write("견적 정보:", db_data)
        company_name = db_data[0]['name']
        email = db_data[0]['email']
        contact = db_data[0]['contact']
        contact_name = db_data[0]['contact_name']
        product = db_data[0]['product']
        biz_type = db_data[0]['biz_type']
        standards = db_data[0]['standards']
        audit_type = db_data[0]['audit_type']

        # 업종 목록 정의
        biz_type_options = ['제조업', '건설업','기타']
        # 기존에 저장된 biz_type 값의 인덱스를 찾음.
        default_biz_type_index = biz_type_options.index(biz_type) if biz_type in biz_type_options else 0

        # 심사유형 매핑
        audit_type_mapping = {
            'initial': '최초심사',
            'surveillance': '사후심사',
            'renewal': '갱신심사',
        }

        # 심사유형 목록 정의
        audit_type_options = ['최초심사', '사후심사', '갱신심사']
        # 매핑된 심사유형을 사용하여 기본 인덱스를 찾음
        mapped_audit_type = audit_type_mapping.get(audit_type, '최초심사')
        default_audit_type_index = audit_type_options.index(mapped_audit_type)


        # 표준 매핑
        standard_mapping = {
            'qms': 'ISO 9001',
            'ems': 'ISO14001',
            'ohsms': 'ISO45001',
            'cms': 'ISO22716',
        }

        # 'standards' 값을 쉼표로 분리하여 각각 ISO 표준으로 매핑
        # DB에서 받은 'standards' 값을 쉼표로 분리 후 매핑을 통해 ISO 표준으로 변환
        mapped_standards = [standard_mapping.get(s.strip()) for s in standards.split(',') if s.strip() in standard_mapping]
        # st.write('default_standards:', mapped_standards)

        # 표준 목록 정의
        standard_options = ['ISO 9001', 'ISO14001', 'ISO45001', 'ISO22716']

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input('회사명', value=company_name)
            company_email = st.text_input('이메일', value=email, help='모든 안내는 이메일로 전송됩니다. 정확한 이메일 주소를 입력해주시고 가능하면 회사 대표이메일을 입력해주세요.')
            st.caption('인증심사 관련 안내는 이메일로 전송됩니다. 정확한 이메일 주소를 입력해주세요.')
            contact_name = st.text_input('담당자명', placeholder='홍길동/과장', value=contact_name)
            contact = st.text_input('담당자 연락처', placeholder='010-1234-5678', value=contact)

        with col2:
            product = st.text_input('제품명', value=product, help='대표적인 제품 및 서비스명을 입력해주세요. (ex. 화장품 제조업)')
            biz_type = st.selectbox('업종', biz_type_options, index=default_biz_type_index, help='자세한 업종정보는 담당 심사원이 상세하게 파악합니다.')
            standards = st.multiselect('적용표준', standard_options, default=mapped_standards)
            audit_type = st.selectbox('심사유형', audit_type_options, index=default_audit_type_index)


        st.divider()

        # 옵션 입력
        st.subheader('[옵션선택]')
        st.caption('견적계산 시 선택하신 옵션이 정확한 지 확인해주세요.')

        # 멀티 체크박스
        st.checkbox('견적서 확인', value=True)
    else:
        # 데이터가 없는 경우의 처리
        st.error("입력하신 견적번호에 해당하는 정보를 찾을 수 없습니다.")
else:
    st.warning("견적번호를 입력하시면 견적정보를 불러옵니다.")


st.divider()

# 사업자등록증 업로드
uploaded_file = st.file_uploader('사업자등록증', type=['pdf', 'jpg', 'png'], help='사업자등록증을 업로드해주세요. PDF 파일만 업로드 가능합니다.')

if uploaded_file is not None:
    # 파일 저장
    file_path = os.path.join("temp_files", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("파일 업로드 성공!")