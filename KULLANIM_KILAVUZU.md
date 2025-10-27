# Balina2Droid - Kripto Cüzdan Takip Sistemi

Ethereum cüzdan bakiyelerini ve Hyperliquid pozisyonlarını izleyen, değişiklikler olduğunda Telegram üzerinden bildirim gönderen Python uygulaması.

## 🚀 Özellikler

- **Cüzdan Takibi**: ETH bakiye değişiklikleri ve token transferlerini izler
- **Pozisyon Takibi**: Hyperliquid perpetual pozisyonlarını izler
- **Akıllı Bildirimler**: Sadece önemli olaylar için bildirim gönderir:
  - Pozisyon açma/kapama/değiştirme
  - Para yatırma ve çekme işlemleri (ETH, BTC ve diğer ERC-20 tokenler)
  - Anlamlı bakiye değişiklikleri
- **Telegram Entegrasyonu**: Gerçek zamanlı bildirimler
- **Yapılandırılabilir**: 10 dakikalık kontrol aralıkları
- **Güvenli**: Hassas bilgiler şifreli olarak saklanır

## 📋 Kurulum

### 1. Depoyu Klonlama
```bash
git clone https://github.com/stvowns/balina2.git
cd balina2droid
```

### 2. Sanal Ortam Oluşturma
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

### 3. Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

### 4. Kurulum Script'ini Çalıştırma (Önerilen)
```bash
chmod +x install.sh
./install.sh
```

## ⚙️ Yapılandırma

### 1. Telegram Bot Oluşturma

1. Telegram'da [@BotFather](https://t.me/botfather) hesabını açın
2. `/newbot` komutu ile yeni bot oluşturun
3. Bot token'ını kopyalayın (örn: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Chat ID Öğrenme

**Yöntem 1: Otomatik Script**
```bash
python3 telegram_setup.py
```
Bu script sizden bot token'ı isteyecek ve chat ID'nizi otomatik olarak bulacaktır.

**Yöntem 2: Manuel**
```bash
python3 get_chat_id.py
```
Bot token'ı girip ardından botunuza bir mesaj gönderin.

### 3. Konfigürasyon Dosyası Oluşturma

1. `config.example.py` dosyasını kopyalayın:
```bash
cp config.example.py config.py
```

2. `.env.example` dosyasını kopyalayın:
```bash
cp .env.example .env
```

`.env` dosyasına aşağıdaki bilgileri ekleyin:
```bash
# Takip edilecek cüzdan adresi
WALLET_ADDRESS=0xSIZIN_CUZDAN_ADRESINIZ

# Etherscan API anahtarı (https://etherscan.io/apis adresinden alın)
ETHERSCAN_API_KEY=SIZIN_ETHERSCAN_API_KEY

# Telegram ayarları
TELEGRAM_BOT_TOKEN=BOTFATHERDAN_ALDIGINIZ_BOT_TOKEN
TELEGRAM_CHAT_ID=get_chat_id_ile_ogrendiginiz_chat_id

# Gmail bildirimleri (isteğe bağlı)
EMAIL_SENDER=gmail_adresiniz@gmail.com
EMAIL_PASSWORD=16_haneli_google_app_password
EMAIL_RECIPIENT=bildirim_alacak_adres@email.com
```

**Önemli**:
- `config.py` dosyasını doğrudan düzenlemenize gerek yoktur. Bu dosya `.env` dosyasından bilgileri otomatik olarak okur.
- `.env` dosyası .gitignore'da tanımlıdır, hassas bilgileriniz depoya eklenmez.
- Email ayarları isteğe bağlıdır, sadece Gmail bildirimleri istiyorsanız doldurun.

### 4. Güvenli Konfigürasyon (İsteğe Bağlı)

Hassas bilgilerinizi şifreli saklamak için:
```bash
python3 -c "from secure_config import setup_secure_config; setup_secure_config()"
```

## 🎯 Kullanım

### Tekil Kontrol
Cüzdan durumunu bir kez kontrol etmek için:
```bash
python3 main.py --check
```

### Sürekli İzleme
Arkaplanda sürekli izleme başlatmak için:
```bash
python3 main.py
```

Uygulama her 10 dakikada bir kontrol yapacak ve değişiklikler için bildirim gönderecektir.

### Telegram Bildirimleri

Uygulama aşağıdaki durumlar için bildirim gönderecektir:

- 🚀 **Pozisyon Açıldı**: Yeni pozisyon oluşturulduğunda
- ✅ **Pozisyon Kapandı**: Pozisyon kapatıldığında
- 🔄 **Pozisyon Değişti**: Pozisyon büyüklüğü değiştiğinde
- 📥 **Para Yatırma**: Cüzdana ETH, BTC veya token geldiğinde
- 📤 **Para Çekme**: Cüzdan para gönderdiğinde

