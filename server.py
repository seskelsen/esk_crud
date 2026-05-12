from api.app import app

if __name__ == '__main__':
    # reloader_type='watchdog' evita o OSError: [WinError 10038] no shutdown
    # causado pelo reloader 'stat' do Werkzeug no Windows com Python 3.12+
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=True, reloader_type='watchdog')