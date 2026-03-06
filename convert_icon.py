from PIL import Image
import os

def convert_to_ico():
    source = "macro_icon.png"
    target = "macro.ico"
    
    if os.path.exists(source):
        img = Image.open(source)
        # Create ico with various sizes for Windows
        img.save(target, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"Başarılı! '{target}' oluşturuldu. ⚡")
    else:
        print(f"Hata: '{source}' bulunamadı. Lütfen görseli bu klasöre kopyalayın.")

if __name__ == "__main__":
    convert_to_ico()
