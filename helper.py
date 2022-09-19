import tkinter as tk


class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', width=10):
        super().__init__(master, width=width)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    def __init__(self, *args):
        self.ecs = args

    def __call__(self, driver):
        for fn in self.ecs:
            try:
                res = fn(driver)
                if res:
                    return True
                    # Or return res if you need the element found
            except:
                pass
