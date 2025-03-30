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
            field_type = types.get(key, 'str')
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
            type_func = str
            if types.get(key) == 'int':
                try:
                    value = int(value)
                except ValueError:
                    pass
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
            fieldset {{ margin: 20px; padding: 20px; }}
            legend {{ font-weight: bold; }}
            input {{ margin-left: 10px; }}
        </style>
    </head>
    <body>
        <h1>Dynamic Form</h1>
        <form method="POST" action="/submit">
            {form_html}
            <div style="margin: 20px;">
                <input type="submit" value="Submit">
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
    <h1>Form Submitted Successfully</h1>
    <p>Check submitted_form.json for the results</p>
    <a href="/">Back to form</a>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)