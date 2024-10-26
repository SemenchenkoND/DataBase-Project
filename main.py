from Utils.windows import MainWindow


def main():
    db_file = "DataBases\\DataBase.sqlite"
    mainWindow = MainWindow(db_file)
    mainWindow.window.show()
    mainWindow.app.exec()


if __name__ == "__main__":
    main()
