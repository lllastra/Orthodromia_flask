from os import name
from flask import Flask, render_template, request, jsonify
import json
from shapely import from_wkt, points, get_coordinates, LineString
from functools import partial
from pyproj import Geod, Proj, transform


app= Flask(__name__)



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/test', methods=['POST'])
def test():
    output = request.get_json()

# Сбор данных из output в отдельные переменные (эту часть наверное можно сделать "по уму", но пока так)

    Point1 =from_wkt(output.partition('"FirstPoint":')[2].partition(",")[0].replace('"', ''))
    Point2 =from_wkt(output.partition('"SecondPoint":')[2].partition(",")[0].replace('"', ''))
    sk = output.partition('"SK":')[2].partition(",")[0].replace('"', '')
    Number_of_points = output.partition('"Number_of_points":')[2].partition("}")[0].replace('"', '')

 # Данные о системах координат для transform 
    P4284 = Proj(init='epsg:4284')
    P4326 = Proj(init='epsg:4326')

# Перевод данных из СК-42 в WGS84 если ввод был в СК-42
    if sk == "SK-42":

        x1,y1 = transform(P4284,P4326,  Point1.x, Point1.y)
        x2,y2 = transform(P4284,P4326,  Point2.x, Point2.y)
    else:
        x1,y1= Point1.x, Point1.y
        x2, y2 =Point2.x, Point2.y

# Инициализация переменных для создание дополнительных точек с помощью geod.npts
    lon1, lat1 = x1,y1
    lon2, lat2 = x2,y2
    n_extra_points = int(Number_of_points)

# Создание дополнительных точек

    geoid = Geod(ellps="WGS84")
    extra_points = geoid.npts(lon1, lat1, lon2, lat2, n_extra_points)


# Инициализация переменных и настройка transformer для перевода координат полученных точек 
# обратно в Ск-42 из WGS84 для отображения в окне результатов

    all_points = points(extra_points)

    proj_4284 = Proj(init="epsg:4284")
    proj_4326 = Proj(init="epsg:4326")
    transformer = partial(transform, proj_4326, proj_4284)



    list_of_final_points = []
    List_of_coordinates_of_final_points=[]


# Перевод координат полученных точек обратно в Ск-42 из WGS84 если для вводна был выбран СК-43
# Сбор полученных точек в лист

    if sk == {'SK': '1'}:

        if n_extra_points != 0:
            i = 0
            while i < n_extra_points:
                    list_of_final_points.append(
                            transformer(get_coordinates(all_points)[i][0], get_coordinates(all_points)[i][1]))
                    i += 1
    else:
        if n_extra_points != 0:
            i = 0
            while i < n_extra_points:
                    list_of_final_points.append((get_coordinates(all_points)[i][0], get_coordinates(all_points)[i][1]))
                    i += 1
        

    


# Получение координат для простроения MultiLineString 

    if n_extra_points!= 0:
        i=0
        while i<n_extra_points-1:
            List_of_coordinates_of_final_points.append((get_coordinates(all_points)[i].tolist(), get_coordinates(all_points)[i+1].tolist()))
            i += 1


# Добавление первой и последней точки введенных пользователем


    List_of_coordinates_of_final_points.insert(0,(get_coordinates(Point1)[0].tolist(), get_coordinates(all_points)[0].tolist()))
    List_of_coordinates_of_final_points.append((get_coordinates(all_points)[ n_extra_points - 1].tolist(), get_coordinates(Point2)[0].tolist()))

    list_of_final_points.insert(0,(Point1.x,Point1.y))
    list_of_final_points.append((Point2.x,Point2.y))

    # Создание Line для вывода в окне резуьтата

    Line = LineString(list_of_final_points)

    
    
    return json.dumps({'Line': str(Line),'coordinates_date':List_of_coordinates_of_final_points})


if __name__ == '__main__':
    app.run(debug=True, port=8000)