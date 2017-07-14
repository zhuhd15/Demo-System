from face_detection import faceSimilarityCompare

def spider(img,caffemodel1,caffemodel2):
    '''
    Fetch the information of the  photo that may have relationship with the image input
    need to use the face detection system
    :param img: input image of a specific person
    :return:(dict){'personal information':,'similar images':}
    '''
    #codes here
    #the image you fetch from the website is img2
    min_size = 50
    img2 = []
    score = faceSimilarityCompare(caffemodel1,caffemodel2,img,img2,min_size)
    #return the relative information or image
    pass


def spiderRenew(information,image,caffemodel1,caffemodel2):
    '''
    Spider's daily work in renewing the existing database
    :param information(dict): personal information of the existing person
    :param image(list):       existing image in the database
    :param caffemodel:        caffemodel to compare the similarity between two pictures
    :return:(dict){'name':,'occupation':,'image':}
    '''
    min_size = 50
    image2 = []
    score = faceSimilarityCompare(caffemodel1,caffemodel2,image,image2,min_size)
    #dealing with score larger than a threshold
    pass