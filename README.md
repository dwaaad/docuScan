<div align="center">
  <picture>
    <source srcset="images/docuScan_dark.svg" media="(prefers-color-scheme: dark)">
    <img src="images/docuScan_light.svg" alt="Project Logo" width="300">
  </picture>
  <p><em><sub>Logo created in Adobe Illustrator 2026</sub></em></p>
</div>
<br>

<p>In retaliation to the discontinuation of Microsoft Office Lens, I have created this simple tool to convert images into a scanned document appearance, without the need for a printer.</p>

### Document Comparison
<p>Here is a demonstration of what docuScan achieves.</p>
<table>
  <tr align="center">
    <td><strong>Input</strong></td>
    <td><strong>Output</strong></td>
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

# Pseudocode
<p>There already exists tons of apps that achieve the same results, but they all hide their features behind paywalls and ads that bloat your phone.</p>
<p>I came up with a theoretical algorithm to achieve the same in seconds, and had a working prototype in less than a day.</p>
<p>It was deceptively simple, and I want it to be publically available, free to use for anybody:</p>

```python
greyscale the image
loop through each pixel:
     if the_current_pixel < 50% black: # then it's grey which should be white
          the_current_pixel = white
     if the_current_pixel > 50% black AND the_current_pixel <= 99% black: # then it's dark grey which should black
          the_current_pixel = black
```

# Build Instructions
To build a python copy from source, follow the instructions below:
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
python gui.py
```
If this doesn't work, you can try:
```cmd
python3 gui.py
```

# To Do
- [ ] React Web Version
- [ ] React Native Mobile Version
<!-- REFERENCES -->
<!-- github.com/agyorev/DocuScan/tree/master - openCV autocrop rectangles -->
<!-- github.com/joehanmisquitta/DocuScan/tree/main - check out this web app -->
<!-- https://github.com/AlexScotland/DocuScan-Python - extract text from a pdf into strings -->
<!-- https://github.com/IharLobach/docuscan - Crop documents from photos -->

# Licence
This project is licensed under the GNU AGPLv3 licence.

However, the file [`gui.py`](https://github.com/dwaaad/docuScan/blob/main/py/gui.py)
contains code derived from StackOverflow answers licensed under CC BY-SA 4.0
and its classes are therefore distributed under CC BY-SA 4.0.
