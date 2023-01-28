#!/bin/bash
python3 upload_model.py
cd python_tests/
python3 create_config.py
python3 create_ders_data.py