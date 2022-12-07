import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import os

def getModel(file_name, parameters):

    __location__ = os.path.realpath(os.getcwd())

    #reviews = pd.read_csv(os.path.join(__location__, f'HotelProphet/{file_name}'))
    #reviews = pd.read_csv('ReviewData.csv')
    #print(reviews.head())
    #print(reviews.isna().any())
    reviews = pd.read_csv(file_name)
    print(reviews.corrwith(reviews.iloc[:, 0]).sort_values(ascending=False))
    print(reviews.isna().any())

    #0.27 correlation with late checkout and review - offer free late checkout to increase reviews
    #references = reviews[['Stayed_nights', 'Complaint_parking_av', 'Complaint_room', 'Rooms_booked', 'SunToThu_chkin', 'Chkin_early']]
    #references_plus = reviews[['Stayed_nights', 'Complaint_parking_av', 'Complaint_room', 'Rooms_booked', 'SunToThu_chkin', 'Chkin_early', 'BB', 'Bought_parking']]
    references_plusplus = reviews[parameters]
    scores = reviews.iloc[:, 0]

    #TODO:
    #One-hot encode the discrete data, eg room no

    X_train, X_test, y_train, y_test = train_test_split(references_plusplus, scores, test_size=0.2)

    regressor = LinearRegression()
    regressor.fit(X_train, y_train)

    print(regressor.score(X_train, y_train))
    print(regressor.score(X_test, y_test))

    return regressor, reviews.corrwith(reviews.iloc[:, 0]).abs().sort_values(ascending=False)

def main():
    getModel('E:/PythonStuff/HotelProphet/ReviewData.csv')

if __name__ == '__main__':
    main()