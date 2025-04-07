from flask import Flask, request, render_template_string
import json

app = Flask(__name__)

# Load form structure and field types
with open('form.json') as f:
    form_structure = json.load(f)

with open('form-type.json') as f:
    form_types = json.load(f)

def generate_form_fields(data, types, parent_key=''):
    html = ''
    for key, value in data.items():
        current_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            html += f"<fieldset><legend>{key}</legend>"
            html += generate_form_fields(value, types.get(key, {}), current_key)
            html += "</fieldset>"
        else:
            field_type = str(types.get(key, 'str')).lower()
            
            # List type handling
            if field_type.startswith('list['):
                element_type = field_type[5:-1].strip()
                list_values = value if isinstance(value, list) else []
                current_value = ', '.join(map(str, list_values))
                html += f"""
                <div style="margin: 10px;">
                    <label>{key}:</label>
                    <input type="text" name="{current_key}" value='{current_value}'>
                    <span style="font-size: 0.8em; color: #666;">
                        (comma-separated {element_type} values)
                    </span>
                </div>
                """
            # Boolean handling
            elif field_type == 'bool':
                checked_true = 'selected' if str(value).lower() == 'true' else ''
                checked_false = 'selected' if str(value).lower() == 'false' else ''
                html += f"""
                <div style="margin: 10px;">
                    <label>{key}:</label>
                    <select name="{current_key}">
                        <option value="true" {checked_true}>True</option>
                        <option value="false" {checked_false}>False</option>
                    </select>
                </div>
                """
            # Other types
            else:
                input_type = 'number' if field_type == 'int' else 'text'
                html += f"""
                <div style="margin: 10px;">
                    <label>{key}:</label>
                    <input type="{input_type}" name="{current_key}" value='{value}'>
                </div>
                """
    return html

def parse_form_data(flat_data):
    nested_data = {}
    for key_path, value in flat_data.items():
        parts = key_path.split('.')
        current = nested_data
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = value
    return nested_data

def validate_and_convert(data, types):
    validated = {}
    for key, value in data.items():
        if isinstance(value, dict):
            validated[key] = validate_and_convert(value, types.get(key, {}))
        else:
            field_type = str(types.get(key, 'str')).lower()
            
            # List type conversion
            if field_type.startswith('list['):
                element_type = field_type[5:-1].strip().lower()
                elements = [e.strip() for e in value.split(',') if e.strip()]
                converted = []
                for e in elements:
                    try:
                        if element_type == 'int':
                            converted.append(int(e))
                        elif element_type == 'bool':
                            converted.append(e.lower() == 'true')
                        else:  # str or unknown types
                            converted.append(e)
                    except ValueError:
                        converted.append(e)
                validated[key] = converted
            # Boolean conversion
            elif field_type == 'bool':
                validated[key] = value.lower() == 'true'
            # Integer conversion
            elif field_type == 'int':
                try:
                    validated[key] = int(value)
                except ValueError:
                    validated[key] = value
            # String (default)
            else:
                validated[key] = value
    return validated

@app.route('/', methods=['GET'])
def show_form():
    form_html = generate_form_fields(form_structure, form_types)
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dynamic Form</title>
        <style>
            fieldset {{ 
                margin: 20px; 
                padding: 20px; 
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            legend {{ 
                font-weight: bold;
                padding: 0 10px;
            }}
            input, select {{ 
                margin-left: 10px; 
                padding: 5px;
            }}
            div {{ margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>Dynamic Form</h1>
        <form method="POST" action="/submit">
            {form_html}
            <div style="margin: 20px;">
                <input type="submit" value="Submit" style="padding: 10px 20px;">
            </div>
        </form>
    </body>
    </html>
    """)

@app.route('/submit', methods=['POST'])
def submit_form():
    form_data = parse_form_data(request.form.to_dict(flat=True))
    validated_data = validate_and_convert(form_data, form_types)
    
    with open('submitted_form.json', 'w') as f:
        json.dump(validated_data, f, indent=4)
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Form Submitted</title>
        <style>
            body {{ padding: 20px; font-family: Arial, sans-serif; }}
            a {{ color: #0066cc; text-decoration: none; }}
        </style>
    </head>
    <body>
        <h1>Form Submitted Successfully</h1>
        <p>Check submitted_form.json for the results</p>
        <a href="/">&larr; Back to form</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)