@echo off
echo 🚀 Sincronizando Greta Shop con la web...
cd /d "c:\Users\Sofia\.gemini\antigravity\scratch\bot_whatsapp"
"C:\Program Files\Git\bin\git.exe" add .
"C:\Program Files\Git\bin\git.exe" commit -m "Actualización automática de contenido"
"C:\Program Files\Git\bin\git.exe" push origin main
echo ✅ ¡Web actualizada! Ya podés ver los cambios en tu Instagram.
pause
