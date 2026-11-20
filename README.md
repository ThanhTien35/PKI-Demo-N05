
# PKI & Chain of Trust Demo

**Group N05 – Ton Duc Thang University**

Demo môn học Bảo mật thông tin, minh họa cơ chế xác thực chứng chỉ số HTTPS thông qua Public Key Infrastructure (PKI) và Chain of Trust.

## 1. Giới thiệu

Dự án mô phỏng quy trình thiết lập HTTPS bằng chứng chỉ X.509 do một Root Certificate Authority (Root CA) riêng cấp phát.

Mục tiêu:
- Tạo Root CA bằng OpenSSL.
- Tạo khóa riêng và chứng chỉ cho localhost.
- Sử dụng Root CA để ký chứng chỉ máy chủ.
- Chạy HTTPS Server bằng Python.
- Kiểm chứng trạng thái Untrusted và Trusted.
- Hiển thị thông tin chứng chỉ trên giao diện web.
- Minh họa Certificate Chain of Trust.

## 2. Công nghệ sử dụng

- HTML5, CSS3, JavaScript
- Python 3
- OpenSSL
- Python cryptography
- HTTPS / TLS
- X.509 Digital Certificate
- Google Chrome
- Windows Certificate Manager

## 3. Cấu trúc thư mục

```text
PKI-Demo-N05/
│
├── index.html        # Giao diện demo
├── server.py         # HTTPS Server và Certificate API
├── localhost.ext     # Cấu hình X.509 Extensions
│
├── rootCA.key        # Private Key của Root CA
├── rootCA.crt        # Root CA Certificate
├── rootCA.srl        # Certificate Serial Number
│
├── localhost.key     # Private Key của Server
├── localhost.csr     # Certificate Signing Request
├── localhost.crt     # Server Certificate
│
└── README.md
```

Lưu ý: Các file .key là khóa riêng, không được đưa lên repository công khai.

## 4. Yêu cầu môi trường

Cần cài đặt:

1. Python 3
2. OpenSSL
3. Git Bash
4. Visual Studio Code
5. Google Chrome

Kiểm tra môi trường trong Git Bash:

```bash
python --version
openssl version
```

Cài đặt thư viện Python:

```bash
python -m pip install cryptography
```

## 5. Quick Start – Chạy nhanh

Áp dụng khi đã có sẵn các file chứng chỉ trong thư mục dự án.

### Bước 1: Mở thư mục dự án

Mở thư mục PKI-Demo-N05 bằng VS Code.

Chọn Terminal → New Terminal → Git Bash.

### Bước 2: Cài thư viện

```bash
python -m pip install cryptography
```

### Bước 3: Chạy HTTPS Server

```bash
python server.py
```

Kết quả mong đợi:

```text
PKI & CHAIN OF TRUST - GROUP N05
HTTPS Server: https://localhost:8443
Certificate API: /api/certificate
Press Ctrl+C to stop
```

### Bước 4: Mở website

Truy cập:

https://localhost:8443

Nếu Root CA chưa được tin cậy, Chrome sẽ hiển thị cảnh báo bảo mật.

Nếu Root CA đã được cài đặt và tin cậy, website sẽ hiển thị bình thường.

Dừng server bằng Ctrl+C.

## 6. Tạo Root CA và chứng chỉ từ đầu

Thực hiện các lệnh sau trong Git Bash tại thư mục dự án.

### 6.1. Tạo Private Key cho Root CA

```bash
openssl genrsa -out rootCA.key 2048
```

### 6.2. Tạo Root CA Certificate

```bash
MSYS_NO_PATHCONV=1 openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 3650 -subj "/C=VN/ST=HoChiMinh/O=TDTU Group N05/CN=TDTU Group N05 Private Root CA" -out rootCA.crt
```

### 6.3. Tạo Private Key cho localhost

```bash
openssl genrsa -out localhost.key 2048
```

### 6.4. Tạo Certificate Signing Request

```bash
MSYS_NO_PATHCONV=1 openssl req -new -key localhost.key -subj "/C=VN/ST=HoChiMinh/O=TDTU Group N05/CN=localhost" -out localhost.csr
```

### 6.5. Tạo file localhost.ext

Nội dung:

```ini
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
IP.1 = 127.0.0.1
```

### 6.6. Root CA ký chứng chỉ localhost

```bash
openssl x509 -req -in localhost.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out localhost.crt -days 365 -sha256 -extfile localhost.ext
```

Kiểm tra chứng chỉ:

```bash
openssl verify -CAfile rootCA.crt localhost.crt
```

Kết quả mong đợi:

```text
localhost.crt: OK
```

## 7. Demo giai đoạn 1 – Untrusted Certificate

### Bước 1

Chưa import Root CA vào Windows Trusted Root Store.

Nếu đã từng import Root CA thử nghiệm này, cần xóa chứng chỉ đó khỏi Trust Store trước khi kiểm thử.

### Bước 2

Chạy:

```bash
python server.py
```

### Bước 3

Mở Chrome:

https://localhost:8443

Kết quả mong đợi:

