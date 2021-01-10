from database import PPPLDatabase
import gui

db_host = input('Database Host Name: ')
db_user = input('Database Username: ')
db_password = input('Database Password: ')
pppl_db = PPPLDatabase()
ui = gui.MainGUI(pppl_db)
pppl_db.connect_server(db_host, db_user, db_password)
ui.mainloop()
pppl_db.disconnect_server()