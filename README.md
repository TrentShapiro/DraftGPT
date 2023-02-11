# DraftGPT
Magic: The Gathering Online OCR from arbitrary screen selection in Python

</br>

## Usage
`python cardfinder.py`

-  This will pop up a window on your main screen to select a bounding box to search for multiple cards.
-  Drag from top left to bottom right, type 'w' to confirm selection
-  A second window will pop up to show cards and their names as found by cv2 and identified by tesseract
-  While the second window is open, you can scroll slowly through any number of cards, type 'q' to exit this window
-  On close, the total unqiue list of cards seen is compiled, and card details are retrieved from Scryfall fuzzy search API
-  Example usage: [Youtube Example](https://youtu.be/5zyQDpBWJ8Q)

## Notes
-  It's recommended to make the individual card size as large as possible in mtgo.
-  Code has only been run on windows, Mac OS and Linux use at your own risk.
-  Google how to set up tesseract
-  If your python cannot find the executable from PATH, add the line `pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'` to the beginning of `cardfinder.py`


## Dependencies
-  pytesseract
-  PIL
-  cv2
-  pynput