- Chrome hiển thị cảnh báo "Your connection is not private".
- Mã lỗi thường là NET::ERR_CERT_AUTHORITY_INVALID.
- Root CA chưa được trình duyệt tin cậy.

Chụp ảnh:

01_Untrusted_Certificate.png

## 8. Demo giai đoạn 2 – Trusted Certificate

### Bước 1: Mở Certificate Manager

Nhấn Win+R, nhập:

```text
certmgr.msc
```

### Bước 2: Import Root CA

1. Chọn Trusted Root Certification Authorities.
2. Chọn Certificates.
3. Nhấn chuột phải → All Tasks → Import.
4. Chọn file rootCA.crt.
5. Chọn Trusted Root Certification Authorities.
6. Nhấn Next → Finish.
7. Xác nhận nếu Windows hiển thị cảnh báo.

Chỉ import Root CA do nhóm tự tạo trên máy thử nghiệm.

### Bước 3: Kiểm tra HTTPS

Đóng toàn bộ Chrome rồi mở lại.

Truy cập:

https://localhost:8443

Kết quả mong đợi:

- Không còn cảnh báo bảo mật.
- Website PKI & Chain of Trust hiển thị.
- Trình duyệt chấp nhận chứng chỉ localhost.

Chụp ảnh:

02_HTTPS_Verified.png

## 9. Kiểm tra Chain of Trust

Trên Chrome:

1. Truy cập https://localhost:8443.
2. Nhấn biểu tượng thông tin kết nối bên trái địa chỉ.
3. Mở Certificate Viewer.
4. Chọn tab Details.
5. Quan sát Certificate Hierarchy.

Chuỗi chứng chỉ:

```text
TDTU Group N05 Private Root CA
              |
              v
          localhost
```

Root CA là Trust Anchor.

Leaf Certificate được Root CA ký và sử dụng cho HTTPS Server.

Chụp ảnh:

03_Certificate_General.png
04_Certificate_Chain_of_Trust.png

## 10. Certificate Viewer trên website

Website cung cấp chức năng xem thông tin chứng chỉ thông qua API.

### Xem chứng chỉ

Nhấn nút View Certificate trên giao diện.

Thông tin hiển thị:

- Subject
- Issuer
- Serial Number
- Valid From
- Valid Until
- Signature Algorithm
- Subject Alternative Name
- SHA-256 Fingerprint

### Kiểm tra API trực tiếp

Truy cập:

https://localhost:8443/api/certificate

API trả về dữ liệu JSON được đọc từ localhost.crt.

### Tải chứng chỉ

Truy cập:

https://localhost:8443/api/certificate/download

Hoặc nhấn Download Certificate trên website.

### Sao chép Fingerprint

Nhấn Copy Fingerprint trong Certificate Viewer.

Lưu ý: Certificate Viewer trên website chỉ hiển thị dữ liệu chứng chỉ. Trình duyệt mới là thành phần thực hiện xác minh trạng thái tin cậy của kết nối HTTPS.

## 11. Kiểm tra Responsive

Website hỗ trợ:

- Desktop
- Tablet
- Mobile

Kiểm tra:

1. Mở Chrome.
2. Nhấn F12.
3. Nhấn Ctrl+Shift+M.
4. Chọn kích thước màn hình.
5. Kiểm tra Navbar, Dashboard và Certificate Viewer.

Navbar sử dụng Sticky Position và hỗ trợ Smooth Scrolling.

## 12. Các lỗi thường gặp

### ERR_CONNECTION_REFUSED

Nguyên nhân: HTTPS Server chưa chạy.

Khắc phục:

```bash
python server.py
```

### ModuleNotFoundError: cryptography

Khắc phục:

```bash
python -m pip install cryptography
```

### Address already in use

Nguyên nhân: Cổng 8443 đang được sử dụng.

Dừng server cũ bằng Ctrl+C hoặc kiểm tra tiến trình đang sử dụng cổng.

### NET::ERR_CERT_AUTHORITY_INVALID

Nguyên nhân: Root CA chưa được tin cậy.

Đây là kết quả mong đợi trong giai đoạn Untrusted.

### Certificate API không hoạt động

Kiểm tra server.py đã hỗ trợ endpoint:

```text
/api/certificate
```

Sau đó khởi động lại HTTPS Server.

## 13. Dọn dẹp môi trường sau demo

Sau khi hoàn thành kiểm thử, nên xóa Root CA thử nghiệm khỏi Windows.

1. Nhấn Win+R.
2. Nhập certmgr.msc.
3. Mở Trusted Root Certification Authorities.
4. Chọn Certificates.
5. Tìm TDTU Group N05 Private Root CA.
6. Kiểm tra đúng chứng chỉ thử nghiệm.
7. Nhấn Delete và xác nhận.

Không xóa các Root CA khác của hệ thống.

## 14. Thành viên nhóm

| Họ và tên | MSSV |
|---|---|
| Nguyễn Thanh Tiền | 524H0035 |
| Nguyễn Minh Đăng | 524H0082 |
| Trần Gia Huy | 524H0092 |

**Group N05 – Ton Duc Thang University**

Information Security – PKI & Chain of Trust Demo

2026
