
from flask.views import View

class Startup_view(View):

    def dispatch_request(self):
        return "startup_view"
