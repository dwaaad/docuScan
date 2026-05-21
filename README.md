<picture>
  <source srcset="images/docuScan_dark.svg" media="(prefers-color-scheme: dark)">
  <img src="images/docuScan_light.svg" alt="Project Logo" width="300">
</picture>
<p>In retaliation to the discontinuation of Microsoft Office Lens, I have created this simple tool to convert images into a scanned document appearance.</p>

<table>
  <tr>
    <td align="center"><strong>Before</strong></td>
    <td align="center"><strong>After</strong></td>
  </tr>
  <tr>
    <td>
      <img src="https://github.com/user-attachments/assets/8e02ecb3-e22b-4c4b-866c-c8653c5ef84d" width="300">
    </td>
    <td>
      <img src="https://github.com/user-attachments/assets/588c81ae-e98d-47f8-b45b-5b2e4caf0bee" width="300">
    </td>
  </tr>
</table>

# Installation
1. Clone repository
```cmd
git clone https://github.com/dwaaad/docuScan.git
cd docuScan
```
2. Install dependencies
```cmd
pip install -r requirements.txt
```
3. Run program
```cmd
python main.py
```
If this doesn't work, you can try:
```cmd
python3 main.py
```

# To Do
- [ ] React Web Version
- [ ] React Native Mobile Version

# Licence
This project is licensed under a modified version of the MIT License.
However, the file [`gui.py`](https://github.com/dwaaad/docuScan/blob/main/py/gui.py) contains code derived from StackOverflow answers
licensed under CC BY-SA 4.0 and its classes are therefore distributed under CC BY-SA 4.0.
