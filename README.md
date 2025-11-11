# ビンゴメーカー

## フォント

[Noto Sans Japanese](https://fonts.google.com/noto/specimen/Noto+Sans+JP)

## PyInstallerのコマンド

```
pyinstaller ^
  --noconfirm ^
  --clean ^
  --name bingo-maker ^
  --onefile ^
  --windowed ^
  --add-data "bingo_maker/pdf;pdf" ^
  --add-data "bingo_maker/ui;ui" ^
  --add-data "fonts;fonts" ^
  bingo_maker/app.py
```
