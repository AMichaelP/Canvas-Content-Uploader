cd ..
pyinstaller run_ccu.spec -y --clean
rm dist\canvas_content_uploader -r
ren dist\run_ccu canvas_content_uploader
