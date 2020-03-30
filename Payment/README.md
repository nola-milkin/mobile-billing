# Payment document
<img src="./images/screenshot.png" alt="" width="300"/>
<img src="./images/document.png" alt="" width="300"/>

```
.
├── fonts\
├── images\
├── payment.py
├── payment.pdf
└── reports\
```
### Description
Программа для создания отчёта о тарификации абонентов. 

### Run
Для запуска программы необходим:
- Python3 с библиотекой `fpdf`
```
pip3 install fpdf
```
А также зависимости от предыдущих проектов:
- Python библиотека `matplotlib`
- утилита nfdump
В случае запуска под ОС Linux достаточно просто запустить файл (присутствует шибенг).
```
python3 ./payment.py
```

### Input/Output files
Программа изначально запускает предыдущие два проекта, соответственно, они должны быть склонированы из репозитория и на ходиться на уровень выше:
```
.
├── CDR
├── NetFlow
└── Payment
    └── payment.py
```
Необходимы файлы `nfcapd.202002251200` или `dump.txt` в директории `NetFlow` и `data.csv` в директории `CDR`.

По окончании работы программа создаёт отчёт в директории `Payment`. Для корректного отображения Юникода нужны шрифты, они находятся в директории `./fonts`.