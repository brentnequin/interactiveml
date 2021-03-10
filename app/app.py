# for deploying: https://flask.palletsprojects.com/en/1.1.x/deploying/mod_wsgi/

from flask import Flask, render_template, request, session
from flask.testing import FlaskClient

import os
import json
import random

import plotly
import plotly.graph_objects as go

from sklearn.cluster import KMeans
from sklearn_extra.cluster import KMedoids

import numpy as np

app = Flask(__name__)

app.secret_key = os.urandom(24)

width = 800

def update_plot():
    
    fig = go.Figure(
            data = [
                go.Scatter(
                    x=session.get('x_train'),
                    y=session.get('y_train'),
                    mode='markers',
                    marker_color='grey',
                    marker_symbol='circle',
                    name='Train Data',
                    marker_size=10,
                    marker_line_width=1.5,
                ),
                go.Scatter(
                    x=session.get('x_test'),
                    y=session.get('y_test'),
                    mode='markers',
                    marker_color='grey',
                    marker_symbol='square',
                    name='Test Data',
                    marker_size=10,
                    marker_line_width=1.5,
                ),
                go.Scatter(
                    x=session.get('x_center'),
                    y=session.get('y_center'),
                    mode='markers',
                    marker_color='red',
                    marker_symbol='star',
                    name="Cluster Centers",
                    marker_size=10,
                    marker_line_width=1.5,
                )],
            layout=go.Layout(
                height=width, width=width+60,
                xaxis_title="x", yaxis_title="y",
                xaxis_fixedrange=True, yaxis_fixedrange=True,
                showlegend=True,
                margin=dict(r=160),
            )
        )

    if session.get('x_center'):
        if session.get('x_train'): fig['data'][0]['marker']['color'] = session.get('train_labels')
        if session.get('x_test'): fig['data'][1]['marker']['color'] = session.get('test_labels')
    return fig
    
@app.route('/')
def home():

    session['x_train'] = [1,2,2,5,5,6]
    session['y_train'] = [2,1,2,5,6,5]
    session['train_labels'] = []
    session['x_test'] = []
    session['y_test'] = []
    session['test_labels'] = []
    session['x_center'] = []
    session['y_center'] = []

    return render_template('index.html', plot=json.dumps(update_plot(), cls=plotly.utils.PlotlyJSONEncoder))

@app.route('/addpoint', methods = ['POST'])
def addpoint():
    jsdata = request.form['point_data']
    point = json.loads(jsdata)
    
    if point['type'] == "train":
        session['x_train'] = session.get('x_train') + [point['x']]
        session['y_train'] = session.get('y_train') + [point['y']]
    
    if point['type'] == "test":
        session['x_test'] = session.get('x_test') + [point['x']]
        session['y_test'] = session.get('y_test') + [point['y']]

    return jsdata

@app.route('/algorithmrun', methods = ['POST'])
def algorithmrun():
    jsdata = request.form['algorithm_data']
    algorithm_data = json.loads(jsdata)
    
    if algorithm_data['algorithm'] == 'kmeans':
        cluster = KMeans(n_clusters=int(algorithm_data['k']), random_state=random.randint(0, int(algorithm_data['k']))).fit(np.column_stack((session.get('x_train'), session.get('y_train'))))
    if algorithm_data['algorithm'] == 'kmedoids':
        cluster = KMedoids(n_clusters=int(algorithm_data['k']), random_state=random.randint(0, int(algorithm_data['k']))).fit(np.column_stack((session.get('x_train'), session.get('y_train'))))
    
    session['x_center'] = (cluster.cluster_centers_[:,0]).tolist()
    session['y_center'] = (cluster.cluster_centers_[:,1]).tolist()
    session['train_labels'] = (cluster.labels_).tolist()
    if session.get('x_test'): session['test_labels'] = (cluster.predict(np.column_stack((session.get('x_test'), session.get('y_test'))))).tolist()
    
    return json.dumps(update_plot(), cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/clearplot', methods = ['POST'])
def clearplot():
    session['x_train'] = []
    session['y_train'] = []
    session['train_labels'] = []
    session['x_test'] = []
    session['y_test'] = []
    session['test_labels'] = []
    session['x_center'] = []
    session['y_center'] = []
    
    return json.dumps(update_plot(), cls=plotly.utils.PlotlyJSONEncoder)

debug = False
if __name__ == "__main__":
    app.run(debug=debug)
    
