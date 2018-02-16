'''
        This is the main function of the whole system.

        There are two threads running in this system. The first thread is for interaction with users as well as
    appending data to the database, while the second often run at night to rebuild the whole database or to combine
    the data input and those existing in this database. The first thread also has a mini thread in it, to appending
    data whenever in need through the second small interface.
'''
from System import UIMain

if __name__ == '__main__':
    UIMain.SystemStart()