from Utils.mainWindow import MainWindow


def main():
    db_file = "DataBases\\db_filled.sqlite"
    mainWindow = MainWindow(db_file)
    mainWindow.window.show()
    mainWindow.app.exec()


if __name__ == "__main__":
    main()
