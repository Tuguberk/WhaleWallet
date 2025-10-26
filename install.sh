#!/bin/bash
# Kripto Cüzdan Takip Yazılımı Kurulum Scripti

echo "🚀 Kripto Cüzdan Takip Yazılımı Kuruluyor..."

# Python'ın yüklü olup olmadığını kontrol et
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 bulunamadı. Lütfen önce Python3 kurun."
    exit 1
fi

# Python versiyonunu kontrol et
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
echo "✅ Python3 $python_version bulundu"

# Sanal ortam oluşturma (isteğe bağlı)
echo "📦 Sanal ortam oluşturuluyor..."
python3 -m venv venv

# Sanal ortamı aktifleştirme
echo "🔄 Sanal ortam aktifleştiriliyor..."
source venv/bin/activate

# Gerekli kütüphaneleri yükleme
echo "📚 Kütüphaneler yükleniyor..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Kurulum tamamlandı!"
echo ""
echo "Başlatmak için:"
echo "1. source venv/bin/activate"
echo "2. config.py dosyasını düzenleyin"
echo "3. python main.py"
