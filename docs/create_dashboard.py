html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Saudi eVisa Automation Dashboard</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1600px; margin: 0 auto; }
        h1 { color: #333; margin-bottom: 30px; display: flex; align-items: center; gap: 10px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .stat-card h3 { color: #666; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }
        .stat-card .value { font-size: 36px; color: #2196F3; font-weight: bold; }
        .controls { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .btn-group { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
        button { background: #2196F3; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.3s; }
        button:hover { background: #1976D2; transform: translateY(-1px); }
        button:disabled { background: #ccc; cursor: not-allowed; transform: none; }
        .btn-orange { background: #FF9800; } .btn-orange:hover { background: #F57C00; }
        .btn-green { background: #4CAF50; } .btn-green:hover { background: #388E3C; }
        .btn-red { background: #f44336; } .btn-red:hover { background: #d32f2f; }
        .btn-gray { background: #666; } .btn-gray:hover { background: #555; }
        .btn-small { padding: 6px 12px; font-size: 12px; }
        .progress-bar { display: none; margin-top: 15px; }
        .progress-container { background: #e0e0e0; border-radius: 4px; height: 30px; position: relative; overflow: hidden; }
        .progress-fill { background: linear-gradient(90deg, #4CAF50, #8BC34A); height: 100%; width: 0%; transition: width 0.3s; }
        .progress-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 13px; font-weight: bold; color: #333; }
'''

with open('templates/dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Dashboard HTML created successfully!")
