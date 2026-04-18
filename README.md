# lake-encroachment-detector

This project is designed to see detect encroachments within 30m buffer zones of lakes in Coimbatore. Sentinel-2 images from Google Earth Engine and geometry of boundaries of lakes obtained from Open Street Map served as the data source. The project identifies and flags zones with high and moderate changes between the years 2019 and 2024. The future scope/improvements for this project include detecting lake shrinkage and illegal construction around lakes and automating the product to run every three months to detect changes regularly.

## Instructions to run
```bash
python -m venv **name your virtual env**
```
```bash
pip install requirements.txt
```
```bash
pip src/get_lakes.py
```
```bash
pip src/get_imagery.py
```
```bash
pip src/buffer_zones.py
```
```bash
pip src/change_detection.py
```
```bash
pip src/visualisation.py
```
- Run the html file "flagged_zones.html" in your browser to see the map
