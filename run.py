from app import create_app
import os
from app.utils.scheduler_util import start_scheduler

app = create_app()
application = app

if __name__ == "__main__":

    # Prevent scheduler from running twice on Flask reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        scheduler = start_scheduler(app) 
        
    app.run(debug=True)