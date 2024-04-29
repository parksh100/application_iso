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
        st.error(f'데이터베이스 저장 중 오류가 발생했습니다. 자세한 정보는 관리자에게 문의하세요.')


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

# 이메일 전송 함수
load_dotenv()

def send_email_with_attachment(attachment_path, customer_info):
    # 환경 변수에서 이메일 설정 불러오기
    from_email = os.getenv('EMAIL_FROM')
    smtp_password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = os.getenv('SMTP_PORT')

    # 이메일 메시지 생성
    msg = EmailMessage()
    msg.set_content(f'''
        ISO인증 심사 신청서가 접수되었습니다. 아래 정보를 확인해주세요.\n\n
        심사비: {customer_info['audit_fee']}\n
        회사명: {customer_info['name']}\n
        이메일: {customer_info['email']}\n
        담당자명: {customer_info['contact_name']}\n
        연락처: {customer_info['contact']}\n
        제품명: {customer_info['product']}\n
        업종: {customer_info['biz_type']}\n
        적용표준: {customer_info['standards']}\n
        심사유형: {customer_info['audit_type']}\n
        견적번호: {customer_info['quote_id']}\n
        지역: {customer_info['locale']}\n
        올인원패키지: {customer_info['all_support']}\n
        문서옵션: {customer_info['documents_support']}\n
        부적합옵션: {customer_info['nc_support']}\n
        심사대응옵션: {customer_info['response_support']}\n\n

        첨부된 사업자등록증을 확인해주세요.
        ''')
    msg['Subject'] = f"Surprise! {customer_info['name']} ISO인증 심사 심사 신청서 접수 확인"
    msg['From'] = from_email
    msg['To'] = 'parksh@kaicert.co.kr'

    # 파일 첨부
    if attachment_path:
        with open(attachment_path, 'rb') as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
    
    # 이메일 전송
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(from_email, smtp_password)
        server.send_message(msg)
        st.session_state.email_sent = True
        st.success("이메일 전송 완료! 심사원을 배정하겠습니다. 배정된 심사원이 연락드릴 예정입니다.")

# 페이지 설정
st.set_page_config(
    page_title="ISO인증심사신청",
    page_icon=":sunglasses:",
)



st.title('ISO인증심사신청')
st.write('이제 ISO인증 심사를 신청해보세요!')
st.write('인증심사와 관련한 자세한 사항은 인증심사원이 배정된 후 안내드리겠습니다.')
st.write(':bulb: 견적번호가 없으신 경우, 클릭해주세요.')
button_html = """
    <style>
        .custom-button {
            color: white;
            background-color: orange;
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }
    </style>
    <button onclick="window.location.href='https://iso-quote.streamlit.app/';" class="custom-button">견적 확인하기</button>
"""
st.markdown(button_html, unsafe_allow_html=True)

st.divider()

# 회사정보 입력
st.subheader('[기본정보]')
st.write(':rainbow[견적산출 시 발급된 견적번호를 입력하시면 작성하신 정보를 불러옵니다. 견적신청 시 선택한 사항과 일치하는지 확인해주세요. 필요 시 수정해주세요.]')

quote_id = st.text_input(
    '견적번호',
    help='견적계산 시 발급된 견적번호를 입력해주세요.',
)

db_data = get_applications(quote_id) if quote_id is not None else None
# st.write(db_data)

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
        audit_fee = db_data[0]['audit_fee']
        all_support = db_data[0]['all_support']
        documents_support = db_data[0]['documents_support']
        nc_support = db_data[0]['nc_support']
        response_support = db_data[0]['response_support']

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
            contact_name = st.text_input('담당자명', placeholder='홍길동/과장', value=contact_name)
            contact = st.text_input('담당자 연락처', placeholder='010-1234-5678', value=contact)
            product = st.text_input('제품명', value=product, help='대표적인 제품 및 서비스명을 입력해주세요. (ex. 화장품 제조업)')

        with col2:
            biz_type = st.selectbox('업종', biz_type_options, index=default_biz_type_index, help='자세한 업종정보는 담당 심사원이 상세하게 파악합니다.', disabled=True)
            standards = st.multiselect('적용표준', standard_options, default=mapped_standards, disabled=True)
            audit_type = st.selectbox('심사유형', audit_type_options, index=default_audit_type_index, disabled=True)
            audit_fee  = st.text_input('심사비', value=f"{int(audit_fee):,}원" ,disabled=True)
            all_support = st.checkbox('인증보장 패키지', value=all_support, disabled=True)
            documents_support = st.checkbox('시스템 문선 준비 포함', value=documents_support, disabled=True)
            nc_support = st.checkbox('부적합 시정조치 대응 포함', value=nc_support, disabled=True)
            response_support = st.checkbox('심사응대 및 대응 포함', value=response_support, disabled=True)



        st.divider()
        # 사업자등록증 업로드
        # st.write(":rainbow[아래에서 파일을 드래그하거나 클릭하여 브라우저에서 파일을 선택하세요.]")
        uploaded_file = st.file_uploader(':sparkles: :rainbow[사업자등록증을 업로드 하면 자동으로 전송 진행됩니다.]', type=['pdf', 'jpg', 'png', 'jpeg'], help='사업자등록증을 업로드해주세요. pdf, jpg, png, jpeg 파일만 업로드 가능합니다.')
        if uploaded_file is not None:
            with st.spinner('사업자등록증을 업로드 중입니다...'):
                time.sleep(3)  # 시뮬레이션을 위한 대기 시간
                # 파일 저장
                file_path = os.path.join("temp_files", uploaded_file.name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 디렉토리가 없으면 생성
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success("파일 업로드 성공!")

            with st.spinner('이메일 전송 중입니다...'):
                # 최대 시간을 20초로 설정
                max_time = 30
                progress_bar = st.progress(0)

                start_time = time.time()
                elapsed_time = 0

                # 시간이 최대 시간에 도달할 때까지 프로그레스 바 업데이트
                while elapsed_time < max_time:
                    elapsed_time = time.time() - start_time
                    percent_complete = int((elapsed_time / max_time) * 100)
                    progress_bar.progress(percent_complete)
                    time.sleep(0.1)  # 프로그레스 바를 부드럽게 업데이트

                progress_bar.progress(100)  # 마지막으로 프로그레스 바를 100%로 설정
                progress_bar.empty()  # 프로그레스 바를 화면에서 제거

                # 이메일 관련 정보를 데이터베이스에서 가져옴
                customer_info = get_applications(quote_id)[0]
                # st.write(customer_info)
                
                # 이메일 전송 함수 호출
                send_email_with_attachment(file_path, customer_info)
                
                if st.session_state.email_sent:
                    st.balloons()
                    st.success("모든 처리가 완료되었습니다. 제출해주셔서 감사합니다!")
    else:
        # 데이터가 없는 경우의 처리
        st.error("입력하신 견적번호에 해당하는 정보를 찾을 수 없습니다.")
else:
    st.warning("견적번호를 입력하시면 견적정보를 불러옵니다.")


st.divider()


