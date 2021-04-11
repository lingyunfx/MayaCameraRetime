__description__ = "The Animation Retime Tool for Maya"
__version__ = "0.2"
__author__ = "lingyun"
__author_email__ = "lingyunfx@88.com"
__url__ = "https://github.com/lingyunfx/MayaCameraRetime"


import view
reload(view)


def main():
    global local
    local = view.MainUI()
    local.show()


if __name__ == '__main__':
    main()
