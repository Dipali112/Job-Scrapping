from sys import platform


def get_driver_name():
    """
    Compatibility function. Modern versions use direct API / TLS scraping
    and do not require external chromedriver binaries.
    """
    if platform in ['linux', 'linux2']:
        return 'chromedriver_linux'
    elif platform == 'darwin':
        return 'chromedriver_macOS'
    elif platform == 'win32':
        return 'chromedriver_windows.exe'
    return 'chromedriver'
