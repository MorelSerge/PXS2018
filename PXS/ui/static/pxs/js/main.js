$(document).ready(function () {
    $('#scale-chooser .option').click(function () {
        $('#scale-chooser .option').removeClass('selected');
        $(this).addClass('selected');
    });

    $('#map-close, #map-close a, #map-wrapper').click(function () {
        hideMap();
    });

    $('#map').click(function (e) {
        e.stopPropagation();
    });

    var map;
    var alertTimeout;
    var cantonGeoJSONLayer;
    var cityGeoJSONLayer;
    var removedCanton;
    var infoControl;
    var dataType = 'city';
    var currentSide;
    var drawnLayer;
    var drawButtonOptions;
    var cantonScores;
    var cityScores;

    if (window.location.hash) {
        if (['canton', 'city', 'area'].indexOf(window.location.hash.substr(1)) > -1) {
            dataType = window.location.hash.substr(1);
            $('#scale-chooser .option').each(function() {
                if ($(this).data('type') == dataType) {
                    $(this).addClass('selected');
                } else {
                    $(this).removeClass('selected');
                }
            });
        }
    }

    $('.map-image-wrapper').click(function() {
        currentSide = $(this).data('side');
        showMap();
    });

    $('#scale-chooser .option').click(function() {
        dataType = $(this).data('type');
    });

    var showAlert = function(alertText) {
        var alert = $('#alert');
        alert.text(alertText);
        if (alertTimeout) {
            clearTimeout(alertTimeout);
            alertTimeout = undefined;
        } else {
            alert.slideToggle();
        }
        alertTimeout = setTimeout(function() {
            alert.slideToggle();
            alertTimeout = undefined;
        }, 2000);
    }

    var loadPolygon = function(side, type, id) {
        if (type == 'city') {
            $(".map-image-wrapper[data-side=" + side + "]").css(
                'background-image', 'url(' + '/city/' + id + '/polygon)'
            );
        } else if (type == 'canton') {
            $(".map-image-wrapper[data-side=" + side + "]").css(
                'background-image', 'url(' + '/canton/' + id + '/polygon)'
            );
        }
        $(".map-image-wrapper[data-side=" + side + "] > .desc").hide()
    }

    var loadPolygonUrl = function(side, url) {
        $(".map-image-wrapper[data-side=" + side + "]").css(
            'background-image', 'url(' + url + ')'
        );
        $(".map-image-wrapper[data-side=" + side + "] > .desc").hide()
    }

    var showPolygonStats = function(side, url) {
        $.ajax({
            dataType: 'json',
            url: url,
            success: function (data) {
                $name = $('.name[data-side=' + side + '] > span');
                $name.hide();
                stats = $('.stats[data-side=' + side + ']');
                rank = stats.find('.stat[data-type=rank]');
                treeCoverage = stats.find('.stat[data-type=tree-coverage]');
                score = stats.find('.stat[data-type=score]');
                rank.find('.number').text(Math.round(data.tree_sparsity * 100));
                treeCoverage.find('.number').text(Math.round(data.tree_density * 100));
                score.find('.number').text(Math.round(data.score));
                rank.find('.description').text('percentage tree sparsity');
                score.find('.description').text('overall score');
            }
        })
    }

    var showStats = function(side, type, id) {
        if (type != 'city' && type != 'canton') return;
        $.ajax({
            dataType: 'json',
            url: '/' + (type == 'city' ? 'city' : 'canton') + '/' + id,
            success: function (data) {
                $name = $('.name[data-side=' + side + '] > span');
                $name.text(data.fields.name);
                $name.show();
                if (data.fields.has_mapping) {
                    stats = $('.stats[data-side=' + side + ']');
                    rank = stats.find('.stat[data-type=rank]');
                    treeCoverage = stats.find('.stat[data-type=tree-coverage]');
                    score = stats.find('.stat[data-type=score]');
                    rank.find('.number').text(data.fields.rank);
                    treeCoverage.find('.number').text(Math.round(data.fields.tree_density * 100));
                    score.find('.number').text(Math.round(data.fields.score));
                    if (type == 'city') {
                        rank.find('.description').text('place in city ranking');
                        score.find('.description').text('overall city score');
                    } else {
                        rank.find('.description').text('place in canton ranking');
                        score.find('.description').text('overall canton score');
                    }
                }
            }
        });
    }

    var showMap = function () {
        cityGeoJSONLayer.clearLayers();
        if (removedCanton !== undefined) {
            cantonGeoJSONLayer.addData(removedCanton);
            removedCanton = undefined;
        }
        cantonGeoJSONLayer.eachLayer(function(layer) {
            layer.clicked = false;
            cantonGeoJSONLayer.resetStyle(layer);
        });
        // remove drawn layer if possible
        if (drawnLayer) {
            map.removeLayer(drawnLayer);
            map.pm.disableDraw();
        }
        if (dataType == 'area') {
            map.pm.addControls(drawButtonOptions);
        } else {
            map.pm.removeControls();
        }
        map.setView([46.7985624, 8.2319736], 8, {"animate": false});
        $('#map-wrapper').show();
        map.invalidateSize();
    }

    var hideMap = function() {
        $('#map-wrapper').hide();
    };

    function percentRank(array, n) {
        var L = 0;
        var S = 0;
        var N = array.length
    
        for (var i = 0; i < array.length; i++) {
            if (array[i] < n) {
                L += 1
            } else if (array[i] === n) {
                S += 1
            } else {
    
            }
        }
    
        var pct = (L + (0.5 * S)) / N
    
        return pct
    }

    var getFillColor = function (score, allScores) {
        var colors = [
            '#f7fcf5',
            '#e5f5e0',
            '#c7e9c0',
            '#a1d99b',
            '#74c476',
            '#41ab5d',
            '#238b45',
            '#006d2c',
            '#00441b'
        ];
        var rank = percentRank(allScores, score);
        var idx = Math.round(rank * 10 - 2);
        idx = idx < 0 ? 0 : idx;
        /*var idx = score > 130 ? 8 :
                score  > 105 ? 7 :
                score > 90 ? 6 :
                score > 80 ? 5 :
                score > 70 ? 4 :
                score > 60 ? 3 :
                score > 50 ? 2 :
                score > 40 ? 1 :
                              0;*/
        return colors[idx];
    }

    var styleCityFeature = function (feature) {
        if (feature.properties.name=='Veyrier') {
            console.log('hi');
        }
        return {
            fillColor: feature.properties.has_mapping ? getFillColor(feature.properties.score, cityScores) : '#E5E9F2',
            color: '#47525E',
            dashArray: '3',
            fillOpacity: 0.7,
            weight: 2,
            opacity: 1
        };
    }

    var styleCantonFeature = function (feature) {
        return {
            fillColor: feature.properties.has_mapping ? getFillColor(feature.properties.score, cantonScores) : '#E5E9F2',
            color: '#47525E',
            dashArray: '5',
            fillOpacity: 0.7,
            weight: 2,
            opacity: 1
        };
    }

    var highlightCityFeature = function (e) {
        if (!e.target.clicked) {
            if (dataType == 'city' && !e.target.feature.properties.has_mapping) {
                e.target.setStyle({
                    dashArray: '',
                    weight: 4,
                    color: '#b50c0c'
                });
            } else {
                e.target.setStyle({
                    dashArray: '',
                    weight: 4,
                    color: '#47525E'
                });
            }
        }

        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
            e.target.bringToFront();
        }

        infoControl.update(e.target.feature.properties.name);
    }

    var highlightCantonFeature = function (e) {
        if (!e.target.clicked) {
            if (dataType == 'canton' && !e.target.feature.properties.has_mapping) {
                e.target.setStyle({
                    dashArray: '',
                    weight: 4,
                    color: '#b50c0c'
                });
            } else {
                e.target.setStyle({
                    dashArray: '',
                    weight: 4,
                    color: '#47525E'
                });
            }
        }

        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
            e.target.bringToFront();
        }

        infoControl.update(e.target.feature.properties.name);
    }

    var resetCityHighlight = function (e) {
        if (!e.target.clicked) {
            cityGeoJSONLayer.resetStyle(e.target);
        }
        infoControl.update();
    }

    var resetCantonHighlight = function (e) {
        if (!e.target.clicked) {
            cantonGeoJSONLayer.resetStyle(e.target);
        }
        infoControl.update();
    }

    var zoomToCityFeature = function (e) {
        console.log(e.target.feature.properties);
        if (e.target.clicked && dataType == 'city') {
            if (e.target.feature.properties.has_mapping) {
                // TODO: show this city stats
                console.log('CHOSE CITY ' + e.target.feature.properties.name + ' FOR SIDE ' + currentSide);
                loadPolygon(currentSide, 'city', e.target.feature.properties.pk);
                showStats(currentSide, 'city', e.target.feature.properties.pk);
                hideMap();
            } else {
                showAlert('This city has not been mapped yet');
            }
        } else {
            // reset other city click status
            cityGeoJSONLayer.eachLayer(function(layer) {
                layer.clicked = false;
                cityGeoJSONLayer.resetStyle(layer);
            });
            // set this one to clicked
            e.target.clicked = true;

            // fit to bounds
            map.fitBounds(e.target.getBounds());

            // set click status style
            if (e.target.feature.properties.has_mapping) {
                e.target.setStyle({
                    dashArray: '',
                    weight: 4,
                    color: '#00441b'
                });
            } else {
                if (dataType == 'city') {
                    e.target.setStyle({
                        dashArray: '',
                        weight: 4,
                        color: '#b50c0c'
                    });
                }
            }
        }
    }

    var zoomToCantonFeature = function (e) {
        if (e.target.clicked && dataType == 'canton') {
            if (e.target.feature.properties.has_mapping) {
                console.log('CHOSE CANTON ' + e.target.feature.properties.name + ' FOR SIDE ' + currentSide);
                loadPolygon(currentSide, 'canton', e.target.feature.properties.pk);
                showStats(currentSide, 'canton', e.target.feature.properties.pk);
                hideMap();
            } else {
                showAlert('This canton has not been mapped yet');
            }
        } else {
            // reset other canton click status
            cantonGeoJSONLayer.eachLayer(function(layer) {
                layer.clicked = false;
                cantonGeoJSONLayer.resetStyle(layer);
            });
            // set this one to clicked
            e.target.clicked = true;
            // fit to bounds
            map.fitBounds(e.target.getBounds());
            // set click status style
            if (e.target.feature.properties.has_mapping) {
                e.target.setStyle({
                    dashArray: '',
                    weight: 4,
                    color: '#00441b'
                });
            } else {
                if (dataType == 'canton') {
                    e.target.setStyle({
                        dashArray: '',
                        weight: 4,
                        color: '#b50c0c'
                    });
                }
            }

            if (dataType != 'canton') {
                // remove all cities
                cityGeoJSONLayer.clearLayers();
                // reshow the previously removed canton
                if (removedCanton !== undefined) {
                    cantonGeoJSONLayer.addData(removedCanton);
                    removedCanton = undefined;
                }
                // load this city geojson
                var cantonId = e.target.feature.properties["pk"];
                cityScores = []
                $.ajax({
                    dataType: 'json',
                    url: '/canton/' + cantonId + '/cities',
                    success: function (data) {
                        $(data.features).each(function (key, data) {
                            if (data.properties.score) {
                                cityScores.push(data.properties.score);
                            }
                        });
                        $(data.features).each(function (key, data) {
                            cityGeoJSONLayer.addData(data);
                        });
                        removedCanton = e.target.feature;
                        cantonGeoJSONLayer.removeLayer(e.target);
                    }
                })
            }
        }
    }

    var onEachCityFeature = function (feature, layer) {
        layer.on({
            mouseover: highlightCityFeature,
            mouseout: resetCityHighlight,
            click: zoomToCityFeature
        });
    }

    var onEachCantonFeature = function (feature, layer) {
        layer.on({
            mouseover: highlightCantonFeature,
            mouseout: resetCantonHighlight,
            click: zoomToCantonFeature
        });
    }

    var initiateDrawer = function() {
        // define toolbar options
        drawButtonOptions = {
            position: 'topleft', // toolbar position, options are 'topleft', 'topright', 'bottomleft', 'bottomright'
            drawRectangle: true, // adds button to draw a rectangle
            drawPolygon: true, // adds button to draw a polygon
            drawCircle: false, // adds button to draw a cricle
            editMode: false,
            cutPolygon: false,
            removalMode: false,
            drawMarker: false,
            drawPolyline: false
        };
        var drawOptions = {
            snappable: false,
            allowSelfIntersection: false,
            templineStyle: {
                color: '#00441b'
            },
            hintlineStyle: {
                color: '#00441b',
                dashArray: [5, 5]
            },
            finishOnDoubleClick: true
        };
        map.pm.setPathOptions({
            color: '#00441b',
            fillColor: '#47525E',
            fillOpacity: 0.25
        });
        map.pm.enableDraw('Poly', drawOptions);
        map.pm.disableDraw('Poly');
        map.pm.enableDraw('Rectangle', drawOptions);
        map.pm.disableDraw('Rectangle');
        map.on('pm:drawstart', function(e) {
            drawnLayer = e.workingLayer;
        });
        map.on('pm:create', function(e) {
            area = LGeo.area(e.layer);
            if (area < 10000) { // Let's require at least 10,000 square meters
                map.removeLayer(e.layer);
                showAlert('The selected area is not big enough')
            } else {
                drawnLayer = e.layer;
                geoJSON = JSON.stringify(e.layer.toGeoJSON());
                showPolygonStats(currentSide, polygonGeoJsonUrl + '/stats?geojson=' + encodeURIComponent(geoJSON));
                loadPolygonUrl(currentSide, polygonGeoJsonUrl + '?geojson=' + encodeURIComponent(geoJSON));
                hideMap();
            }
        });
    }

    var initiateMap = function () {
        map = L.map('map').setView([46.7985624, 8.2319736], 8);

        L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
            attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
            maxZoom: 18,
            minZoom: 8,
            id: 'mapbox.light',
            accessToken: 'pk.eyJ1Ijoidmx1ZiIsImEiOiJjamVpbDMxamEwYmI3MnFuNW8ybnI0NHdyIn0.dxuL9WvARgL4FFbSt-KUqA'
        }).addTo(map);

        cityGeoJSONLayer = L.geoJSON(null, {
            style: styleCityFeature,
            onEachFeature: onEachCityFeature,
            pmIgnore: true
        }).addTo(map);

        cantonGeoJSONLayer = L.geoJSON(null, {
            style: styleCantonFeature,
            onEachFeature: onEachCantonFeature,
            pmIgnore: true
        }).addTo(map);

        infoControl = L.control({pmIgnore: true});
        infoControl.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'info');
            this.update();
            return this._div;
        };
        infoControl.update = function (name) {
            $(this._div).html('<h4>' + (name ? name : 'Hover a shape to see details') + '</h4>');
        }
        infoControl.addTo(map);

        initiateDrawer();

        $.ajax({
            dataType: 'json',
            url: cantonsGeoJsonUrl,
            success: function (data) {
                cantonScores = []
                $(data.features).each(function (key, data) {
                    if (data.properties.score) {
                        cantonScores.push(data.properties.score);
                    }
                });
                $(data.features).each(function (key, data) {
                    cantonGeoJSONLayer.addData(data);
                });
            }
        })
    };

    initiateMap();
});