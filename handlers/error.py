from handler import Handler


class ErrorHandler(Handler):
    def get(self):
        self.render("error.html")
