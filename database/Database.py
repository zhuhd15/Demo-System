

def databaseInit():
    #database init
    pass

def databaseFetch(img,name,occupation):
    ''' Fetch the information in a database
        input:  (list)img------the photo of this person
                (str)name-----the name of the person (empty list possible)
                (str)occuapation-----the job of the person (empty list possible)
        output: (dict) infomation ------personal information (name, pic, ....), empty dict if existing is False
                (list) hisInformation -----[last visit time:str, recent visit fequency]
                (bool) existing ------whether the information of this person is in this database
    '''
    pass

def databaseAppend(personalInformation,date):
    '''
    This function is used when the system gets the information from a NEW person
    :param personalInformation: (dict) {'img':list,'name':str,'occupation':str,''}
    :param date: (str) the date of the image fetch
    :return: None
    '''
    pass

def databaseSearch():
    '''
    During free time, intend to renew the information or fill the blanks in the system
    Need to deal with the frequency here(possibly one's information is never fetched on a website)
    :return: (dict)infomation: personal information (name, pic, ....),the blank in the dict need to be filled
                                or the information of a person that has not been renewed for a long time
    '''

def databaseRenew(personalInformation):
    '''
    renew the information in a database
    :param personalInformation(dict): the newest information needs to write in the database
    :return:None
    '''
    pass


if __name__=="__main__":
    databaseInit()