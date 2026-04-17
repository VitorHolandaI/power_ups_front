from flask import Flask, render_template, request
from datetime import datetime, date

app = Flask(__name__)

DATA_FILE = "data.txt"

@app.route('/')
def homepage():
    labels = []
    voltages = []
    temperatures = []
    loads = []
    statuses = []
    full_rows = []

    today_str = date.today().isoformat()
    start_arg = request.args.get('start', today_str)
    end_arg = request.args.get('end', today_str)

    try:
        start_date = datetime.strptime(start_arg, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_arg, "%Y-%m-%d").date()
    except ValueError:
        start_date = date.today()
        end_date = date.today()

    multi_day = start_date != end_date

    try:
        with open(DATA_FILE, "r") as f:
            for line in f:
                parts = [p.strip() for p in line.split(";")]

                if len(parts) < 7:
                    continue

                try:
                    file_date_obj = datetime.strptime(parts[0], "%Y,%m,%d").date()
                except ValueError:
                    continue

                if start_date <= file_date_obj <= end_date:
                    time_display = parts[1].replace(",", ":")
                    date_display = file_date_obj.strftime("%d/%m")
                    label = f"{date_display} {time_display}" if multi_day else time_display

                    try:
                        voltage = float(parts[3])
                        temperature = float(parts[4])
                        load = int(parts[6])
                        status = parts[5].strip()

                        labels.append(label)
                        voltages.append(voltage)
                        temperatures.append(temperature)
                        loads.append(load)
                        statuses.append(status)
                        full_rows.append({
                            "label": label,
                            "voltage": voltage,
                            "temperature": temperature,
                            "load": load,
                            "status": status,
                        })
                    except (ValueError, IndexError):
                        continue

    except FileNotFoundError:
        print("Data file not found.")

    # Stats
    stats = {}
    if voltages:
        stats["voltage_min"] = round(min(voltages), 1)
        stats["voltage_max"] = round(max(voltages), 1)
        stats["voltage_avg"] = round(sum(voltages) / len(voltages), 1)
        stats["voltage_last"] = voltages[-1]
        stats["temp_last"] = temperatures[-1]
        stats["load_last"] = loads[-1]
        stats["load_avg"] = round(sum(loads) / len(loads), 1)
        stats["status_last"] = statuses[-1]
        stats["count"] = len(voltages)

        # Downsample for large datasets (keep chart performant)
        max_points = 500
        if len(labels) > max_points:
            step = len(labels) // max_points
            labels = labels[::step]
            voltages = voltages[::step]
            temperatures = temperatures[::step]
            loads = loads[::step]

    return render_template(
        'chartjs-example.html',
        labels=labels,
        voltages=voltages,
        temperatures=temperatures,
        loads=loads,
        stats=stats,
        start_date=start_arg,
        end_date=end_arg
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
