# Dynamic JSON Form Generator

[![Python](https://img.shields.io/badge/python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-lightgrey?logo=flask)](https://flask.palletsprojects.com/)

A configurable web form generator that creates dynamic forms from JSON specifications. Perfect for rapid prototyping and configuration management.
**Not production ready**

## ✨ Features

- **JSON-Driven Forms**: Define forms through simple JSON configuration
- **Dynamic Fields**: Supports nested structures and list inputs
- **Type Validation**: Automatic type conversion (int/bool/list/str)
- **Web Interface**: Built with Flask for easy access
- **Persistent Storage**: Saves submissions to JSON file

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask 2.0+
- Git

### Installation
```bash
git clone https://github.com/yourusername/json_to_form.git
cd json_to_form
python -m venv .venv
sourve .venv/bin/activate
pip install flask #or pip install -r requirements.txt
python main.py
