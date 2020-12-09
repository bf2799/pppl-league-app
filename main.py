from database import PPPLDatabase
import gui

pppl_db = PPPLDatabase()
a = gui.MainGUI(pppl_db)
pppl_db.connect_server('localhost', 'ben', 'benpassword123')
a.mainloop()
pppl_db.disconnect_server()