from qt import QApplication, QPalette


class Theme():
    def __init__(self):
        pass

    # def get_mode(self):
    #     # Check if dark mode is enabled
    #     is_dark_mode = darkdetect.isDark()
    #     return is_dark_mode

    def get_mode(self):
        """
        get_mode

        Args:
        """
        # Get the current application's instance
        app = QApplication.instance()
        if not app:
            raise RuntimeError("No QApplication instance found")

        # Access the application's palette
        palette = app.palette()
        # Check the background color lightness
        background_color = palette.color(QPalette.Window)
        is_dark_mode = background_color.lightness() < 128
        return "dark" if is_dark_mode else "light"

    def set_foreground(self, theme):
        """
        set_foreground

        Args:
            theme: Description of theme.
        """
        if theme == "dark":
            return 'white'
        if theme == "light":
            return 'black'