## 📊 Bildirim Örnekleri

### Başlangıç Bildirimi
```
🚀 WALLET TRACKER STARTED
Wallet: 0x1234...abcd
ETH Balance: 1.2345 ETH
Start Time: 2024-01-01 12:00:00

Monitoring active...
```

### Pozisyon Değişikliği
```
📈 POSITION OPENED
🔹 ETH: $50,000 → 1.0x
Entry: $3,200
Size: 15.625 ETH
```

### Bakiye Değişikliği
```
💰 BALANCE CHANGE
Previous: 1.2345 ETH
Current: 2.7345 ETH
Change: +1.5000 ETH (+$4,800)
```

## 🔧 Test

### Telegram Bağlantısını Test Etme
```bash
python3 test_notification.py
```

### Pozisyon Debug Modu
```bash
python3 debug_positions.py
```

## 📁 Dosya Yapısı

- `main.py` - Ana uygulama
- `wallet_tracker.py` - Cüzdan takip işlemleri
- `notification_system.py` - Bildirim sistemi
- `telegram_helper.py` - Telegram entegrasyonu
- `config.py` - Konfigürasyon dosyası
- `secure_config.py` - Şifreli konfigürasyon
- `transactions.log` - İşlem kayıtları

## ⚠️ Güvenlik Notları

- **HASSAS BİLGİLERİ GÜVENCEDE TUTUN**: API anahtarlarınızı ve özel anahtarlarınızı asla paylaşmayın
- **GIT IGNORE**: `config.py` dosyası şablon olarak depoda mevcuttur ancak gerçek API anahtarlarınızı içermemelidir. Hassas bilgileri `.env` dosyasında saklayın
- **GÜVENLİ DEPOLAMA**: Hassas bilgiler için `secure_config.py` kullanın
- **API ANAHTARI LİMİTLERİ**: Etherscan API kullanım limitlerine dikkat edin

## 🛠️ Yapılandırma Seçenekleri

### Kontrol Aralığı
```python
# config.py dosyasında
CHECK_INTERVAL = 600  # 10 dakika (saniye cinsinden)
```

### Bildirim Eşikleri
```python
# config.py dosyasında
BALANCE_CHANGE_THRESHOLD = 0.1  # 0.1 ETH üzeri değişiklikler için bildirim
POSITION_CHANGE_THRESHOLD = 1000  # $1000 üzeri değişiklikler için bildirim
```

### Bildirim Kanalları
```python
NOTIFICATION_SETTINGS = {
    "telegram": {"enabled": True},
    "email": {"enabled": False},  # E-posta bildirimleri (Gmail desteği mevcut)
    "console": {"enabled": True}  # Konsol çıktıları
}
```

### Gmail Bildirimleri için Kurulum (Opsiyonel)

1. **Google App Password Oluşturma**:
   - Google hesabınızda "2 Adımlı Doğrulama"yı aktif edin
   - Google App Password oluşturun: https://myaccount.google.com/apppasswords
   - "Uygulama" olarak "Diğer (Özel ad)" seçin
   - Uygulama adı olarak "Balina2Droid" yazın
   - Oluşturulan 16 haneli şifreyi kopyalayın

2. **Gmail Ayarlarını Etkinleştirme**:
   `.env` dosyasına Gmail bilgilerini ekleyin ve `config.py` dosyasında email ayarını aktif edin:

   `.env` dosyasına ekleyin:
   ```bash
   EMAIL_SENDER=gmail_adresiniz@gmail.com
   EMAIL_PASSWORD=16_haneli_google_app_password
   EMAIL_RECIPIENT=bildirim_alacak_adres@email.com
   ```

   **Önemli**: `config.py` dosyasını düzenlemenize gerek yoktur. Email ayarları `.env` dosyasından otomatik olarak okunur ve gerekli bilgiler varsa otomatik olarak aktif olur.

## 📞 Sorun Giderme

### Bot Token Çalışmıyor
1. BotFather'dan doğru token'ı aldığınızdan emin olun
2. Botunuza bir mesaj gönderdiğinizden emin olun
3. Chat ID'nizi kontrol edin

### Bildirimler Gelmiyor
1. İnternet bağlantınızı kontrol edin
2. Telegram botunun çalıştığını test edin:
```bash
python3 check_telegram.py
```

### API Hataları
1. Etherscan API anahtarınızın geçerli olduğunu kontrol edin
2. API limitlerini aşıp aşmadığınızı kontrol edin
3. Cüzdan adresinin doğru yazıldığından emin olun

## 📄 Gereksinimler

- Python 3.6+
- requests
- schedule
- python-dotenv

## 🤝 Destek

Sorunlarınız veya önerileriniz için GitHub issues kullanabilirsiniz.