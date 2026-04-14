from flask import Flask, render_template, request
from datetime import datetime, date

app = Flask(__name__)

DATA_FILE = "data.txt"

@app.route('/')
def homepage():
    labels = []
    data = []

    # 1. Get query parameters or set defaults to TODAY
    # date.today().isoformat() returns "YYYY-MM-DD"
    today_str = date.today().isoformat()
    
    start_arg = request.args.get('start', today_str)
    end_arg = request.args.get('end', today_str)

    # Convert strings to date objects for comparison
    try:
        start_date = datetime.strptime(start_arg, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_arg, "%Y-%m-%d").date()
    except ValueError:
        # Fallback if user inputs garbage
        start_date = date.today()
        end_date = date.today()

    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split(";")]

                if len(parts) < 4:
                    continue

                # 2. Parse the date from the file (Format: 2025,10,27)
                try:
                    # We assume parts[0] is date "YYYY,MM,DD"
                    file_date_obj = datetime.strptime(parts[0], "%Y,%m,%d").date()
                except ValueError:
                    continue

                # 3. Filter: Is this line inside our window?
                if start_date <= file_date_obj <= end_date:
                    
                    # Create Label
                    date_display = parts[0].replace(",", "-")
                    time_display = parts[1].replace(",", ":")
                    full_label = f"{time_display}" # Just showing time makes sense for daily view

                    # Extract Voltage
                    try:
                        voltage = float(parts[3])
                        labels.append(full_label)
                        data.append(voltage)
                    except ValueError:
                        continue

    except FileNotFoundError:
        print("Data file not found.")

    # 4. Pass data AND current selection back to HTML
    return render_template(
        'chartjs-example.html', 
        labels=labels, 
        data=data,
        start_date=start_arg,
        end_date=end_arg
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
