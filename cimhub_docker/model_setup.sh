#!/bin/bash
cd python_tests/
echo "changing directory to /python_scripts/"
read -p "Press Enter to continue"
python3 create_ders_hist_data.py
cd ../
python3 upload_model.py