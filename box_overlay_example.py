from misc import CurverFitter

x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
y_data = [2.1, 4.3, 6.2, 8.5, 11.1, 14.0, 17.2, 21.0, 25.3, 30.1]  # Slight quadratic trend


fitter = CurverFitter(x_data,y_data)

x,y = fitter.fit_best_model()
print(x,y)
print(fitter.get_equation())



