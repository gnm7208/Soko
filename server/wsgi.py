from server.app import create_app

app = create_app()

if __name__ == "__main__":
    port = app.config.get("PORT", 5000)
    debug = app.config.get("ENV") != "production"
    from server.extensions import socketio

    socketio.run(app, host="0.0.0.0", port=port, debug=debug)
