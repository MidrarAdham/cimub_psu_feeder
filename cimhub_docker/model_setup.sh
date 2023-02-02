#!/bin/bash
python3 upload_model.py
read -p "changed directory to cimhub_docker/python_scripts/. Press Enter to continue"
cd python_tests/
python3 create_ders_hist_data.py

